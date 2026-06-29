"""Addon preferences."""

import bpy
from bpy.props import FloatProperty

from .ui.branding import FLIP_FLUIDS_URL, MAINTAINER_LABEL, draw_team_branding


class OpenGatePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    default_mask_opacity: FloatProperty(
        name="Default Mask Opacity",
        description="Starting opacity when a mask overlay is first applied",
        min=0.0,
        max=1.0,
        default=0.95,
        subtype="FACTOR",
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="About", icon="INFO")
        draw_team_branding(box)
        row = box.row()
        row.label(text="Maintainer")
        row.label(text=MAINTAINER_LABEL)
        row = box.row()
        row.operator("wm.url_open", text="FLIP Fluids", icon="URL").url = FLIP_FLUIDS_URL

        layout.separator()
        layout.prop(self, "default_mask_opacity")


_classes = (OpenGatePreferences,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
