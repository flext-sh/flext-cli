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
import subprocess
import time
import uuid
from pathlib import Path
from subprocess import TimeoutExpired
from urllib.parse import urlparse

import toml
import yaml
from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm, Prompt
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

    def __init__(self, console: Console | None = None, *, quiet: bool = False) -> None:
        """Initialize FlextCli helper.

        Args:
            console: Optional Rich console instance (created if None)
            quiet: If True, enables quiet mode for confirmations and prompts

        """
        self.console = console or Console()
        self.quiet = quiet

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
            >>> helper.flext_cli_save_file(
            ...     data, "output.yaml", file_format="yaml"
            ... ).unwrap()

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

    def flext_cli_validate_input(
        self,
        value: str,
        validation_type: FlextCliValidationType,
    ) -> FlextResult[bool]:
        """Validate input with built-in validators using Strategy Pattern.

        SOLID REFACTORING: Reduced complexity from 20 to 2 by extracting
        focused validator functions using Strategy Pattern.

        Args:
            value: Value to validate
            validation_type: Type of validation to perform

        Returns:
            FlextResult indicating validation success or failure

        Examples:
            >>> helper = FlextCliHelper()
            >>> result = helper.flext_cli_validate_input(
            ...     "test@example.com", FlextCliValidationType.EMAIL
            ... )
            >>> is_valid = result.unwrap()

        """
        try:
            # Strategy Pattern: delegate to specialized validators
            validators = {
                FlextCliValidationType.EMAIL: self._validate_email,
                FlextCliValidationType.URL: self._validate_url,
                FlextCliValidationType.PATH: self._validate_path,
                FlextCliValidationType.FILE: self._validate_file,
                FlextCliValidationType.DIR: self._validate_directory,
                FlextCliValidationType.UUID: self._validate_uuid,
                FlextCliValidationType.PORT: self._validate_port,
            }

            validator = validators.get(validation_type)
            if validator is None:
                return FlextResult.fail(f"Unknown validation type: {validation_type}")

            return validator(value)

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
        and automatic default handling. In quiet mode, returns default without prompting.

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
            # In quiet mode, return default without prompting
            if self.quiet:
                return FlextResult.ok(default)

            result = Confirm.ask(message, default=default, console=self.console)
            return FlextResult.ok(result)

        except KeyboardInterrupt:
            return FlextResult.fail("Operation cancelled by user")
        except Exception as e:
            return FlextResult.fail(f"Confirmation failed: {e}")

    def flext_cli_prompt(
        self,
        message: str,
        default: str | None = None,
    ) -> FlextResult[str]:
        """Get user input with zero boilerplate.

        Zero-boilerplate user prompt with Rich console integration,
        automatic validation, and default value handling.

        Args:
            message: Prompt message to display
            default: Default value if user presses Enter (None for required input)

        Returns:
            FlextResult containing user's input

        Examples:
            >>> helper = FlextCliHelper()
            >>> name = helper.flext_cli_prompt("Enter your name:").unwrap()
            >>> email = helper.flext_cli_prompt(
            ...     "Email:", default="user@example.com"
            ... ).unwrap()

        """
        try:
            result = Prompt.ask(message, default=default, console=self.console)

            # If no default and user provided empty input, fail
            if not result and default is None:
                return FlextResult.fail("Input is required")

            # Use default if result is empty
            final_result = result or default
            return FlextResult.ok(final_result or "")

        except KeyboardInterrupt:
            return FlextResult.fail("Operation cancelled by user")
        except Exception as e:
            return FlextResult.fail(f"Prompt failed: {e}")

    def flext_cli_execute_command(
        self,
        command: str,
        timeout: int | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute shell command with zero boilerplate.

        Zero-boilerplate command execution with subprocess integration,
        automatic error handling, and comprehensive result reporting.

        Args:
            command: Shell command to execute
            timeout: Optional timeout in seconds (None for no timeout)

        Returns:
            FlextResult containing execution details dict with keys:
            - success: bool indicating if command succeeded (returncode == 0)
            - stdout: str containing command output
            - stderr: str containing command errors
            - returncode: int command exit code

        Examples:
            >>> helper = FlextCliHelper()
            >>> result = helper.flext_cli_execute_command("echo 'test'").unwrap()
            >>> if result["success"]:
            ...     print(f"Output: {result['stdout']}")

        """
        try:
            # Validate command
            if not command or not command.strip():
                return FlextResult.fail("Command cannot be empty")

            # Execute command with proper error handling
            try:
                process_result = subprocess.run(
                    command,
                    shell=True,  # Intentional for CLI helper functionality
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,  # Don't raise exception on non-zero exit
                )

                # Build comprehensive result dict
                execution_result = {
                    "success": process_result.returncode == 0,
                    "stdout": process_result.stdout or "",
                    "stderr": process_result.stderr or "",
                    "returncode": process_result.returncode,
                }

                return FlextResult.ok(execution_result)

            except TimeoutExpired:
                return FlextResult.fail(f"Command timed out after {timeout} seconds")

        except Exception as e:
            return FlextResult.fail(f"Command execution failed: {e}")

    def flext_cli_with_progress(
        self,
        items: list[object],
        description: str,
    ) -> list[object]:
        """Process items with progress tracking display.

        Zero-boilerplate progress tracking that displays progress bar
        while processing items. This is a simple version that returns
        items unchanged but can be extended for actual processing.

        Args:
            items: List of items to process
            description: Progress description text

        Returns:
            The same items list (suitable for progress display)

        Examples:
            >>> helper = FlextCliHelper()
            >>> items = ["file1", "file2", "file3"]
            >>> processed = helper.flext_cli_with_progress(items, "Processing files")
            >>> assert processed == items

        """
        # Simple implementation - just return the items
        # Can be extended later with actual progress bar display
        # NOTE: Future enhancement - use description for progress bar display
        _ = description  # Mark as intentionally unused for now
        return items

    def flext_cli_sanitize_filename(
        self,
        filename: str,
    ) -> FlextResult[str]:
        """Sanitize filename removing invalid characters.

        Zero-boilerplate filename sanitization that removes invalid characters
        for cross-platform compatibility and handles edge cases.

        Args:
            filename: Original filename to sanitize

        Returns:
            FlextResult containing sanitized filename

        Examples:
            >>> helper = FlextCliHelper()
            >>> result = helper.flext_cli_sanitize_filename("file<>*.txt").unwrap()
            >>> # Returns filename without <>* characters

        """
        try:
            # Validate input
            if not filename or not filename.strip():
                return FlextResult.fail("Filename cannot be empty")

            # Define invalid characters for cross-platform compatibility
            invalid_chars = '<>:"/\\|?*'

            # Remove invalid characters
            sanitized = filename
            for char in invalid_chars:
                sanitized = sanitized.replace(char, "")

            # Remove leading dots to avoid hidden files issues
            sanitized = sanitized.lstrip(".")

            # Ensure result is not empty after sanitization
            if not sanitized or not sanitized.strip():
                return FlextResult.fail("Filename becomes empty after sanitization")

            return FlextResult.ok(sanitized)

        except Exception as e:
            return FlextResult.fail(f"Filename sanitization failed: {e}")

    def flext_cli_print_status(
        self,
        message: str,
        *,
        status: str = "info",
    ) -> None:
        """Print status message with Rich console styling.

        Zero-boilerplate status printing with Rich console integration
        and automatic color coding based on status type.

        Args:
            message: Status message to display
            status: Status type for styling ("info", "success", "warning", "error")

        Examples:
            >>> helper = FlextCliHelper()
            >>> helper.flext_cli_print_status("Operation completed", status="success")
            >>> helper.flext_cli_print_status("Warning: Check config", status="warning")

        """
        try:
            # Define status styles with Rich markup
            status_styles = {
                "info": "[blue]ⓘ[/blue]",
                "success": "[green]✅[/green]",
                "warning": "[yellow]⚠️[/yellow]",
                "error": "[red]❌[/red]",
            }

            # Get style for status (default to info)
            status_icon = status_styles.get(status, status_styles["info"])

            # Print formatted message
            self.console.print(f"{status_icon} {message}")

        except Exception:
            # Fallback to simple console print if Rich fails
            self.console.print(f"[{status.upper()}] {message}")

    def format_size(self, size_bytes: int) -> str:
        """Format byte size into human-readable format.

        Zero-boilerplate file size formatting that converts bytes to
        appropriate units (B, KB, MB, GB) with consistent decimal precision.

        Args:
            size_bytes: Size in bytes to format

        Returns:
            Human-readable size string with unit

        Examples:
            >>> helper = FlextCliHelper()
            >>> helper.format_size(1024)
            '1.0 KB'
            >>> helper.format_size(1024 * 1024)
            '1.0 MB'

        """
        if size_bytes == 0:
            return "0.0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(size_bytes)
        unit_index = 0

        # Standard binary size conversion
        bytes_per_unit = 1024.0

        while size >= bytes_per_unit and unit_index < len(units) - 1:
            size /= bytes_per_unit
            unit_index += 1

        return f"{size:.1f} {units[unit_index]}"

    def truncate_text(self, text: str, *, max_length: int) -> str:
        """Truncate text to maximum length with ellipsis.

        Zero-boilerplate text truncation that adds ellipsis when text
        exceeds maximum length, handling edge cases gracefully.

        Args:
            text: Text to truncate
            max_length: Maximum length including ellipsis

        Returns:
            Truncated text with ellipsis if needed

        Examples:
            >>> helper = FlextCliHelper()
            >>> helper.truncate_text("Long text here", max_length=10)
            'Long te...'
            >>> helper.truncate_text("Short", max_length=10)
            'Short'

        """
        if len(text) <= max_length:
            return text

        # Minimum length for meaningful truncation with ellipsis
        min_ellipsis_length = 3

        if max_length <= min_ellipsis_length:
            return text[:max_length]

        return text[: max_length - min_ellipsis_length] + "..."

    def print_info(self, message: str) -> None:
        """Print info message with Rich console styling.

        Zero-boilerplate info message printing with consistent styling
        using Rich markup and blue color scheme.

        Args:
            message: Info message to display

        Examples:
            >>> helper = FlextCliHelper()
            >>> helper.print_info("Process completed successfully")

        """
        try:
            self.console.print(f"[bold blue]i[/bold blue] {message}")
        except Exception:
            # Fallback to simple console print if Rich fails
            self.console.print(f"[INFO] {message}")

    # Simple validation methods (boolean return) - for backward compatibility
    def validate_email(self, email: str | None) -> bool:
        """Validate email format - simple boolean return."""
        if not email:
            return False
        try:
            result = self.flext_cli_validate_input(email, FlextCliValidationType.EMAIL)
            return result.success
        except Exception:
            return False

    def validate_url(self, url: str | None) -> bool:
        """Validate URL format - simple boolean return."""
        if not url:
            return False
        try:
            result = self.flext_cli_validate_input(url, FlextCliValidationType.URL)
            return result.success
        except Exception:
            return False

    def validate_path(self, path: str | None, *, must_exist: bool = False) -> bool:
        """Validate path format - simple boolean return."""
        if not path:
            return False
        try:
            if must_exist:
                result = self.flext_cli_validate_input(
                    path, FlextCliValidationType.FILE
                )
                if not result.success:
                    # Try as directory too
                    result = self.flext_cli_validate_input(
                        path, FlextCliValidationType.DIR
                    )
                return result.success
            # Just validate path format
            result = self.flext_cli_validate_input(path, FlextCliValidationType.PATH)
            return result.success
        except Exception:
            return False

    # =============================================================================
    # VALIDATION STRATEGIES - Extracted for complexity reduction
    # =============================================================================

    def _validate_email(self, value: str) -> FlextResult[bool]:
        """Validate email format using regex - Single Responsibility Pattern."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            return FlextResult.fail(f"Invalid email format: {value}")
        return FlextResult.ok(True)

    def _validate_url(self, value: str) -> FlextResult[bool]:
        """Validate URL format using urlparse - Single Responsibility Pattern."""
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return FlextResult.fail(f"Invalid URL format: {value}")
            return FlextResult.ok(True)
        except Exception:
            return FlextResult.fail(f"Invalid URL format: {value}")

    def _validate_path(self, value: str) -> FlextResult[bool]:
        """Validate path format - Single Responsibility Pattern."""
        try:
            Path(value)
            return FlextResult.ok(True)
        except (ValueError, TypeError):
            return FlextResult.fail(f"Invalid path format: {value}")

    def _validate_file(self, value: str) -> FlextResult[bool]:
        """Validate file existence and type - Single Responsibility Pattern."""
        path = Path(value)
        if not path.exists():
            return FlextResult.fail(f"File does not exist: {value}")
        if not path.is_file():
            return FlextResult.fail(f"Path is not a file: {value}")
        return FlextResult.ok(True)

    def _validate_directory(self, value: str) -> FlextResult[bool]:
        """Validate directory existence and type - Single Responsibility Pattern."""
        path = Path(value)
        if not path.exists():
            return FlextResult.fail(f"Directory does not exist: {value}")
        if not path.is_dir():
            return FlextResult.fail(f"Path is not a directory: {value}")
        return FlextResult.ok(True)

    def _validate_uuid(self, value: str) -> FlextResult[bool]:
        """Validate UUID format - Single Responsibility Pattern."""
        try:
            uuid.UUID(value)
            return FlextResult.ok(True)
        except ValueError:
            return FlextResult.fail(f"Invalid UUID format: {value}")

    def _validate_port(self, value: str) -> FlextResult[bool]:
        """Validate port number range - Single Responsibility Pattern."""
        try:
            port = int(value)
            if not (MIN_PORT_NUMBER <= port <= MAX_PORT_NUMBER):
                return FlextResult.fail(f"Invalid port number (1-65535): {value}")
            return FlextResult.ok(True)
        except ValueError:
            return FlextResult.fail(f"Invalid port number: {value}")


# =============================================================================
# Zero-Boilerplate Utility Functions
# =============================================================================
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


def flext_cli_validate_url(url: str) -> FlextResult[bool]:
    """Validate URL with zero boilerplate.

    Args:
        url: URL to validate

    Returns:
        FlextResult containing validation result

    Examples:
        >>> is_valid = flext_cli_validate_url("https://example.com").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_validate_input(url, FlextCliValidationType.URL)


def flext_cli_validate_path(path: str) -> FlextResult[bool]:
    """Validate path with zero boilerplate.

    Args:
        path: Path to validate

    Returns:
        FlextResult containing validation result

    Examples:
        >>> is_valid = flext_cli_validate_path("/tmp/file.txt").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_validate_input(path, FlextCliValidationType.PATH)


def flext_cli_validate_file(path: str) -> FlextResult[bool]:
    """Validate file existence with zero boilerplate.

    Args:
        path: File path to validate

    Returns:
        FlextResult containing validation result

    Examples:
        >>> is_valid = flext_cli_validate_file("/tmp/existing_file.txt").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_validate_input(path, FlextCliValidationType.FILE)


def flext_cli_validate_dir(path: str) -> FlextResult[bool]:
    """Validate directory existence with zero boilerplate.

    Args:
        path: Directory path to validate

    Returns:
        FlextResult containing validation result

    Examples:
        >>> is_valid = flext_cli_validate_dir("/tmp").unwrap()

    """
    helper = FlextCliHelper()
    return helper.flext_cli_validate_input(path, FlextCliValidationType.DIR)


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


def flext_cli_batch_validate(
    inputs: dict[str, tuple[str, str]],
) -> FlextResult[dict[str, str]]:
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
            result = helper.flext_cli_validate_input(
                value, FlextCliValidationType.EMAIL
            )
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
        elif validation_type == "int":
            # Handle integer validation
            try:
                int(value)
                result = FlextResult.ok(True)
            except ValueError:
                result = FlextResult.fail(f"Invalid integer: {value}")
        else:
            return FlextResult.fail(f"Unknown validation type: {validation_type}")

        if not result.success:
            return FlextResult.fail(
                f"Validation failed for {field_name}: {result.error}"
            )

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
def flext_cli_create_helper(
    console: Console | None = None, *, quiet: bool = False
) -> FlextCliHelper:
    """Create FlextCliHelper with optional configuration.

    Args:
        console: Optional Rich console instance
        quiet: If True, enables quiet mode for prompts

    Returns:
        Configured FlextCliHelper instance

    Examples:
        >>> helper = flext_cli_create_helper()
        >>> result = helper.flext_cli_load_file("data.json")

    """
    return FlextCliHelper(console=console, quiet=quiet)


def flext_cli_create_data_processor(
    helper: FlextCliHelper | None = None,
) -> FlextCliDataProcessor:
    """Create FlextCliDataProcessor instance.

    Args:
        helper: Optional FlextCliHelper instance

    Returns:
        Configured FlextCliDataProcessor instance

    Examples:
        >>> processor = flext_cli_create_data_processor()
        >>> result = processor.process({"key": "value"})

    """
    return FlextCliDataProcessor(helper=helper)


def flext_cli_create_file_manager(
    helper: FlextCliHelper | None = None,
) -> FlextCliFileManager:
    """Create FlextCliFileManager instance.

    Args:
        helper: Optional FlextCliHelper instance

    Returns:
        Configured FlextCliFileManager instance

    Examples:
        >>> manager = flext_cli_create_file_manager()
        >>> result = manager.load_file("data.json")

    """
    return FlextCliFileManager(helper=helper)


# =============================================================================
# CONCRETE IMPLEMENTATIONS - Pattern completion
# =============================================================================


class FlextCliDataProcessor:
    """Concrete data processor implementation."""

    def __init__(self, helper: FlextCliHelper | None = None) -> None:
        """Initialize data processor."""
        self.helper = helper or FlextCliHelper()

    def process(self, data: dict[str, object]) -> FlextResult[dict[str, object]]:
        """Process data with validation and transformation."""
        try:
            # Basic validation and processing
            processed_data: dict[str, object] = {}
            for key, value in data.items():
                if isinstance(value, str) and value.strip():
                    processed_data[f"processed_{key}"] = value.strip()
                elif isinstance(value, (int, float, bool)):
                    processed_data[f"processed_{key}"] = value
                else:
                    processed_data[f"processed_{key}"] = (
                        str(value) if value is not None else ""
                    )

            return FlextResult.ok(processed_data)

        except Exception as e:
            return FlextResult.fail(f"Data processing failed: {e}")

    def validate(self, data: dict[str, object]) -> FlextResult[bool]:
        """Validate data structure."""
        try:
            if not data:
                return FlextResult.fail("Data cannot be empty")

            return FlextResult.ok(True)

        except Exception as e:
            return FlextResult.fail(f"Data validation failed: {e}")

    def flext_cli_process_workflow(
        self,
        data: dict[str, object],
        workflow_steps: list[tuple[str, object]],
        *,
        show_progress: bool = True,
    ) -> FlextResult[dict[str, object]]:
        """Process data through workflow steps."""
        try:
            current_data = data

            # Use show_progress parameter for future progress display
            _ = show_progress  # Mark as intentionally unused for now

            for step_name, step_func in workflow_steps:
                try:
                    # Call step function and handle both FlextResult and direct returns
                    step_result = step_func(current_data)
                    if hasattr(step_result, "success"):  # It's a FlextResult
                        if not step_result.success:
                            return FlextResult.fail(
                                f"Step '{step_name}' failed: {step_result.error}"
                            )
                        current_data = step_result.data
                    else:  # Direct return value
                        current_data = step_result

                except Exception as e:
                    return FlextResult.fail(f"Step '{step_name}' raised exception: {e}")

            return FlextResult.ok(current_data)

        except Exception as e:
            return FlextResult.fail(f"Workflow processing failed: {e}")

    def flext_cli_validate_and_transform(
        self,
        data: dict[str, object],
        validators: dict[str, str],
        transformers: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Validate and transform data."""
        try:
            # First validate the data using Strategy Pattern
            validation_result = self._validate_fields(data, validators)
            if not validation_result.success:
                return FlextResult.fail(validation_result.error or "Validation failed")

            # Apply transformers and handle validated fields
            result_data = dict(data)

            # Apply automatic transformations and custom transformers
            transform_result = self._apply_transformations(
                result_data, validators, transformers
            )
            if not transform_result.success:
                return FlextResult.fail(
                    transform_result.error or "Transformation failed"
                )

            return FlextResult.ok(transform_result.data or {})

        except Exception as e:
            return FlextResult.fail(f"Validation and transformation failed: {e}")

    def _validate_fields(
        self, data: dict[str, object], validators: dict[str, str]
    ) -> FlextResult[None]:
        """Validate fields using Strategy Pattern - Single Responsibility."""
        helper = FlextCliHelper()

        for field, validation_type in validators.items():
            if field not in data:
                return FlextResult.fail(f"Required field '{field}' missing")

            value = str(data[field])
            validation_result = self._get_validation_result(
                helper, value, validation_type
            )

            if validation_result and not validation_result.success:
                return FlextResult.fail(
                    f"Validation failed for '{field}': {validation_result.error}"
                )

        return FlextResult.ok(None)

    def _get_validation_result(
        self, helper: FlextCliHelper, value: str, validation_type: str
    ) -> FlextResult[bool] | None:
        """Get validation result for specific type - Strategy Pattern."""
        validation_map = {
            "email": FlextCliValidationType.EMAIL,
            "url": FlextCliValidationType.URL,
            "file": FlextCliValidationType.FILE,
        }

        validation_enum = validation_map.get(validation_type)
        if validation_enum:
            return helper.flext_cli_validate_input(value, validation_enum)
        return None  # Skip unknown validation types

    def _apply_transformations(
        self,
        result_data: dict[str, object],
        validators: dict[str, str],
        transformers: dict[str, object] | None,
    ) -> FlextResult[dict[str, object]]:
        """Apply automatic and custom transformations - Single Responsibility."""
        # First apply automatic transformations based on validation types
        for field, validation_type in validators.items():
            if (
                field in result_data
                and validation_type == "file"
                and (not transformers or field not in transformers)
            ):
                # Convert validated files to Path objects unless there's a specific transformer
                result_data[field] = Path(str(result_data[field]))

        # Then apply custom transformers if provided
        if transformers:
            for field, transformer in transformers.items():
                if field in result_data:
                    try:
                        result_data[field] = transformer(result_data[field])
                    except Exception as e:
                        return FlextResult.fail(
                            f"Transformation failed for '{field}': {e}"
                        )

        return FlextResult.ok(result_data)

    def flext_cli_aggregate_data(
        self,
        data_sources: dict[str, object],
        *,
        fail_fast: bool = True,
    ) -> FlextResult[dict[str, object]]:
        """Aggregate data from multiple sources with fail-fast option."""
        try:
            aggregated_data: dict[str, object] = {}
            errors: list[str] = []

            for source_name, source_func in data_sources.items():
                source_result = self._process_data_source(
                    source_name, source_func, fail_fast=fail_fast
                )

                if source_result is None:
                    # Early return due to fail_fast
                    continue

                if source_result.success:
                    aggregated_data[source_name] = source_result.data
                else:
                    errors.append(f"{source_name}: {source_result.error}")
                    if fail_fast:
                        return FlextResult.fail(
                            f"Source {source_name} failed: {source_result.error}"
                        )

            if errors and not aggregated_data:
                return FlextResult.fail(f"All sources failed: {'; '.join(errors)}")

            if errors:
                aggregated_data["_errors"] = errors

            return FlextResult.ok(aggregated_data)

        except Exception as e:
            return FlextResult.fail(f"Data aggregation failed: {e}")

    def _process_data_source(
        self,
        source_name: str,
        source_func: object,
        *,
        fail_fast: bool,
    ) -> FlextResult[object] | None:
        """Process single data source - extracted for complexity reduction."""
        try:
            if callable(source_func):
                result = source_func()
                if hasattr(result, "success"):
                    return result
                # Direct data return
                return FlextResult.ok(result)
            # Direct data (not callable)
            return FlextResult.ok(source_func)
        except Exception as e:
            error_result: FlextResult[object] = FlextResult.fail(
                f"Source {source_name} exception: {e!s}"
            )
            if fail_fast:
                return error_result
            return FlextResult.fail(f"{e!s}")

    def flext_cli_transform_data_pipeline(
        self,
        data: dict[str, object] | list[dict[str, object]],
        transformers: list[tuple[str, object]],
    ) -> FlextResult[dict[str, object] | list[dict[str, object]]]:
        """Transform data through pipeline of transformers."""
        try:
            current_data = data

            for transformer_name, transformer_func in transformers:
                try:
                    # Apply transformer
                    transform_result = transformer_func(current_data)

                    # Handle both FlextResult and direct returns
                    if hasattr(transform_result, "success"):
                        if not transform_result.success:
                            return FlextResult.fail(
                                f"Transformer '{transformer_name}' failed: {transform_result.error}"
                            )
                        current_data = transform_result.data
                    else:
                        current_data = transform_result

                except Exception as e:
                    return FlextResult.fail(
                        f"Transformer '{transformer_name}' raised exception: {e}"
                    )

            return FlextResult.ok(current_data)

        except Exception as e:
            return FlextResult.fail(f"Data transformation pipeline failed: {e}")


class FlextCliFileManager:
    """Concrete file manager implementation."""

    def __init__(self, helper: FlextCliHelper | None = None) -> None:
        """Initialize file manager."""
        self.helper = helper or FlextCliHelper()

    def load_file(self, path: str | Path) -> FlextResult[dict[str, object]]:
        """Load file and return parsed data."""
        return self.helper.flext_cli_load_file(path)

    def save_file(self, data: dict[str, object], path: str | Path) -> FlextResult[None]:
        """Save data to file."""
        return self.helper.flext_cli_save_file(data, path)

    def exists(self, path: str | Path) -> bool:
        """Check if file exists."""
        return Path(path).exists()

    def create_directory(self, path: str | Path) -> FlextResult[None]:
        """Create directory if it doesn't exist."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to create directory {path}: {e}")

    def flext_cli_safe_write(
        self,
        content: str,
        path: str | Path,
        *,
        backup: bool = False,
        create_dirs: bool = False,
    ) -> FlextResult[str]:
        """Safely write content to file with backup and directory creation options."""
        try:
            file_path = Path(path)

            # Create directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                backup_path.write_text(
                    file_path.read_text(encoding="utf-8"), encoding="utf-8"
                )

            # Write new content
            file_path.write_text(content, encoding="utf-8")
            return FlextResult.ok(str(file_path))

        except Exception as e:
            return FlextResult.fail(f"Safe write failed for {path}: {e}")

    def flext_cli_backup_and_process(
        self,
        file_path: str | Path,
        processor_func: object,
        *,
        require_confirmation: bool = False,
    ) -> FlextResult[dict[str, str]]:
        """Backup file and process it with recovery on failure."""
        try:
            path = Path(file_path)

            if not path.exists():
                return FlextResult.fail(f"File does not exist: {file_path}")

            # Read original content
            original_content = path.read_text(encoding="utf-8")

            # Ask for confirmation if required
            if require_confirmation:
                confirm_result = self.helper.flext_cli_confirm(
                    f"Process file {path.name}? This will create a backup.",
                )
                if not confirm_result.success or not confirm_result.unwrap():
                    return FlextResult.fail("Operation cancelled by user")

            # Create backup
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = path.with_name(f"{path.stem}_{timestamp}_backup{path.suffix}")
            backup_path.write_text(original_content, encoding="utf-8")

            try:
                # Process content
                result = processor_func(original_content)
                if (
                    hasattr(result, "success") and not result.success
                ):  # FlextResult failed
                    # Restore from backup
                    path.write_text(original_content, encoding="utf-8")
                    return FlextResult.fail(
                        f"Processing failed, file restored: {result.error}"
                    )

                # Get processed content
                processed_content = result.data if hasattr(result, "data") else result

                # Write processed content
                path.write_text(str(processed_content), encoding="utf-8")

                return FlextResult.ok(
                    {
                        "status": "completed",
                        "original_file": str(path),
                        "backup_file": str(backup_path),
                        "processed": "true",
                    }
                )

            except Exception as e:
                # Restore from backup on any exception
                path.write_text(original_content, encoding="utf-8")
                return FlextResult.fail(f"Processing failed, file restored: {e}")

        except Exception as e:
            return FlextResult.fail(f"Backup and process failed: {e}")


# Legacy alias for backward compatibility
CLIHelper = FlextCliHelper
