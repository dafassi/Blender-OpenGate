"""Camera background images for OpenGate framing overlays."""

from __future__ import annotations

import json
import os
import re

import bpy

from .image_collector import (
    get_mask_image_from_collector,
    image_is_usable,
    prepare_image_for_background,
    refresh_collector_images,
)
from .mask_combos import (
    BACKUP_PROP_KEY,
    OPENGATE_ACTIVE_FLAGS_KEY,
    OPENGATE_ACTIVE_SAFEZONE_FILE_KEY,
    OPENGATE_ACTIVE_SAFEZONES_KEY,
    OPENGATE_MASK_FILE_KEY,
    describe_mask_combo,
    is_opengate_mask_file,
    resolve_mask_image_filename,
    resolve_safezone_filename,
)
from .masks import has_active_framing_mask

_BG_ENTRY_KEYS = (
    "alpha",
    "display_depth",
    "frame_method",
    "offset",
    "rotation",
    "scale",
)

_NAME_SUFFIX_RE = re.compile(r"^(.+\.png)\.(\d+)$")


def _image_basename(image: bpy.types.Image) -> str:
    if image.filepath:
        return os.path.basename(image.filepath.replace("\\", "/"))
    return os.path.basename(image.name)


def _opengate_mask_filename(image: bpy.types.Image) -> str | None:
    tagged = image.get(OPENGATE_MASK_FILE_KEY)
    if isinstance(tagged, str) and is_opengate_mask_file(tagged):
        return tagged

    if is_opengate_mask_file(image.name):
        return image.name

    basename = _image_basename(image)
    if is_opengate_mask_file(basename):
        return basename

    match = _NAME_SUFFIX_RE.match(image.name)
    if match and is_opengate_mask_file(match.group(1)):
        return match.group(1)

    return None


def _is_opengate_entry(entry: bpy.types.CameraBackgroundImage) -> bool:
    image = entry.image
    if image is None:
        return False
    return _opengate_mask_filename(image) is not None


def _serialize_bg_entry(entry: bpy.types.CameraBackgroundImage) -> dict:
    data: dict = {}
    for key in _BG_ENTRY_KEYS:
        if not hasattr(entry, key):
            continue
        value = getattr(entry, key)
        if hasattr(value, "to_tuple"):
            data[key] = list(value.to_tuple())
        else:
            data[key] = value

    if entry.image is not None:
        data["image_name"] = entry.image.name
        filepath = bpy.path.abspath(entry.image.filepath)
        if filepath:
            data["image_filepath"] = filepath
    return data


def _apply_bg_entry(
    entry: bpy.types.CameraBackgroundImage,
    data: dict,
) -> None:
    image_name = data.get("image_name")
    image_filepath = data.get("image_filepath")
    image = None
    if image_name and image_name in bpy.data.images:
        image = bpy.data.images[image_name]
    elif image_filepath and os.path.isfile(image_filepath):
        image = bpy.data.images.load(image_filepath, check_existing=True)

    entry.image = image

    for key in _BG_ENTRY_KEYS:
        if key not in data or not hasattr(entry, key):
            continue
        value = data[key]
        if key == "offset" and hasattr(value, "__iter__"):
            entry.offset = value
        else:
            setattr(entry, key, value)


def _active_safezone_file(
    mask_flags: int,
    *,
    show_safezones: bool,
    platform_preset_id: str,
) -> str:
    return resolve_safezone_filename(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    ) or ""


