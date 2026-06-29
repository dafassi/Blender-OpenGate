"""Select the OpenGate target camera in the viewport and outliner."""

import bpy

from ..core.camera_target import get_target_camera


class OPENGATE_OT_select_target_camera(bpy.types.Operator):
    bl_idname = "opengate.select_target_camera"
    bl_label = "Select Camera"
    bl_description = "Select OpenGate camera in viewport and outliner"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None or not hasattr(scene, "opengate"):
            return False
        return get_target_camera(scene.opengate, scene) is not None

    def execute(self, context):
        scene = context.scene
        camera = get_target_camera(scene.opengate, scene)
        if camera is None:
            self.report({"WARNING"}, "No camera assigned")
            return {"CANCELLED"}

        view_layer = context.view_layer
        for obj in view_layer.objects.selected:
            obj.select_set(False)
        camera.select_set(True)
        view_layer.objects.active = camera
        return {"FINISHED"}


_classes = (OPENGATE_OT_select_target_camera,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
