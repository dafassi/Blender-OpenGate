"""Platform delivery presets — loaded from assets/platform_presets.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

import bpy

from . import masks
from .paths import extension_asset_abspath
from .render_format import combined_frame_resolution_label

PRESETS_JSON_PATH = ("assets", "platform_presets.json")


@dataclass(frozen=True)
class PresetSource:
    """Backend-only citation for a preset field (not shown in the UI)."""

    url: str
    title: str
    fields: tuple[str, ...] = ()
    excerpt: str = ""


@dataclass(frozen=True)
class PlatformPreset:
    id: str
    label: str
    mask_16_9: bool
    mask_9_16: bool
    mask_5_4: bool
    delivery_width: int
    delivery_height: int
    recommended_fps: tuple[int, ...]
    max_duration_sec: int | None
    notes: str
    sources: tuple[PresetSource, ...]
    safezone_filename: str | None = None

    @property
    def source_url(self) -> str:
        """Primary source URL (first entry); kept for internal callers."""
        return self.sources[0].url if self.sources else ""

    def matches_settings(self, settings) -> bool:
        return (
            bool(settings.mask_16_9) == self.mask_16_9
            and bool(settings.mask_9_16) == self.mask_9_16
            and bool(settings.mask_5_4) == self.mask_5_4
        )

    def mask_flags(self) -> int:
        flags = 0
        if self.mask_16_9:
            flags |= masks.MaskFlag.RATIO_16_9
        if self.mask_9_16:
            flags |= masks.MaskFlag.RATIO_9_16
        if self.mask_5_4:
            flags |= masks.MaskFlag.RATIO_5_4
        return flags

    def recommended_canvas_size(self) -> int:
        """Square Open Gate size whose mask crop matches ``delivery_width×height``."""
        if self.mask_16_9:
            return self.delivery_width
        return self.delivery_height

    @property
    def recommended_fps_label(self) -> str:
        """Comma-separated FPS values, e.g. ``24, 30, 60``."""
        return ", ".join(str(fps) for fps in self.recommended_fps)


def _parse_recommended_fps(raw) -> tuple[int, ...]:
    if isinstance(raw, list):
        values = tuple(int(fps) for fps in raw)
        if not values:
            raise ValueError("recommended_fps list must not be empty")
        return values
    return (int(raw),)


def _parse_sources(item: dict) -> tuple[PresetSource, ...]:
    raw = item.get("sources")
    if isinstance(raw, list) and raw:
        return tuple(
            PresetSource(
                url=str(entry["url"]),
                title=str(entry.get("title", "")),
                fields=tuple(str(field) for field in entry.get("fields", [])),
                excerpt=str(entry.get("excerpt", "")),
            )
            for entry in raw
        )
    legacy_url = item.get("source_url")
    if legacy_url:
        return (PresetSource(url=str(legacy_url), title=""),)
    return ()


def _load_from_json() -> tuple[str, str, tuple[PlatformPreset, ...]]:
    """Parse assets/platform_presets.json and return (verified_as_of, disclaimer, presets).

    Raises RuntimeError if the file is missing or malformed so the addon fails
    loudly at register() rather than silently serving stale/empty data.
    """
    json_path = extension_asset_abspath(*PRESETS_JSON_PATH)
    try:
        with open(json_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise RuntimeError(
            f"OpenGate: platform presets file not found: {json_path}"
        ) from None
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"OpenGate: malformed platform presets JSON ({json_path}): {exc}"
        ) from exc

    verified_as_of: str = data.get("verified_as_of", "unknown")
    disclaimer: str = data.get("disclaimer", "Verify platform specs before publish.")

    presets: list[PlatformPreset] = []
    for item in data.get("presets", []):
        presets.append(
            PlatformPreset(
                id=item["id"],
                label=item["label"],
                mask_16_9=bool(item["mask_16_9"]),
                mask_9_16=bool(item["mask_9_16"]),
                mask_5_4=bool(item["mask_5_4"]),
                delivery_width=int(item["delivery_width"]),
                delivery_height=int(item["delivery_height"]),
                recommended_fps=_parse_recommended_fps(item.get("recommended_fps", 30)),
                max_duration_sec=(
                    int(item["max_duration_sec"])
                    if item.get("max_duration_sec") is not None
                    else None
                ),
                notes=str(item.get("notes", "")),
                sources=_parse_sources(item),
                safezone_filename=(
                    str(item["safezone_filename"])
                    if item.get("safezone_filename") is not None
                    else None
                ),
            )
        )

    return verified_as_of, disclaimer, tuple(presets)


VERIFIED_AS_OF, DISCLAIMER, PLATFORM_PRESETS = _load_from_json()

PRESET_BY_ID: dict[str, PlatformPreset] = {p.id: p for p in PLATFORM_PRESETS}


def safezone_filename_for_preset(preset_id: str) -> str | None:
    preset = preset_by_id(preset_id)
    if preset is None:
        return None
    return preset.safezone_filename


def platform_has_safezones(preset_id: str) -> bool:
    return safezone_filename_for_preset(preset_id) is not None


def all_safezone_filenames() -> frozenset[str]:
    return frozenset(
        p.safezone_filename for p in PLATFORM_PRESETS if p.safezone_filename
    )


def _preset_enum_description(preset: PlatformPreset) -> str:
    """Compact tooltip for the platform preset dropdown."""
    parts = [
        f"{preset.delivery_width}×{preset.delivery_height}",
        f"{preset.recommended_fps_label} fps",
    ]
    if preset.max_duration_sec is None:
        parts.append("no max length")
    else:
        parts.append(f"max {format_duration(preset.max_duration_sec)}")
    masks: list[str] = []
    if preset.mask_16_9:
        masks.append("16:9")
    if preset.mask_9_16:
        masks.append("9:16")
    if preset.mask_5_4:
        masks.append("5:4")
    if masks:
        parts.append("+".join(masks))
    return " · ".join(parts)


def enum_items() -> list[tuple[str, str, str]]:
    items = [
        (
            "NONE",
            "Manual",
            "Pick masks yourself; no platform limits or FPS hints",
        ),
    ]
    for preset in sorted(PLATFORM_PRESETS, key=lambda p: p.label.casefold()):
        items.append((preset.id, preset.label, _preset_enum_description(preset)))
    return items


def preset_by_id(preset_id: str) -> PlatformPreset | None:
    if preset_id == "NONE":
        return None
    return PRESET_BY_ID.get(preset_id)


def scene_duration_seconds(scene: bpy.types.Scene) -> float:
    frame_count = max(0, scene.frame_end - scene.frame_start + 1)
    return frame_count / scene_render_fps(scene)


def scene_render_fps(scene: bpy.types.Scene) -> float:
    return scene.render.fps / max(1.0, scene.render.fps_base)


def format_scene_fps(scene: bpy.types.Scene) -> str:
    """Human-readable scene frame rate, e.g. ``30 fps`` or ``29.97 fps``."""
    fps = scene_render_fps(scene)
    rounded = round(fps)
    if abs(fps - rounded) < 0.01:
        return f"{int(rounded)} fps"
    return f"{fps:.2f} fps"


def format_recommended_length(max_duration_sec: int | None) -> str:
    """Human-readable platform max duration, or ``No limit``."""
    if max_duration_sec is None:
        return "No limit"
    return format_duration(max_duration_sec)


def format_duration_words(total_seconds: float) -> str:
    total = max(0, int(round(total_seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} hr")
    if minutes or hours:
        parts.append(f"{minutes} min")
    parts.append(f"{seconds} sec")
    return " ".join(parts)


def format_duration(total_seconds: float) -> str:
    """Human-readable duration, e.g. ``2 min 20 sec``."""
    return format_duration_words(total_seconds)


def format_verified_as_of(iso_date: str) -> str:
    """Display date as ``June 2026`` from ``YYYY-MM-DD``."""
    parsed = datetime.strptime(iso_date, "%Y-%m-%d")
    return parsed.strftime("%B %Y")


def duration_within_limit(duration_sec: float, max_duration_sec: int | None) -> bool:
    if max_duration_sec is None:
        return True
    return duration_sec <= max_duration_sec


def crop_resolution_label(settings, canvas_percent: float) -> str | None:
    preset = preset_by_id(settings.platform_preset)
    if preset is not None:
        return combined_frame_resolution_label(preset.mask_flags(), canvas_percent)
    return combined_frame_resolution_label(settings.mask_flags, canvas_percent)


def recommended_canvas_percent(preset: PlatformPreset) -> float:
    from .render_format import canvas_percent_for_square_size

    return canvas_percent_for_square_size(preset.recommended_canvas_size())
