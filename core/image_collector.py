"""Append mask images from the bundled opengate-imagecollector.blend."""

from __future__ import annotations

import os

import bpy

from .mask_combos import (
    OPENGATE_MASK_FILE_KEY,
    OPENGATE_MASK_FLAGS_KEY,
    OPENGATE_MASK_SAFEZONE_FILE_KEY,
    OPENGATE_MASK_SAFEZONES_KEY,
    canonical_combo_filename,
    is_opengate_mask_file,
    is_safezone_variant_file,
    iter_combo_filename_candidates,
    mask_flags_from_combo_filename,
    mask_image_abspath,
    resolve_mask_image_filename,
)
from .paths import extension_asset_abspath

COLLECTOR_BLEND_PARTS = ("assets", "shader", "opengate-imagecollector.blend")
COLLECTOR_OBJECT_NAME = "opengate-imagecollector"
COLLECTOR_MATERIAL_NAME = "opengate-mask"
OPENGATE_BG_GL_LOADED_KEY = "opengate_bg_gl_loaded"

_COLLECTOR_IMAGES_TAGGED = False


def collector_blend_abspath() -> str:
    return extension_asset_abspath(*COLLECTOR_BLEND_PARTS)


def image_is_usable(image: bpy.types.Image) -> bool:
    """Fast check — never touch image.pixels (multi‑megapixel arrays are expensive)."""
    if image.packed_file is not None:
        return True
    try:
        if image.size[0] > 0 and image.size[1] > 0:
            return True
    except (AttributeError, TypeError):
        pass
    if image.has_data:
        return True
    if image.filepath:
        return os.path.isfile(bpy.path.abspath(image.filepath))
    return False


def prepare_image_for_background(image: bpy.types.Image) -> None:
    """Upload to GPU once per image — not on every slider tick."""
    if image.get(OPENGATE_BG_GL_LOADED_KEY):
        return
    if hasattr(image, "gl_load"):
        try:
            image.gl_load()
            image[OPENGATE_BG_GL_LOADED_KEY] = True
        except RuntimeError:
            pass


def _hide_collector_object(obj: bpy.types.Object) -> None:
    obj.hide_set(True)
    obj.hide_render = True
    if hasattr(obj, "hide_viewport"):
        obj.hide_viewport = True


def _append_collector_object() -> bpy.types.Object:
    blend_path = collector_blend_abspath()
    if not os.path.isfile(blend_path):
        raise FileNotFoundError(f"OpenGate image collector not found: {blend_path}")

    if COLLECTOR_OBJECT_NAME in bpy.data.objects:
        return bpy.data.objects[COLLECTOR_OBJECT_NAME]

    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if COLLECTOR_OBJECT_NAME not in data_from.objects:
            raise RuntimeError(
                f'Object "{COLLECTOR_OBJECT_NAME}" missing in {blend_path}'
            )

        mask_images = [
            name for name in data_from.images if is_opengate_mask_file(name)
        ]
        data_to.images = mask_images
        data_to.objects = [COLLECTOR_OBJECT_NAME]

    obj = bpy.data.objects.get(COLLECTOR_OBJECT_NAME)
    if obj is None:
        raise RuntimeError(f'Failed to append "{COLLECTOR_OBJECT_NAME}" from {blend_path}')

    return obj


def _link_collector_to_scene(scene: bpy.types.Scene, obj: bpy.types.Object) -> None:
    if obj.name not in scene.objects:
        scene.collection.objects.link(obj)
    _hide_collector_object(obj)


def _tag_mask_image(
    image: bpy.types.Image,
    filename: str,
    mask_flags: int,
) -> None:
    image[OPENGATE_MASK_FILE_KEY] = filename
    image[OPENGATE_MASK_FLAGS_KEY] = int(mask_flags)
    safezone_file = filename if is_safezone_variant_file(filename) else ""
    image[OPENGATE_MASK_SAFEZONE_FILE_KEY] = safezone_file
    image[OPENGATE_MASK_SAFEZONES_KEY] = bool(safezone_file)


