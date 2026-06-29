"""Canonical mask-combo → PNG filename mapping (bitmask flags 1–7)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

from .masks import MASK_IMAGE_PREFIX, iter_active_masks


def _combo_filename(mask_ids: tuple[str, ...]) -> str:
    return f"{MASK_IMAGE_PREFIX}-{'-'.join(mask_ids)}.png"


@dataclass(frozen=True)
class MaskComboMatrixEntry:
    flags: int
    mask_ids: tuple[str, ...]
    canonical_filename: str

    @property
    def equivalent_label_orderings(self) -> tuple[str, ...]:
        """Every checkbox order that maps to this combo (same file)."""
        active = [mask.label for mask in iter_active_masks(self.flags)]
        if not active:
            return ()
        if len(active) == 1:
            return (active[0],)

        seen: set[str] = set()
        orderings: list[str] = []
        for ordering in permutations(active):
            text = " + ".join(ordering)
            if text in seen:
                continue
            seen.add(text)
            orderings.append(text)
        return tuple(orderings)


# One row per unique mask set (flags 1–7). Checkbox / label order does not matter.
MASK_COMBO_MATRIX: tuple[MaskComboMatrixEntry, ...] = (
    MaskComboMatrixEntry(1, ("16_9",), _combo_filename(("16_9",))),
    MaskComboMatrixEntry(2, ("9_16",), _combo_filename(("9_16",))),
    MaskComboMatrixEntry(3, ("16_9", "9_16"), _combo_filename(("16_9", "9_16"))),
    MaskComboMatrixEntry(4, ("5_4",), _combo_filename(("5_4",))),
    MaskComboMatrixEntry(5, ("16_9", "5_4"), _combo_filename(("16_9", "5_4"))),
    MaskComboMatrixEntry(6, ("9_16", "5_4"), _combo_filename(("9_16", "5_4"))),
    MaskComboMatrixEntry(7, ("16_9", "9_16", "5_4"), _combo_filename(("16_9", "9_16", "5_4"))),
)

_MASK_COMBO_BY_FLAGS = {entry.flags: entry for entry in MASK_COMBO_MATRIX}


def mask_combo_entry(mask_flags: int) -> MaskComboMatrixEntry | None:
    return _MASK_COMBO_BY_FLAGS.get(mask_flags)
