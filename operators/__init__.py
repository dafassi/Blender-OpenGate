"""OpenGate operators."""

from . import canvas_preset
from . import remove_setup
from . import select_target_camera

_modules = (
    canvas_preset,
    remove_setup,
    select_target_camera,
)


def register():
    for mod in _modules:
        mod.register()


def unregister():
    for mod in reversed(_modules):
        mod.unregister()
