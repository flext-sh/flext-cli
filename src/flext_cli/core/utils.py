"""FLEXT CLI Core Utils - Zero-Boilerplate Utility Functions.

This module provides ultra-concise utility functions that eliminate 95%+
boilerplate code for common CLI operations through intelligent automation
and workflow patterns following flext-core architecture.

Utility Categories:
    - Workflow utilities: Complete operations in single function calls
    - Data utilities: JSON, CSV, YAML processing with validation
    - File utilities: Batch operations with safety and progress
    - System utilities: Command execution, process management

Key Features:
    - Single-function complete operations (no manual steps)
    - Automatic error handling with FlextResult integration
    - Built-in validation, confirmation, and progress tracking
    - Rich console output with zero configuration
    - Intelligent defaults for maximum productivity

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import io
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from flext_core import FlextResult, get_logger

from flext_cli.core.helpers import (
    FlextCliHelper,
    flext_cli_batch_validate,
)

# Type aliases to avoid false positive FBT001 warnings
FlextCliData = dict[str, object] | list[object] | str | float | int | None

# YAML support for configuration export
import yaml

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


def flext_cli_quick_setup(
    project_name: str,
    *,
    create_dirs: bool = True,
    create_config: bool = True,
    init_git: bool = False,
) -> FlextResult[dict[str, object]]:
    """Create complete project setup in one function call - eliminates 50+ lines of setup code."""
    helper = FlextCliHelper()
    results: dict[str, object] = {}

    try:
        # Validate project name
        if not project_name or not project_name.strip():
            return FlextResult.fail("Project name cannot be empty")

        project_path = Path(project_name).resolve()

        if project_path.exists():
            confirmation = helper.flext_cli_confirm(
                f"Directory {project_path} exists. Continue?", default=False
            )
            if not confirmation.success or not confirmation.data:
                return FlextResult.fail("Setup cancelled")

        # Create directory structure
        if create_dirs:
            dirs = ["src", "tests", "docs", "scripts", "config"]
            helper.console.print("[blue]Creating directory structure...[/blue]")

            for dir_name in dirs:
                dir_path = project_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                results[f"dir_{dir_name}"] = str(dir_path)

            helper.console.print("[green]✓ Directory structure created[/green]")

        # Create basic configuration
        if create_config:
            helper.console.print("[blue]Creating configuration files...[/blue]")

            # Create pyproject.toml
            config_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "FLEXT CLI Project"
authors = ["Developer <dev@example.com>"]
requires-python = ">=3.13"
dependencies = [
    "flext-core>=0.9.0",
    "flext-cli>=0.1.0",
]

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 79
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
"""

            with (project_path / "pyproject.toml").open("w") as f:
                f.write(config_content)

            results["pyproject"] = str(project_path / "pyproject.toml")

            # Create basic README
            readme_content = f"""# {project_name}

FLEXT CLI Project - Enterprise-grade data integration solution.

## Setup

```bash
pip install -e .
```

## Usage

```python
from {project_name.replace("-", "_")} import main
main()
```
"""

            with (project_path / "README.md").open("w") as f:
                f.write(readme_content)

            results["readme"] = str(project_path / "README.md")
            helper.console.print("[green]✓ Configuration files created[/green]")

        # Initialize git repository
        if init_git:
            helper.console.print("Initializing git repository...")

            try:
                git_cmd = shutil.which("git")
                if not git_cmd:
                    results["git"] = "git not found in PATH"
                else:
                    subprocess.run(
                        [git_cmd, "init"],
                        check=True,
                        cwd=project_path,
                        capture_output=True,
                    )
                    results["git"] = "initialized"
                    helper.console.print("[green]✓ Git repository initialized[/green]")
            except (subprocess.CalledProcessError, FileNotFoundError):
                helper.console.print("[yellow]⚠ Git initialization failed[/yellow]")

        results["project_path"] = str(project_path)
        results["status"] = "completed"

        helper.console.print(f"[green]✓ Project {project_name} setup completed[/green]")
        return FlextResult.ok(results)

    except Exception as e:
        return FlextResult.fail(f"Project setup failed: {e}")


