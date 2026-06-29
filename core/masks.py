"""
Aspect-ratio mask registry for OpenGate framing.

Mask combo images live in ``assets/shader/opengate-imagecollector.blend`` — see
``core/image_collector.py`` and ``assets/masks/MASK_COMBO_MATRIX.md``.

Bitmask reference
-----------------
Value   Binary   Active masks
-----   ------   ------------
0       000      (none)
1       001      16:9
2       010      9:16
3       011      16:9 + 9:16
4       100      5:4
5       101      16:9 + 5:4
6       110      9:16 + 5:4
7       111      16:9 + 9:16 + 5:4

Next available bit: 8 (2³) — reserve for future masks (e.g. 1:1, 4:5).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Iterator

from .paths import IMAGE_FILENAME_DOT_PREFIX


class MaskFlag(IntFlag):
    """Bitmask flags — always powers of two."""

    NONE = 0
    RATIO_16_9 = 1   # 2^0 — landscape
    RATIO_9_16 = 2   # 2^1 — portrait / story
    RATIO_5_4 = 4    # 2^2 — photo / print


MASK_NAME_PREFIX = "opengate"
MASK_IMAGE_PREFIX = f"{IMAGE_FILENAME_DOT_PREFIX}{MASK_NAME_PREFIX}"


@dataclass(frozen=True)
class MaskDefinition:
    """Single mask image and its bitmask slot."""

    flag: MaskFlag
    id: str
    label: str
    aspect_width: int
    aspect_height: int

    @property
    def bit_value(self) -> int:
        return int(self.flag)

    @property
    def aspect_ratio(self) -> float:
        return self.aspect_width / self.aspect_height


MASKS: tuple[MaskDefinition, ...] = (
    MaskDefinition(
        flag=MaskFlag.RATIO_16_9,
        id="16_9",
        label="16:9",
        aspect_width=16,
        aspect_height=9,
    ),
    MaskDefinition(
        flag=MaskFlag.RATIO_9_16,
        id="9_16",
        label="9:16",
        aspect_width=9,
        aspect_height=16,
    ),
    MaskDefinition(
        flag=MaskFlag.RATIO_5_4,
        id="5_4",
        label="5:4",
        aspect_width=4,
        aspect_height=5,
    ),
)

def iter_active_masks(mask_flags: int) -> Iterator[MaskDefinition]:
    """Yield masks whose bit is set in ``mask_flags``."""
    for mask in MASKS:
        if is_mask_enabled(mask_flags, mask.flag):
            yield mask


def is_mask_enabled(mask_flags: int, flag: MaskFlag | int) -> bool:
    return bool(mask_flags & int(flag))


def has_active_framing_mask(settings) -> bool:
    """True when at least one aspect mask checkbox is enabled."""
    return bool(settings.mask_16_9 or settings.mask_9_16 or settings.mask_5_4)


def mask_flags_label(mask_flags: int) -> str:
    """Human-readable summary, e.g. ``16:9 + 9:16`` or ``(none)``."""
    active = [m.label for m in iter_active_masks(mask_flags)]
    return " + ".join(active) if active else "(none)"
