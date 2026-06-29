"""Set the OpenGate canvas to a standard format preset."""

import bpy

from ..core.render_format import (
    CANVAS_FORMAT_PRESETS,
    canvas_percent_for_preset,
    canvas_preset_description,
)

_classes: tuple[type, ...] = ()


def _make_canvas_preset_operator(
    preset_id: str,
    label: str,
) -> type:
    bl_idname = f"opengate.set_canvas_{preset_id.lower()}"

    def execute(self, context):
        percent = canvas_percent_for_preset(preset_id)
        if percent is None:
            return {"CANCELLED"}
        context.scene.opengate.canvas_resolution = percent
        return {"FINISHED"}

    return type(
        f"OPENGATE_OT_canvas_{preset_id}",
        (bpy.types.Operator,),
        {
            "bl_idname": bl_idname,
            "bl_label": label,
            "bl_description": canvas_preset_description(preset_id),
            "bl_options": {"REGISTER", "UNDO", "INTERNAL"},
            "execute": execute,
        },
    )


def register():
    global _classes
    _classes = tuple(
        _make_canvas_preset_operator(preset_id, label)
        for preset_id, _percent, label in CANVAS_FORMAT_PRESETS
    )
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
