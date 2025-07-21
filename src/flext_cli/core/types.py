"""FLEXT CLI custom parameter types - Unified typing system using flext-core.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module builds on the unified typing system in flext-core and defines
CLI-specific Click parameter types using modern Python 3.13 patterns.
Uses real Click framework with zero tolerance for mock implementations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import click

# Import from unified core typing system
from flext_core.domain.shared_types import (
    URL as CORE_URL,
    DirPath,
    FilePath as CoreFilePath,
    Port as CorePort,
    PositiveInt as CorePositiveInt,
)

if TYPE_CHECKING:
    from click import Context, Parameter


# ==============================================================================
# CLICK PARAMETER TYPES USING UNIFIED CORE TYPES
# ==============================================================================


class PositiveInt(click.ParamType):
    """Click parameter type for positive integers using flext-core validation."""

    name = "positive_int"

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> CorePositiveInt:
        """Convert value to core PositiveInt type."""
        try:
            int_value = int(value)
            if int_value <= 0:
                self.fail(f"{value} is not a positive integer", param, ctx)
            # Return the actual validated type from core
            return int_value  # CorePositiveInt annotation applied
        except ValueError:
            self.fail(f"{value} is not a valid integer", param, ctx)


class FilePath(click.ParamType):
    """Click parameter type for file paths using flext-core FilePath validation."""

    name = "file_path"

    def __init__(self, exists: bool = True, readable: bool = True) -> None:
        """Initialize file path validator with core type validation."""
        self.exists = exists
        self.readable = readable

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> CoreFilePath:
        """Convert value to validated Path object using core types."""
        path = Path(value)

        if self.exists and not path.exists():
            self.fail(f"File '{value}' does not exist", param, ctx)

        if self.exists and not path.is_file():
            self.fail(f"'{value}' is not a file", param, ctx)

        if self.readable and self.exists:
            try:
                path.open("r", encoding="utf-8").close()
            except OSError:
                self.fail(f"File '{value}' is not readable", param, ctx)

        # Return core FilePath type
        return path


class DirectoryPath(click.ParamType):
    """Click parameter type for directory paths using flext-core DirPath validation."""

    name = "directory_path"

    def __init__(self, exists: bool = True, writable: bool = False) -> None:
        """Initialize directory path validator using core type validation."""
        self.exists = exists
        self.writable = writable

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> DirPath:
        """Convert value to validated directory Path using core types."""
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

        # Return core DirPath type
        return path


class URLType(click.ParamType):
    """Click parameter type for URLs using flext-core URL validation."""

    name = "url"

    def __init__(self, schemes: list[str] | None = None) -> None:
        """Initialize URL validator with allowed schemes using core validation."""
        self.schemes = schemes or ["http", "https"]

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> CORE_URL:
        """Convert value to validated URL using core types."""
        try:
            # Ensure value is a string
            value_str = str(value)
            parsed = urlparse(value_str)

            if not parsed.scheme:
                self.fail(
                    f"'{value_str}' is not a valid URL (missing scheme)",
                    param,
                    ctx,
                )

            if parsed.scheme not in self.schemes:
                self.fail(
                    f"URL scheme '{parsed.scheme}' not allowed. "
                    f"Allowed schemes: {', '.join(self.schemes)}",
                    param,
                    ctx,
                )

            if not parsed.netloc:
                self.fail(
                    f"'{value_str}' is not a valid URL (missing netloc)",
                    param,
                    ctx,
                )

            # Return core URL type
            return value_str
        except Exception as e:
            self.fail(f"Invalid URL '{value}': {e}", param, ctx)


class PortType(click.ParamType):
    """Click parameter type for network ports using flext-core Port validation."""

    name = "port"

    def __init__(self, min_port: int = 1, max_port: int = 65535) -> None:
        """Initialize port validator with range limits using core validation."""
        self.min_port = min_port
        self.max_port = max_port

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> CorePort:
        """Convert value to core Port type."""
        try:
            port = int(value)
            if not (self.min_port <= port <= self.max_port):
                self.fail(
                    f"Port {port} is out of range ({self.min_port}-{self.max_port})",
                    param,
                    ctx,
                )
            # Return core Port type
            return port
        except ValueError:
            self.fail(f"'{value}' is not a valid port number", param, ctx)


# ==============================================================================
# PRE-CONFIGURED INSTANCES FOR COMMON CLI USAGE
# ==============================================================================

# Click parameter type instances using unified core validation
POSITIVE_INT = PositiveInt()
FILE_PATH = FilePath(exists=True, readable=True)
NEW_FILE_PATH = FilePath(exists=False, readable=False)
DIRECTORY_PATH = DirectoryPath(exists=True, writable=False)
WRITABLE_DIRECTORY = DirectoryPath(exists=True, writable=True)
URL = URLType()
HTTPS_URL = URLType(schemes=["https"])
PORT = PortType()

# ==============================================================================
# EXPORTS - ALL CLI PARAMETER TYPES
# ==============================================================================

__all__ = [
    # Core types from unified system
    "CORE_URL",
    # Pre-configured instances
    "DIRECTORY_PATH",
    "FILE_PATH",
    "HTTPS_URL",
    "NEW_FILE_PATH",
    "PORT",
    "POSITIVE_INT",
    "URL",
    "WRITABLE_DIRECTORY",
    "CoreFilePath",
    "CorePort",
    "CorePositiveInt",
    "DirPath",
    # Click parameter type classes
    "DirectoryPath",
    "FilePath",
    "PortType",
    "PositiveInt",
    "URLType",
]
