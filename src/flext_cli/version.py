"""FLEXT CLI Version - Single unified class following FLEXT standards.

Provides version and package metadata using importlib.metadata.
Single FlextCliVersion class with nested version subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

from flext_core import FlextService


class FlextCliVersion(FlextService[object]):
    """Single unified CLI version class following FLEXT standards.

    Provides version and package metadata using importlib.metadata.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    def __init__(self, **data: object) -> None:
        """Initialize version service with metadata."""
        super().__init__(**data)
        self._metadata = metadata("flext-cli")
        self._version = self._metadata["Version"]
        self._version_info = tuple(
            int(part) if part.isdigit() else part for part in self._version.split(".")
        )

    @property
    def version(self) -> str:
        """Get version string."""
        return self._version

    @property
    def version_info(self) -> tuple[int | str, ...]:
        """Get version info tuple."""
        return self._version_info

    @property
    def title(self) -> str:
        """Get package title."""
        return self._metadata["Name"]

    @property
    def description(self) -> str:
        """Get package description."""
        return self._metadata["Summary"]

    @property
    def author(self) -> str | None:
        """Get package author."""
        return self._metadata.get("Author")

    @property
    def author_email(self) -> str | None:
        """Get package author email."""
        return self._metadata.get("Author-Email")

    @property
    def license(self) -> str | None:
        """Get package license."""
        return self._metadata.get("License")

    @property
    def url(self) -> str | None:
        """Get package URL."""
        return self._metadata.get("Home-Page")

    @classmethod
    def current(cls) -> FlextCliVersion:
        """Return canonical version instance loaded from package metadata."""
        return cls()


# Create singleton instance for module-level access
_VERSION_INSTANCE: Final[FlextCliVersion] = FlextCliVersion.current()

# Module-level properties for backward compatibility
__version__: str = _VERSION_INSTANCE.version
__version_info__: tuple[int | str, ...] = _VERSION_INSTANCE.version_info
__title__: str = _VERSION_INSTANCE.title
__description__: str = _VERSION_INSTANCE.description
__author__: str | None = _VERSION_INSTANCE.author
__author_email__: str | None = _VERSION_INSTANCE.author_email
__license__: str | None = _VERSION_INSTANCE.license
__url__: str | None = _VERSION_INSTANCE.url

VERSION: Final[FlextCliVersion] = _VERSION_INSTANCE

__all__ = [
    "VERSION",
    "FlextCliVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
