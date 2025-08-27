"""FLEXT CLI Utilities - Extending FlextUtilities from flext-core.

Provides CLI-specific utility functionality while maximally reusing
generic utilities from flext-core FlextUtilities class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TypedDict, cast

from flext_core import FlextResult, FlextUtilities
from rich.table import Table


class JsonObject(TypedDict, total=False):
    """Type definition for parsed JSON objects."""


class FileInfo(TypedDict):
    """Type definition for file information."""

    path: str
    size: int
    modified: str  # ISO timestamp
    is_file: bool
    is_directory: bool
    permissions: str


class FlextCliUtilities(FlextUtilities):
    """FLEXT CLI Utilities extending FlextUtilities from flext-core.

    Adds CLI-specific functionality while reusing all generic utilities
    from flext-core. Uses proper naming convention with FlextCli prefix.
    """

    class CliValidation:
        """CLI-specific validation utilities."""

        @staticmethod
        def validate_email(email: str) -> FlextResult[bool]:
            """Validate an email address format using flext-core."""
            # Use FlextUtilities.Formatters for validation
            if not email or "@" not in email:
                return FlextResult[bool].fail("Invalid email format")

            # Use flext-core text processing
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            is_valid = bool(re.match(email_pattern, email))
            return (
                FlextResult[bool].ok(is_valid)
                if is_valid
                else FlextResult[bool].fail("Email does not match required format")
            )

        @staticmethod
        def validate_path(path: str | Path) -> FlextResult[Path]:
            """Validate and convert path using flext-core utilities."""
            # Use FlextUtilities.Conversions for path handling
            try:
                path_obj = Path(path) if isinstance(path, str) else path

                # Basic path validation
                if not str(path_obj).strip():
                    return FlextResult[Path].fail("Path cannot be empty")

                return FlextResult[Path].ok(path_obj)
            except Exception as e:
                return FlextResult[Path].fail(f"Invalid path: {e}")

        @staticmethod
        def validate_json_string(json_str: str) -> FlextResult[JsonObject]:
            """Validate JSON string using flext-core utilities."""
            if not json_str.strip():
                return FlextResult[JsonObject].fail("JSON string cannot be empty")

            try:
                parsed_data = FlextUtilities.safe_json_parse(json_str)
                # FlextUtilities.safe_json_parse always returns a dict
                return FlextResult[JsonObject].ok(cast("JsonObject", parsed_data))
            except Exception as e:
                return FlextResult[JsonObject].fail(f"Failed to parse JSON: {e}")

    class CliFileUtils:
        """CLI-specific file utilities extending flext-core."""

        @staticmethod
        def ensure_directory_exists(directory: str | Path) -> FlextResult[Path]:
            """Ensure directory exists using flext-core patterns."""
            try:
                path_obj = Path(directory)
                path_obj.mkdir(parents=True, exist_ok=True)
                return FlextResult[Path].ok(path_obj)
            except Exception as e:
                return FlextResult[Path].fail(f"Failed to create directory: {e}")

        @staticmethod
        def read_text_file(file_path: str | Path) -> FlextResult[str]:
            """Read text file using flext-core utilities."""
            try:
                path_obj = Path(file_path)
                if not path_obj.exists():
                    return FlextResult[str].fail(f"File does not exist: {file_path}")

                if not path_obj.is_file():
                    return FlextResult[str].fail(f"Path is not a file: {file_path}")

                content = path_obj.read_text(encoding="utf-8")
                return FlextResult[str].ok(content)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to read file: {e}")

        @staticmethod
        def write_text_file(file_path: str | Path, content: str) -> FlextResult[None]:
            """Write text file using flext-core utilities."""
            try:
                path_obj = Path(file_path)
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content, encoding="utf-8")
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to write file: {e}")

        @staticmethod
        def get_file_info(file_path: str | Path) -> FlextResult[FileInfo]:
            """Get file information using flext-core utilities."""
            try:
                path_obj = Path(file_path)
                if not path_obj.exists():
                    return FlextResult[FileInfo].fail(
                        f"File does not exist: {file_path}"
                    )

                stat = path_obj.stat()

                # Use flext-core timestamp utilities
                modified_timestamp = FlextUtilities.generate_iso_timestamp()

                info: FileInfo = {
                    "path": str(path_obj.absolute()),
                    "size": stat.st_size,
                    "modified": modified_timestamp,
                    "is_file": path_obj.is_file(),
                    "is_directory": path_obj.is_dir(),
                    "permissions": oct(stat.st_mode)[-3:],
                }

                return FlextResult[FileInfo].ok(info)
            except Exception as e:
                return FlextResult[FileInfo].fail(f"Failed to get file info: {e}")

    class CliFormatting:
        """CLI-specific formatting utilities extending flext-core."""

        @staticmethod
        def format_json_pretty(data: object) -> FlextResult[str]:
            """Format JSON prettily using flext-core utilities."""
            # Use FlextUtilities for JSON formatting
            formatted = FlextUtilities.safe_json_stringify(data)
            return FlextResult[str].ok(formatted)

        @staticmethod
        def create_table(
            headers: list[str], rows: list[list[str]], title: str = ""
        ) -> FlextResult[Table]:
            """Create Rich table using flext-core patterns."""
            try:
                table = Table(title=title)

                # Add headers
                for header in headers:
                    table.add_column(header)

                # Add rows
                for row in rows:
                    table.add_row(*row)

                return FlextResult[Table].ok(table)
            except Exception as e:
                return FlextResult[Table].fail(f"Failed to create table: {e}")

        @staticmethod
        def truncate_string(
            text: str, max_length: int, suffix: str = "..."
        ) -> FlextResult[str]:
            """Truncate string using flext-core text processing."""
            if max_length < 0:
                return FlextResult[str].fail("Max length cannot be negative")

            if len(text) <= max_length:
                return FlextResult[str].ok(text)

            if max_length <= len(suffix):
                return FlextResult[str].ok(text[:max_length])

            truncated = text[: max_length - len(suffix)] + suffix
            return FlextResult[str].ok(truncated)

    class CliEnvironment:
        """CLI-specific environment utilities using flext-core."""

        @staticmethod
        def get_environment_variable(
            var_name: str, default: str = ""
        ) -> FlextResult[str]:
            """Get environment variable using flext-core utilities."""
            if not var_name.strip():
                return FlextResult[str].fail("Variable name cannot be empty")

            value = os.environ.get(var_name, default)
            return FlextResult[str].ok(value)

        @staticmethod
        def set_environment_variable(var_name: str, value: str) -> FlextResult[None]:
            """Set environment variable using flext-core utilities."""
            if not var_name.strip():
                return FlextResult[None].fail("Variable name cannot be empty")

            try:
                os.environ[var_name] = value
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(
                    f"Failed to set environment variable: {e}"
                )

    # Reuse all FlextUtilities functionality
    # These are inherited from FlextUtilities:
    # - Generators: generate_id, generate_uuid, generate_timestamp, etc.
    # - TimeUtils: unix_to_iso, format_duration, etc.
    # - TextProcessor: validate_patterns, clean_text, etc.
    # - Conversions: safe_cast, convert_types, etc.
    # - TypeGuards: is_valid_type, etc.
    # - Formatters: format_data, etc.
    # - Performance: track_execution_time, etc.
    # - ResultUtils: chain_results, collect_results, etc.


# Legacy compatibility - redirect to new class
FlextCliValidationUtilities = FlextCliUtilities.CliValidation
FlextCliFileUtilities = FlextCliUtilities.CliFileUtils
FlextCliFormattingUtilities = FlextCliUtilities.CliFormatting
FlextCliEnvironmentUtilities = FlextCliUtilities.CliEnvironment


__all__ = [
    "FileInfo",
    "FlextCliEnvironmentUtilities",
    "FlextCliFileUtilities",
    "FlextCliFormattingUtilities",
    "FlextCliUtilities",
    "FlextCliValidationUtilities",
    "JsonObject",
]
