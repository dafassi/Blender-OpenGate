"""OpenGate — Social media render format extension for Blender.

Copyright (C) 2026 Dennis Fassbaender & Ryan Guy
SPDX-License-Identifier: GPL-3.0-or-later

Developers: Dennis Fassbaender & Ryan Guy (support@flipfluids.com)

Concept, masks, architecture, and tests are original work by the FLIP Fluids team.
Note: Python source was written with AI assistance.
"""

from . import (
    operators,
    prefs,
    properties,
    ui,
)
from .core import handlers

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


def unregister():
    handlers.unregister()
    for mod in reversed(_modules):
        mod.unregister()
