"""OpenGate UI panels."""

from . import branding, panels

_modules = (panels,)


def register():
    branding.register()
    for mod in _modules:
        mod.register()


def unregister():
    for mod in reversed(_modules):
        mod.unregister()
    branding.unregister()
