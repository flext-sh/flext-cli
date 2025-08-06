"""FlextCli Helpers - Zero-Boilerplate Utility Functions.

This module provides comprehensive helper functions and classes for massive
boilerplate reduction in CLI applications. All helpers follow flext-core patterns
and use FlextResult for railway-oriented programming.

Helper Categories:
    - File Operations: Load, save, validate files with zero error handling
    - Data Processing: Transform, validate, format data with built-in error recovery
    - User Interaction: Prompts, confirmations, progress tracking
    - Configuration: Environment loading, validation, type conversion

Examples:
    >>> from flext_cli import flext_cli_load_json, flext_cli_save_data
    >>>
    >>> # Zero-boilerplate file operations
    >>> data = flext_cli_load_json("config.json").unwrap()
    >>> flext_cli_save_data(data, "output.yaml", format="yaml").unwrap()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from urllib.parse import urlparse

import yaml
import toml

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm
from rich.table import Table

from flext_cli.core.typedefs import (
    FlextCliValidationType,
)

# Type aliases to avoid false positive FBT001 warnings
FlextCliData = dict[str, object] | list[object] | str | float | int | None

# Dynamic imports are used in methods to avoid MyPy issues

# Constants
MAX_PORT_NUMBER = 65535
MIN_PORT_NUMBER = 1


class FlextCliHelper:
    """FlextCli helper class for zero-boilerplate operations.

    Provides comprehensive helper methods for common CLI operations with
    built-in error handling, validation, and FlextResult patterns.

    Features:
        - File operations with automatic format detection
        - Data validation with type-safe patterns
        - User interaction with Rich console integration
        - Progress tracking with customizable displays

    Examples:
        >>> helper = FlextCliHelper()
        >>> result = helper.flext_cli_load_file("data.json")
        >>> if result.success:
        ...     print(f"Loaded: {result.data}")

    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize FlextCli helper.

        Args:
            console: Optional Rich console instance (created if None)

        """
        self.console = console or Console()

    def flext_cli_load_file(self, path: str | Path) -> FlextResult[dict[str, object]]:
        """Load file with automatic format detection.

        Zero-boilerplate file loading that automatically detects format
        based on file extension and handles all errors gracefully.

        Args:
            path: Path to file to load

        Returns:
            FlextResult containing loaded data or error message

        Examples:
            >>> helper = FlextCliHelper()
            >>> data = helper.flext_cli_load_file("config.json").unwrap()
            >>> data = helper.flext_cli_load_file("data.yaml").unwrap()

        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                return FlextResult.fail(f"File not found: {path}")

            content = file_path.read_text(encoding="utf-8")

            # Auto-detect format based on extension
            if file_path.suffix.lower() == ".json":
                data = json.loads(content)
            elif file_path.suffix.lower() in {".yaml", ".yml"}:
                data = yaml.safe_load(content)
            elif file_path.suffix.lower() == ".toml":
                data = toml.loads(content)
            else:
                # Return raw text for unknown formats
                data = content

            return FlextResult.ok(data)

        except json.JSONDecodeError as e:
            return FlextResult.fail(f"Invalid JSON format: {e}")
        except Exception as e:
            return FlextResult.fail(f"Failed to load file {path}: {e}")

    def flext_cli_save_file(
        self,
        data: FlextCliData,
        path: str | Path,
        file_format: str | None = None,
    ) -> FlextResult[None]:
        """Save data to file with automatic format handling.

        Zero-boilerplate file saving that automatically handles format
        conversion and creates directories as needed.

        Args:
            data: Data to save
            path: Destination file path
            file_format: Optional format override (auto-detected if None)

        Returns:
            FlextResult indicating success or failure

        Examples:
            >>> helper = FlextCliHelper()
            >>> helper.flext_cli_save_file({"key": "value"}, "output.json").unwrap()
            >>> helper.flext_cli_save_file(data, "output.yaml", file_format="yaml").unwrap()

        """
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Determine format
            save_format = file_format or file_path.suffix.lower().lstrip(".")

            if save_format == "json":
                content = json.dumps(data, indent=2, ensure_ascii=False)
            elif save_format in {"yaml", "yml"}:
                content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            elif save_format == "toml":
                # TOML only supports dict data
                if not isinstance(data, dict):
                    return FlextResult.fail("TOML format requires dictionary data")
                content = toml.dumps(data)
            else:
                # Save as plain text
                content = str(data)

            file_path.write_text(content, encoding="utf-8")
            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Failed to save file {path}: {e}")

    def flext_cli_validate_input(  # noqa: PLR0912
        self,
        value: str,
        validation_type: FlextCliValidationType,
    ) -> FlextResult[bool]:
        """Validate input with built-in validators.

        Zero-boilerplate input validation using predefined validators
        with comprehensive error messages.

        Args:
            value: Value to validate
            validation_type: Type of validation to perform

        Returns:
            FlextResult indicating validation success or failure

        Examples:
            >>> helper = FlextCliHelper()
            >>> result = helper.flext_cli_validate_input("test@example.com", FlextCliValidationType.EMAIL)
            >>> is_valid = result.unwrap()

        """
        # Using re and urlparse imported at module level

        # Direct validation with early returns (Clean Code pattern)
        try:
            if validation_type == FlextCliValidationType.EMAIL:
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, value):
                    return FlextResult.fail(f"Invalid email format: {value}")
                return FlextResult.ok(data=True)

            if validation_type == FlextCliValidationType.URL:
                try:
                    result = urlparse(value)
                    if not all([result.scheme, result.netloc]):
                        return FlextResult.fail(f"Invalid URL format: {value}")
                    return FlextResult.ok(data=True)
                except Exception:
                    return FlextResult.fail(f"Invalid URL format: {value}")

            elif validation_type == FlextCliValidationType.PATH:
                try:
                    Path(value)
                    return FlextResult.ok(data=True)
                except (ValueError, TypeError):
                    return FlextResult.fail(f"Invalid path format: {value}")

            elif validation_type == FlextCliValidationType.FILE:
                path = Path(value)
                if not path.exists():
                    return FlextResult.fail(f"File does not exist: {value}")
                if not path.is_file():
                    return FlextResult.fail(f"Path is not a file: {value}")
                return FlextResult.ok(data=True)

            elif validation_type == FlextCliValidationType.DIR:
                path = Path(value)
                if not path.exists():
                    return FlextResult.fail(f"Directory does not exist: {value}")
                if not path.is_dir():
                    return FlextResult.fail(f"Path is not a directory: {value}")
                return FlextResult.ok(data=True)

            elif validation_type == FlextCliValidationType.UUID:
                try:
                    uuid.UUID(value)
                    return FlextResult.ok(data=True)
                except ValueError:
                    return FlextResult.fail(f"Invalid UUID format: {value}")

            elif validation_type == FlextCliValidationType.PORT:
                try:
                    port = int(value)
                    if not (MIN_PORT_NUMBER <= port <= MAX_PORT_NUMBER):
                        return FlextResult.fail(f"Invalid port number (1-65535): {value}")
                    return FlextResult.ok(data=True)
                except ValueError:
                    return FlextResult.fail(f"Invalid port number: {value}")

            # All enum values exhaustively handled above

        except Exception as e:
            return FlextResult.fail(f"Validation error: {e}")

    def flext_cli_create_table(
        self,
        data: list[dict[str, object]],
        title: str | None = None,
    ) -> FlextResult[Table]:
        """Create Rich table from data with automatic column detection.

        Zero-boilerplate table creation that automatically detects columns
        and formats data for Rich console display.

        Args:
            data: List of dictionaries to display
            title: Optional table title

        Returns:
            FlextResult containing Rich Table or error message

        Examples:
            >>> helper = FlextCliHelper()
            >>> data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
            >>> table = helper.flext_cli_create_table(data, title="Users").unwrap()
            >>> helper.console.print(table)

        """
        try:
            if not data:
                return FlextResult.fail("Cannot create table from empty data")

            table = Table(title=title)

            # Auto-detect columns from first row
            columns = list(data[0].keys())
            for column in columns:
                table.add_column(column.replace("_", " ").title())

            # Add rows
            for row in data:
                values = [str(row.get(col, "")) for col in columns]
                table.add_row(*values)

            return FlextResult.ok(table)

        except Exception as e:
            return FlextResult.fail(f"Failed to create table: {e}")

    def flext_cli_confirm(
        self,
        message: str,
        *,
        default: bool = False,
    ) -> FlextResult[bool]:
        """Get user confirmation with zero boilerplate.

        Zero-boilerplate confirmation dialog with Rich console integration
        and automatic default handling.

        Args:
            message: Confirmation message to display
            default: Default value if user presses Enter

        Returns:
            FlextResult containing user's choice

        Examples:
            >>> helper = FlextCliHelper()
            >>> confirmed = helper.flext_cli_confirm("Delete all files?").unwrap()
            >>> if confirmed:
            ...     print("User confirmed deletion")

        """
        try:
            result = Confirm.ask(message, default=default, console=self.console)
            return FlextResult.ok(result)

        except KeyboardInterrupt:
            return FlextResult.fail("Operation cancelled by user")
        except Exception as e:
            return FlextResult.fail(f"Confirmation failed: {e}")


