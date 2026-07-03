"""Shared mask setup logic used by property updates and operators."""

from __future__ import annotations

import bpy

from .background_image import clear_opengate_background, sync_opengate_background
from .camera_display import release_camera_safe_areas
from .camera_target import assign_target_camera, get_target_camera
from .image_collector import remove_image_collector
from .masks import has_active_framing_mask
from .render_format import (
    CANVAS_RESOLUTION_DEFAULT,
    apply_canvas_resolution,
    restore_render_resolution,
)

_MASK_SETUP_CLEARING = False


def mask_setup_clearing() -> bool:
    return _MASK_SETUP_CLEARING


def clear_mask_setup(context: bpy.types.Context) -> None:
    global _MASK_SETUP_CLEARING
    scene = context.scene
    settings = scene.opengate
    camera = get_target_camera(settings, scene)

    clear_opengate_background(scene, settings, camera=camera)

    if camera is not None and camera.type == "CAMERA":
        release_camera_safe_areas(scene, camera.data)

    restore_render_resolution(scene)
    remove_image_collector()

    _MASK_SETUP_CLEARING = True
    try:
        settings.mask_16_9 = False
        settings.mask_9_16 = False
        settings.mask_5_4 = False
        settings.show_safezones = False
        settings.mask_flags = 0
        settings.mask_sync_message = ""
        settings.canvas_resolution = CANVAS_RESOLUTION_DEFAULT
    finally:
        _MASK_SETUP_CLEARING = False


def try_ensure_mask_setup(context: bpy.types.Context) -> str | None:
    """Enable the OpenGate background image when framing masks are active.

    Returns an error message on failure, or None on success.
    """
    scene = context.scene
    settings = scene.opengate

    if not has_active_framing_mask(settings):
        return None

    camera = get_target_camera(settings, scene)
    if camera is None:
        return "Select a camera first"

    if settings.target_camera is None:
        assign_target_camera(settings, camera)

    apply_canvas_resolution(scene, settings.canvas_resolution)

    try:
        sync_opengate_background(settings, scene, camera=camera)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        return str(exc)

    return None
