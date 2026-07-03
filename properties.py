"""Scene-level custom properties for OpenGate."""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from .core import masks
from .core.background_image import (
    clear_opengate_background,
    sync_opengate_background,
    sync_opengate_background_opacity,
)
from .core.camera_target import (
    camera_poll,
    ensure_default_target_cameras_for_all_scenes,
    get_target_camera,
    is_valid_camera,
    target_camera_update_suppressed,
)
from .core.masks import has_active_framing_mask, MaskFlag
from .core.mask_setup import mask_setup_clearing, try_ensure_mask_setup
from .core.render_format import (
    CANVAS_RESOLUTION_DEFAULT,
    CANVAS_RESOLUTION_MAX,
    CANVAS_RESOLUTION_MIN,
    apply_canvas_resolution,
)
from .core.platform_presets import (
    enum_items,
    platform_has_safezones,
    preset_by_id,
    recommended_canvas_percent,
)
from .core.camera_display import (
    display_update_suppressed,
    pull_display_settings_from_camera,
    push_passepartout_to_camera,
    release_camera_safe_areas,
    schedule_camera_safe_areas_sync,
)


_APPLYING_PLATFORM_PRESET = False


def _rebuild_mask_flags(settings: "OpenGateSceneSettings") -> None:
    flags = 0
    if settings.mask_16_9:
        flags |= masks.MaskFlag.RATIO_16_9
    if settings.mask_9_16:
        flags |= masks.MaskFlag.RATIO_9_16
    if settings.mask_5_4:
        flags |= masks.MaskFlag.RATIO_5_4
    settings.mask_flags = flags
    if settings.show_safezones and (
        flags != int(MaskFlag.RATIO_9_16)
        or not platform_has_safezones(settings.platform_preset)
    ):
        settings.show_safezones = False


def _apply_platform_preset(settings: "OpenGateSceneSettings", preset_id: str) -> None:
    global _APPLYING_PLATFORM_PRESET
    preset = preset_by_id(preset_id)
    _APPLYING_PLATFORM_PRESET = True
    try:
        if preset is None:
            return
        settings.mask_16_9 = preset.mask_16_9
        settings.mask_9_16 = preset.mask_9_16
        settings.mask_5_4 = preset.mask_5_4
        settings.canvas_resolution = recommended_canvas_percent(preset)
    finally:
        _APPLYING_PLATFORM_PRESET = False


def _platform_preset_update(self, context):
    if context is None:
        return
    _apply_platform_preset(self, self.platform_preset)
    _sync_mask_update(self, context)


def _sync_mask_opacity_update(self, context):
    if context is None or mask_setup_clearing():
        return
    scene = context.scene
    if has_active_framing_mask(self) and self.show_mask:
        sync_opengate_background_opacity(self, scene)
    else:
        _sync_mask_update(self, context)


def _sync_mask_update(self, context):
    if context is None or mask_setup_clearing():
        return
    if (
        not _APPLYING_PLATFORM_PRESET
        and self.platform_preset != "NONE"
    ):
        preset = preset_by_id(self.platform_preset)
        if preset is not None and not preset.matches_settings(self):
            self.platform_preset = "NONE"

    _rebuild_mask_flags(self)

    scene = context.scene
    self.mask_sync_message = ""

    if has_active_framing_mask(self) and self.show_mask:
        apply_canvas_resolution(scene, self.canvas_resolution)
        try:
            sync_opengate_background(self, scene)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            self.mask_sync_message = str(exc)
    else:
        clear_opengate_background(scene, self)

    schedule_camera_safe_areas_sync(scene)


def _apply_canvas_resolution_update(self, context):
    if context is None or mask_setup_clearing():
        return
    apply_canvas_resolution(context.scene, self.canvas_resolution)
    if has_active_framing_mask(self):
        schedule_camera_safe_areas_sync(context.scene)


def _viewport_display_update(self, context):
    if context is None or display_update_suppressed():
        return
    push_passepartout_to_camera(self, get_target_camera(self, context.scene))


