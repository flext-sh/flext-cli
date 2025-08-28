"""Core utils.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import csv
import io
import os
import secrets
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import yaml
from flext_core import FlextResult, FlextUtilities
from rich.console import Console
from rich.progress import track as rich_track
from rich.table import Table

from flext_cli.helpers import FlextCliHelper


def _generate_session_id() -> str:
    """Generate unique session ID with timestamp and secure random component."""
    timestamp = int(datetime.now(tz=UTC).timestamp())
    random_part = secrets.randbelow(900) + 100  # 3-digit number (100-999)
    return f"{timestamp:08d}{random_part}"[-8:]


# def _get_version() -> str:  # Unused function removed
#     return _cli_version


def _current_timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


def _load_env_overrides() -> dict[str, object]:
    overrides: dict[str, object] = {}
    for key, val in os.environ.items():
        if not key.startswith("FLEXT_"):
            continue
        norm = key.removeprefix("FLEXT_").lower()
        if val.lower() in {"true", "false"}:
            overrides[norm] = val.lower() == "true"
        else:
            try:
                overrides[norm] = int(val)
            except ValueError:
                overrides[norm] = val
    return overrides


def _load_config_file(path: str | Path) -> FlextResult[dict[str, object]]:
    p = Path(path)
    if not p.exists():
        return FlextResult[dict[str, object]].fail("Config file not found")
    try:
        if p.suffix.lower() in {".yml", ".yaml"}:
            return FlextResult[dict[str, object]].ok(
                yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            )
        if p.suffix.lower() == ".json":
            parsed_data = FlextUtilities.ProcessingUtils.safe_json_parse(
                p.read_text(encoding="utf-8")
            )
            return FlextResult[dict[str, object]].ok(parsed_data)
        return FlextResult[dict[str, object]].fail("Unsupported config format")
    except Exception as e:
        return FlextResult[dict[str, object]].fail(str(e))


def flext_cli_quick_setup(config: dict[str, object]) -> FlextResult[dict[str, object]]:
    """Quick setup of CLI context with configuration defaults."""
    try:
        defaults: dict[str, str | bool] = {"profile": "default", "debug": False}
        merged: dict[str, object] = {**defaults, **config}
        console_width = merged.get("console_width") or 80
        console = Console(
            width=int(console_width) if isinstance(console_width, (int, str)) else 80,
        )
        context: dict[str, object] = {
            "config": merged,
            "console": console,
            "session_id": _generate_session_id(),
            "initialized": True,
        }
        return FlextResult[dict[str, object]].ok(context)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(f"CLI setup failed: {e}")


def flext_cli_auto_config(
    profile: str,
    config_files: list[str],
) -> FlextResult[dict[str, object]]:
    """Load and merge CLI configuration automatically from profile and files."""
    env = _load_env_overrides()
    loaded: dict[str, object] = {"profile": profile}
    for file in config_files:
        p = Path(file)
        if p.exists():
            file_res = _load_config_file(p)
            if file_res.is_success:
                # File values have lower precedence than explicit profile argument
                file_loaded = file_res.value
                for k, v in file_loaded.items():
                    if k == "profile":
                        continue
                    loaded[k] = v
                loaded["config_source"] = str(p)
                break
    # Always include config_source key for test expectations
    if "config_source" not in loaded:
        loaded["config_source"] = None
    loaded.update(env)
    if env:
        loaded["env_overrides"] = env
    loaded["loaded_at"] = _current_timestamp()
    return FlextResult[dict[str, object]].ok(loaded)


def flext_cli_validate_all(
    validations: dict[str, tuple[object, str]],
) -> FlextResult[dict[str, object]]:
    """Validate multiple values and return aggregated results."""
    output: dict[str, object] = {}

    def _email(v: object) -> FlextResult[str]:
        s = str(v)
        return (
            FlextResult[str].ok(s)
            if ("@" in s and "." in s)
            else FlextResult[str].fail("Invalid email")
        )

    def _url(v: object) -> FlextResult[str]:
        s = str(v)
        return (
            FlextResult[str].ok(s)
            if s.startswith(("http://", "https://"))
            else FlextResult[str].fail("Invalid URL")
        )

    def _path(v: object) -> FlextResult[Path]:
        return FlextResult[Path].ok(Path(str(v)))

    def _file(v: object) -> FlextResult[Path]:
        p = Path(str(v))
        return (
            FlextResult[Path].ok(p)
            if p.exists()
            else FlextResult[Path].fail("File not found")
        )

    def _dir(v: object) -> FlextResult[Path]:
        p = Path(str(v))
        return (
            FlextResult[Path].ok(p)
            if (p.exists() and p.is_dir())
            else FlextResult[Path].fail("Directory not found")
        )

    def _filename(v: object) -> FlextResult[str]:
        name = str(v)
        sanitized = name.replace("<", "_").replace(">", "_")
        return FlextResult[str].ok(sanitized)

    def _int(v: object) -> FlextResult[int]:
        if isinstance(v, bool):
            return FlextResult[int].fail("Invalid integer")
        if isinstance(v, int):
            return FlextResult[int].ok(v)
        if isinstance(v, str):
            try:
                return FlextResult[int].ok(int(v))
            except ValueError:
                return FlextResult[int].fail("Invalid integer")
        return FlextResult[int].fail("Invalid integer")

    validators: dict[str, Callable[[object], FlextResult[object]]] = {
        "email": cast("Callable[[object], FlextResult[object]]", _email),
        "url": cast("Callable[[object], FlextResult[object]]", _url),
        "path": cast("Callable[[object], FlextResult[object]]", _path),
        "file": cast("Callable[[object], FlextResult[object]]", _file),
        "dir": cast("Callable[[object], FlextResult[object]]", _dir),
        "filename": cast("Callable[[object], FlextResult[object]]", _filename),
        "int": cast("Callable[[object], FlextResult[object]]", _int),
    }

    for key, (value, vtype) in validations.items():
        validate = validators.get(vtype)
        if validate is None:
            return FlextResult[dict[str, object]].fail("Unknown validation type")
        res = validate(value)
        if res.is_failure:
            return FlextResult[dict[str, object]].fail(f"Validation failed for {key}")
        # For path/file/dir, return Path objects per tests
        unwrapped = res.value
        if vtype in {"path", "file", "dir"}:
            output[key] = Path(str(unwrapped))
        else:
            output[key] = unwrapped

    return FlextResult[dict[str, object]].ok(output)


def flext_cli_require_all(confirmations: list[tuple[str, bool]]) -> FlextResult[bool]:
    """Require all confirmations to be True, return aggregated result."""
    helper = FlextCliHelper()
    for message, _default in confirmations:
        res = helper.flext_cli_confirm(message)
        if res.is_failure:
            return FlextResult[bool].fail(res.error or "Confirmation failed")
        if not res.value:
            return FlextResult[bool].ok(data=False)
    return FlextResult[bool].ok(data=True)


def flext_cli_output_data(
    data: object,
    format_type: str,
    *,
    console: Console,
    indent: int | None = None,
) -> FlextResult[bool]:
    """Render data to console in the specified format."""
    try:
        if format_type == "json":
            console.print(FlextUtilities.ProcessingUtils.safe_json_stringify(data))
        elif format_type == "yaml":
            console.print(yaml.dump(data, default_flow_style=False))
        elif format_type == "table":
            table = flext_cli_create_table(data)
            console.print(table)
        elif format_type == "csv":
            output = io.StringIO()
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # Type-safe dict handling for CSV output
                typed_data = cast("list[dict[str, object]]", data)
                first_item = typed_data[0]
                writer = csv.DictWriter(output, fieldnames=list(first_item.keys()))
                writer.writeheader()
                # Convert to dict[str, str] for CSV compatibility
                csv_rows: list[dict[str, str]] = []
                for csv_item in typed_data:
                    csv_row: dict[str, str] = {
                        str(k): str(v) for k, v in csv_item.items()
                    }
                    csv_rows.append(csv_row)
                writer.writerows(csv_rows)
            console.print(output.getvalue())
        elif format_type == "text":
            if isinstance(data, list):
                typed_list = cast("list[object]", data)
                for text_item in typed_list:
                    console.print(str(text_item))
            else:
                console.print(str(data))
        else:
            console.print(data)
        return FlextResult[bool].ok(data=True)
    except Exception as e:
        return FlextResult[bool].fail(str(e))


def flext_cli_create_table(
    data: object,
    *,
    title: str | None = None,
    columns: list[str] | None = None,
) -> Table:
    """Create a Rich table from data with optional title and columns."""
    table = Table(title=title)
    if isinstance(data, list):
        typed_list = cast("list[object]", data)
        if not typed_list:
            table.add_column("No Data")
            return table
        if isinstance(typed_list[0], dict):
            first_dict = cast("dict[str, object]", typed_list[0])
            headers = columns or list(first_dict.keys())
            for h in headers:
                table.add_column(str(h))
            for item in typed_list:
                if isinstance(item, dict):
                    item_dict = cast("dict[str, object]", item)
                    table.add_row(*(str(item_dict.get(h, "")) for h in headers))
        else:
            table.add_column("Value")
            for item in typed_list:
                table.add_row(str(item))
    elif isinstance(data, dict):
        table.add_column("Key")
        table.add_column("Value")
        typed_data = cast("dict[str, object]", data)
        for k, v in typed_data.items():
            table.add_row(str(k), str(v))
    else:
        table.add_column("Value")
        table.add_row(str(data))
    return table


def flext_cli_load_file(
    file_path: str | Path,
    *,
    format_type: str | None = None,
) -> FlextResult[object]:
    """Load a file and parse its content according to the format."""
    p = Path(file_path)
    if not p.exists():
        return FlextResult[object].fail("File not found")
    try:
        suffix = p.suffix.lower()
        if format_type == "text" or suffix == ".txt":
            return FlextResult[object].ok(p.read_text(encoding="utf-8"))
        if suffix in {".yml", ".yaml"}:
            return FlextResult[object].ok(yaml.safe_load(p.read_text(encoding="utf-8")))
        if suffix == ".json":
            parsed_data = FlextUtilities.ProcessingUtils.safe_json_parse(
                p.read_text(encoding="utf-8")
            )
            return FlextResult[object].ok(parsed_data)
        return FlextResult[object].fail("Unsupported file format")
    except Exception as e:
        return FlextResult[object].fail(str(e))


def flext_cli_save_file(data: object, file_path: str | Path) -> FlextResult[bool]:
    """Save data to file with automatic format detection based on extension."""
    try:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix.lower() in {".yml", ".yaml"}:
            p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        elif p.suffix.lower() == ".json":
            p.write_text(
                FlextUtilities.ProcessingUtils.safe_json_stringify(data),
                encoding="utf-8",
            )
        else:
            p.write_text(str(data), encoding="utf-8")
        return FlextResult[bool].ok(data=True)
    except Exception as e:
        return FlextResult[bool].fail(str(e))


def _execute_named_operations[T](
    named_operations: list[tuple[str, Callable[[], FlextResult[T]]]],
    *,
    stop_on_error: bool,
) -> FlextResult[dict[str, dict[str, object]]]:
    """Execute named operation tuples and return dict results."""
    operation_results: dict[str, dict[str, object]] = {}

    for name, op in named_operations:
        try:
            res = op()
            if res.is_success:
                operation_results[name] = {"success": True, "result": res.value}
            else:
                operation_results[name] = {
                    "success": False,
                    "error": res.error or "Unknown error",
                }
                if stop_on_error:
                    error_msg = (
                        f"Operation {name} failed: {res.error or 'Unknown error'}"
                    )
                    return FlextResult[dict[str, dict[str, object]]].fail(error_msg)
        except Exception as e:
            operation_results[name] = {"success": False, "error": str(e)}
            if stop_on_error:
                return FlextResult[dict[str, dict[str, object]]].fail(
                    f"Operation {name} raised exception: {e}"
                )

    return FlextResult[dict[str, dict[str, object]]].ok(operation_results)


def _execute_items_with_operation[T](
    items: list[object],
    operation: Callable[[object], FlextResult[T]],
    *,
    stop_on_error: bool,
    show_progress: bool,
) -> FlextResult[list[T]]:
    """Execute operation on each item and return list results."""
    results: list[T] = []
    errors: list[str] = []

    # Use Rich progress bar if requested
    items_iter: Iterable[object] = items
    if show_progress:
        with contextlib.suppress(ImportError):
            items_iter = rich_track(items, description="Processing batch...")

    for i, item in enumerate(items_iter):
        try:
            res = operation(item)
            if res.is_success:
                results.append(res.value)
            else:
                error_msg = f"Item {i} failed: {res.error or 'Unknown error'}"
                errors.append(error_msg)
                if stop_on_error:
                    return FlextResult[list[T]].fail(error_msg)
        except Exception as e:
            error_msg = f"Item {i} raised exception: {e}"
            errors.append(error_msg)
            if stop_on_error:
                return FlextResult[list[T]].fail(error_msg)

    if errors and not stop_on_error:
        max_errors = 3
        error_summary = f"Batch completed with {len(errors)} errors: {'; '.join(errors[:max_errors])}"
        if len(errors) > max_errors:
            error_summary += f" and {len(errors) - max_errors} more..."
        return FlextResult[list[T]].fail(error_summary)

    return FlextResult[list[T]].ok(results)


def flext_cli_batch_execute[T](
    items: list[object] | list[tuple[str, Callable[[], FlextResult[T]]]],
    operation: Callable[[object], FlextResult[T]] | None = None,
    *,
    stop_on_error: bool = True,
    show_progress: bool = False,
) -> FlextResult[list[T]] | FlextResult[dict[str, dict[str, object]]]:
    """Execute operation on each item in batch, collecting results.

    Args:
        items: List of items to process
        operation: Function that takes an item and returns FlextResult[T]
        stop_on_error: If True, stop on first error; if False, continue and collect all results
        show_progress: If True, show Rich progress bar during processing

    Returns:
        FlextResult containing list of successful results, or error if stop_on_error=True

    Example:
        def process_item(item: str) -> FlextResult[str]:
            return FlextResult[str].ok(f"processed_{item}")

        result = flext_cli_batch_execute(["a", "b"], process_item)
        assert result.is_success
        assert result.value == ["processed_a", "processed_b"]

    """
    # Check if we have tuples of (name, operation) or regular items with single operation
    if items:
        first_item = items[0]
        # Simple check: if first item is a tuple, assume it's named operations
        if isinstance(first_item, tuple):
            # Handle (name, operation) tuples - return dict format
            named_operations = cast(
                "list[tuple[str, Callable[[], FlextResult[T]]]]", items
            )
            return _execute_named_operations(
                named_operations, stop_on_error=stop_on_error
            )

    # Handle regular items with single operation - return list format
    if operation is None:
        return FlextResult[list[T]].fail(
            "Operation function is required for item processing"
        )

    # Cast is safe here because we already checked it's not tuples above
    items_list = cast("list[object]", items)
    return _execute_items_with_operation(
        items_list, operation, stop_on_error=stop_on_error, show_progress=show_progress
    )


def track[T](
    sequence: Iterable[T], *, description: str = "Working...", total: int | None = None
) -> Iterable[T]:
    """Track progress of processing a sequence with Rich progress bar.

    Args:
        sequence: Iterable to track (list, generator, etc.)
        description: Description to show in progress bar
        total: Total number of items (auto-detected for sequences with len())

    Returns:
        Iterator that yields items while showing progress

    Example:
        for item in track([1, 2, 3], description="Processing"):
            process(item)

    """
    # Use Rich's track function for progress bar
    return rich_track(sequence, description=description, total=total)
