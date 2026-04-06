"""FLEXT CLI file operations utilities."""

from __future__ import annotations

import csv
import shutil
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from flext_cli import c, p, r, s, t, u


class FlextCliFileTools(s):
    """File operations with r."""

    @staticmethod
    def _execute_file_operation[T](
        operation_func: t.Cli.NullaryOperation[T],
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
    def _run_bool_operation[T](
        operation_func: t.Cli.NullaryOperation[T],
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
        file_path: t.Cli.TextPath,
        writer: t.Cli.TextStreamWriter,
        error_template: str,
    ) -> r[bool]:
        path = Path(file_path)

        def _write() -> bool:
            with path.open(mode="w", encoding=c.Cli.Encoding.DEFAULT) as f:
                writer(f)
            return True

        return FlextCliFileTools._execute_file_operation(_write, error_template)

    @staticmethod
    def delete_file(file_path: t.Cli.TextPath) -> r[bool]:
        path = Path(file_path)
        return FlextCliFileTools._run_bool_operation(
            path.unlink,
            c.Cli.FileErrorMessages.FILE_DELETION_FAILED,
        )

    @staticmethod
    def read_text_file(file_path: t.Cli.TextPath) -> r[str]:
        return FlextCliFileTools._execute_file_operation(
            lambda: Path(file_path).read_text(encoding=c.Cli.Encoding.DEFAULT),
            "Text read failed: {error}",
        )

    @staticmethod
    def write_text_file(file_path: t.Cli.TextPath, content: str) -> r[bool]:

        def _write() -> bool:
            Path(file_path).write_text(content, encoding=c.Cli.Encoding.DEFAULT)
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            "Text write failed: {error}",
        )

    @staticmethod
    def atomic_write_text_file(file_path: t.Cli.TextPath, content: str) -> r[bool]:
        """Write text file atomically via the canonical ``u.Cli`` utility surface."""
        result = u.Cli.atomic_write_text_file(file_path, content)
        if result.is_failure:
            return r[bool].fail(
                result.error or "Text write failed",
            )
        return result

    @staticmethod
    def read_json_file(file_path: t.Cli.TextPath) -> r[t.Cli.JsonValue]:

        def _load() -> t.Cli.JsonValue:
            raw = Path(file_path).read_text(encoding=c.Cli.Encoding.DEFAULT)
            return t.Cli.JSON_VALUE_ADAPTER.validate_json(raw)

        return FlextCliFileTools._execute_file_operation(
            _load,
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def read_json_model[M: BaseModel](
        file_path: t.Cli.TextPath,
        model_type: type[M],
    ) -> r[M]:
        """Read JSON file directly into a Pydantic model via model_validate_json.

        Uses pydantic-core Rust path (no intermediate dict) — ~3x faster than
        json.loads + model_validate.
        """

        def _load() -> M:
            raw = Path(file_path).read_bytes()
            return model_type.model_validate_json(raw, strict=False)

        return FlextCliFileTools._execute_file_operation(
            _load,
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def write_json_model(
        file_path: t.Cli.TextPath,
        model: BaseModel,
        indent: int = 2,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> r[bool]:
        """Write a Pydantic model directly to JSON via model_dump_json.

        Type-safe: accepts only BaseModel, serializes via Rust path.
        """

        def _write() -> bool:
            json_str = model.model_dump_json(
                indent=indent,
                by_alias=by_alias,
                exclude_none=exclude_none,
            )
            Path(file_path).write_text(json_str, encoding=c.Cli.Encoding.DEFAULT)
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            c.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )

    @staticmethod
    def read_yaml_file(file_path: t.Cli.TextPath) -> r[t.Cli.JsonValue]:
        result = u.Cli.yaml_safe_load(Path(file_path))
        if result.is_failure:
            return r[t.Cli.JsonValue].fail(result.error or "YAML load failed")
        validated: t.Cli.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_python(
            result.value,
        )
        return r[t.Cli.JsonValue].ok(validated)

    @staticmethod
    def write_json_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
    ) -> r[bool]:
        payload_raw: t.RecursiveContainer | Sequence[t.ContainerMapping] = (
            data.data if isinstance(data, p.Cli.DisplayData) else data
        )
        return u.Cli.json_write(
            Path(file_path),
            u.Cli.normalize_json_value(payload_raw),
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
            indent=indent,
        )

    @staticmethod
    def write_yaml_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
    ) -> r[bool]:
        payload_raw: t.RecursiveContainer | Sequence[t.ContainerMapping] = (
            data.data if isinstance(data, p.Cli.DisplayData) else data
        )
        payload: t.Cli.JsonValue = u.Cli.normalize_json_value(payload_raw)
        return u.Cli.yaml_dump(Path(file_path), payload)

    @staticmethod
    def write_csv_file(
        file_path: t.Cli.TextPath,
        rows: Sequence[t.StrSequence],
    ) -> r[bool]:

        def _write() -> bool:
            with Path(file_path).open(
                mode="w",
                encoding=c.Cli.Encoding.DEFAULT,
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
        file_path: t.Cli.TextPath,
    ) -> r[Sequence[t.StrMapping]]:

        def _load() -> Sequence[t.StrMapping]:
            with Path(file_path).open(
                encoding=c.Cli.Encoding.DEFAULT,
                newline="",
            ) as f:
                return [dict(row) for row in csv.DictReader(f)]

        return FlextCliFileTools._execute_file_operation(
            _load,
            "CSV read failed: {error}",
        )

    @staticmethod
    def read_binary_file(file_path: t.Cli.TextPath) -> r[bytes]:
        return FlextCliFileTools._execute_file_operation(
            lambda: Path(file_path).read_bytes(),
            "Binary read failed: {error}",
        )

    @staticmethod
    def write_binary_file(file_path: t.Cli.TextPath, data: bytes) -> r[bool]:

        def _write() -> bool:
            Path(file_path).write_bytes(data)
            return True

        return FlextCliFileTools._execute_file_operation(
            _write,
            "Binary write failed: {error}",
        )

    @staticmethod
    def copy_file(
        source_path: t.Cli.TextPath,
        destination_path: t.Cli.TextPath,
    ) -> r[bool]:

        def _copy() -> bool:
            shutil.copy2(source_path, destination_path)
            return True

        return FlextCliFileTools._execute_file_operation(
            _copy,
            "File copy failed: {error}",
        )

    @staticmethod
    def detect_file_format(file_path: t.Cli.TextPath) -> r[str]:
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
    def load_file_auto_dict(file_path: t.Cli.TextPath) -> t.Cli.JsonMappingResult:
        path = Path(file_path)
        if path.suffix.lower() == ".json":
            result = FlextCliFileTools.read_json_file(path)
        elif path.suffix.lower() in {".yaml", ".yml"}:
            result = FlextCliFileTools.read_yaml_file(path)
        else:
            return r[t.Cli.JsonMapping].fail(
                f"Unsupported format: {path.suffix or '<none>'}",
            )
        if result.is_failure:
            return r[t.Cli.JsonMapping].fail(
                result.error or "Auto load failed",
            )
        payload = result.value
        if not isinstance(payload, dict):
            return r[t.Cli.JsonMapping].fail(
                "Auto-detected file must contain a mapping",
            )
        normalized_payload: t.Cli.JsonMapping = {
            str(key): u.Cli.normalize_json_value(value)
            for key, value in payload.items()
        }
        return r[t.Cli.JsonMapping].ok(normalized_payload)


__all__ = ["FlextCliFileTools"]
