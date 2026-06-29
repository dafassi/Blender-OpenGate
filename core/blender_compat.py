"""RNA paths that differ between Blender releases."""

from __future__ import annotations

import bpy


def scene_safe_areas(scene: bpy.types.Scene) -> bpy.types.DisplaySafeAreas:
    """Safe-area margin values (shared with the sequencer since Blender 2.8+)."""
    return scene.safe_areas
