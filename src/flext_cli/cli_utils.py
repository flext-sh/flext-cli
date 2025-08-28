"""FLEXT CLI Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import contextlib
import csv
import datetime
import getpass
import importlib
import io
import json
import shlex
from collections.abc import Callable
from pathlib import Path
from typing import Literal, Protocol, TypedDict, TypeVar
from uuid import UUID

import yaml
from flext_core import FlextLogger, FlextResult, FlextUtilities
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.style import Style
from rich.table import Table

from flext_cli.typings import FlextCliOutputFormat

T = TypeVar("T")
# Type aliases for utility functions
FlextCliData = dict[str, object] | list[object] | str | float | int | None


class ProcessingResults(TypedDict):
    """Type definition for file processing results."""

    processed: int
    failed: int
    errors: list[dict[str, str]]
    successful: list[str]


class SetupResults(TypedDict, total=False):
    """Type definition for project setup results."""

    project_path: str
    config_file: str
    git_init: bool
    dir_src: str
    dir_tests: str
    dir_docs: str
    dir_scripts: str
    dir_config: str


class CommandResult(TypedDict):
    """Type definition for command execution results."""

    command: list[str]
    returncode: int
    stdout: str | None
    stderr: str | None
    success: bool


class ConsoleLike(Protocol):
    """Protocol for console-like objects that can print."""

    def print(
        self,
        *objects: object,
        sep: str = " ",
        end: str = "\n",
        style: Style | str | None = None,
        justify: Literal["default", "left", "center", "right", "full"] | None = None,
        overflow: Literal["fold", "crop", "ellipsis", "ignore"] | None = None,
        no_wrap: bool | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
    ) -> None:
        """Print method for console output compatible with Rich Console."""
        ...


# =============================================================================
# WORKFLOW UTILITIES - Complete operations in single function calls
# =============================================================================


def _write_basic_pyproject(project_name: str, project_path: Path) -> Path:
    """Write a minimal pyproject.toml and return its path."""
    config_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "FLEXT CLI Project"
requires-python = ">=3.13"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "FLEXT CLI Project"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.13"
flext-cli = "*"

[tool.poetry.group.dev.dependencies]
pytest = "*"
mypy = "*"
ruff = "*"
"""
    config_path = project_path / "pyproject.toml"
    config_path.write_text(config_content, encoding="utf-8")
    return config_path


def _init_git_repo(project_path: Path) -> bool:
    """Initialize a git repository in-process using GitPython if available.

    Falls back to returning False with guidance instead of spawning subprocess.
    """
    try:
        git_mod = importlib.import_module("git")
        repo_cls = getattr(git_mod, "Repo", None)
        if repo_cls is None:
            return False
        repo_cls.init(str(project_path))
        return True
    except Exception:
        return False


def _create_directory_structure(base: Path, dir_names: list[str]) -> dict[str, str]:
    """Create directories under base and return a map for results."""
    created: dict[str, str] = {}
    for dir_name in dir_names:
        dir_path = base / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        created[f"dir_{dir_name}"] = str(dir_path)
    return created


def _record_success(results: ProcessingResults, path: Path) -> None:
    """Record successful file processing."""
    results["processed"] += 1
    results["successful"].append(str(path))


def _record_failure(
    results: ProcessingResults,
    path: Path,
    error_msg: str,
) -> None:
    """Record failed file processing."""
    results["failed"] += 1
    results["errors"].append({"file": str(path), "error": error_msg})


def _process_single_file(
    path: Path,
    processor: Callable[[Path], FlextResult[object]],
    results: ProcessingResults,
    *,
    fail_fast: bool,
) -> tuple[bool, str | None]:
    """Process a single file and update results.

    Returns a tuple (should_stop, stop_message) when fail_fast is enabled and a
    failure occurs; otherwise (False, None).
    """
    try:
        result = processor(path)
        if result.is_success:
            _record_success(results, path)
            return False, None
        _record_failure(results, path, result.error or "Unknown error")
        if fail_fast:
            return True, f"Processing failed for {path}: {result.error}"
        return False, None
    except Exception as e:
        _record_failure(results, path, str(e))
        if fail_fast:
            return True, f"Processing failed for {path}: {e}"
        return False, None


