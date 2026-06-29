"""Addon preferences."""

import bpy
from bpy.props import FloatProperty

from .ui.branding import draw_preferences_about


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
        layout.use_property_split = False

        box = layout.box()
        box.label(text="About", icon="INFO")
        draw_preferences_about(box)

        layout.separator()
        layout.prop(self, "default_mask_opacity")


_classes = (OpenGatePreferences,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
