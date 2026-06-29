"""Shared mask setup logic used by property updates and operators."""

from __future__ import annotations

import bpy

from .background_image import clear_opengate_background, sync_opengate_background
from .camera_target import assign_target_camera, get_target_camera
from .masks import has_active_framing_mask
from .render_format import apply_canvas_resolution


def clear_mask_setup(context: bpy.types.Context) -> None:
    scene = context.scene
    settings = scene.opengate
    clear_opengate_background(scene, settings)


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
