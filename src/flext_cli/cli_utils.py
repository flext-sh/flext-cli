"""FLEXT CLI Utilities - Complete utility system consolidating all CLI utilities.

This module consolidates all CLI utility functionality from multiple scattered files
into a single, well-organized module following PEP8 naming conventions.

Consolidated from:
    - core/utils.py (workflow and automation utilities)
    - utils/output.py (output formatting utilities)
    - core/helpers.py (helper functions)
    - Various utility definitions across modules

Design Principles:
    - PEP8 naming: cli_utils.py (not utils.py for clarity)
    - Single source of truth for all CLI utilities
    - Zero-boilerplate approach with intelligent automation
    - Type safety with comprehensive annotations
    - Rich console integration for beautiful output

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import getpass
import io
import json
import shlex
import subprocess
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, TypeVar, cast

import yaml
from flext_core import FlextResult, get_logger
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from flext_cli.cli_types import OutputFormat

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")

# Type aliases for utility functions
FlextCliData = dict[str, object] | list[object] | str | float | int | None


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
    """Initialize a git repository, returning True on success."""
    git_exe = which("git") or "git"
    try:
        subprocess.run(  # noqa: S603, S607
            [git_exe, "init"],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _create_directory_structure(base: Path, dir_names: list[str]) -> dict[str, str]:
    """Create directories under base and return a map for results."""
    created: dict[str, str] = {}
    for dir_name in dir_names:
        dir_path = base / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        created[f"dir_{dir_name}"] = str(dir_path)
    return created


def _record_success(results: dict[str, object], path: Path) -> None:
    processed_count = cast("int", results["processed"])
    results["processed"] = processed_count + 1
    successful_list = cast("list[str]", results["successful"])
    successful_list.append(str(path))
    results["successful"] = successful_list


def _record_failure(
    results: dict[str, object], path: Path, error_msg: str,
) -> None:
    failed_count = cast("int", results["failed"])
    results["failed"] = failed_count + 1
    errors_list = cast("list[dict[str, str]]", results["errors"])
    errors_list.append({"file": str(path), "error": error_msg})
    results["errors"] = errors_list


def cli_quick_setup(
    project_name: str,
    *,
    create_dirs: bool = True,
    create_config: bool = True,
    init_git: bool = False,
) -> FlextResult[dict[str, object]]:
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
    results: dict[str, object] = {}

    try:
        # Validate project name
        if not project_name or not project_name.strip():
            return FlextResult.fail("Project name cannot be empty")

        project_path = Path(project_name).resolve()

        if project_path.exists():
            confirmation = cli_confirm(
                f"Directory {project_path} exists. Continue?",
                default=False,
            )
            if not confirmation.success or not confirmation.data:
                return FlextResult.fail("Setup cancelled")

        # Create directory structure
        if create_dirs:
            dirs = ["src", "tests", "docs", "scripts", "config"]
            console.print("[blue]Creating directory structure...[/blue]")
            results.update(_create_directory_structure(project_path, dirs))
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
                results["git_init"] = True
                console.print("[green]✓ Git repository initialized[/green]")
            else:
                console.print("[yellow]⚠ Git init failed[/yellow]")
                results["git_init"] = False

        results["project_path"] = str(project_path)
        console.print(f"[green]🎉 Project '{project_name}' setup complete![/green]")

        return FlextResult.ok(results)

    except (OSError, PermissionError) as e:
        return FlextResult.fail(f"Setup failed: {e}")
    except Exception as e:
        return FlextResult.fail(f"Unexpected error during setup: {e}")


def cli_batch_process_files(
    file_paths: list[Path | str],
    processor: Callable[[Path], FlextResult[object]],
    *,
    show_progress: bool = True,
    fail_fast: bool = False,
) -> FlextResult[dict[str, object]]:
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
    results: dict[str, object] = {
        "processed": 0,
        "failed": 0,
        "errors": [],
        "successful": [],
    }

    if not file_paths:
        return FlextResult.ok(results)

    # Convert string paths to Path objects
    paths = [Path(p) for p in file_paths]

    progress: Progress | None = None
    task_id: int | None = None

    try:
        if show_progress:
            progress = Progress()
            progress.start()
            task_id = progress.add_task("Processing files...", total=len(paths))

        for path in paths:
            try:
                result = processor(path)
                if result.is_success:
                    _record_success(results, path)
                else:
                    _record_failure(results, path, result.error or "Unknown error")

                    if fail_fast:
                        return FlextResult.fail(
                            f"Processing failed for {path}: {result.error}",
                        )

                if progress and task_id is not None:
                    progress.update(task_id, advance=1)

            except Exception as e:
                _record_failure(results, path, str(e))

                if fail_fast:
                    return FlextResult.fail(f"Processing failed for {path}: {e}")

        # Show summary
        if show_progress:
            processed_count = cast("int", results["processed"])
            failed_count = cast("int", results["failed"])
            console.print(f"[green]✓ Processed {processed_count} files[/green]")
            if failed_count > 0:
                console.print(f"[yellow]⚠ {failed_count} files failed[/yellow]")

        return FlextResult.ok(results)

    finally:
        if progress:
            progress.stop()


# =============================================================================
# DATA UTILITIES - JSON, CSV, YAML processing with validation
# =============================================================================


def cli_load_data_file(
    file_path: Path | str, *, validate_format: bool = True,
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
            return FlextResult.fail(f"File does not exist: {path}")

        # Detect format from extension
        suffix = path.suffix.lower()

        if suffix == ".json":
            return _load_json_file(path)
        if suffix in {".yaml", ".yml"}:
            return _load_yaml_file(path)
        if suffix == ".csv":
            csv_result = _load_csv_file(path)
            return csv_result.map(lambda data: data)  # Cast to object
        if suffix == ".txt":
            text_result = _load_text_file(path)
            return text_result.map(lambda data: data)  # Cast to object
        if validate_format:
            return FlextResult.fail(f"Unsupported file format: {suffix}")
        # Try to load as text
        text_result = _load_text_file(path)
        return text_result.map(lambda data: data)  # Cast to object

    except Exception as e:
        return FlextResult.fail(f"Failed to load data file: {e}")


def _load_json_file(path: Path) -> FlextResult[object]:
    """Load JSON file with error handling."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return FlextResult.ok(data)
    except json.JSONDecodeError as e:
        return FlextResult.fail(f"Invalid JSON in {path}: {e}")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult.fail(f"Failed to read JSON file {path}: {e}")


