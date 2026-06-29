"""Sync OpenGate viewport display settings with the target camera."""

from __future__ import annotations

import json

import bpy

from . import masks
from .blender_compat import scene_safe_areas
from .camera_target import get_target_camera
from .render_format import canvas_pixel_size, combined_mask_safe_margins

SCENE_BACKUP_KEY = "opengate_scene_safe_areas_backup"
CAMERA_SHOW_BACKUP_KEY = "opengate_camera_safe_show_backup"
_UPDATING_FROM_CAMERA = False
_PENDING_SAFE_AREA_SCENES: set[str] = set()

# Safe-area crop uses the title slot; action stays at (0, 0).
_CROP_OUTLINE_SLOT = "title"
_ALL_MARGIN_ATTRS = ("title", "action", "title_center", "action_center")


def display_update_suppressed() -> bool:
    return _UPDATING_FROM_CAMERA


def _canvas_size_for_scene(scene: bpy.types.Scene) -> int:
    return canvas_pixel_size(scene.opengate.canvas_resolution)


def _read_scene_safe_margins(scene: bpy.types.Scene) -> dict:
    safe = scene_safe_areas(scene)
    return {
        "title": [float(safe.title[0]), float(safe.title[1])],
        "action": [float(safe.action[0]), float(safe.action[1])],
        "title_center": [float(safe.title_center[0]), float(safe.title_center[1])],
        "action_center": [float(safe.action_center[0]), float(safe.action_center[1])],
    }


def _write_scene_safe_margins(scene: bpy.types.Scene, margins: dict) -> None:
    safe = scene_safe_areas(scene)
    safe.title = margins["title"]
    safe.action = margins["action"]
    safe.title_center = margins["title_center"]
    safe.action_center = margins["action_center"]


def _read_camera_show_flags(cam_data: bpy.types.Camera) -> dict:
    return {
        "show_safe_areas": cam_data.show_safe_areas,
        "show_safe_center": cam_data.show_safe_center,
    }


def _write_camera_show_flags(cam_data: bpy.types.Camera, flags: dict) -> None:
    cam_data.show_safe_areas = bool(flags["show_safe_areas"])
    cam_data.show_safe_center = bool(flags["show_safe_center"])


def _tag_view3d_redraw() -> None:
    wm = bpy.context.window_manager
    if wm is None:
        return
    for window in wm.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def backup_safe_areas(scene: bpy.types.Scene, cam_data: bpy.types.Camera) -> None:
    if SCENE_BACKUP_KEY not in scene:
        scene[SCENE_BACKUP_KEY] = json.dumps(_read_scene_safe_margins(scene))
    if CAMERA_SHOW_BACKUP_KEY not in cam_data:
        cam_data[CAMERA_SHOW_BACKUP_KEY] = json.dumps(_read_camera_show_flags(cam_data))


def restore_safe_areas(scene: bpy.types.Scene, cam_data: bpy.types.Camera) -> None:
    if SCENE_BACKUP_KEY in scene:
        _write_scene_safe_margins(scene, json.loads(scene[SCENE_BACKUP_KEY]))
        del scene[SCENE_BACKUP_KEY]
    if CAMERA_SHOW_BACKUP_KEY in cam_data:
        _write_camera_show_flags(cam_data, json.loads(cam_data[CAMERA_SHOW_BACKUP_KEY]))
        del cam_data[CAMERA_SHOW_BACKUP_KEY]
    _tag_view3d_redraw()


def release_camera_safe_areas(
    scene: bpy.types.Scene,
    cam_data: bpy.types.Camera,
) -> None:
    """Turn off guides on a camera OpenGate no longer drives."""
    restore_safe_areas(scene, cam_data)
    cam_data.show_safe_areas = False
    cam_data.show_safe_center = False


def apply_safe_areas_from_masks(
    scene: bpy.types.Scene,
    cam_data: bpy.types.Camera,
    mask_flags: int,
) -> None:
    """Draw one safe-area rectangle for the combined active mask crop.

    With multiple masks, margins use the pixel intersection (tightest frame).
    Margins live on ``scene.safe_areas``; visibility on ``camera.show_safe_areas``.
    """
    active = list(masks.iter_active_masks(mask_flags))
    if not active:
        restore_safe_areas(scene, cam_data)
        cam_data.show_safe_areas = False
        cam_data.show_safe_center = False
        _tag_view3d_redraw()
        return

    backup_safe_areas(scene, cam_data)

    canvas_size = _canvas_size_for_scene(scene)
    safe = scene_safe_areas(scene)
    for attr in _ALL_MARGIN_ATTRS:
        setattr(safe, attr, (0.0, 0.0))

    setattr(
        safe,
        _CROP_OUTLINE_SLOT,
        combined_mask_safe_margins(active, canvas_size),
    )

    cam_data.show_safe_areas = True
    cam_data.show_safe_center = False
    cam_data.update_tag()
    _tag_view3d_redraw()


def push_passepartout_to_camera(settings, camera: bpy.types.Object | None) -> None:
    if camera is None or camera.type != "CAMERA":
        return
    cam_data = camera.data
    cam_data.show_passepartout = settings.show_passepartout
    cam_data.passepartout_alpha = settings.passepartout_alpha


def sync_camera_safe_areas(settings, scene: bpy.types.Scene) -> None:
    camera = get_target_camera(settings, scene)
    if camera is None or camera.type != "CAMERA":
        return
    apply_safe_areas_from_masks(scene, camera.data, settings.mask_flags)


def schedule_camera_safe_areas_sync(scene: bpy.types.Scene) -> None:
    """Apply safe areas on the next frame (safe during RNA property updates)."""
    if scene is None or scene.name in _PENDING_SAFE_AREA_SCENES:
        return

    scene_name = scene.name
    _PENDING_SAFE_AREA_SCENES.add(scene_name)

    def _apply() -> None:
        _PENDING_SAFE_AREA_SCENES.discard(scene_name)
        if scene_name not in bpy.data.scenes:
            return None
        active_scene = bpy.data.scenes[scene_name]
        settings = getattr(active_scene, "opengate", None)
        if settings is not None:
            sync_camera_safe_areas(settings, active_scene)
        return None

    bpy.app.timers.register(_apply, first_interval=0.0)


def pull_display_settings_from_camera(settings, camera: bpy.types.Object | None) -> None:
    global _UPDATING_FROM_CAMERA
    if camera is None or camera.type != "CAMERA":
        return

    cam_data = camera.data
    _UPDATING_FROM_CAMERA = True
    try:
        settings.show_passepartout = cam_data.show_passepartout
        settings.passepartout_alpha = cam_data.passepartout_alpha
    finally:
        _UPDATING_FROM_CAMERA = False


def pull_passepartout_from_camera_to_scenes(camera: bpy.types.Object) -> None:
    """Mirror camera passepartout edits from the native camera panel."""
    if camera.type != "CAMERA":
        return

    for scene in bpy.data.scenes:
        settings = getattr(scene, "opengate", None)
        if settings is None or settings.target_camera != camera:
            continue
        pull_display_settings_from_camera(settings, camera)