def cli_quick_setup(  # noqa: PLR0912
    project_name: str,
    *,
    create_dirs: bool = True,
    create_config: bool = True,
    init_git: bool = False,
) -> FlextResult[SetupResults]:
    """Create complete project setup in one function call.

    Eliminates 50+ lines of setup code by providing intelligent automation.

    Args:
      project_name: Name of the project to create
      create_dirs: Create standard directory structure
      create_config: Create basic configuration files
      init_git: Initialize git repository

    Returns:
      Result with setup information or error

    """
    console = Console()
    results: SetupResults = {}

    try:
        # Validate project name
        if not project_name or not project_name.strip():
            return FlextResult[SetupResults].fail("Project name cannot be empty")

        project_path = Path(project_name).resolve()

        if project_path.exists():
            confirmation = cli_confirm(
                f"Directory {project_path} exists. Continue?",
                default=False,
            )
            if not (confirmation.value if confirmation.is_success else False):
                return FlextResult[SetupResults].fail("Setup cancelled")

        # Create directory structure
        if create_dirs:
            dirs = ["src", "tests", "docs", "scripts", "config"]
            console.print("[blue]Creating directory structure...[/blue]")
            dir_results = _create_directory_structure(project_path, dirs)
            # Manually add directory results to SetupResults
            for key, value in dir_results.items():
                if key == "dir_src":
                    results["dir_src"] = value
                elif key == "dir_tests":
                    results["dir_tests"] = value
                elif key == "dir_docs":
                    results["dir_docs"] = value
                elif key == "dir_scripts":
                    results["dir_scripts"] = value
                elif key == "dir_config":
                    results["dir_config"] = value
            console.print("[green]✓ Directory structure created[/green]")

        # Create basic configuration
        if create_config:
            console.print("[blue]Creating configuration files...[/blue]")
            config_path = _write_basic_pyproject(project_name, project_path)
            results["config_file"] = str(config_path)

            console.print("[green]✓ Configuration files created[/green]")

        # Initialize git repository
        if init_git:
            console.print("[blue]Initializing git repository...[/blue]")
            if _init_git_repo(project_path):
                git_success = True
                results["git_init"] = git_success
                console.print("[green]✓ Git repository initialized[/green]")
            else:
                console.print("[yellow]⚠ Git init failed[/yellow]")
                git_failure = False
                results["git_init"] = git_failure

        results["project_path"] = str(project_path)
        console.print(f"[green]🎉 Project '{project_name}' setup complete![/green]")

        return FlextResult[SetupResults].ok(results)

    except (OSError, PermissionError) as e:
        return FlextResult[SetupResults].fail(f"Setup failed: {e}")
    except Exception as e:
        return FlextResult[SetupResults].fail(f"Unexpected error during setup: {e}")


def cli_batch_process_files(
    file_paths: list[Path | str],
    processor: Callable[[Path], FlextResult[object]],
    *,
    show_progress: bool = True,
    fail_fast: bool = False,
) -> FlextResult[ProcessingResults]:
    """Process multiple files with progress tracking and error handling.

    Args:
      file_paths: List of file paths to process
      processor: Function to process each file
      show_progress: Show progress bar during processing
      fail_fast: Stop on first error

    Returns:
      Result with processing statistics

    """
    console = Console()
    results: ProcessingResults = {
        "processed": 0,
        "failed": 0,
        "errors": [],
        "successful": [],
    }

    if not file_paths:
        return FlextResult[ProcessingResults].ok(results)

    # Convert string paths to Path objects
    paths = [Path(p) for p in file_paths]

    progress: Progress | None = None
    task_id: TaskID | None = None

    try:
        if show_progress:
            progress = Progress()
            progress.start()
            task_id = progress.add_task("Processing files...", total=len(paths))

        for path in paths:
            should_stop, stop_message = _process_single_file(
                path,
                processor,
                results,
                fail_fast=fail_fast,
            )
            if progress and task_id is not None:
                progress.update(task_id, advance=1)
            if should_stop:
                msg = stop_message or "Processing failed"
                return FlextResult[ProcessingResults].fail(msg)

        # Show summary
        if show_progress:
            processed_count = results["processed"]
            failed_count = results["failed"]
            console.print(f"[green]✓ Processed {processed_count} files[/green]")
            if failed_count > 0:
                console.print(f"[yellow]⚠ {failed_count} files failed[/yellow]")

        return FlextResult[ProcessingResults].ok(results)

    finally:
        if progress:
            progress.stop()


