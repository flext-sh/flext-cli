"""Version and package metadata from project declarations.

Single source of truth lives in pyproject.toml.
This module reads required package metadata directly from the local project
declarations and fails fast if any mandatory field is missing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import t

_PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"
_PROJECT_METADATA = tomllib.loads(_PYPROJECT_PATH.read_text(encoding="utf-8"))[
    "project"
]
_AUTHOR_METADATA = _PROJECT_METADATA["authors"][0]

__version__ = _PROJECT_METADATA["version"]
_version_without_metadata = __version__.split("+", maxsplit=1)[0]
_version_base, _has_prerelease, _prerelease = _version_without_metadata.partition("-")
_base_parts = _version_base.split(".")
_prerelease_parts: t.StrSequence = _prerelease.split(".") if _has_prerelease else []
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in _base_parts + _prerelease_parts
)
__title__ = _PROJECT_METADATA["name"]
__description__ = _PROJECT_METADATA["description"]
__author__ = _AUTHOR_METADATA["name"]
__author_email__ = _AUTHOR_METADATA["email"]
__license__ = _PROJECT_METADATA["license"]
__url__ = _PROJECT_METADATA["urls"]["Homepage"]
__all__: list[str] = [
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