def _store_active_mask_state(
    cam_data: bpy.types.Camera,
    mask_flags: int,
    *,
    show_safezones: bool,
    platform_preset_id: str,
) -> None:
    cam_data[OPENGATE_ACTIVE_FLAGS_KEY] = int(mask_flags)
    cam_data[OPENGATE_ACTIVE_SAFEZONE_FILE_KEY] = _active_safezone_file(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    cam_data[OPENGATE_ACTIVE_SAFEZONES_KEY] = bool(show_safezones)


def _configure_opengate_entry(
    entry: bpy.types.CameraBackgroundImage,
    image: bpy.types.Image,
    opacity: float,
    *,
    prepare_gpu: bool = True,
) -> None:
    if prepare_gpu:
        prepare_image_for_background(image)
    entry.image = image
    entry.alpha = opacity
    entry.display_depth = "FRONT"
    entry.frame_method = "FIT"
    if hasattr(entry, "source"):
        entry.source = "IMAGE"
    if hasattr(entry, "show_on_foreground"):
        entry.show_on_foreground = True


def _update_opengate_entry(
    cam_data: bpy.types.Camera,
    image: bpy.types.Image,
    opacity: float,
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> None:
    """Update the existing OpenGate background slot without clearing the list."""
    entry = _get_opengate_bg_entry(cam_data)
    image_changed = entry is None or entry.image != image

    if entry is None:
        entry = cam_data.background_images.new()

    _configure_opengate_entry(
        entry,
        image,
        opacity,
        prepare_gpu=image_changed,
    )
    cam_data.show_background_images = True
    _store_active_mask_state(
        cam_data,
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )


def _backup_camera_backgrounds(cam_data: bpy.types.Camera) -> None:
    if BACKUP_PROP_KEY in cam_data:
        return

    entries = [
        _serialize_bg_entry(entry)
        for entry in cam_data.background_images
        if not _is_opengate_entry(entry)
    ]
    payload = {
        "show_background_images": bool(cam_data.show_background_images),
        "entries": entries,
    }
    cam_data[BACKUP_PROP_KEY] = json.dumps(payload)


def _restore_camera_backgrounds(cam_data: bpy.types.Camera) -> None:
    backup_raw = cam_data.get(BACKUP_PROP_KEY)
    _remove_opengate_entries(cam_data)

    if OPENGATE_ACTIVE_FLAGS_KEY in cam_data:
        del cam_data[OPENGATE_ACTIVE_FLAGS_KEY]

    if OPENGATE_ACTIVE_SAFEZONES_KEY in cam_data:
        del cam_data[OPENGATE_ACTIVE_SAFEZONES_KEY]

    if OPENGATE_ACTIVE_SAFEZONE_FILE_KEY in cam_data:
        del cam_data[OPENGATE_ACTIVE_SAFEZONE_FILE_KEY]

    if not backup_raw:
        if len(cam_data.background_images) == 0:
            cam_data.show_background_images = False
        return

    payload = json.loads(backup_raw)
    cam_data.background_images.clear()
    for entry_data in payload.get("entries", []):
        entry = cam_data.background_images.new()
        _apply_bg_entry(entry, entry_data)

    cam_data.show_background_images = bool(
        payload.get("show_background_images", False)
    )
    del cam_data[BACKUP_PROP_KEY]


def _apply_opengate_background(
    cam_data: bpy.types.Camera,
    image: bpy.types.Image,
    opacity: float,
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> None:
    """First-time setup: backup user backgrounds, then show OpenGate overlay."""
    _backup_camera_backgrounds(cam_data)
    cam_data.background_images.clear()

    entry = cam_data.background_images.new()
    _configure_opengate_entry(entry, image, opacity, prepare_gpu=True)
    cam_data.show_background_images = True
    _store_active_mask_state(
        cam_data,
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )


def _load_mask_image(
    mask_flags: int,
    scene: bpy.types.Scene,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> bpy.types.Image:
    image = get_mask_image_from_collector(
        scene,
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    if image is not None:
        return image

    combo = describe_mask_combo(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    raise FileNotFoundError(f"OpenGate mask image unavailable: {combo}")


def _get_opengate_bg_entry(
    cam_data: bpy.types.Camera,
) -> bpy.types.CameraBackgroundImage | None:
    for entry in cam_data.background_images:
        if _is_opengate_entry(entry):
            return entry
    return None


def mask_background_matches_flags(
    cam_data: bpy.types.Camera,
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> bool:
    if not cam_data.show_background_images:
        return False

    if cam_data.get(OPENGATE_ACTIVE_FLAGS_KEY) != int(mask_flags):
        return False

    expected_safezone_file = _active_safezone_file(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    active_safezone_file = str(cam_data.get(OPENGATE_ACTIVE_SAFEZONE_FILE_KEY) or "")
    if active_safezone_file != expected_safezone_file:
        return False

    entry = _get_opengate_bg_entry(cam_data)
    if entry is None or entry.image is None:
        return False

    if not image_is_usable(entry.image):
        return False

    expected_filename = resolve_mask_image_filename(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    return _opengate_mask_filename(entry.image) == expected_filename


def refresh_opengate_mask_images() -> None:
    """Refresh appended collector images after file load."""
    refresh_collector_images()


def mask_background_active(cam_data: bpy.types.Camera) -> bool:
    for entry in cam_data.background_images:
        if _is_opengate_entry(entry) and entry.image is not None:
            return True
    return False


def _remove_opengate_entries(cam_data: bpy.types.Camera) -> None:
    for index in range(len(cam_data.background_images) - 1, -1, -1):
        entry = cam_data.background_images[index]
        if entry.image is None or _is_opengate_entry(entry):
            cam_data.background_images.remove(entry)


def sync_opengate_background_opacity(
    settings,
    scene: bpy.types.Scene,
    *,
    camera: bpy.types.Object | None = None,
) -> None:
    """Fast path for mask opacity slider — alpha only, no image reload."""
    if camera is None:
        from .camera_target import get_target_camera

        camera = get_target_camera(settings, scene)

    if camera is None or camera.type != "CAMERA":
        return

    if not (
        settings.show_mask
        and has_active_framing_mask(settings)
        and settings.mask_flags > 0
    ):
        return

    entry = _get_opengate_bg_entry(camera.data)
    if entry is None:
        sync_opengate_background(settings, scene, camera=camera)
        return

    opacity = float(settings.mask_opacity)
    if abs(entry.alpha - opacity) > 1e-6:
        entry.alpha = opacity


def sync_opengate_background(
    settings,
    scene: bpy.types.Scene,
    *,
    camera: bpy.types.Object | None = None,
) -> None:
    """Apply, update, or restore camera background images from OpenGate settings."""
    if camera is None:
        from .camera_target import get_target_camera

        camera = get_target_camera(settings, scene)

    if camera is None or camera.type != "CAMERA":
        return

    cam_data = camera.data
    should_show = (
        settings.show_mask
        and has_active_framing_mask(settings)
        and settings.mask_flags > 0
    )

    if not should_show:
        _restore_camera_backgrounds(cam_data)
        return

    mask_flags = int(settings.mask_flags)
    show_safezones = bool(getattr(settings, "show_safezones", False))
    platform_preset_id = str(getattr(settings, "platform_preset", "NONE"))
    opacity = float(settings.mask_opacity)

    if mask_background_matches_flags(
        cam_data,
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    ):
        entry = _get_opengate_bg_entry(cam_data)
        if entry is not None and abs(entry.alpha - opacity) <= 1e-6:
            return
        if entry is not None:
            entry.alpha = opacity
            cam_data.show_background_images = True
            return

    image = _load_mask_image(
        mask_flags,
        scene,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )

    if BACKUP_PROP_KEY in cam_data and _get_opengate_bg_entry(cam_data) is not None:
        _update_opengate_entry(
            cam_data,
            image,
            opacity,
            mask_flags,
            show_safezones=show_safezones,
            platform_preset_id=platform_preset_id,
        )
        return

    _apply_opengate_background(
        cam_data,
        image,
        opacity,
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )


def clear_opengate_background(
    scene: bpy.types.Scene,
    settings,
    *,
    camera: bpy.types.Object | None = None,
) -> None:
    if camera is None:
        from .camera_target import get_target_camera

        camera = get_target_camera(settings, scene)

    if camera is None or camera.type != "CAMERA":
        return

    _restore_camera_backgrounds(camera.data)
