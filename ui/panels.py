"""Main OpenGate sidebar panel."""

import bpy

from ..core import masks
from ..core.platform_presets import (
    DISCLAIMER,
    VERIFIED_AS_OF,
    crop_resolution_label,
    format_duration,
    format_recommended_length,
    format_scene_fps,
    format_verified_as_of,
    platform_has_safezones,
    preset_by_id,
    scene_duration_seconds,
)
from ..core.render_format import (
    CANVAS_FORMAT_PRESETS,
    active_canvas_preset,
    canvas_pixel_size,
)
from ..core.camera_target import get_target_camera, schedule_default_target_camera
from .branding import draw_team_branding


class OPENGATE_PT_main(bpy.types.Panel):
    bl_label = "OpenGate"
    bl_idname = "OPENGATE_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenGate"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene is not None and hasattr(scene, "opengate")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.opengate
        schedule_default_target_camera(scene)
        camera = get_target_camera(settings, scene)

        layout.use_property_split = False
        layout.use_property_decorate = False

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(settings, "target_camera", text="Camera")
        select_btn = row.row(align=True)
        select_btn.scale_x = 0.6
        select_btn.enabled = camera is not None
        select_btn.operator(
            "opengate.select_target_camera",
            text="",
            icon="RESTRICT_SELECT_OFF",
        )
        if camera is None:
            col.label(text="Assign a scene camera", icon="ERROR")

        layout.separator()

        box = layout.box()
        box.label(text="Platform", icon="URL")
        col = box.column(align=True)
        col.prop(settings, "platform_preset", text="Preset")

        preset = preset_by_id(settings.platform_preset)
        if preset is not None:
            box.separator()
            stats = box.column(align=True)
            stats.label(
                text=f"Recommendations (as of {format_verified_as_of(VERIFIED_AS_OF)}):",
                icon="PRESET",
            )
            stats.separator(factor=0.35)
            stats.label(text=f"Active: {preset.label}")
            stats.label(
                text=(
                    f"Platform resolution: "
                    f"{preset.delivery_width}×{preset.delivery_height} "
                    f"({preset.recommended_fps_label} fps)"
                ),
            )
            stats.label(
                text=f"Length up to: {format_recommended_length(preset.max_duration_sec)}",
            )
            gap = box.row()
            gap.scale_y = 0.35
            box.label(text=DISCLAIMER, icon="INFO")

        layout.separator()

        box = layout.box()
        box.label(text="Framing Masks", icon="MOD_MASK")
        col = box.column(align=True)
        col.enabled = camera is not None
        col.prop(settings, "mask_16_9")
        col.prop(settings, "mask_9_16")
        col.prop(settings, "mask_5_4")

        if platform_has_safezones(settings.platform_preset):
            safezones_row = col.row()
            safezones_row.enabled = (
                settings.mask_flags == int(masks.MaskFlag.RATIO_9_16)
            )
            safezones_row.prop(settings, "show_safezones")

        if settings.mask_sync_message:
            box.label(text=settings.mask_sync_message, icon="ERROR")

        layout.separator()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.use_property_split = False
        row.prop(settings, "show_mask", text="")
        row.prop(settings, "mask_opacity", text="Mask")

        row = col.row(align=True)
        row.use_property_split = False
        row.prop(settings, "show_passepartout", text="")
        sub = row.row(align=True)
        sub.enabled = settings.show_passepartout
        sub.prop(settings, "passepartout_alpha", text="Passepartout", slider=True)

        layout.separator()

        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator("opengate.remove_setup", icon="TRASH")

        layout.separator()

        box = layout.box()
        box.label(text="Canvas")

        active_preset = active_canvas_preset(settings.canvas_resolution)
        for row_index in range(0, len(CANVAS_FORMAT_PRESETS), 2):
            row = box.row(align=True)
            row.scale_y = 1.3
            for preset_id, _percent, label in CANVAS_FORMAT_PRESETS[row_index:row_index + 2]:
                pressed = active_preset == preset_id
                op = row.operator(
                    f"opengate.set_canvas_{preset_id.lower()}",
                    text=label,
                    depress=pressed,
                )

        col = box.column(align=True)
        col.prop(settings, "canvas_resolution", slider=True, text="Resolution")

        size = canvas_pixel_size(settings.canvas_resolution)
        crop_label = crop_resolution_label(settings, settings.canvas_resolution)

        box.separator()
        info = box.column(align=True)
        export = info.column(align=True)
        export.label(text="Your export resolution:")
        export.label(
            text=(
                f"{size} × {size} px / "
                f"{format_scene_fps(scene)} / "
                f"{format_duration(scene_duration_seconds(scene))}"
            ),
        )
        if crop_label:
            info.separator(factor=0.35)
            post = info.column(align=True)
            post.label(text="Your post resolution:")
            post.label(text=f"{crop_label} / {format_scene_fps(scene)}")

        layout.separator()
        draw_team_branding(layout)


_classes = (OPENGATE_PT_main,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
