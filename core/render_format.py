"""OpenGate canvas — square render resolution with format presets + slider."""

from __future__ import annotations

import json

import bpy

from . import masks

# Matches the 8K UHD frame height (7680×4320) as a 1:1 open canvas at 100%.
OPENGATE_CANVAS_SIZE = 4320
CANVAS_RESOLUTION_MIN = 10.0
CANVAS_RESOLUTION_MAX = 100.0
CANVAS_RESOLUTION_DEFAULT = 50.0

RENDER_BACKUP_KEY = "opengate_render_backup"

# Ordered for the 2-column preset button grid (landscape 16:9 frame widths at 100% gate).
CANVAS_FORMAT_PRESETS: tuple[tuple[str, float, str], ...] = (
    ("HD_READY", 1280 / OPENGATE_CANVAS_SIZE * 100.0, "HD Ready"),
    ("FULL_HD", 1920 / OPENGATE_CANVAS_SIZE * 100.0, "Full HD"),
    ("4K", 3840 / OPENGATE_CANVAS_SIZE * 100.0, "4K"),
    ("8K", 100.0, "8K"),
)

CANVAS_PRESET_BY_ID: dict[str, tuple[float, str]] = {
    preset_id: (percent, label)
    for preset_id, percent, label in CANVAS_FORMAT_PRESETS
}

def canvas_preset_description(preset_id: str) -> str:
    """Compact tooltip for a canvas format preset button."""
    entry = CANVAS_PRESET_BY_ID.get(preset_id)
    if entry is None:
        return "Square open-gate render size"
    percent, label = entry
    size = canvas_pixel_size(percent)
    return f"{size}×{size} px square gate ({label})"


def _clamp_canvas_percent(percent: float) -> float:
    return max(CANVAS_RESOLUTION_MIN, min(CANVAS_RESOLUTION_MAX, float(percent)))


def canvas_percent_for_square_size(pixel_size: int) -> float:
    """Canvas slider % so the square Open Gate equals ``pixel_size``."""
    return _clamp_canvas_percent(pixel_size / OPENGATE_CANVAS_SIZE * 100.0)


def canvas_pixel_size(percent: float) -> int:
    """Map slider percentage (10–100) to square render resolution in pixels."""
    return max(1, round(OPENGATE_CANVAS_SIZE * _clamp_canvas_percent(percent) / 100))


def canvas_percent_for_preset(preset_id: str) -> float | None:
    entry = CANVAS_PRESET_BY_ID.get(preset_id)
    if entry is None:
        return None
    return entry[0]


def active_canvas_preset(percent: float) -> str | None:
    """Return the preset id when the slider matches a format button, else None."""
    current_size = canvas_pixel_size(percent)
    for preset_id, preset_percent, _label in CANVAS_FORMAT_PRESETS:
        if canvas_pixel_size(preset_percent) == current_size:
            return preset_id
    return None


def mask_crop_normalized(mask: masks.MaskDefinition) -> tuple[float, float]:
    """Width and height of the mask crop as fractions of the square canvas (0–1)."""
    aspect_w = mask.aspect_width
    aspect_h = mask.aspect_height

    if aspect_w >= aspect_h:
        return 1.0, aspect_h / aspect_w
    return aspect_w / aspect_h, 1.0


def mask_frame_in_canvas(mask: masks.MaskDefinition, canvas_size: int) -> tuple[int, int]:
    """
    Largest mask rectangle that fits inside the square open-gate canvas.

    Landscape masks use the full canvas width; portrait masks use the full height.
    """
    width_norm, height_norm = mask_crop_normalized(mask)
    if width_norm >= height_norm:
        width = canvas_size
        height = max(1, round(canvas_size * height_norm / width_norm))
    else:
        height = canvas_size
        width = max(1, round(canvas_size * width_norm / height_norm))

    return width, height


def mask_frame_rect_in_canvas(
    mask: masks.MaskDefinition,
    canvas_size: int,
) -> tuple[int, int, int, int]:
    """Centered mask crop as ``(x, y, width, height)`` in canvas pixels."""
    width, height = mask_frame_in_canvas(mask, canvas_size)
    x = (canvas_size - width) // 2
    y = (canvas_size - height) // 2
    return x, y, width, height