def flext_cli_auto_config(
    data: dict[str, object],
    *,
    template_path: str | None = None,
    output_path: str | None = None,
    format_type: str = "json",
) -> FlextResult[str]:
    """Generate configuration file from data with template support - eliminates config generation boilerplate."""
    helper = FlextCliHelper()

    try:
        # Generate output filename if not provided
        if not output_path:
            timestamp = int(time.time())
            output_path = f"config_{timestamp}.{format_type}"

        # Load template if provided
        if template_path:
            template_result = helper.flext_cli_load_file(template_path)
            if template_result.success:
                # Merge template with provided data
                template_data = template_result.data
                if isinstance(template_data, dict):
                    template_data.update(data)
                    data = template_data
            else:
                helper.console.print(
                    f"[yellow]⚠ Template load failed: {template_result.error}[/yellow]"
                )

        # Save configuration
        if format_type.lower() == "json":
            save_result = helper.flext_cli_save_file(
                data, output_path, file_format="json"
            )
        else:
            return FlextResult.fail(f"Unsupported format: {format_type}")

        if save_result.success:
            helper.console.print(
                f"[green]✓ Configuration saved to {output_path}[/green]"
            )
            return FlextResult.ok(output_path)
        return FlextResult.fail(save_result.error or "Save failed")

    except Exception as e:
        return FlextResult.fail(f"Auto config failed: {e}")


def _load_file_content(
    path_obj: Path, encoding: str, *, format_detection: bool, helper: FlextCliHelper
) -> tuple[dict[str, object] | None, str | None]:
    """Helper function to load file content based on format detection."""
    # Validate file first
    if not path_obj.exists() or not path_obj.is_file():
        error_msg = (
            f"File not found: {path_obj}"
            if not path_obj.exists()
            else f"Path is not a file: {path_obj}"
        )
        return None, error_msg

    # Handle non-format detection or simple text loading
    if not format_detection:
        with path_obj.open(encoding=encoding) as f:
            return {"content": f.read()}, None

    suffix = path_obj.suffix.lower()

    # Handle JSON format via helper
    if suffix == ".json":
        result = helper.flext_cli_load_file(str(path_obj))
        return (result.data, None) if result.success else (None, result.error)

    # Handle YAML with dependency check
    if suffix in {".yml", ".yaml"}:
        try:
            with path_obj.open(encoding=encoding) as f:
                return yaml.safe_load(f) if yaml else {}, None
        except AttributeError:
            return None, "PyYAML not installed for YAML support"

    # Handle all other formats (CSV and text) in single path
    with path_obj.open(encoding=encoding) as f:
        content_data: dict[str, object] = (
            {"rows": list(csv.DictReader(f))}
            if suffix == ".csv"
            else {"content": f.read(), "type": "text"}
        )

    return content_data, None


def flext_cli_load_file(
    file_path: str, *, encoding: str = "utf-8", format_detection: bool = True
) -> FlextResult[dict[str, object]]:
    """Smart file loading with automatic format detection - eliminates format-specific loading code."""
    helper = FlextCliHelper()

    try:
        path_obj = Path(file_path)
        result_data, error_msg = _load_file_content(
            path_obj, encoding, format_detection=format_detection, helper=helper
        )

        if error_msg:
            return FlextResult.fail(error_msg)

        return FlextResult.ok(result_data or {})

    except Exception as e:
        return FlextResult.fail(f"File loading failed: {e}")


def _detect_file_format(path_obj: Path, format_type: str | None) -> str:
    """Helper function to detect file format from extension."""
    if format_type:
        return format_type

    suffix = path_obj.suffix.lower()
    format_mapping = {
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".csv": "csv",
    }
    return format_mapping.get(suffix, "text")