# =============================================================================
# DATA UTILITIES - JSON, CSV, YAML processing with validation
# =============================================================================


def cli_load_data_file(
    file_path: Path | str,
    *,
    validate_format: bool = True,
) -> FlextResult[object]:
    """Load data from various file formats with automatic format detection.

    Args:
      file_path: Path to the data file
      validate_format: Validate file format before loading

    Returns:
      Result with loaded data or error

    """
    try:
        path = Path(file_path)

        if not path.exists():
            return FlextResult[object].fail(f"File does not exist: {path}")

        # Detect format from extension
        suffix = path.suffix.lower()
        result: FlextResult[object]
        if suffix == ".json":
            result = _load_json_file(path)
        elif suffix in {".yaml", ".yml"}:
            result = _load_yaml_file(path)
        elif suffix == ".csv":
            # Cast list[dict] to object
            result = _load_csv_file(path).map(lambda data: data)
        elif suffix == ".txt":
            result = _load_text_file(path).map(lambda data: data)
        else:
            if validate_format:
                return FlextResult[object].fail(f"Unsupported file format: {suffix}")
            result = _load_text_file(path).map(lambda data: data)

        return result

    except Exception as e:
        return FlextResult[object].fail(f"Failed to load data file: {e}")


def _load_json_file(path: Path) -> FlextResult[object]:
    """Load JSON file with error handling using FlextUtilities."""
    try:
        content = path.read_text(encoding="utf-8")
        # Use json.loads directly to handle different return types
        try:
            data = json.loads(content)
            return FlextResult[object].ok(data)
        except json.JSONDecodeError:
            return FlextResult[object].fail(f"Invalid JSON in {path}")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[object].fail(f"Failed to read JSON file {path}: {e}")


