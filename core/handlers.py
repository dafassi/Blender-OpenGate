"""Auto-refresh OpenGate state when render or camera settings change."""

from __future__ import annotations

import bpy

from .background_image import refresh_opengate_mask_images, sync_opengate_background
from .camera_display import (
    pull_passepartout_from_camera_to_scenes,
    schedule_camera_safe_areas_sync,
)
from .camera_target import ensure_default_target_cameras_for_all_scenes, get_target_camera
from .masks import has_active_framing_mask

_MSG_BUS_OWNER = object()
_REFRESH_TIMER_PENDING = False

_RENDER_PROPS = (
    "resolution_x",
    "resolution_y",
    "resolution_percentage",
    "pixel_aspect_x",
    "pixel_aspect_y",
)

_CAMERA_DISPLAY_PROPS = (
    "show_passepartout",
    "passepartout_alpha",
)


def _on_camera_display_change(*_args) -> None:
    camera = bpy.context.object
    if camera is not None and camera.type == "CAMERA":
        pull_passepartout_from_camera_to_scenes(camera)
        return

    scene = bpy.context.scene
    if scene is not None:
        settings = getattr(scene, "opengate", None)
        if settings is not None and settings.target_camera is not None:
            pull_passepartout_from_camera_to_scenes(settings.target_camera)


def _schedule_mask_refresh(*_args) -> None:
    global _REFRESH_TIMER_PENDING
    if _REFRESH_TIMER_PENDING:
        return
    _REFRESH_TIMER_PENDING = True
    bpy.app.timers.register(_run_mask_refresh, first_interval=0.05)


def _run_mask_refresh() -> None:
    global _REFRESH_TIMER_PENDING
    _REFRESH_TIMER_PENDING = False
    for scene in bpy.data.scenes:
        settings = getattr(scene, "opengate", None)
        if settings is None:
            continue
        schedule_camera_safe_areas_sync(scene)
        if not has_active_framing_mask(settings) or not settings.show_mask:
            continue
        try:
            sync_opengate_background(settings, scene)
        except (FileNotFoundError, ValueError, RuntimeError):
            pass
    return None


@bpy.app.handlers.persistent
def _opengate_load_post(_dummy) -> None:
    ensure_default_target_cameras_for_all_scenes()
    refresh_opengate_mask_images()
    if not hasattr(bpy.data, "scenes"):
        return
    for scene in bpy.data.scenes:
        settings = getattr(scene, "opengate", None)
        if settings is None:
            continue
        if has_active_framing_mask(settings) and settings.show_mask:
            try:
                sync_opengate_background(settings, scene)
            except (FileNotFoundError, ValueError, RuntimeError):
                pass
        if has_active_framing_mask(settings):
            schedule_camera_safe_areas_sync(scene)


def register() -> None:
    if _opengate_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_opengate_load_post)

    owner = _MSG_BUS_OWNER
    options = {"PERSISTENT"}

    for prop in _RENDER_PROPS:
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.RenderSettings, prop),
            owner=owner,
            args=(),
            notify=_schedule_mask_refresh,
            options=options,
        )

    for prop in _CAMERA_DISPLAY_PROPS:
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.Camera, prop),
            owner=owner,
            args=(),
            notify=_on_camera_display_change,
            options=options,
        )


def unregister() -> None:
    if _opengate_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_opengate_load_post)

    bpy.msgbus.clear_by_owner(_MSG_BUS_OWNER)
