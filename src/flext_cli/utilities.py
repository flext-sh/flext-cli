"""FLEXT CLI Utility Classes with Static Methods.

Provides comprehensive utility classes following user requirement to
"criar utilities classes com métodos estáticos"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

from flext_core import FlextResult
from rich.table import Table

from flext_cli.config import FlextCliSettings


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
    """Static utility methods for CLI validation operations."""

    @staticmethod
    def validate_email(email: str) -> FlextResult[bool]:
        """Validate an email address format.

        Args:
            email: Email address to validate

        Returns:
            FlextResult[bool]: True if valid email format

        """
        if not email.strip():
            return FlextResult[bool].fail("Email cannot be empty")

        # Basic email validation pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = bool(re.match(email_pattern, email.strip()))
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
        """Validate and parse JSON string.

        Args:
            json_str: JSON string to validate and parse

        Returns:
            FlextResult[JsonObject]: Parsed JSON object

        """
        if not json_str.strip():
            return FlextResult[JsonObject].fail("JSON string cannot be empty")

        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return FlextResult[JsonObject].ok(parsed)  # type: ignore[arg-type]  # Dict is compatible with JsonObject
            return FlextResult[JsonObject].fail("JSON must be an object")
        except json.JSONDecodeError as e:
            return FlextResult[JsonObject].fail(f"Invalid JSON: {e}")


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
        """Format data as pretty JSON string.

        Args:
            data: Data to format as JSON

        Returns:
            FlextResult[str]: Pretty formatted JSON string

        """
        try:
            formatted = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            return FlextResult[str].ok(formatted)
        except (TypeError, ValueError) as e:
            return FlextResult[str].fail(f"Failed to format JSON: {e}")

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
        """Format duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            FlextResult[str]: Formatted duration string

        """
        try:
            if seconds < 0:
                return FlextResult[str].fail("Duration cannot be negative")

            # Constants for time conversion
            seconds_per_minute = 60
            seconds_per_hour = 3600

            if seconds < 1:
                return FlextResult[str].ok(f"{seconds * 1000:.1f}ms")
            if seconds < seconds_per_minute:
                return FlextResult[str].ok(f"{seconds:.2f}s")
            if seconds < seconds_per_hour:
                minutes = int(seconds // seconds_per_minute)
                remaining_seconds = seconds % seconds_per_minute
                return FlextResult[str].ok(f"{minutes}m {remaining_seconds:.1f}s")
            hours = int(seconds // seconds_per_hour)
            remaining_minutes = int((seconds % seconds_per_hour) // seconds_per_minute)
            remaining_seconds = seconds % seconds_per_minute
            return FlextResult[str].ok(
                f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"
            )

        except (TypeError, ValueError) as e:
            return FlextResult[str].fail(f"Invalid duration: {e}")

    @staticmethod
    def truncate_string(
        text: str, max_length: int, suffix: str = "..."
    ) -> FlextResult[str]:
        """Truncate string to maximum length with suffix.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncating

        Returns:
            FlextResult[str]: Truncated string

        """
        try:
            if max_length < 0:
                return FlextResult[str].fail("Max length cannot be negative")

            if len(text) <= max_length:
                return FlextResult[str].ok(text)

            if max_length <= len(suffix):
                return FlextResult[str].ok(text[:max_length])

            truncated = text[: max_length - len(suffix)] + suffix
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
    def get_current_timestamp() -> FlextResult[datetime]:
        """Get current UTC timestamp.

        Returns:
            FlextResult[datetime]: Current UTC datetime

        """
        try:
            current_time = datetime.now(UTC)
            return FlextResult[datetime].ok(current_time)
        except Exception as e:
            return FlextResult[datetime].fail(f"Failed to get timestamp: {e}")

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
    def parse_timestamp(
        timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> FlextResult[datetime]:
        """Parse timestamp string to datetime.

        Args:
            timestamp_str: Timestamp string to parse
            format_str: Format string

        Returns:
            FlextResult[datetime]: Parsed datetime object

        """
        try:
            if not timestamp_str.strip():
                return FlextResult[datetime].fail("Timestamp cannot be empty")

            dt = datetime.strptime(timestamp_str, format_str).replace(tzinfo=UTC)
            return FlextResult[datetime].ok(dt)

        except ValueError as e:
            return FlextResult[datetime].fail(f"Failed to parse timestamp: {e}")

    @staticmethod
    def get_time_difference(start: datetime, end: datetime) -> FlextResult[float]:
        """Get time difference in seconds.

        Args:
            start: Start datetime
            end: End datetime

        Returns:
            FlextResult[float]: Difference in seconds

        """
        try:
            difference = (end - start).total_seconds()
            return FlextResult[float].ok(difference)

        except Exception as e:
            return FlextResult[float].fail(f"Failed to calculate time difference: {e}")
