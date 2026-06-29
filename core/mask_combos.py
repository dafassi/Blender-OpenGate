"""Mask combo image names — datablocks live in opengate-imagecollector.blend."""

from __future__ import annotations

import os
from itertools import permutations

from .mask_combo_matrix import mask_combo_entry
from .masks import MASK_IMAGE_PREFIX, MASKS, iter_active_masks
from .paths import extension_asset_abspath
from .platform_presets import (
    all_safezone_filenames,
    preset_by_id,
    safezone_filename_for_preset,
)

BACKUP_PROP_KEY = "opengate_bg_backup"

# Last mask flags applied to this camera (0 = OpenGate overlay not active).
OPENGATE_ACTIVE_FLAGS_KEY = "opengate_active_mask_flags"

# Custom property on Image datablocks — stable identity regardless of filepath/name suffixes.
OPENGATE_MASK_FILE_KEY = "opengate_mask_file"
OPENGATE_MASK_FLAGS_KEY = "opengate_mask_flags"
OPENGATE_MASK_SAFEZONE_FILE_KEY = "opengate_mask_safezone_file"

# Active safezone PNG basename on the camera ("" = standard combo).
OPENGATE_ACTIVE_SAFEZONE_FILE_KEY = "opengate_active_safezone_file"

# Legacy bool keys from earlier builds — read-only fallback during matching.
OPENGATE_MASK_SAFEZONES_KEY = "opengate_mask_safezones"
OPENGATE_ACTIVE_SAFEZONES_KEY = "opengate_active_safezones"

MASK_ASSET_PARTS = ("assets", "masks")


def _combo_basename(mask_ids: list[str]) -> str:
    return f"{MASK_IMAGE_PREFIX}-{'-'.join(mask_ids)}.png"


def is_pure_9_16_mask(mask_flags: int) -> bool:
    return mask_flags == int(MASKS[1].bit_value)


def safezones_applicable(
    mask_flags: int,
    show_safezones: bool,
    platform_preset_id: str,
) -> bool:
    return (
        bool(show_safezones)
        and is_pure_9_16_mask(mask_flags)
        and safezone_filename_for_preset(platform_preset_id) is not None
    )


def is_safezone_variant_file(filename: str) -> bool:
    return os.path.basename(filename.replace("\\", "/")) in all_safezone_filenames()


def resolve_safezone_filename(
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> str | None:
    """Platform-specific 9:16 safezone PNG, or None for the standard combo."""
    if not safezones_applicable(mask_flags, show_safezones, platform_preset_id):
        return None
    return safezone_filename_for_preset(platform_preset_id)


def resolve_mask_image_filename(
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> str | None:
    """Pick the PNG for the active mask set, including platform safezone variants."""
    safezone_file = resolve_safezone_filename(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    if safezone_file is not None:
        return safezone_file
    return canonical_combo_filename(mask_flags)


def canonical_combo_filename(mask_flags: int) -> str | None:
    """Preferred filename using registry order (16:9, 9:16, 5:4)."""
    entry = mask_combo_entry(mask_flags)
    if entry is not None:
        return entry.canonical_filename

    mask_ids = [mask.id for mask in iter_active_masks(mask_flags)]
    if not mask_ids:
        return None
    return _combo_basename(mask_ids)


def iter_combo_filename_candidates(mask_flags: int):
    """All filename orderings for the same active mask set."""
    mask_ids = [mask.id for mask in iter_active_masks(mask_flags)]
    if not mask_ids:
        return

    canonical = _combo_basename(mask_ids)
    yield canonical

    if len(mask_ids) == 1:
        return

    for ordering in permutations(mask_ids):
        candidate = _combo_basename(list(ordering))
        if candidate != canonical:
            yield candidate


def describe_mask_combo(
    mask_flags: int,
    *,
    show_safezones: bool = False,
    platform_preset_id: str = "NONE",
) -> str:
    """Human-readable combo → image datablock summary for UI and errors."""
    if mask_flags <= 0:
        return "(none)"

    filename = resolve_mask_image_filename(
        mask_flags,
        show_safezones=show_safezones,
        platform_preset_id=platform_preset_id,
    )
    if filename is None:
        return f"flags {mask_flags}"

    if safezones_applicable(mask_flags, show_safezones, platform_preset_id):
        preset = preset_by_id(platform_preset_id)
        platform_label = preset.label if preset is not None else platform_preset_id
        return f"9:16 + safezones ({platform_label}) → {filename}"

    entry = mask_combo_entry(mask_flags)
    if entry is None:
        return f"flags {mask_flags} → {filename}"

    labels = " / ".join(entry.equivalent_label_orderings)
    return f"{labels} → {filename}"


def mask_image_abspath(filename: str) -> str:
    """Fallback path when collector images reference external PNGs."""
    return extension_asset_abspath(*MASK_ASSET_PARTS, filename)


def parse_combo_filename(filename: str) -> frozenset[str] | None:
    """Extract mask ids from ``.opengate-16_9-5_4.png`` style names."""
    base = os.path.basename(filename.replace("\\", "/"))
    prefix = f"{MASK_IMAGE_PREFIX}-"
    if not base.startswith(prefix) or not base.endswith(".png"):
        return None

    id_part = base[len(prefix) : -4]
    if not id_part:
        return None

    parts = id_part.split("-")
    known = {mask.id for mask in MASKS}
    if not all(part in known for part in parts):
        return None

    return frozenset(parts)


def mask_flags_from_combo_filename(filename: str) -> int | None:
    """Bitmask for a combo PNG regardless of id order in the filename."""
    if is_safezone_variant_file(filename):
        return int(MASKS[1].bit_value)

    ids = parse_combo_filename(filename)
    if ids is None:
        return None

    flags = 0
    for mask in MASKS:
        if mask.id in ids:
            flags |= mask.bit_value

    active_ids = frozenset(mask.id for mask in iter_active_masks(flags))
    if active_ids != ids:
        return None

    return flags or None


def is_opengate_mask_file(filename: str) -> bool:
    if is_safezone_variant_file(filename):
        return True
    return mask_flags_from_combo_filename(filename) is not None