# Zero-Boilerplate Utility Functions
def flext_cli_load_json(path: str | Path) -> FlextResult[dict[str, object]]:
    """Load JSON file with zero boilerplate.

    Args:
        path: Path to JSON file

    Returns:
        FlextResult containing loaded JSON data

    Examples:
        >>> data = flext_cli_load_json("config.json").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_load_file(path)


def flext_cli_save_data(
    data: FlextCliData,
    path: str | Path,
    file_format: str = "json",
) -> FlextResult[None]:
    """Save data to file with zero boilerplate.

    Args:
        data: Data to save
        path: Destination path
        file_format: File format (json, yaml, toml)

    Returns:
        FlextResult indicating success or failure

    Examples:
        >>> flext_cli_save_data({"key": "value"}, "output.json").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_save_file(data, path, file_format)


def flext_cli_validate_email(email: str) -> FlextResult[bool]:
    """Validate email with zero boilerplate.

    Args:
        email: Email address to validate

    Returns:
        FlextResult containing validation result

    Examples:
        >>> is_valid = flext_cli_validate_email("test@example.com").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_validate_input(email, FlextCliValidationType.EMAIL)


def flext_cli_create_progress() -> Progress:
    """Create Rich progress bar with sensible defaults.

    Returns:
        Configured Progress instance

    Examples:
        >>> progress = flext_cli_create_progress()
        >>> task = progress.add_task("Processing...", total=100)
        >>> progress.update(task, advance=10)

    """
    return Progress(
        "[progress.description]{task.description}",
        "[progress.percentage]{task.percentage:>3.0f}%",
        "[bar][progress.completed]{task.completed}/{task.total}",
    )


def flext_cli_batch_validate(inputs: dict[str, tuple[str, str]]) -> FlextResult[dict[str, str]]:
    """Batch validate multiple inputs with specified types.

    Args:
        inputs: Dict mapping field names to (value, validation_type) tuples

    Returns:
        FlextResult containing validated inputs dict

    Example:
        >>> inputs = {"email": ("user@test.com", "email"), "port": ("8080", "port")}
        >>> result = flext_cli_batch_validate(inputs)
        >>> if result.success:
        ...     print("All valid:", result.data)

    """
    helper = FlextCliHelper()
    validated = {}

    for field_name, (value, validation_type) in inputs.items():
        if validation_type == "email":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.EMAIL)
        elif validation_type == "url":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.URL)
        elif validation_type == "path":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.PATH)
        elif validation_type == "file":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.FILE)
        elif validation_type == "uuid":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.UUID)
        elif validation_type == "port":
            result = helper.flext_cli_validate_input(value, FlextCliValidationType.PORT)
        else:
            return FlextResult.fail(f"Unknown validation type: {validation_type}")

        if not result.success:
            return FlextResult.fail(f"Validation failed for {field_name}: {result.error}")

        validated[field_name] = value

    return FlextResult.ok(validated)


def flext_cli_quick_confirm(message: str, *, default: bool = False) -> bool:
    """Quick confirmation dialog with automatic error handling.

    Args:
        message: Confirmation message
        default: Default value on error or empty input

    Returns:
        User's confirmation choice (default on error)

    Examples:
        >>> if flext_cli_quick_confirm("Continue with operation?"):
        ...     perform_operation()

    """
    try:
        helper = FlextCliHelper()
        result = helper.flext_cli_confirm(message, default=default)
        return result.unwrap_or(default)
    except Exception:
        return default


# Factory functions for easy instantiation
def flext_cli_create_helper(console: Console | None = None) -> FlextCliHelper:
    """Create FlextCliHelper with optional configuration.

    Args:
        console: Optional Rich console instance

    Returns:
        Configured FlextCliHelper instance

    Examples:
        >>> helper = flext_cli_create_helper()
        >>> result = helper.flext_cli_load_file("data.json")

    """
    return FlextCliHelper(console=console)


# Legacy alias for backward compatibility
CLIHelper = FlextCliHelper
