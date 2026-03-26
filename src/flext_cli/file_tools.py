"""FLEXT CLI file operations utilities."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TextIO

from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_cli import c, m, t

_JSON_OBJECT_ADAPTER: TypeAdapter[t.Cli.JsonValue] = TypeAdapter(t.Cli.JsonValue)


class FlextCliFileTools:
    """File operations for JSON with r."""

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
    def read_json_file(file_path: str | Path) -> r[t.Cli.JsonValue]:

        def _load() -> t.Cli.JsonValue:
            raw = Path(file_path).read_text(encoding=c.DEFAULT_ENCODING)
            parsed = _JSON_OBJECT_ADAPTER.validate_json(raw)
            if parsed is None:
                msg = "JSON load returned None"
                raise ValueError(msg)
            return parsed

        return FlextCliFileTools._execute_file_operation(
            _load,
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
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
            payload: t.Cli.JsonValue = _JSON_OBJECT_ADAPTER.validate_python(payload_raw)
        except ValidationError:
            payload = str(payload_raw)

        def _writer(f: TextIO) -> None:
            f.write(
                _JSON_OBJECT_ADAPTER.dump_json(payload, indent=indent).decode("utf-8"),
            )

        return FlextCliFileTools._write_structured_file(
            file_path,
            _writer,
            c.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )


__all__ = ["FlextCliFileTools"]