def _format_data_content(data: FlextCliData, format_type: str) -> FlextResult[str]:
    """Helper function to format data content based on format type."""
    content = ""

    if format_type == "json":
        content = json.dumps(data, indent=2, ensure_ascii=False)
    elif format_type == "yaml":
        try:
            content = (
                yaml.dump(data, default_flow_style=False, allow_unicode=True)
                if yaml
                else ""
            )
        except AttributeError:
            return FlextResult.fail("PyYAML not installed for YAML support")
    elif format_type == "csv":
        if not isinstance(data, dict) or "rows" not in data:
            return FlextResult.fail(
                "CSV data must be dict with 'rows' key containing list of dicts"
            )

        rows = data["rows"]
        if (
            not rows
            or not isinstance(rows, list)
            or not rows[0]
            or not isinstance(rows[0], dict)
        ):
            content = ""
        else:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            content = output.getvalue()
    else:
        # Text format
        content = str(data) if not isinstance(data, str) else data

    return FlextResult.ok(content)


def flext_cli_save_file(
    data: FlextCliData,
    file_path: str,
    *,
    format_type: str | None = None,
    encoding: str = "utf-8",
    backup: bool = False,
) -> FlextResult[str]:
    """Smart file saving with automatic format detection - eliminates format-specific saving code."""
    try:
        path_obj = Path(file_path)
        detected_format = _detect_file_format(path_obj, format_type)

        # Format data content
        content_result = _format_data_content(data, detected_format)
        if not content_result.success:
            return content_result

        content = content_result.data or ""

        # Handle backup if requested
        if backup and path_obj.exists():
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)

        # Write content to file
        with path_obj.open("w", encoding=encoding) as f:
            f.write(content)

        return FlextResult.ok(str(path_obj))

    except (OSError, PermissionError) as e:
        return FlextResult.fail(f"Failed to write file {file_path}: {e}")
    except Exception as e:
        return FlextResult.fail(f"File saving failed: {e}")


def flext_cli_create_table(
    data: list[dict[str, object]],
    *,
    title: str | None = None,
    _max_width: int = 120,
    _show_lines: bool = True,
) -> FlextResult[None]:
    """Create and display formatted table - eliminates table formatting boilerplate."""
    helper = FlextCliHelper()
    table_result = helper.flext_cli_create_table(data, title=title)
    if table_result.success:
        helper.console.print(table_result.data)
        return FlextResult.ok(None)
    return FlextResult.fail(table_result.error or "Table creation failed")


def flext_cli_batch_execute(
    operations: list[tuple[str, Callable[[], FlextResult[object]]]],
    *,
    stop_on_first_error: bool = True,
) -> FlextResult[dict[str, object]]:
    """Execute multiple operations in batch with comprehensive error handling and progress."""
    helper = FlextCliHelper()
    results = {}

    try:
        # Progress is handled by printing, no special progress wrapper needed
        operations_to_run = operations

        for operation_name, operation_func in operations_to_run:
            helper.console.print(f"Executing: {operation_name}")

            try:
                result = operation_func()

                if result.success:
                    results[operation_name] = result.data
                    helper.console.print(f"[green]✓ {operation_name} completed[/green]")
                else:
                    results[operation_name] = {"error": result.error}
                    helper.console.print(
                        f"[red]✗ {operation_name} failed: {result.error}[/red]"
                    )

                    if stop_on_first_error:
                        return FlextResult.fail(
                            f"Batch execution stopped at {operation_name}: {result.error}"
                        )

            except Exception as e:
                error_msg = f"Operation {operation_name} raised exception: {e}"
                results[operation_name] = {"exception": str(e)}
                helper.console.print(f"[red]✗ {error_msg}[/red]")

                if stop_on_first_error:
                    return FlextResult.fail(error_msg)

        # Summary
        successful = sum(
            1
            for r in results.values()
            if not isinstance(r, dict) or ("error" not in r and "exception" not in r)
        )
        total = len(operations)

        if successful == total:
            helper.console.print(
                f"[green]✓ All {total} operations completed successfully[/green]"
            )
        else:
            helper.console.print(
                f"[yellow]⚠ {successful}/{total} operations completed successfully[/yellow]"
            )

        results["_summary"] = {
            "successful": successful,
            "total": total,
            "failed": total - successful,
        }
        return FlextResult.ok(results)

    except Exception as e:
        return FlextResult.fail(f"Batch execution failed: {e}")


