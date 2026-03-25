"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from importlib.metadata import metadata

_metadata = metadata("flext_cli")
_raw_version = _metadata["Version"]
__version__ = re.sub(
    r"(\d)(a|b|rc)(\d+)$",
    "\\1-\\2\\3",
    re.sub(r"\.dev(\d+)$", r"-dev\1", _raw_version),
)
_version_without_metadata = __version__.split("+", maxsplit=1)[0]
_version_base, _has_prerelease, _prerelease = _version_without_metadata.partition("-")
_base_parts = _version_base.split(".")
_prerelease_parts: list[str] = _prerelease.split(".") if _has_prerelease else []
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in _base_parts + _prerelease_parts
)
_name = _metadata.get("Name")
__title__ = _name if _name is not None else ""
_summary = _metadata.get("Summary")
__description__ = _summary if _summary is not None else ""
_author = _metadata.get("Author")
__author__ = _author if _author is not None else ""
_author_email = _metadata.get("Author-Email")
__author_email__ = _author_email if _author_email is not None else ""
_license_value = _metadata.get("License")
__license__ = _license_value if _license_value is not None else ""
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
