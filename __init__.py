"""OpenGate — Social media render format extension for Blender.

Concept, masks, architecture, and tests are original handcrafted work by the
FLIP Fluids team. Python source code was written with AI assistance.
"""

from . import (
    operators,
    prefs,
    properties,
    ui,
)
from .core import handlers
from .core.render_format import apply_opengate_canvas_to_all_scenes

_modules = (
    properties,
    prefs,
    operators,
    ui,
)


def register():
    for mod in _modules:
        mod.register()
    handlers.register()
    apply_opengate_canvas_to_all_scenes()


def unregister():
    handlers.unregister()
    for mod in reversed(_modules):
        mod.unregister()
