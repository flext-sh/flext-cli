"""FLEXT CLI Utilities - Extension of flext-core FlextUtilities.

Provides CLI-specific utilities while massively using FlextUtilities from flext-core.
Follows FLEXT architectural pattern of extending core functionality with proper prefixes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, cast

from flext_core import FlextResult, FlextUtilities
from rich.table import Table

from flext_cli import FlextCliSettings

# Re-export FlextUtilities for convenience
FlextCliUtilities = FlextUtilities


class JsonObject(TypedDict, total=False):
    """Type definition for parsed JSON objects."""

    # Allow any string keys with object values
    # Will be extended as dict[str, object]


class FileInfo(TypedDict):
    """Type definition for file information."""

    path: str
    size: int
    modified: datetime
    is_file: bool
    is_directory: bool
    permissions: str


class FlextCliValidationUtilities:
    """CLI-specific validation utilities extending flext-core patterns."""

    @staticmethod
    def validate_email(email: str) -> FlextResult[bool]:
        """Validate an email address format using flext-core type guards.

        Args:
            email: Email address to validate

        Returns:
            FlextResult[bool]: True if valid email format

        """
        # Use FlextUtilities type guards and text processing
        if not FlextUtilities.is_non_empty_string(email):
            return FlextResult[bool].fail("Email cannot be empty")

        # Use flext-core text processing for cleaning
        clean_email = FlextUtilities.clean_text(email.strip())

        # Basic email validation pattern using FlextUtilities
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = bool(re.match(email_pattern, clean_email))
        return (
            FlextResult[bool].ok(is_valid)
            if is_valid
            else FlextResult[bool].fail("Invalid email format")
        )

    @staticmethod
    def validate_path(path: str | Path) -> FlextResult[Path]:
        """Validate and convert path to Path object.

        Args:
            path: Path string or Path object

        Returns:
            FlextResult[Path]: Validated Path object

        """
        try:
            # Always try to create Path object - this will validate the type
            path_obj = Path(path)

            # Basic path validation
            if str(path_obj).strip() == "":
                return FlextResult[Path].fail("Path cannot be empty")

            return FlextResult[Path].ok(path_obj)

        except (TypeError, ValueError) as e:
            return FlextResult[Path].fail(f"Invalid path: {e}")
        except Exception as e:
            return FlextResult[Path].fail(f"Unexpected error: {e}")

    @staticmethod
    def validate_config(config: object) -> FlextResult[bool]:
        """Validate CLI configuration object.

        Args:
            config: Configuration object to validate

        Returns:
            FlextResult[bool]: True if configuration is valid

        """
        if config is None:
            return FlextResult[bool].fail("Configuration cannot be None")

        is_cli_settings = isinstance(config, FlextCliSettings)
        is_pydantic_model = hasattr(config, "model_config")

        if is_cli_settings or is_pydantic_model:
            return FlextResult[bool].ok(is_cli_settings or is_pydantic_model)

        return FlextResult[bool].fail("Invalid configuration type")

    @staticmethod
    def validate_json_string(json_str: str) -> FlextResult[JsonObject]:
        """Validate and parse JSON string using FlextUtilities.

        Args:
            json_str: JSON string to validate and parse

        Returns:
            FlextResult[JsonObject]: Parsed JSON object

        """
        # Use FlextUtilities for safe JSON parsing
        if not FlextUtilities.is_non_empty_string(json_str):
            return FlextResult[JsonObject].fail("JSON string cannot be empty")

        # Use flext-core safe JSON parsing
        parsed_dict = FlextUtilities.safe_json_parse(json_str.strip())
        if not parsed_dict:
            return FlextResult[JsonObject].fail("Invalid JSON format")

        return FlextResult[JsonObject].ok(cast("JsonObject", parsed_dict))


class FlextCliFileUtilities:
    """Static utility methods for CLI file operations."""

    @staticmethod
    def ensure_directory_exists(directory: str | Path) -> FlextResult[Path]:
        """Ensure directory exists, creating it if necessary.

        Args:
            directory: Directory path to ensure exists

        Returns:
            FlextResult[Path]: Path to the directory

        """
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            return FlextResult[Path].ok(dir_path)
        except (OSError, PermissionError) as e:
            return FlextResult[Path].fail(f"Failed to create directory: {e}")

    @staticmethod
    def read_text_file(file_path: str | Path) -> FlextResult[str]:
        """Read text content from file.

        Args:
            file_path: Path to the file to read

        Returns:
            FlextResult[str]: File content

        """
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[str].fail("File does not exist")

            if not path.is_file():
                return FlextResult[str].fail("Path is not a file")

            content = path.read_text(encoding="utf-8")
            return FlextResult[str].ok(content)

        except (OSError, UnicodeDecodeError) as e:
            return FlextResult[str].fail(f"Failed to read file: {e}")

    @staticmethod
    def write_text_file(file_path: str | Path, content: str) -> FlextResult[None]:
        """Write text content to file.

        Args:
            file_path: Path to the file to write
            content: Content to write

        Returns:
            FlextResult[None]: Success or failure

        """
        try:
            path = Path(file_path)
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            path.write_text(content, encoding="utf-8")
            return FlextResult[None].ok(None)

        except (OSError, PermissionError) as e:
            return FlextResult[None].fail(f"Failed to write file: {e}")

    @staticmethod
    def get_file_info(file_path: str | Path) -> FlextResult[FileInfo]:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            FlextResult[FileInfo]: File information

        """
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[FileInfo].fail("File does not exist")

            stat = path.stat()
            info: FileInfo = {
                "path": str(path.absolute()),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "permissions": oct(stat.st_mode)[-3:],
            }

            return FlextResult[FileInfo].ok(info)

        except (OSError, ValueError) as e:
            return FlextResult[FileInfo].fail(f"Failed to get file info: {e}")


