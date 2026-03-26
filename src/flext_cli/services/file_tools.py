"""FLEXT CLI file operations utilities."""

from __future__ import annotations

import csv
import shutil
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TextIO

import yaml
from flext_core import r
from pydantic import ValidationError

from flext_cli import FlextCliServiceBase, c, m, t, u


class FlextCliFileTools(FlextCliServiceBase):
    """File operations with r."""

    @staticmethod
    def _execute_file_operation[T](
        operation_func: Callable[[], T],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> r[T]:
        try:
            return r[T].ok(operation_func())
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as exc:
            return r[T].fail(error_template.format(error=exc, **format_kwargs))

    @staticmethod
    def _run_bool_operation(
        operation_func: Callable[[], t.Cli.JsonValue],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> r[bool]:

        def _run() -> bool:
            _ = operation_func()
            return True

        return FlextCliFileTools._execute_file_operation(
            _run,
            error_template,
            **format_kwargs,
        )

    @staticmethod
    def _write_structured_file(
        file_path: str | Path,
        writer: Callable[[TextIO], None],
        error_template: str,
    ) -> r[bool]:
        path = Path(file_path)

        def _write() -> bool:
            with path.open(mode="w", encoding=c.DEFAULT_ENCODING) as f:
                writer(f)
            return True

        return FlextCliFileTools._execute_file_operation(_write, error_template)

    @staticmethod
    def delete_file(file_path: str | Path) -> r[bool]:
        path = Path(file_path)
        return FlextCliFileTools._run_bool_operation(
            path.unlink,
            c.Cli.FileErrorMessages.FILE_DELETION_FAILED,
        )

    @staticmethod
    def read_text_file(file_path: str | Path) -> r[str]:
        return FlextCliFileTools._execute_file_operation(
            lambda: Path(file_path).read_text(encoding=c.DEFAULT_ENCODING),
            "Text read failed: {error}",
        )

    @staticmethod
    def write_text_file(file_path: str | Path, content: str) -> r[bool]:

        def _write() -> bool:
            Path(file_path).write_text(content, encoding=c.DEFAULT_ENCODING)
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            "Text write failed: {error}",
        )

    @staticmethod
    def read_json_file(file_path: str | Path) -> r[t.Cli.JsonValue]:

        def _load() -> t.Cli.JsonValue:
            raw = Path(file_path).read_text(encoding=c.DEFAULT_ENCODING)
            parsed = t.Cli.JSON_OBJECT_ADAPTER.validate_json(raw)
            if parsed is None:
                msg = "JSON load returned None"
                raise ValueError(msg)
            return parsed

        return FlextCliFileTools._execute_file_operation(
            _load,
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def read_yaml_file(file_path: str | Path) -> r[t.Cli.JsonValue]:

        def _load() -> t.Cli.JsonValue:
            raw = Path(file_path).read_text(encoding=c.DEFAULT_ENCODING)
            return t.Cli.JSON_OBJECT_ADAPTER.validate_python(yaml.safe_load(raw))

        return FlextCliFileTools._execute_file_operation(
            _load,
            "YAML load failed: {error}",
        )

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: t.Cli.JsonValue | m.Cli.DisplayData,
        indent: int = 2,
    ) -> r[bool]:
        payload_raw: t.Cli.JsonValue = (
            data.data if isinstance(data, m.Cli.DisplayData) else data
        )
        try:
            payload: t.Cli.JsonValue = t.Cli.JSON_OBJECT_ADAPTER.validate_python(
                payload_raw
            )
        except ValidationError:
            payload = str(payload_raw)

        def _writer(f: TextIO) -> None:
            f.write(
                t.Cli.JSON_OBJECT_ADAPTER.dump_json(payload, indent=indent).decode(
                    c.DEFAULT_ENCODING,
                ),
            )

        return FlextCliFileTools._write_structured_file(
            file_path,
            _writer,
            c.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: t.Cli.JsonValue | m.Cli.DisplayData,
    ) -> r[bool]:
        payload_raw: t.Cli.JsonValue = (
            data.data if isinstance(data, m.Cli.DisplayData) else data
        )
        try:
            payload: t.Cli.JsonValue = t.Cli.JSON_OBJECT_ADAPTER.validate_python(
                payload_raw
            )
        except ValidationError:
            payload = str(payload_raw)

        def _writer(f: TextIO) -> None:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

        return FlextCliFileTools._write_structured_file(
            file_path,
            _writer,
            "YAML write failed: {error}",
        )

    @staticmethod
    def write_csv_file(
        file_path: str | Path,
        rows: Sequence[t.StrSequence],
    ) -> r[bool]:

        def _write() -> bool:
            with Path(file_path).open(
                mode="w",
                encoding=c.DEFAULT_ENCODING,
                newline="",
            ) as f:
                writer = csv.writer(f)
                for row in rows:
                    writer.writerow(list(row))
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            "CSV write failed: {error}",
        )

    @staticmethod
    def read_csv_file_with_headers(
        file_path: str | Path,
    ) -> r[Sequence[Mapping[str, str]]]:

        def _load() -> Sequence[Mapping[str, str]]:
            with Path(file_path).open(
                encoding=c.DEFAULT_ENCODING,
                newline="",
            ) as f:
                return [dict(row) for row in csv.DictReader(f)]

        return FlextCliFileTools._execute_file_operation(
            _load,
            "CSV read failed: {error}",
        )

    @staticmethod
    def read_binary_file(file_path: str | Path) -> r[bytes]:
        return FlextCliFileTools._execute_file_operation(
            lambda: Path(file_path).read_bytes(),
            "Binary read failed: {error}",
        )

    @staticmethod
    def write_binary_file(file_path: str | Path, data: bytes) -> r[bool]:

        def _write() -> bool:
            Path(file_path).write_bytes(data)
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            "Binary write failed: {error}",
        )

    @staticmethod
    def copy_file(source_path: str | Path, destination_path: str | Path) -> r[bool]:

        def _copy() -> bool:
            shutil.copy2(source_path, destination_path)
            return True

        return FlextCliFileTools._execute_file_operation(
            _copy,
            "File copy failed: {error}",
        )

    @staticmethod
    def detect_file_format(file_path: str | Path) -> r[str]:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".json":
            return r[str].ok("json")
        if suffix in {".yaml", ".yml"}:
            return r[str].ok("yaml")
        if suffix == ".csv":
            return r[str].ok("csv")
        if suffix in {".txt", ".log"}:
            return r[str].ok("text")
        if suffix:
            return r[str].fail(f"Unsupported format: {suffix}")
        return r[str].fail("Unable to detect file format without an extension")

    @staticmethod
    def load_file_auto_dict(file_path: str | Path) -> r[Mapping[str, t.Cli.JsonValue]]:
        path = Path(file_path)
        if path.suffix.lower() == ".json":
            result = FlextCliFileTools.read_json_file(path)
        elif path.suffix.lower() in {".yaml", ".yml"}:
            result = FlextCliFileTools.read_yaml_file(path)
        else:
            return r[Mapping[str, t.Cli.JsonValue]].fail(
                f"Unsupported format: {path.suffix or '<none>'}",
            )
        if result.is_failure:
            return r[Mapping[str, t.Cli.JsonValue]].fail(
                result.error or "Auto load failed",
            )
        payload = result.value
        if not isinstance(payload, Mapping):
            return r[Mapping[str, t.Cli.JsonValue]].fail(
                "Auto-detected file must contain a mapping",
            )
        return r[Mapping[str, t.Cli.JsonValue]].ok(
            {
                str(key): u.Cli.normalize_json_value(value)
                for key, value in payload.items()
            },
        )


__all__ = ["FlextCliFileTools"]
