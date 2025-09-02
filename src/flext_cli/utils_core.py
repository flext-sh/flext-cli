"""Core setup utilities (class-only) for CLI tests using new patterns."""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, cast, overload

from flext_core import FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli.cli_utils import FlextCliUtils
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.helpers import FlextCliHelper
from flext_cli.utils_output import FlextCliOutput


class QuickSetupContext(TypedDict, total=False):
    """Quick setup context."""

    console: Console
    config: FlextCliConfig


class FlextCliUtilsCore:
    """Class-based utilities for core CLI (no module-level helpers)."""

    @classmethod
    def quick_setup(
        cls,
        _options: dict[str, object] | None = None,
    ) -> FlextResult[QuickSetupContext]:
        """Provide a minimal context with console and config for tests."""
        try:
            _ = _options
            config = FlextCliConfig()
            console = Console()
            return FlextResult[QuickSetupContext].ok({
                "console": console,
                "config": config,
            })
        except Exception as e:
            return FlextResult[QuickSetupContext].fail(f"CLI setup failed: {e}")

    # ---------------- Internal helpers (class-scoped) ----------------
    @staticmethod
    def _current_timestamp() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _generate_session_id() -> str:
        return uuid.uuid4().hex[:8]

    @staticmethod
    def _load_config_file(path: Path) -> FlextResult[dict[str, object]]:
        try:
            if not path.exists():
                return FlextResult[dict[str, object]].fail("Config file not found")
            text = path.read_text(encoding=FlextCliConstants.DEFAULT_ENCODING)
            if path.suffix.lower() in {".yaml", ".yml"}:
                import importlib

                yaml_mod = importlib.import_module("yaml")
                data = yaml_mod.safe_load(text)
            elif path.suffix.lower() == ".json":
                data = json.loads(text)
            else:
                return FlextResult[dict[str, object]].fail("Unsupported config format")
            if not isinstance(data, dict):
                return FlextResult[dict[str, object]].fail("Invalid config data")
            return FlextResult[dict[str, object]].ok(data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    @staticmethod
    def _load_env_overrides() -> dict[str, object]:
        overrides: dict[str, object] = {}
        for k, v in os.environ.items():
            if not k.startswith("FLEXT_"):
                continue
            key = k.removeprefix("FLEXT_").lower()
            if v.lower() in {"true", "false"}:
                overrides[key] = v.lower() == "true"
            elif v.isdigit():
                overrides[key] = int(v)
            else:
                overrides[key] = v
        return overrides

    # ---------------- Public utility operations ----------------
    @classmethod
    def auto_config(
        cls, profile: str, files: list[str]
    ) -> FlextResult[dict[str, object]]:
        try:
            selected: Path | None = None
            for f in files:
                p = Path(f)
                if p.exists():
                    selected = p
                    break
            base: dict[str, object] = {}
            if selected is not None:
                res = cls._load_config_file(selected)
                if res.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        res.error or "Load error"
                    )
                base = res.value
            env = cls._load_env_overrides()
            # merge
            merged = {**base, **env}
            merged.setdefault("profile", profile)
            merged.setdefault("debug", False)
            merged["config_source"] = str(selected) if selected else None
            merged["env_overrides"] = env
            merged["loaded_at"] = cls._current_timestamp()
            return FlextResult[dict[str, object]].ok(merged)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    @classmethod
    def validate_all(
        cls, validations: dict[str, tuple[object, str]]
    ) -> FlextResult[dict[str, object]]:
        try:
            helper = FlextCliHelper(quiet=True)
            out: dict[str, object] = {}
            for key, (value, vtype) in validations.items():
                if vtype == "email":
                    res = helper.flext_cli_validate_email(str(value))
                    if res.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Validation failed for {key}: {res.error}"
                        )
                    out[key] = res.value
                elif vtype == "url":
                    res = helper.flext_cli_validate_url(str(value))
                    if res.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Validation failed for {key}: {res.error}"
                        )
                    out[key] = res.value
                elif vtype == "path":
                    res = helper.flext_cli_validate_path(str(value), must_exist=True)
                    if res.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Validation failed for {key}: {res.error}"
                        )
                    out[key] = Path(res.value)
                elif vtype == "file":
                    res = helper.flext_cli_validate_path(
                        str(value), must_exist=True, must_be_file=True
                    )
                    if res.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Validation failed for {key}: {res.error}"
                        )
                    out[key] = Path(res.value)
                elif vtype == "dir":
                    res = helper.flext_cli_validate_path(
                        str(value), must_exist=True, must_be_dir=True
                    )
                    if res.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Validation failed for {key}: {res.error}"
                        )
                    out[key] = Path(res.value)
                elif vtype == "filename":
                    out[key] = helper.sanitize_filename(str(value))
                else:
                    return FlextResult[dict[str, object]].fail(
                        "Unknown validation type"
                    )
            return FlextResult[dict[str, object]].ok(out)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    @classmethod
    def require_all(cls, confirmations: list[tuple[str, bool]]) -> FlextResult[bool]:
        try:
            helper = FlextCliHelper(quiet=True)
            for message, default in confirmations:
                res = helper.flext_cli_confirm(message, default=default)
                if res.is_failure:
                    return FlextResult[bool].fail(res.error or "Confirmation failed")
                if not res.value:
                    value: bool = False
                    return FlextResult[bool].ok(value)
            all_ok: bool = True
            return FlextResult[bool].ok(all_ok)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    @classmethod
    def load_file(
        cls, path: str | Path, format_type: str | None = None
    ) -> FlextResult[object]:
        p = Path(path)
        if not p.exists():
            return FlextResult[object].fail("File not found")
        if format_type == "text":
            try:
                return FlextResult[object].ok(
                    p.read_text(encoding=FlextCliConstants.DEFAULT_ENCODING)
                )
            except Exception as e:
                return FlextResult[object].fail(str(e))
        return FlextCliUtils.load_data_file(p)

    @classmethod
    def save_file(
        cls, data: object, path: str | Path, fmt: str | None = None
    ) -> FlextResult[None]:
        from flext_cli.cli_utils import FlextCliData
        from flext_cli.typings import FlextCliOutputFormat as O

        p = Path(path)
        hint = (fmt or p.suffix.lstrip(".").lower() or "json").lower()
        fmt_enum = {
            "json": O.JSON,
            "yaml": O.YAML,
            "yml": O.YAML,
            "csv": O.CSV,
            "plain": O.PLAIN,
            "text": O.PLAIN,
            "table": O.TABLE,
        }.get(hint, O.JSON)
        # Cast to FlextCliData for type compatibility
        typed_data: FlextCliData = data
        return FlextCliUtils.save_data_file(typed_data, p, fmt_enum)

    @classmethod
    def create_table(
        cls, data: object, *, title: str | None = None, columns: list[str] | None = None
    ) -> Table:
        table = Table(title=title)
        if isinstance(data, list):
            if not data:
                table.add_column("No Data")
                return table
            first = data[0]
            if isinstance(first, dict):
                keys = columns or list(first.keys())
                for k in keys:
                    table.add_column(str(k))
                for row in data:
                    table.add_row(*[str(row.get(k, "")) for k in keys])
            else:
                table.add_column("Value")
                for v in data:
                    table.add_row(str(v))
        elif isinstance(data, dict):
            keys = columns or list(data.keys())
            for k in keys:
                table.add_column(str(k))
            table.add_row(*[str(data.get(k, "")) for k in keys])
        else:
            table.add_column("Value")
            table.add_row(str(data))
        return table

    @classmethod
    def output_data(
        cls, data: object, fmt: str, *, console: Console | None = None
    ) -> FlextResult[None]:
        try:
            c = console or Console()
            if fmt == "json":
                c.print(FlextCliOutput.format_json(data))
            elif fmt == "yaml":
                c.print(FlextCliOutput.format_yaml(data))
            elif fmt == "table":
                table_res = FlextCliUtils.create_table(data)
                if table_res.is_failure:
                    return FlextResult[None].fail(table_res.error or "Table error")
                c.print(table_res.value)
            else:
                c.print(str(data))
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    @classmethod
    def batch_execute(
        cls,
        operations: list[tuple[str, Callable[[], FlextResult[object]]]] | list[object],
        operation: Callable[[object], FlextResult[object]] | None = None,
        *,
        stop_on_error: bool = True,
    ) -> FlextResult[dict[str, dict[str, object]] | list[object]]:
        try:
            # Mode A: list items + operation(item) -> list of results
            if (
                operation is not None
                and operations
                and not isinstance(operations[0], tuple)
            ):
                seq = cls.track(operations)
                out: list[object] = []
                for item in seq:
                    res = operation(item)
                    if res.is_failure and stop_on_error:
                        return FlextResult[
                            dict[str, dict[str, object]] | list[object]
                        ].fail(res.error or "Operation failed")
                    out.append(res.value if res.is_success else None)
                return FlextResult[dict[str, dict[str, object]] | list[object]].ok(out)

            # Mode B: list of named zero-arg operations -> result map
            results: dict[str, dict[str, object]] = {}
            # Type cast for mypy - we know this is the correct type in this branch
            named_ops: list[tuple[str, Callable[[], FlextResult[object]]]] = cast(
                "list[tuple[str, Callable[[], FlextResult[object]]]]", operations
            )
            named_seq = cls.track(named_ops)
            for name, op in named_seq:
                try:
                    res = op()
                except Exception as e:  # capture unforeseen exceptions
                    return FlextResult[
                        dict[str, dict[str, object]] | list[object]
                    ].fail(f"Operation {name} raised exception: {e}")
                if isinstance(res, FlextResult) and res.is_success:
                    results[name] = {"success": True, "result": res.value}
                else:
                    err = res.error if isinstance(res, FlextResult) else "Unknown error"
                    results[name] = {"success": False, "error": err}
                    if stop_on_error:
                        return FlextResult[
                            dict[str, dict[str, object]] | list[object]
                        ].fail(f"Operation {name} failed: {err}")
            return FlextResult[dict[str, dict[str, object]] | list[object]].ok(results)
        except Exception as e:
            return FlextResult[dict[str, dict[str, object]] | list[object]].fail(str(e))

    # Patch point used by some tests to simulate progress iteration
    @overload
    @staticmethod
    def track(
        seq: list[tuple[str, Callable[[], FlextResult[object]]]],
    ) -> list[tuple[str, Callable[[], FlextResult[object]]]]: ...

    @overload
    @staticmethod
    def track(
        seq: list[object],
    ) -> list[object]: ...

    @staticmethod
    def track(
        seq: list[tuple[str, Callable[[], FlextResult[object]]]] | list[object],
    ) -> list[tuple[str, Callable[[], FlextResult[object]]]] | list[object]:
        return seq


__all__ = ["FlextCliUtilsCore", "QuickSetupContext"]
