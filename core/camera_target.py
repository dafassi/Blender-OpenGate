"""Camera selection helpers (no dependency on properties or mask setup)."""

from __future__ import annotations

import bpy

_suppress_target_camera_update = False
_scheduled_default_scenes: set[str] = set()


def camera_poll(_self, obj: bpy.types.Object) -> bool:
    return obj is not None and obj.type == "CAMERA"


def is_valid_camera(obj: bpy.types.Object | None) -> bool:
    return (
        obj is not None
        and obj.type == "CAMERA"
        and obj.name in bpy.data.objects
    )


def target_camera_update_suppressed() -> bool:
    return _suppress_target_camera_update


def get_target_camera(
    settings,
    scene: bpy.types.Scene,
) -> bpy.types.Object | None:
    cam = settings.target_camera
    if cam is not None and cam.type == "CAMERA":
        return cam
    return scene.camera


def assign_target_camera(settings, camera: bpy.types.Object | None) -> None:
    """Set target camera without running camera-change side effects."""
    global _suppress_target_camera_update
    _suppress_target_camera_update = True
    try:
        settings.target_camera = camera
    finally:
        _suppress_target_camera_update = False


def ensure_default_target_camera(
    settings,
    scene: bpy.types.Scene,
) -> bpy.types.Object | None:
    """Pre-select scene camera, or the first camera in the scene."""
    if is_valid_camera(settings.target_camera):
        return settings.target_camera

    if is_valid_camera(scene.camera):
        assign_target_camera(settings, scene.camera)
        return scene.camera

    for obj in scene.objects:
        if obj.type == "CAMERA":
            assign_target_camera(settings, obj)
            return obj

    assign_target_camera(settings, None)
    return None


def ensure_default_target_cameras_for_all_scenes() -> None:
    if not hasattr(bpy.data, "scenes"):
        return
    for scene in bpy.data.scenes:
        settings = getattr(scene, "opengate", None)
        if settings is not None:
            ensure_default_target_camera(settings, scene)


def schedule_default_target_camera(scene: bpy.types.Scene) -> None:
    """Assign a default camera on the next frame (safe outside panel draw)."""
    if scene is None or scene.name in _scheduled_default_scenes:
        return

    settings = getattr(scene, "opengate", None)
    if settings is None or is_valid_camera(settings.target_camera):
        return

    if get_target_camera(settings, scene) is None:
        return

    _scheduled_default_scenes.add(scene.name)

    def _apply_default() -> None:
        _scheduled_default_scenes.discard(scene.name)
        if scene.name not in bpy.data.scenes:
            return
        active_settings = getattr(scene, "opengate", None)
        if active_settings is not None:
            ensure_default_target_camera(active_settings, scene)

    bpy.app.timers.register(_apply_default, first_interval=0.0)
