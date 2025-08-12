"""Core utils compatibility for legacy tests.

This module contains utility functions that provide backward compatibility
for legacy tests and CLI operations. Functions handle configuration loading,
data validation, file operations, and output formatting.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import yaml
from flext_core import FlextResult
from rich.console import Console
from rich.table import Table


def _generate_session_id() -> str:
    # First 8 chars of epoch seconds for tests
    return f"{int(datetime.now(tz=UTC).timestamp()):08d}"[-8:]


def _get_version() -> str:
    try:
        from flext_cli.__version__ import __version__
        return __version__
    except Exception:  # noqa: BLE001
        return "unknown"


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
        return FlextResult.fail("Config file not found")
    try:
        if p.suffix.lower() in {".yml", ".yaml"}:
            return FlextResult.ok(yaml.safe_load(p.read_text(encoding="utf-8")) or {})
        if p.suffix.lower() == ".json":
            return FlextResult.ok(json.loads(p.read_text(encoding="utf-8")))
        return FlextResult.fail("Unsupported config format")
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(str(e))


def flext_cli_quick_setup(config: dict[str, object]) -> FlextResult[dict[str, object]]:  # noqa: D103
    try:
        defaults = {"profile": "default", "debug": False}
        merged = {**defaults, **config}
        console_width = merged.get("console_width") or 80
        console = Console(
            width=int(console_width) if isinstance(console_width, (int, str)) else 80,
        )
        context = {
            "config": merged,
            "console": console,
            "session_id": _generate_session_id(),
            "initialized": True,
        }
        return FlextResult.ok(context)
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(f"CLI setup failed: {e}")


def flext_cli_auto_config(
    profile: str, config_files: list[str],
) -> FlextResult[dict[str, object]]:
    env = _load_env_overrides()
    loaded: dict[str, object] = {"profile": profile}
    for file in config_files:
        p = Path(file)
        if p.exists():
            file_res = _load_config_file(p)
            if file_res.success:
                loaded.update(file_res.unwrap())
                loaded["config_source"] = str(p)
                break
    loaded.update(env)
    if env:
        loaded["env_overrides"] = env
    loaded["loaded_at"] = _current_timestamp()
    return FlextResult.ok(loaded)


def flext_cli_validate_all(
    validations: dict[str, tuple[object, str]],
) -> FlextResult[dict[str, object]]:
    output: dict[str, object] = {}
    for key, (value, vtype) in validations.items():
        if vtype == "email":
            if not isinstance(value, str) or "@" not in value:
                return FlextResult.fail(f"Validation failed for {key}")
            output[key] = value
        elif vtype == "url":
            if not (
                isinstance(value, str) and (value.startswith(("http://", "https://")))
            ):
                return FlextResult.fail(f"Validation failed for {key}")
            output[key] = value
        elif vtype == "path":
            output[key] = Path(str(value))
        elif vtype in {"file", "dir"}:
            p = Path(str(value))
            if not p.exists():
                return FlextResult.fail(f"Validation failed for {key}")
            output[key] = p
        elif vtype == "filename":
            output[key] = str(value).replace("<", "_").replace(">", "_")
        elif vtype == "int":
            if isinstance(value, (int, str, float)):
                output[key] = int(value)
            else:
                return FlextResult.fail(f"Cannot convert {key} to int")
        else:
            return FlextResult.fail("Unknown validation type")
    return FlextResult.ok(output)


def flext_cli_require_all(confirmations: list[tuple[str, bool]]) -> FlextResult[bool]:  # noqa: D103
    from .helpers import FlextCliHelper

    helper = FlextCliHelper()
    for message, _default in confirmations:
        res = helper.flext_cli_confirm(message)
        if res.is_failure:
            return res
        if not res.unwrap():
            return FlextResult.ok(False)  # noqa: FBT003
    return FlextResult.ok(True)  # noqa: FBT003


def flext_cli_output_data(
    data: object, format_type: str, *, console: Console,
) -> FlextResult[bool]:
    try:
        if format_type == "json":
            console.print(json.dumps(data, indent=2, default=str))
        elif format_type == "yaml":
            console.print(yaml.dump(data, default_flow_style=False))
        elif format_type == "table":
            table = flext_cli_create_table(data)
            console.print(table)
        elif format_type == "csv":
            import csv
            import io

            output = io.StringIO()
            if isinstance(data, list) and data and isinstance(data[0], dict):
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)
            console.print(output.getvalue())
        elif format_type == "text":
            if isinstance(data, list):
                for item in data:
                    console.print(str(item))
            else:
                console.print(str(data))
        else:
            console.print(data)
        return FlextResult.ok(True)  # noqa: FBT003
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(str(e))


def flext_cli_create_table(
    data: object, *, title: str | None = None, columns: list[str] | None = None,
) -> Table:
    table = Table(title=title)
    if isinstance(data, list):
        if not data:
            table.add_column("No Data")
            return table
        if isinstance(data[0], dict):
            headers = columns or list(data[0].keys())
            for h in headers:
                table.add_column(str(h))
            for item in data:
                table.add_row(*(str(item.get(h, "")) for h in headers))
        else:
            table.add_column("Value")
            for item in data:
                table.add_row(str(item))
    elif isinstance(data, dict):
        table.add_column("Key")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(str(k), str(v))
    else:
        table.add_column("Value")
        table.add_row(str(data))
    return table


def flext_cli_load_file(
    file_path: str | Path, *, format_type: str | None = None,
) -> FlextResult[object]:
    p = Path(file_path)
    if not p.exists():
        return FlextResult.fail("File not found")
    try:
        suffix = p.suffix.lower()
        if format_type == "text" or suffix == ".txt":
            return FlextResult.ok(p.read_text(encoding="utf-8"))
        if suffix in {".yml", ".yaml"}:
            return FlextResult.ok(yaml.safe_load(p.read_text(encoding="utf-8")))
        if suffix == ".json":
            return FlextResult.ok(json.loads(p.read_text(encoding="utf-8")))
        return FlextResult.fail("Unsupported file format")
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(str(e))


def flext_cli_save_file(data: object, file_path: str | Path) -> FlextResult[bool]:  # noqa: D103
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        if p.suffix.lower() in {".yml", ".yaml"}:
            p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        elif p.suffix.lower() == ".json":
            p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        else:
            p.write_text(str(data), encoding="utf-8")
        return FlextResult.ok(True)  # noqa: FBT003
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(str(e))


def flext_cli_batch_execute(  # noqa: D103
    operations: list[tuple[str, Callable[[], FlextResult[object]]]],
    *,
    stop_on_error: bool = True,
) -> FlextResult[dict[str, dict[str, object]]]:
    results: dict[str, dict[str, object]] = {}
    for name, op in operations:
        try:
            res = op()
            results[name] = {
                "success": res.success,
                "data": getattr(res, "data", None),
                "error": res.error,
            }
            if res.is_failure and stop_on_error:
                return FlextResult.fail(f"Operation {name} failed: {res.error}")
        except Exception as e:  # noqa: BLE001
            if stop_on_error:
                return FlextResult.fail(f"Operation {name} raised exception: {e}")
            results[name] = {"success": False, "error": str(e)}
    return FlextResult.ok(results)


def track(
    items: list[tuple[str, Callable[[], FlextResult[object]]]],
) -> list[tuple[str, Callable[[], FlextResult[object]]]]:
    return items