def _load_yaml_file(path: Path) -> FlextResult[object]:
    """Load YAML file with error handling."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return FlextResult.ok(data)
    except yaml.YAMLError as e:
        return FlextResult.fail(f"Invalid YAML in {path}: {e}")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult.fail(f"Failed to read YAML file {path}: {e}")


def _load_csv_file(path: Path) -> FlextResult[list[dict[str, str]]]:
    """Load CSV file with error handling."""
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return FlextResult.ok(data)
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult.fail(f"Failed to read CSV file {path}: {e}")


def _load_text_file(path: Path) -> FlextResult[str]:
    """Load text file with error handling."""
    try:
        content = path.read_text(encoding="utf-8")
        return FlextResult.ok(content)
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult.fail(f"Failed to read text file {path}: {e}")


def cli_save_data_file(
    data: object,
    file_path: Path | str,
    format_type: OutputFormat | str | None = None,
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
        if format_type is None:
            suffix = path.suffix.lower()
            if suffix == ".json":
                format_type = OutputFormat.JSON
            elif suffix in {".yaml", ".yml"}:
                format_type = OutputFormat.YAML
            elif suffix == ".csv":
                format_type = OutputFormat.CSV
            else:
                format_type = OutputFormat.TEXT
        elif isinstance(format_type, str):
            format_type = OutputFormat(format_type.lower())

        # Save based on format
        if format_type == OutputFormat.JSON:
            return _save_json_file(data, path)
        if format_type == OutputFormat.YAML:
            return _save_yaml_file(data, path)
        if format_type == OutputFormat.CSV:
            return _save_csv_file(data, path)
        # TEXT
        return _save_text_file(data, path)

    except Exception as e:
        return FlextResult.fail(f"Failed to save data file: {e}")


def _save_json_file(data: object, path: Path) -> FlextResult[None]:
    """Save data as JSON file."""
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        return FlextResult.ok(None)
    except (OSError, TypeError) as e:
        return FlextResult.fail(f"Failed to write JSON file {path}: {e}")


def _save_yaml_file(data: object, path: Path) -> FlextResult[None]:
    """Save data as YAML file."""
    try:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, sort_keys=False, allow_unicode=True,
            )
        return FlextResult.ok(None)
    except (OSError, yaml.YAMLError) as e:
        return FlextResult.fail(f"Failed to write YAML file {path}: {e}")


def _save_csv_file(data: object, path: Path) -> FlextResult[None]:
    """Save data as CSV file."""
    try:
        if not isinstance(data, list) or not data:
            return FlextResult.fail("CSV data must be a non-empty list")

        if not isinstance(data[0], dict):
            return FlextResult.fail("CSV data must be a list of dictionaries")

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return FlextResult.ok(None)
    except (OSError, ValueError) as e:
        return FlextResult.fail(f"Failed to write CSV file {path}: {e}")


def _save_text_file(data: object, path: Path) -> FlextResult[None]:
    """Save data as text file."""
    try:
        content = str(data)
        path.write_text(content, encoding="utf-8")
        return FlextResult.ok(None)
    except (OSError, UnicodeEncodeError) as e:
        return FlextResult.fail(f"Failed to write text file {path}: {e}")


# =============================================================================
# OUTPUT UTILITIES - Rich console output and formatting
# =============================================================================


def cli_create_table(
    data: object,
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
                return FlextResult.fail("Cannot create table from empty list")

            if isinstance(data[0], dict):
                # List of dictionaries - create columns from first item
                headers = list(data[0].keys())
                for header in headers:
                    table.add_column(header.replace("_", " ").title())

                for item in data:
                    row_data = [str(item.get(h, "")) for h in headers]
                    table.add_row(*row_data)
            else:
                # List of values - single column
                table.add_column("Value")
                for item in data:
                    table.add_row(str(item))

        elif isinstance(data, dict):
            # Dictionary - key-value pairs
            table.add_column("Key", style="cyan")
            table.add_column("Value")

            for key, value in data.items():
                table.add_row(key.replace("_", " ").title(), str(value))

        else:
            # Single value - simple table
            table.add_column("Value")
            table.add_row(str(data))

        return FlextResult.ok(table)

    except Exception as e:
        return FlextResult.fail(f"Failed to create table: {e}")


def cli_format_output(
    data: object,
    format_type: OutputFormat = OutputFormat.TABLE,
    **options: object,
) -> FlextResult[str]:
    """Format data for CLI output in specified format.

    Args:
        data: Data to format
        format_type: Output format
        **options: Additional formatting options

    Returns:
        Result with formatted output string

    """
    try:
        if format_type == OutputFormat.JSON:
            formatted = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            return FlextResult.ok(formatted)

        if format_type == OutputFormat.YAML:
            output = io.StringIO()
            yaml.dump(data, output, default_flow_style=False, allow_unicode=True)
            return FlextResult.ok(output.getvalue())

        if format_type == OutputFormat.CSV:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return FlextResult.ok(output.getvalue())
            return FlextResult.fail("CSV format requires list of dictionaries")

        if format_type == OutputFormat.TABLE:
            # Extract title from options for cli_create_table
            title = str(options.get("title")) if options.get("title") else None
            show_lines = bool(options.get("show_lines"))
            max_width = (
                cast("int", options["max_width"]) if options.get("max_width") else None
            )

            table_result = cli_create_table(
                data, title=title, show_lines=show_lines, max_width=max_width,
            )
            if table_result.is_success:
                output = io.StringIO()
                console = Console(file=output, width=80)
                console.print(table_result.unwrap())
                return FlextResult.ok(output.getvalue())
            # Convert table result error to string result error
            if table_result.error:
                return FlextResult.fail(table_result.error)
            return FlextResult.fail("Table creation failed")

        # TEXT
        return FlextResult.ok(str(data))

    except Exception as e:
        return FlextResult.fail(f"Failed to format output: {e}")


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
) -> FlextResult[dict[str, object]]:
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
    try:
        # Convert string command to list and ensure an executable is present
        cmd_list = shlex.split(command) if isinstance(command, str) else command
        if not cmd_list:
            return FlextResult.fail("Empty command")

        logger = get_logger(__name__)
        logger.debug(f"Running command: {cmd_list}")

        result = subprocess.run(  # noqa: S603
            cmd_list,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=check,
        )

        command_result = {
            "command": cmd_list,
            "returncode": result.returncode,
            "stdout": result.stdout if capture_output else None,
            "stderr": result.stderr if capture_output else None,
            "success": result.returncode == 0,
        }

        return FlextResult.ok(command_result)

    except subprocess.TimeoutExpired as e:
        return FlextResult.fail(f"Command timed out after {timeout}s: {e}")
    except subprocess.CalledProcessError as e:
        return FlextResult.fail(f"Command failed with exit code {e.returncode}: {e}")
    except FileNotFoundError as e:
        return FlextResult.fail(f"Command not found: {e}")
    except Exception as e:
        return FlextResult.fail(f"Command execution failed: {e}")


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
            return FlextResult.ok(data=default)

        if response in {"y", "yes", "true", "1"}:
            return FlextResult.ok(data=True)
        if response in {"n", "no", "false", "0"}:
            return FlextResult.ok(data=False)
        return FlextResult.fail("Please answer 'y' or 'n'")

    except (EOFError, KeyboardInterrupt):
        return FlextResult.fail("Confirmation cancelled")
    except Exception as e:
        return FlextResult.fail(f"Confirmation error: {e}")


def cli_prompt(
    message: str, *, default: str | None = None, hidden: bool = False,
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

        return FlextResult.ok(user_input)

    except (EOFError, KeyboardInterrupt):
        return FlextResult.fail("Input cancelled")
    except Exception as e:
        return FlextResult.fail(f"Input error: {e}")


# Legacy aliases for backward compatibility
flext_cli_quick_setup = cli_quick_setup
flext_cli_batch_process_files = cli_batch_process_files
flext_cli_load_data_file = cli_load_data_file
flext_cli_save_data_file = cli_save_data_file
flext_cli_create_table = cli_create_table
flext_cli_format_output = cli_format_output
flext_cli_run_command = cli_run_command
flext_cli_confirm = cli_confirm
flext_cli_prompt = cli_prompt


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
    # Data utilities
    "cli_load_data_file",
    "cli_prompt",
    # Workflow utilities
    "cli_quick_setup",
    # System utilities
    "cli_run_command",
    "cli_save_data_file",
    "flext_cli_batch_process_files",
    "flext_cli_confirm",
    "flext_cli_create_table",
    "flext_cli_format_output",
    "flext_cli_load_data_file",
    "flext_cli_prompt",
    # Legacy aliases
    "flext_cli_quick_setup",
    "flext_cli_run_command",
    "flext_cli_save_data_file",
]
