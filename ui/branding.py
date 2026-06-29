"""Shared branding copy and footer for OpenGate UI."""

from __future__ import annotations

import os

import bpy
import bpy.utils.previews

from ..core.paths import extension_asset_abspath

TEAM_CREDIT_LABEL = "From the FLIP Fluids Addon Team"
TAGLINE_LABEL = "Sim once · publish everywhere"
FLIP_FLUIDS_URL = "https://flipfluids.com/"
MAINTAINER_LABEL = "Ryan Guy & Dennis Fassbaender"

from ..core.paths import prefixed_image_filename

LOGO_FILENAME = prefixed_image_filename("opengate-logo_rev0.png")
LOGO_PREVIEW_KEY = "opengate_logo"
LOGO_ICON_SCALE = 5.5
# Blender rows align to the top by default — pad with scale_y to center visually.
PANEL_VERTICAL_PAD = 0.65
TEXT_VERTICAL_PAD = 1.35

# Filled heart — Blender's HEART icon is outline-only.
HEART_CHAR = "\u2764"

_preview_collection: bpy.utils.previews.SmartPreviewsCollection | None = None


def _logo_abspath() -> str:
    return extension_asset_abspath("assets", LOGO_FILENAME)


def _ensure_logo_preview() -> bpy.utils.previews.SmartPreviewsCollection | None:
    global _preview_collection
    if _preview_collection is None:
        return None
    if LOGO_PREVIEW_KEY in _preview_collection:
        return _preview_collection

    logo_path = _logo_abspath()
    if os.path.isfile(logo_path):
        _preview_collection.load(LOGO_PREVIEW_KEY, logo_path, "IMAGE")
    return _preview_collection


def logo_icon_id() -> int:
    pcoll = _ensure_logo_preview()
    if pcoll is None or LOGO_PREVIEW_KEY not in pcoll:
        return 0
    return pcoll[LOGO_PREVIEW_KEY].icon_id


def _vertical_pad(column: bpy.types.UILayout, factor: float) -> None:
    pad = column.row()
    pad.scale_y = factor
    pad.label(text="")


def _centered_label(column: bpy.types.UILayout, text: str) -> None:
    """Center a label within a shared-width column block."""
    line = column.row()
    line.alignment = "CENTER"
    line.scale_x = 1.0
    line.label(text=text)


def _draw_branding_text(parent: bpy.types.UILayout) -> None:
    block = parent.column(align=True)
    block.scale_x = 1.0

    _vertical_pad(block, TEXT_VERTICAL_PAD)
    _centered_label(block, f"{HEART_CHAR}  {TEAM_CREDIT_LABEL}")
    _centered_label(block, TAGLINE_LABEL)
    _vertical_pad(block, TEXT_VERTICAL_PAD)


def draw_team_branding(layout: bpy.types.UILayout) -> None:
    box = layout.box()
    outer = box.column(align=True)

    _vertical_pad(outer, PANEL_VERTICAL_PAD)

    row = outer.row(align=True)
    row.alignment = "CENTER"

    icon_id = logo_icon_id()
    if icon_id:
        logo_row = row.row(align=True)
        logo_row.alignment = "CENTER"
        logo_row.template_icon(icon_value=icon_id, scale=LOGO_ICON_SCALE)

        text_wrap = row.row()
        text_wrap.alignment = "CENTER"
        text_wrap.scale_x = 1.0
        _draw_branding_text(text_wrap)
    else:
        text_wrap = row.row()
        text_wrap.alignment = "CENTER"
        text_wrap.scale_x = 1.0
        _draw_branding_text(text_wrap)

    _vertical_pad(outer, PANEL_VERTICAL_PAD)


def register() -> None:
    global _preview_collection
    if _preview_collection is not None:
        return

    _preview_collection = bpy.utils.previews.new()
    _ensure_logo_preview()


def unregister() -> None:
    global _preview_collection
    if _preview_collection is None:
        return

    bpy.utils.previews.remove(_preview_collection)
    _preview_collection = None
