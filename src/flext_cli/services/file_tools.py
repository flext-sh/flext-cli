"""FLEXT CLI file operations utilities."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from flext_cli import FlextCliServiceBase, p, r, t, u


class FlextCliFileTools(FlextCliServiceBase):
    """File operations with r."""

    @staticmethod
    def delete_file(file_path: t.Cli.TextPath) -> r[bool]:
        return u.Cli.files_delete(file_path)

    @staticmethod
    def read_text_file(file_path: t.Cli.TextPath) -> r[str]:
        return u.Cli.files_read_text(file_path)

    @staticmethod
    def write_text_file(file_path: t.Cli.TextPath, content: str) -> r[bool]:
        return u.Cli.files_write_text(file_path, content)

    @staticmethod
    def atomic_write_text_file(file_path: t.Cli.TextPath, content: str) -> r[bool]:
        """Write text file atomically via the canonical ``u.Cli`` utility surface."""
        result = u.Cli.atomic_write_text_file(file_path, content)
        if result.failure:
            return r[bool].fail(
                result.error or "Text write failed",
            )
        return result

    @staticmethod
    def read_json_file(file_path: t.Cli.TextPath) -> r[t.Cli.JsonValue]:
        return u.Cli.files_read_json(file_path)

    @staticmethod
    def read_json_model[M: BaseModel](
        file_path: t.Cli.TextPath,
        model_type: type[M],
    ) -> r[M]:
        """Read JSON file directly into a Pydantic model via model_validate_json.

        Uses pydantic-core Rust path (no intermediate dict) — ~3x faster than
        json.loads + model_validate.
        """
        return u.Cli.files_read_json_model(file_path, model_type)

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
        return u.Cli.files_write_json_model(
            file_path,
            model,
            indent=indent,
            by_alias=by_alias,
            exclude_none=exclude_none,
        )

    @staticmethod
    def read_yaml_file(file_path: t.Cli.TextPath) -> r[t.Cli.JsonValue]:
        return u.Cli.files_read_yaml(file_path)

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
        return u.Cli.files_write_csv(file_path, rows)

    @staticmethod
    def read_csv_file_with_headers(
        file_path: t.Cli.TextPath,
    ) -> r[Sequence[t.StrMapping]]:
        return u.Cli.files_read_csv_with_headers(file_path)

    @staticmethod
    def read_binary_file(file_path: t.Cli.TextPath) -> r[bytes]:
        return u.Cli.files_read_binary(file_path)

    @staticmethod
    def write_binary_file(file_path: t.Cli.TextPath, data: bytes) -> r[bool]:
        return u.Cli.files_write_binary(file_path, data)

    @staticmethod
    def copy_file(
        source_path: t.Cli.TextPath,
        destination_path: t.Cli.TextPath,
    ) -> r[bool]:
        return u.Cli.files_copy(source_path, destination_path)

    @staticmethod
    def detect_file_format(file_path: t.Cli.TextPath) -> r[str]:
        return u.Cli.files_detect_format(file_path)

    @staticmethod
    def load_file_auto_dict(file_path: t.Cli.TextPath) -> t.Cli.JsonMappingResult:
        return u.Cli.files_load_auto_mapping(file_path)


__all__: list[str] = ["FlextCliFileTools"]