def _load_yaml_file(path: Path) -> FlextResult[object]:
    """Load YAML file with error handling."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return FlextResult[object].ok(data)
    except yaml.YAMLError as e:
        return FlextResult[object].fail(f"Invalid YAML in {path}: {e}")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[object].fail(f"Failed to read YAML file {path}: {e}")


def _load_csv_file(path: Path) -> FlextResult[list[dict[str, str]]]:
    """Load CSV file with error handling."""
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return FlextResult[list[dict[str, str]]].ok(data)
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[list[dict[str, str]]].fail(
            f"Failed to read CSV file {path}: {e}"
        )


def _load_text_file(path: Path) -> FlextResult[str]:
    """Load text file with error handling."""
    try:
        content = path.read_text(encoding="utf-8")
        return FlextResult[str].ok(content)
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[str].fail(f"Failed to read text file {path}: {e}")


def cli_save_data_file(
    data: FlextCliData,
    file_path: Path | str,
    format_type: FlextCliOutputFormat | str | None = None,
    *,
    create_dirs: bool = True,
) -> FlextResult[None]:
    """Save data to various file formats with automatic format detection.

    Args:
      data: Data to save
      file_path: Path where to save the file
      format_type: Format to use (auto-detected if None)
      create_dirs: Create parent directories if needed

    Returns:
      Result indicating success or error

    """
    try:
        path = Path(file_path)

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format
        detected: FlextCliOutputFormat
        if format_type is None:
            suffix = path.suffix.lower()
            detected = (
                FlextCliOutputFormat.JSON
                if suffix == ".json"
                else FlextCliOutputFormat.YAML
                if suffix in {".yaml", ".yml"}
                else FlextCliOutputFormat.CSV
                if suffix == ".csv"
                else FlextCliOutputFormat.PLAIN
            )
        else:
            detected = (
                FlextCliOutputFormat(format_type.lower())
                if isinstance(format_type, str)
                else format_type
            )

        # Save based on format
        if detected == FlextCliOutputFormat.JSON:
            return _save_json_file(data, path)
        if detected == FlextCliOutputFormat.YAML:
            return _save_yaml_file(data, path)
        if detected == FlextCliOutputFormat.CSV:
            return _save_csv_file(data, path)
        # TEXT
        return _save_text_file(data, path)

    except Exception as e:
        return FlextResult[None].fail(f"Failed to save data file: {e}")


def _save_json_file(data: FlextCliData, path: Path) -> FlextResult[None]:
    """Save data as JSON file using FlextUtilities."""
    try:
        json_content = FlextUtilities.safe_json_stringify(data)
        path.write_text(json_content, encoding="utf-8")
        return FlextResult[None].ok(None)
    except (OSError, TypeError) as e:
        return FlextResult[None].fail(f"Failed to write JSON file {path}: {e}")


def _convert_to_serializable(
    data: object,
) -> str | int | float | bool | None | list[object] | dict[str, object]:
    """Convert data to a YAML/JSON serializable format.

    Args:
      data: Data to convert

    Returns:
      Serializable representation of the data

    """
    # Import statements moved to top of file to fix PLC0415
    if data is None or isinstance(data, (str, int, float, bool)):
        return data

    # Handle datetime types
    if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
        return data.isoformat()

    # Handle Path and UUID types
    if isinstance(data, (Path, UUID)):
        return str(data)

    # Handle dict types with explicit typing
    if isinstance(data, dict):
        result_dict: dict[str, object] = {}
        # After isinstance check, data is already dict
        for key, value in data.items():
            key_str: str = str(key)
            value_converted = _convert_to_serializable(value)
            result_dict[key_str] = value_converted
        return result_dict

    # Handle sequence types (including sets)
    if isinstance(data, (list, tuple, set)):
        result_list: list[object] = []
        # Convert to list for uniform handling - no casts needed after isinstance
        sequence_items: list[object]
        if isinstance(data, list):
            sequence_items = data
        elif isinstance(data, tuple):
            sequence_items = list(data)
        else:  # set
            sequence_items = list(data)

        for item in sequence_items:
            converted_item = _convert_to_serializable(item)
            result_list.append(converted_item)
        return result_list

    # Handle objects with __dict__ or fallback to string
    return (
        _convert_to_serializable(data.__dict__)
        if hasattr(data, "__dict__")
        else str(data)
    )


def _save_yaml_file(data: FlextCliData, path: Path) -> FlextResult[None]:
    """Save data as YAML file."""
    try:
        with path.open("w", encoding="utf-8") as f:
            # First try safe_dump with the original data
            try:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            except (yaml.YAMLError, TypeError) as yaml_error:
                # If safe_dump fails due to non-serializable objects, convert to serializable
                try:
                    serializable_data = _convert_to_serializable(data)
                    f.seek(0)  # Reset file position
                    f.truncate()  # Clear any partial content
                    yaml.safe_dump(
                        serializable_data,
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                    )
                except Exception:
                    # Final error handling: convert to dict/string representation
                    f.seek(0)
                    f.truncate()
                    error_data = {
                        "data": str(data),
                        "error": f"Could not serialize: {yaml_error}",
                    }
                    yaml.safe_dump(
                        error_data,
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                    )
        return FlextResult[None].ok(None)
    except (OSError, yaml.YAMLError) as e:
        return FlextResult[None].fail(f"Failed to write YAML file {path}: {e}")


def _save_csv_file(data: FlextCliData, path: Path) -> FlextResult[None]:
    """Save data as CSV file."""
    try:
        if not isinstance(data, list) or not data:
            return FlextResult[None].fail("CSV data must be a non-empty list")

        if not isinstance(data[0], dict):
            return FlextResult[None].fail("CSV data must be a list of dictionaries")

        # Type the data as list of dicts with proper typing
        typed_data: list[dict[str, object]] = []
        # After isinstance check, data is confirmed as list
        for item in data:
            if isinstance(item, dict):
                # After isinstance check, item is confirmed as dict
                str_dict: dict[str, object] = {str(k): v for k, v in item.items()}
                typed_data.append(str_dict)

        if not typed_data:
            return FlextResult[None].fail("No valid dictionaries in data")

        with path.open("w", encoding="utf-8", newline="") as f:
            fieldnames = list(typed_data[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(typed_data)

        return FlextResult[None].ok(None)
    except (OSError, ValueError) as e:
        return FlextResult[None].fail(f"Failed to write CSV file {path}: {e}")


def _save_text_file(data: FlextCliData, path: Path) -> FlextResult[None]:
    """Save data as text file."""
    try:
        content = str(data)
        path.write_text(content, encoding="utf-8")
        return FlextResult[None].ok(None)
    except (OSError, UnicodeEncodeError) as e:
        return FlextResult[None].fail(f"Failed to write text file {path}: {e}")


# =============================================================================
# OUTPUT UTILITIES - Rich console output and formatting
# =============================================================================


def cli_create_table(
    data: FlextCliData,
    title: str | None = None,
    *,
    show_lines: bool = False,
    max_width: int | None = None,
) -> FlextResult[Table]:
    """Create a Rich table from data with intelligent formatting.

    Args:
      data: Data to display in table format
      title: Optional table title
      show_lines: Show lines between rows
      max_width: Maximum table width

    Returns:
      Result with Rich Table or error

    """
    try:
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
            show_lines=show_lines,
            width=max_width,
        )

        if isinstance(data, list):
            if not data:
                # Empty list creates valid empty table
                return FlextResult[Table].ok(table)

            first_item = data[0]
            if isinstance(first_item, dict):
                # List of dictionaries - create columns from first item
                # After isinstance check, first_item is confirmed as dict
                first_dict: dict[str, object] = {
                    str(k): v for k, v in first_item.items()
                }
                headers: list[str] = list(first_dict.keys())
                for header in headers:
                    formatted_header = str(header).replace("_", " ").title()
                    table.add_column(formatted_header)

                # After isinstance check, data is confirmed as list
                for item in data:
                    if isinstance(item, dict):
                        # After isinstance check, item is confirmed as dict
                        typed_item: dict[str, object] = {
                            str(k): v for k, v in item.items()
                        }
                        row_data = [str(typed_item.get(h, "")) for h in headers]
                        table.add_row(*row_data)
            else:
                # List of values - single column
                table.add_column("Value")
                # After isinstance check, data is confirmed as list
                for item in data:
                    table.add_row(str(item))

        elif isinstance(data, dict):
            # Dictionary - key-value pairs
            table.add_column("Key", style="cyan")
            table.add_column("Value")

            # After isinstance check, data is confirmed as dict
            for key, value in data.items():
                key_str = str(key)
                formatted_key = key_str.replace("_", " ").title()
                table.add_row(formatted_key, str(value))

        else:
            # Single value - simple table
            table.add_column("Value")
            table.add_row(str(data))

        return FlextResult[Table].ok(table)

    except Exception as e:
        return FlextResult[Table].fail(f"Failed to create table: {e}")


# Legacy functions removed - using FlextResult pattern consistently


def cli_format_output(  # noqa: PLR0912, PLR0915
    data: FlextCliData,
    format_type: FlextCliOutputFormat | str = FlextCliOutputFormat.TABLE,
    **options: object,
) -> FlextResult[str]:
    """Format data for CLI output in specified format.

    Args:
      data: Data to format
      format_type: Output format
      **options: Additional formatting options
      **options: Additional formatting options

    Returns:
      Result with formatted output string

    """
    try:
        error: str | None = None
        formatted: str | None = None

        # Convert string format types to FlextCliOutputFormat for backward compatibility
        if isinstance(format_type, str):
            format_map = {
                "json": FlextCliOutputFormat.JSON,
                "yaml": FlextCliOutputFormat.YAML,
                "csv": FlextCliOutputFormat.CSV,
                "table": FlextCliOutputFormat.TABLE,
                "plain": FlextCliOutputFormat.PLAIN,
            }
            if format_type.lower() in format_map:
                format_type = format_map[format_type.lower()]
            else:
                # Unknown format - return FlextResult error
                error = f"Unknown formatter type: {format_type}"
                return FlextResult[str].fail(error)

        if format_type == FlextCliOutputFormat.JSON:
            # Use FlextUtilities for consistent JSON formatting
            formatted = FlextUtilities.safe_json_stringify(data)
        elif format_type == FlextCliOutputFormat.YAML:
            output = io.StringIO()
            yaml.dump(data, output, default_flow_style=False, allow_unicode=True)
            formatted = output.getvalue()
        elif format_type == FlextCliOutputFormat.CSV:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                output = io.StringIO()
                first_item = data[0]
                if isinstance(first_item, dict):
                    # After isinstance check, first_item is confirmed as dict
                    # Convert dict keys to strings for CSV headers
                    fieldnames: list[str] = [str(k) for k in first_item]
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()

                    # Convert all dict items for writing
                    csv_data: list[dict[str, object]] = []
                    # After isinstance check, data is confirmed as list
                    for item in data:
                        if isinstance(item, dict):
                            # After isinstance check, item is confirmed as dict
                            str_dict: dict[str, object] = {
                                str(k): v for k, v in item.items()
                            }
                            csv_data.append(str_dict)
                    writer.writerows(csv_data)
                formatted = output.getvalue()
            else:
                error = "CSV format requires list of dictionaries"
        elif format_type == FlextCliOutputFormat.TABLE:
            # Extract title from options for cli_create_table
            title = str(options.get("title")) if options.get("title") else None
            show_lines_option = bool(options.get("show_lines"))
            max_width = None
            max_width_raw = options.get("max_width")
            if max_width_raw is not None:
                try:
                    # Convert to string first to handle various input types safely
                    max_width_str = str(max_width_raw)
                    if max_width_str.isdigit():
                        max_width = int(max_width_str)
                except (ValueError, TypeError):
                    max_width = None
            table_result = cli_create_table(
                data,
                title=title,
                show_lines=show_lines_option,
                max_width=max_width,
            )
            if table_result.is_success:
                output = io.StringIO()
                console = Console(file=output, width=80)
                console.print(table_result.value)
                formatted = output.getvalue()
            else:
                error = table_result.error or "Table creation failed"
        else:
            formatted = str(data)

        # Handle default formatting for plain text or None cases
        if formatted is None and error is None:
            formatted = str(data)

        if error is not None:
            return FlextResult[str].fail(error)

        result = formatted or ""

        # Return formatted result

        return FlextResult[str].ok(result)

    except Exception as e:
        return FlextResult[str].fail(f"Failed to format output: {e}")


# =============================================================================
# SYSTEM UTILITIES - Command execution and process management
# =============================================================================


def cli_run_command(
    command: str | list[str],
    *,
    cwd: Path | str | None = None,
    timeout: int = 30,
    capture_output: bool = True,
    check: bool = False,
) -> FlextResult[CommandResult]:
    """Run system command with comprehensive error handling.

    Args:
      command: Command to run (string or list)
      cwd: Working directory
      timeout: Command timeout in seconds
      capture_output: Capture stdout/stderr
      check: Raise exception on non-zero exit code

    Returns:
      Result with command execution information

    """
    error_message: str | None = None
    result_payload: CommandResult | None = None
    try:
        cmd_list = shlex.split(command) if isinstance(command, str) else command
        if not cmd_list:
            error_message = "Empty command"
        else:
            logger = FlextLogger(__name__)
            logger.debug(f"Running command: {cmd_list}")

            async def _run() -> CommandResult:
                proc = await asyncio.create_subprocess_exec(
                    *cmd_list,
                    cwd=str(cwd) if isinstance(cwd, Path) else (cwd or None),
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                )
                try:
                    stdout_b, stderr_b = await asyncio.wait_for(
                        proc.communicate(),
                        timeout=timeout,
                    )
                except TimeoutError:
                    with contextlib.suppress(ProcessLookupError):
                        proc.kill()
                    await proc.wait()
                    # Propagate a standard timeout error (no subprocess exceptions)
                    message = f"Command timed out after {timeout}s"
                    raise TimeoutError(message) from None
                stdout_s = (
                    stdout_b.decode("utf-8", errors="replace") if stdout_b else None
                )
                stderr_s = (
                    stderr_b.decode("utf-8", errors="replace") if stderr_b else None
                )
                result: CommandResult = {
                    "command": cmd_list,
                    "returncode": int(proc.returncode or 0),
                    "stdout": stdout_s,
                    "stderr": stderr_s,
                    "success": (proc.returncode or 0) == 0,
                }
                return result

            result_dict = asyncio.run(_run())
            if (
                check
                and isinstance(result_dict.get("returncode"), int)
                and result_dict["returncode"] != 0
            ):
                error_message = f"Command failed with exit code {result_dict['returncode']}: {' '.join(cmd_list)}"
            else:
                result_payload = result_dict
    except TimeoutError as e:
        error_message = str(e) or f"Command timed out after {timeout}s"
    except Exception as e:
        error_message = f"Command execution failed: {e}"

    if error_message is not None:
        return FlextResult[CommandResult].fail(error_message)
    empty_result: CommandResult = {
        "command": [],
        "returncode": -1,
        "stdout": None,
        "stderr": None,
        "success": False,
    }
    return FlextResult[CommandResult].ok(result_payload or empty_result)


# =============================================================================
# INTERACTIVE UTILITIES - User prompts and confirmations
# =============================================================================


def cli_confirm(message: str, *, default: bool = False) -> FlextResult[bool]:
    """Ask user for confirmation with default value.

    Args:
      message: Confirmation message
      default: Default value if user just presses Enter

    Returns:
      Result with user's confirmation

    """
    try:
        default_text = "Y/n" if default else "y/N"
        prompt = f"{message} ({default_text}): "

        response = input(prompt).strip().lower()

        if not response:
            return FlextResult[bool].ok(default)

        if response in {"y", "yes", "true", "1"}:
            confirmed = True
            return FlextResult[bool].ok(confirmed)
        if response in {"n", "no", "false", "0"}:
            confirmed = False
            return FlextResult[bool].ok(confirmed)
        return FlextResult[bool].fail("Please answer 'y' or 'n'")

    except (EOFError, KeyboardInterrupt):
        return FlextResult[bool].fail("Confirmation cancelled")
    except Exception as e:
        return FlextResult[bool].fail(f"Confirmation error: {e}")


def cli_prompt(
    message: str,
    *,
    default: str | None = None,
    hidden: bool = False,
) -> FlextResult[str]:
    """Prompt user for input with optional default and hidden input.

    Args:
      message: Prompt message
      default: Default value if user just presses Enter
      hidden: Hide input (for passwords)

    Returns:
      Result with user input

    """
    try:
        prompt_text = f"{message}"
        if default:
            prompt_text += f" [{default}]"
        prompt_text += ": "

        user_input = getpass.getpass(prompt_text) if hidden else input(prompt_text)

        user_input = user_input.strip()
        if not user_input and default:
            user_input = default

        return FlextResult[str].ok(user_input)

    except (EOFError, KeyboardInterrupt):
        return FlextResult[str].fail("Input cancelled")
    except Exception as e:
        return FlextResult[str].fail(f"Input error: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "cli_batch_process_files",
    # Interactive utilities
    "cli_confirm",
    # Output utilities
    "cli_create_table",
    "cli_format_output",
    "cli_load_data_file",
    "cli_prompt",
    "cli_quick_setup",
    "cli_run_command",
    "cli_save_data_file",
]
