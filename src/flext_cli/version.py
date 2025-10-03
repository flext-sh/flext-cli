"""Version and package metadata using importlib.metadata."""

from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

_metadata = metadata("flext-cli")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata.get("Author")
__author_email__ = _metadata.get("Author-Email")
__license__ = _metadata.get("License")
__url__ = _metadata.get("Home-Page")


class FlextCliVersion:
    """Structured metadata for the flext cli distribution."""

    def __init__(self, version: str, version_info: tuple[int | str, ...]) -> None:
        """Initialize version metadata.

        Args:
            version: Version string
            version_info: Version info tuple

        """
        self.version = version
        self.version_info = version_info

    @classmethod
    def current(cls) -> FlextCliVersion:
        """Return canonical metadata loaded from package metadata."""
        return cls(__version__, __version_info__)


VERSION: Final[FlextCliVersion] = FlextCliVersion.current()

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
