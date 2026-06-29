"""Extension root path on disk."""

from __future__ import annotations

import os

# Leading dot on bundled image filenames (e.g. ``.opengate-16_9.png``).
IMAGE_FILENAME_DOT_PREFIX = "."


def prefixed_image_filename(basename: str) -> str:
    """Return ``basename`` with the required leading dot prefix."""
    if basename.startswith(IMAGE_FILENAME_DOT_PREFIX):
        return basename
    return f"{IMAGE_FILENAME_DOT_PREFIX}{basename}"


def extension_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extension_asset_abspath(*relative_parts: str) -> str:
    """Absolute path to a file inside the extension (cross-platform)."""
    return os.path.normpath(os.path.join(extension_root(), *relative_parts))
