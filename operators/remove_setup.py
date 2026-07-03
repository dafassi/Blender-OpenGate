"""Remove OpenGate mask setup from the scene."""

import bpy

from ..core.mask_setup import clear_mask_setup


class OPENGATE_OT_remove_setup(bpy.types.Operator):
    bl_idname = "opengate.remove_setup"
    bl_label = "Remove OpenGate Setup"
    bl_description = (
        "Remove mask overlay, restore camera backgrounds, safe areas, and render "
        "resolution, delete the image collector, and reset framing masks"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clear_mask_setup(context)
        self.report({"INFO"}, "OpenGate setup removed")
        return {"FINISHED"}


_classes = (OPENGATE_OT_remove_setup,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
