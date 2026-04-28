"""FLEXT CLI file operations utilities."""

from __future__ import annotations

from collections.abc import (
    Sequence,
)
from pathlib import Path

from flext_cli import FlextCliServiceBase, m, p, r, t, u


class FlextCliFileTools(FlextCliServiceBase):
    """File operations with r."""

    @staticmethod
    def atomic_write_text_file(
        file_path: t.Cli.TextPath, content: str
    ) -> p.Result[bool]:
        """Write text file atomically via the canonical ``u.Cli`` utility surface."""
        result = u.Cli.atomic_write_text_file(file_path, content)
        if result.failure:
            return r[bool].fail(
                result.error or "Text write failed",
            )
        return result

    @staticmethod
    def read_json_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        return u.Cli.files_read_json(Path(file_path))

    @staticmethod
    def read_json_model[M: m.BaseModel](
        file_path: t.Cli.TextPath,
        model_type: type[M],
    ) -> p.Result[M]:
        """Read JSON file directly into a Pydantic model via model_validate_json."""
        return u.Cli.files_read_json_model(Path(file_path), model_type)

    @staticmethod
    def read_yaml_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        normalized_path = u.Cli.normalize_optional_text(file_path)
        if normalized_path is None:
            return r[t.JsonValue].fail("File path must be non-empty")
        return u.Cli.files_read_yaml(Path(normalized_path))

    @staticmethod
    def write_json_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
        options: m.Cli.JsonWriteOptions | None = None,
    ) -> p.Result[bool]:
        payload_raw = data.data if isinstance(data, p.Cli.DisplayData) else data
        return u.Cli.json_write(
            Path(file_path),
            u.Cli.normalize_json_value(payload_raw),
            options=options,
        )

    @staticmethod
    def write_yaml_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
    ) -> p.Result[bool]:
        payload_raw = data.data if isinstance(data, p.Cli.DisplayData) else data
        payload: t.JsonValue = u.Cli.normalize_json_value(payload_raw)
        return u.Cli.yaml_dump(Path(file_path), payload)

    @staticmethod
    def write_csv_file(
        file_path: t.Cli.TextPath,
        rows: Sequence[t.StrSequence],
    ) -> p.Result[bool]:
        return u.Cli.files_write_csv(Path(file_path), rows)

    @staticmethod
    def read_csv_file_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[Sequence[t.StrMapping]]:
        return u.Cli.files_read_csv_with_headers(Path(file_path))

    @staticmethod
    def read_binary_file(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        return u.Cli.files_read_binary(Path(file_path))

    @staticmethod
    def write_binary_file(file_path: t.Cli.TextPath, data: bytes) -> p.Result[bool]:
        return u.Cli.files_write_binary(Path(file_path), data)

    @staticmethod
    def copy_file(
        source_path: t.Cli.TextPath,
        destination_path: t.Cli.TextPath,
    ) -> p.Result[bool]:
        return u.Cli.files_copy(
            Path(source_path),
            Path(destination_path),
        )

    @staticmethod
    def detect_file_format(file_path: t.Cli.TextPath) -> p.Result[str]:
        return u.Cli.files_detect_format(Path(file_path))

    @staticmethod
    def load_file_auto_dict(file_path: t.Cli.TextPath) -> p.Result[t.JsonMapping]:
        return u.Cli.files_load_auto_mapping(Path(file_path))


__all__: t.MutableSequenceOf[str] = ["FlextCliFileTools"]