class FlextCliFormattingUtilities:
    """Static utility methods for CLI formatting and output."""

    @staticmethod
    def format_json_pretty(data: object) -> FlextResult[str]:
        """Format data as pretty JSON string using FlextUtilities.

        Args:
            data: Data to format as JSON

        Returns:
            FlextResult[str]: Pretty formatted JSON string

        """
        # Use FlextUtilities for safe JSON stringification
        formatted = FlextUtilities.safe_json_stringify(data)
        if formatted == "{}" and data != {}:
            return FlextResult[str].fail("Failed to format data as JSON")
        return FlextResult[str].ok(formatted)

    @staticmethod
    def create_table(
        title: str,
        headers: list[str],
        rows: list[list[str]],
    ) -> FlextResult[Table]:
        """Create a Rich table with the given data.

        Args:
            title: Table title
            headers: Column headers
            rows: Table rows

        Returns:
            FlextResult[Table]: Rich Table object

        """
        try:
            table = Table(title=title)

            # Add columns
            for header in headers:
                table.add_column(header)

            # Add rows
            for row in rows:
                if len(row) != len(headers):
                    return FlextResult[Table].fail(
                        f"Row has {len(row)} columns, expected {len(headers)}"
                    )
                table.add_row(*row)

            return FlextResult[Table].ok(table)

        except Exception as e:
            return FlextResult[Table].fail(f"Failed to create table: {e}")

    @staticmethod
    def format_duration(seconds: float) -> FlextResult[str]:
        """Format duration using FlextUtilities.

        Args:
            seconds: Duration in seconds

        Returns:
            FlextResult[str]: Formatted duration string

        """
        try:
            # Use FlextUtilities for duration formatting
            formatted = FlextUtilities.format_duration(seconds)
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Invalid duration: {e}")

    @staticmethod
    def truncate_string(
        text: str, max_length: int, suffix: str = "..."
    ) -> FlextResult[str]:
        """Truncate string using FlextUtilities.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncating

        Returns:
            FlextResult[str]: Truncated string

        """
        try:
            # Use FlextUtilities for text truncation
            truncated = FlextUtilities.truncate(text, max_length, suffix)
            return FlextResult[str].ok(truncated)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to truncate string: {e}")