def _intersect_frame_rects(
    rects: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int] | None:
    if not rects:
        return None
    left = max(rect[0] for rect in rects)
    top = max(rect[1] for rect in rects)
    right = min(rect[0] + rect[2] for rect in rects)
    bottom = min(rect[1] + rect[3] for rect in rects)
    if right <= left or bottom <= top:
        return None
    return left, top, right - left, bottom - top


def combined_mask_frame_in_canvas(
    active_masks: list[masks.MaskDefinition],
    canvas_size: int,
) -> tuple[int, int] | None:
    """Pixel size of the intersection crop for all active masks."""
    if not active_masks:
        return None
    if len(active_masks) == 1:
        return mask_frame_in_canvas(active_masks[0], canvas_size)

    combined = _intersect_frame_rects(
        [mask_frame_rect_in_canvas(mask, canvas_size) for mask in active_masks],
    )
    if combined is None:
        return None
    return combined[2], combined[3]


def combined_mask_safe_margins(
    active_masks: list[masks.MaskDefinition],
    canvas_size: int,
) -> tuple[float, float]:
    """Safe-area margins for the intersection of all active mask crops."""
    frame = combined_mask_frame_in_canvas(active_masks, canvas_size)
    if frame is None:
        return 0.0, 0.0

    width, height = frame
    size = max(1, canvas_size)
    return 1.0 - width / size, 1.0 - height / size


def combined_frame_resolution_label(mask_flags: int, percent: float) -> str | None:
    """Pixel size of the intersection crop, e.g. ``1215×2160``."""
    active = list(masks.iter_active_masks(mask_flags))
    if not active:
        return None
    frame = combined_mask_frame_in_canvas(active, canvas_pixel_size(percent))
    if frame is None:
        return None
    width, height = frame
    return f"{width}×{height}"


def _serialize_render_settings(render: bpy.types.RenderSettings) -> dict:
    return {
        "resolution_x": int(render.resolution_x),
        "resolution_y": int(render.resolution_y),
        "resolution_percentage": int(render.resolution_percentage),
        "pixel_aspect_x": float(render.pixel_aspect_x),
        "pixel_aspect_y": float(render.pixel_aspect_y),
    }


def _backup_render_resolution(scene: bpy.types.Scene) -> None:
    if RENDER_BACKUP_KEY in scene:
        return
    scene[RENDER_BACKUP_KEY] = json.dumps(_serialize_render_settings(scene.render))


def restore_render_resolution(scene: bpy.types.Scene) -> None:
    backup_raw = scene.get(RENDER_BACKUP_KEY)
    if not backup_raw:
        return

    payload = json.loads(backup_raw)
    render = scene.render
    render.resolution_x = int(payload["resolution_x"])
    render.resolution_y = int(payload["resolution_y"])
    render.resolution_percentage = int(payload.get("resolution_percentage", 100))
    render.pixel_aspect_x = float(payload.get("pixel_aspect_x", 1.0))
    render.pixel_aspect_y = float(payload.get("pixel_aspect_y", 1.0))
    del scene[RENDER_BACKUP_KEY]


def apply_canvas_resolution(scene: bpy.types.Scene, percent: float) -> None:
    """Set square render resolution; 100% equals OPENGATE_CANVAS_SIZE."""
    _backup_render_resolution(scene)
    size = canvas_pixel_size(percent)
    render = scene.render
    render.resolution_x = size
    render.resolution_y = size
    render.pixel_aspect_x = 1.0
    render.pixel_aspect_y = 1.0


def apply_opengate_canvas_to_all_scenes() -> None:
    # bpy.data is restricted during extension validate / CLI build.
    if not hasattr(bpy.data, "scenes"):
        return
    for scene in bpy.data.scenes:
        settings = getattr(scene, "opengate", None)
        percent = (
            settings.canvas_resolution
            if settings is not None
            else CANVAS_RESOLUTION_DEFAULT
        )
        apply_canvas_resolution(scene, percent)
