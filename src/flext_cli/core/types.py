"""Custom parameter types for FLEXT CLI framework.

Built on flext-core foundation for robust CLI type validation.
Uses Click parameter types with modern Python 3.13 patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from urllib.parse import urlparse

import click

if TYPE_CHECKING:
    from click import Context
    from click import Parameter


class PositiveInt(click.ParamType):
    """Click parameter type for positive integers."""

    name = "positive_int"

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> int:
        """Convert value to positive integer with validation."""
        try:
            int_value = int(value)
            if int_value <= 0:
                self.fail(f"{value} is not a positive integer", param, ctx)
            return int_value
        except ValueError:
            self.fail(f"{value} is not a valid integer", param, ctx)


class FilePath(click.ParamType):
    """Click parameter type for file paths that must exist."""

    name = "file_path"

    def __init__(self, exists: bool = True, readable: bool = True) -> None:
        """Initialize file path validator."""
        self.exists = exists
        self.readable = readable

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> Path:
        """Convert value to validated Path object."""
        path = Path(value)

        if self.exists and not path.exists():
            self.fail(f"File '{value}' does not exist", param, ctx)

        if self.exists and not path.is_file():
            self.fail(f"'{value}' is not a file", param, ctx)

        if self.readable and self.exists:
            try:
                path.open("r").close()
            except OSError:
                self.fail(f"File '{value}' is not readable", param, ctx)

        return path


class DirectoryPath(click.ParamType):
    """Click parameter type for directory paths."""

    name = "directory_path"

    def __init__(self, exists: bool = True, writable: bool = False) -> None:
        """Initialize directory path validator."""
        self.exists = exists
        self.writable = writable

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> Path:
        """Convert value to validated directory Path."""
        path = Path(value)

        if self.exists and not path.exists():
            self.fail(f"Directory '{value}' does not exist", param, ctx)

        if self.exists and not path.is_dir():
            self.fail(f"'{value}' is not a directory", param, ctx)

        if self.writable and self.exists:
            try:
                # Try to create a temporary file to test writability
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
            except OSError:
                self.fail(f"Directory '{value}' is not writable", param, ctx)

        return path


class URLType(click.ParamType):
    """Click parameter type for URLs."""

    name = "url"

    def __init__(self, schemes: list[str] | None = None) -> None:
        """Initialize URL validator with allowed schemes."""
        self.schemes = schemes or ["http", "https"]

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> str:
        """Convert value to validated URL string."""
        try:
            parsed = urlparse(value)

            if not parsed.scheme:
                self.fail(f"'{value}' is not a valid URL (missing scheme)", param, ctx)

            if parsed.scheme not in self.schemes:
                self.fail(
                    f"URL scheme '{parsed.scheme}' not allowed. "
                    f"Allowed schemes: {', '.join(self.schemes)}",
                    param,
                    ctx,
                )

            if not parsed.netloc:
                self.fail(f"'{value}' is not a valid URL (missing netloc)", param, ctx)

            return value
        except Exception as e:
            self.fail(f"Invalid URL '{value}': {e}", param, ctx)


class PortType(click.ParamType):
    """Click parameter type for network ports."""

    name = "port"

    def __init__(self, min_port: int = 1, max_port: int = 65535) -> None:
        """Initialize port validator with range limits."""
        self.min_port = min_port
        self.max_port = max_port

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> int:
        """Convert value to validated port number."""
        try:
            port = int(value)
            if not (self.min_port <= port <= self.max_port):
                self.fail(
                    f"Port {port} is out of range ({self.min_port}-{self.max_port})",
                    param,
                    ctx,
                )
            return port
        except ValueError:
            self.fail(f"'{value}' is not a valid port number", param, ctx)


# Pre-configured instances for common use
POSITIVE_INT = PositiveInt()
FILE_PATH = FilePath(exists=True, readable=True)
NEW_FILE_PATH = FilePath(exists=False, readable=False)
DIRECTORY_PATH = DirectoryPath(exists=True, writable=False)
WRITABLE_DIRECTORY = DirectoryPath(exists=True, writable=True)
URL = URLType()
HTTPS_URL = URLType(schemes=["https"])
PORT = PortType()
