"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 Algar Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from importlib.metadata import metadata

_metadata = metadata("flext_cli")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata["Author"]
__author_email__ = _metadata["Author-Email"]
__license__ = _metadata["License"]
# Validate URL explicitly - no fallback to empty string
_home_page = _metadata.get("Home-Page")
__url__ = _home_page if _home_page is not None else ""

__all__ = [
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