def flext_cli_validate_all(
    inputs: dict[str, tuple[str, str]], *, _strict: bool = True
) -> FlextResult[dict[str, object]]:
    """Validate all inputs with comprehensive reporting - eliminates validation logic boilerplate.

    Note: _strict parameter is reserved for future use.
    """
    validated_result = flext_cli_batch_validate(inputs)
    if validated_result.success and validated_result.data:
        result_dict: dict[str, object] = {}
        result_dict.update(validated_result.data)
        return FlextResult.ok(result_dict)
    return FlextResult.fail(validated_result.error or "Validation failed")


def flext_cli_require_all(
    requirements: list[str],
    *,
    check_commands: bool = True,
    check_files: bool = True,
    check_env_vars: bool = True,
) -> FlextResult[dict[str, bool]]:
    """Check all requirements (commands, files, env vars) - eliminates prerequisite checking boilerplate."""
    helper = FlextCliHelper()
    results = {}
    missing = []

    try:
        for requirement in requirements:
            if check_commands:
                # Check if it's a command
                try:
                    # Use shutil.which() instead of shell command for security
                    cmd_path = shutil.which(requirement)
                    if cmd_path:
                        results[f"command_{requirement}"] = True
                        continue
                except Exception as e:
                    logger = get_logger(__name__)
                    logger.debug(f"Command check failed for '{requirement}': {e}")
                    # Continue checking other requirement types

            if check_files and Path(requirement).exists():
                # Check if it's a file/directory
                results[f"file_{requirement}"] = True
                continue

            if check_env_vars and os.environ.get(requirement):
                results[f"env_{requirement}"] = True
                continue

            # Not found
            results[requirement] = False
            missing.append(requirement)

        if missing:
            return FlextResult.fail(f"Missing requirements: {', '.join(missing)}")

        helper.console.print("[green]✓ All requirements satisfied[/green]")
        return FlextResult.ok(results)

    except Exception as e:
        return FlextResult.fail(f"Requirements check failed: {e}")


def flext_cli_output_data(
    data: FlextCliData,
    *,
    format_type: str = "auto",
    file_path: str | None = None,
    console_output: bool = True,
) -> FlextResult[str | None]:
    """Output data in specified format to console and/or file - eliminates output formatting boilerplate."""
    helper = FlextCliHelper()

    try:
        # Auto-detect format based on data type
        if format_type == "auto":
            format_type = "json" if isinstance(data, (dict, list)) else "text"

        # Format data
        if format_type == "json":
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
        elif (
            format_type == "table"
            and isinstance(data, list)
            and data
            and isinstance(data[0], dict)
        ):
            if console_output:
                table_data = [dict(item) for item in data if isinstance(item, dict)]
                table_result = helper.flext_cli_create_table(table_data)
                if table_result.success:
                    helper.console.print(table_result.data)
                formatted = f"Table with {len(data)} rows displayed"
            else:
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            formatted = str(data)

        # Console output
        if console_output and format_type != "table":
            helper.console.print(formatted)

        # File output
        output_path: str | None = None
        if file_path:
            save_result = flext_cli_save_file(data, file_path, format_type=format_type)
            if save_result.success:
                output_path = str(file_path)
                helper.console.print(f"[green]✓ Data saved to {output_path}[/green]")
            else:
                return FlextResult.fail(save_result.error or "Save failed")

        return FlextResult.ok(output_path)

    except Exception as e:
        return FlextResult.fail(f"Data output failed: {e}")