def _target_camera_update(self, context):
    if context is None or target_camera_update_suppressed():
        return

    new_camera = self.target_camera
    if new_camera is not None and not is_valid_camera(new_camera):
        return

    scene = context.scene
    old_name = self.get("_last_target_camera_name", "")
    old_camera = bpy.data.objects.get(old_name) if old_name else None

    if (
        old_camera is not None
        and old_camera != new_camera
        and old_camera.type == "CAMERA"
    ):
        from .core.background_image import clear_opengate_background

        release_camera_safe_areas(scene, old_camera.data)
        clear_opengate_background(scene, self, camera=old_camera)

    if (
        new_camera is not None
        and has_active_framing_mask(self)
        and self.show_mask
    ):
        try_ensure_mask_setup(context)

    pull_display_settings_from_camera(self, new_camera)
    schedule_camera_safe_areas_sync(scene)

    if new_camera is not None:
        self["_last_target_camera_name"] = new_camera.name
    elif "_last_target_camera_name" in self:
        del self["_last_target_camera_name"]


class OpenGateSceneSettings(bpy.types.PropertyGroup):
    mask_sync_message: StringProperty(
        name="Mask Sync Message",
        description="Last mask sync error (shown in panel when set)",
        default="",
        options={"HIDDEN"},
    )

    canvas_resolution: FloatProperty(
        name="Resolution",
        description="Square render size (% of 4320×4320 open gate)",
        min=CANVAS_RESOLUTION_MIN,
        max=CANVAS_RESOLUTION_MAX,
        default=CANVAS_RESOLUTION_DEFAULT,
        precision=2,
        step=1,
        subtype="PERCENTAGE",
        update=_apply_canvas_resolution_update,
    )

    target_camera: PointerProperty(
        name="Camera",
        description="Camera for mask overlay, safe areas, and crop guides",
        type=bpy.types.Object,
        poll=camera_poll,
        update=_target_camera_update,
    )

    platform_preset: EnumProperty(
        name="Platform",
        description="Delivery target — sets masks, limits, and FPS hints",
        items=enum_items(),
        default="NONE",
        update=_platform_preset_update,
    )

    mask_16_9: BoolProperty(
        name="16:9",
        description="16:9 landscape crop overlay",
        default=False,
        update=_sync_mask_update,
    )

    mask_9_16: BoolProperty(
        name="9:16",
        description="9:16 portrait/story crop overlay",
        default=False,
        update=_sync_mask_update,
    )

    mask_5_4: BoolProperty(
        name="5:4",
        description="5:4 feed crop overlay",
        default=False,
        update=_sync_mask_update,
    )

    show_safezones: BoolProperty(
        name="Show Safezones",
        description="Platform UI safe zones (9:16 only, needs preset)",
        default=False,
        update=_sync_mask_update,
    )

    mask_flags: IntProperty(
        name="Mask Flags",
        description="Internal bitmask of active framing masks",
        default=0,
        min=0,
    )

    show_mask: BoolProperty(
        name="Show Overlay",
        description="Show mask image on camera background",
        default=True,
        update=_sync_mask_update,
    )

    mask_opacity: FloatProperty(
        name="Mask Opacity",
        description="Mask overlay opacity in camera view",
        min=0.0,
        max=1.0,
        default=0.95,
        subtype="FACTOR",
        update=_sync_mask_opacity_update,
    )

    show_passepartout: BoolProperty(
        name="Passepartout",
        description="Dim viewport outside the camera frame",
        default=True,
        update=_viewport_display_update,
    )

    passepartout_alpha: FloatProperty(
        name="Passepartout Opacity",
        description="Passepartout strength in camera view",
        min=0.0,
        max=1.0,
        default=0.75,
        subtype="FACTOR",
        update=_viewport_display_update,
    )


_classes = (OpenGateSceneSettings,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.opengate = PointerProperty(type=OpenGateSceneSettings)

    def _deferred_default_cameras() -> None:
        ensure_default_target_cameras_for_all_scenes()
        for scene in bpy.data.scenes:
            settings = getattr(scene, "opengate", None)
            if settings is not None and has_active_framing_mask(settings):
                schedule_camera_safe_areas_sync(scene)
        return None

    bpy.app.timers.register(_deferred_default_cameras, first_interval=0.0)


def unregister():
    del bpy.types.Scene.opengate
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