class FlextCliSystemUtilities:
    """Static utility methods for CLI system operations."""

    @staticmethod
    def get_environment_variable(
        var_name: str, default: str | None = None
    ) -> FlextResult[str]:
        """Get environment variable value.

        Args:
            var_name: Environment variable name
            default: Default value if not found

        Returns:
            FlextResult[str]: Environment variable value

        """
        if not var_name.strip():
            return FlextResult[str].fail("Variable name cannot be empty")

        value = os.environ.get(var_name, default)
        if value is None:
            return FlextResult[str].fail(f"Environment variable '{var_name}' not found")

        return FlextResult[str].ok(value)

    @staticmethod
    def set_environment_variable(var_name: str, value: str) -> FlextResult[None]:
        """Set environment variable value.

        Args:
            var_name: Environment variable name
            value: Value to set

        Returns:
            FlextResult[None]: Success or failure

        """
        try:
            if not var_name.strip():
                return FlextResult[None].fail("Variable name cannot be empty")

            os.environ[var_name] = value
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to set environment variable: {e}")

    @staticmethod
    def get_current_working_directory() -> FlextResult[Path]:
        """Get current working directory.

        Returns:
            FlextResult[Path]: Current working directory

        """
        try:
            cwd = Path.cwd()
            return FlextResult[Path].ok(cwd)
        except (OSError, RuntimeError) as e:
            return FlextResult[Path].fail(f"Failed to get current directory: {e}")

    @staticmethod
    def check_file_permissions(
        file_path: str | Path, mode: str = "r"
    ) -> FlextResult[bool]:
        """Check file permissions.

        Args:
            file_path: Path to file to check
            mode: Permission mode to check ("r", "w", "x")

        Returns:
            FlextResult[bool]: True if permission exists

        """
        try:
            path = Path(file_path)

            if not path.exists():
                return FlextResult[bool].fail("File does not exist")

            if mode == "r":
                has_permission = os.access(path, os.R_OK)
            elif mode == "w":
                has_permission = os.access(path, os.W_OK)
            elif mode == "x":
                has_permission = os.access(path, os.X_OK)
            else:
                return FlextResult[bool].fail(f"Invalid permission mode: {mode}")

            return FlextResult[bool].ok(has_permission)

        except Exception as e:
            return FlextResult[bool].fail(f"Failed to check permissions: {e}")


class FlextCliTimeUtilities:
    """Static utility methods for CLI time operations."""

    @staticmethod
    def get_current_timestamp() -> FlextResult[str]:
        """Get current timestamp using FlextUtilities.

        Returns:
            FlextResult[str]: Current timestamp as string

        """
        try:
            # Use FlextUtilities for timestamp generation
            timestamp = FlextUtilities.generate_timestamp()
            return FlextResult[str].ok(str(timestamp))
        except Exception as e:
            return FlextResult[str].fail(f"Failed to get timestamp: {e}")

    @staticmethod
    def get_current_iso_timestamp() -> FlextResult[str]:
        """Get current ISO timestamp using FlextUtilities.

        Returns:
            FlextResult[str]: Current ISO timestamp

        """
        try:
            # Use FlextUtilities for ISO timestamp generation
            timestamp = FlextUtilities.generate_iso_timestamp()
            return FlextResult[str].ok(timestamp)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to get ISO timestamp: {e}")

    @staticmethod
    def format_timestamp(
        dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> FlextResult[str]:
        """Format datetime as string.

        Args:
            dt: Datetime object to format
            format_str: Format string

        Returns:
            FlextResult[str]: Formatted datetime string

        """
        try:
            formatted = dt.strftime(format_str)
            return FlextResult[str].ok(formatted)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult[str].fail(f"Failed to format timestamp: {e}")
        except Exception as e:
            return FlextResult[str].fail(f"Unexpected error: {e}")

    @staticmethod
    def parse_iso_timestamp(timestamp_str: str) -> FlextResult[object]:
        """Parse ISO timestamp string using FlextUtilities.

        Args:
            timestamp_str: ISO timestamp string to parse

        Returns:
            FlextResult[object]: Parsed datetime object

        """
        try:
            # Use FlextUtilities type guard for validation
            if not FlextUtilities.is_non_empty_string(timestamp_str):
                return FlextResult[object].fail("Timestamp cannot be empty")

            # Use FlextUtilities for ISO timestamp parsing
            dt = FlextUtilities.parse_iso_timestamp(timestamp_str.strip())
            return FlextResult[object].ok(dt)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to parse timestamp: {e}")

    @staticmethod
    def get_elapsed_time(start_time: float) -> FlextResult[float]:
        """Get elapsed time using FlextUtilities.

        Args:
            start_time: Start timestamp

        Returns:
            FlextResult[float]: Elapsed time in seconds

        """
        try:
            # Use FlextUtilities for elapsed time calculation
            from datetime import datetime
            start_datetime = datetime.fromtimestamp(start_time)
            elapsed = FlextUtilities.get_elapsed_time(start_datetime)
            return FlextResult[float].ok(elapsed)
        except Exception as e:
            return FlextResult[float].fail(f"Failed to calculate elapsed time: {e}")