def _fix_collector_image(image: bpy.types.Image, filename: str) -> None:
    if image.packed_file is not None:
        return

    abs_path = mask_image_abspath(filename)
    if os.path.isfile(abs_path):
        image.filepath = abs_path
        if not image_is_usable(image):
            image.reload()


def refresh_collector_images() -> None:
    """Retag mask images once after the collector blend is appended."""
    global _COLLECTOR_IMAGES_TAGGED
    for image in bpy.data.images:
        filename = image.name
        if not is_opengate_mask_file(filename):
            basename = os.path.basename(image.filepath.replace("\\", "/")) if image.filepath else ""
            if is_opengate_mask_file(basename):
                filename = basename
            else:
                continue

        mask_flags = mask_flags_from_combo_filename(filename)
        if mask_flags is None:
            continue

        _tag_mask_image(image, filename, mask_flags)
        _fix_collector_image(image, filename)

    _COLLECTOR_IMAGES_TAGGED = True


def ensure_image_collector(scene: bpy.types.Scene) -> bpy.types.Object:
    """Append and link the collector object so mask images stay in memory."""
    global _COLLECTOR_IMAGES_TAGGED
    was_new = COLLECTOR_OBJECT_NAME not in bpy.data.objects
    obj = _append_collector_object()
    _link_collector_to_scene(scene, obj)
    if was_new or not _COLLECTOR_IMAGES_TAGGED:
        refresh_collector_images()
    return obj


def _is_collector_mask_image(image: bpy.types.Image) -> bool:
    tagged = image.get(OPENGATE_MASK_FILE_KEY)
    if isinstance(tagged, str) and is_opengate_mask_file(tagged):
        return True
    if is_opengate_mask_file(image.name):
        return True
    if image.filepath:
        basename = os.path.basename(image.filepath.replace("\\", "/"))
        if is_opengate_mask_file(basename):
            return True
    return False


def _collector_materials(obj: bpy.types.Object) -> list[bpy.types.Material]:
    materials: list[bpy.types.Material] = []
    if obj.type != "MESH":
        return materials
    for slot in obj.material_slots:
        if slot.material is not None and slot.material not in materials:
            materials.append(slot.material)
    return materials


def _remove_orphan_collector_materials(
    materials: list[bpy.types.Material],
) -> None:
    by_name = bpy.data.materials.get(COLLECTOR_MATERIAL_NAME)
    if by_name is not None and by_name not in materials:
        materials.append(by_name)

    for material in materials:
        if material.users == 0:
            bpy.data.materials.remove(material)


def remove_image_collector() -> bool:
    """Remove the appended collector object and unused OpenGate mask images."""
    global _COLLECTOR_IMAGES_TAGGED
    removed_object = False
    materials: list[bpy.types.Material] = []

    obj = bpy.data.objects.get(COLLECTOR_OBJECT_NAME)
    if obj is not None:
        materials = _collector_materials(obj)
        mesh = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        removed_object = True

    _remove_orphan_collector_materials(materials)

    for image in list(bpy.data.images):
        if image.users != 0 or not _is_collector_mask_image(image):
            continue
        bpy.data.images.remove(image)

    _COLLECTOR_IMAGES_TAGGED = False
    return removed_object


def resolve_collector_image_name(
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> str | None:
    """Find an appended image datablock name for the active mask flags."""
    preferred = resolve_mask_image_filename(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    if preferred is not None and preferred in bpy.data.images:
        return preferred

    if show_safezones:
        return preferred

    for candidate in iter_combo_filename_candidates(mask_flags):
        if candidate in bpy.data.images:
            return candidate

    return canonical_combo_filename(mask_flags)


def get_mask_image_from_collector(
    scene: bpy.types.Scene,
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> bpy.types.Image | None:
    ensure_image_collector(scene)

    filename = resolve_collector_image_name(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    if filename is None:
        return None

    image = bpy.data.images.get(filename)
    if image is None:
        return None

    if not image_is_usable(image):
        _fix_collector_image(image, filename)

    flags = mask_flags_from_combo_filename(filename)
    if flags is not None:
        _tag_mask_image(image, filename, flags)

    if not image_is_usable(image):
        return None

    return image
