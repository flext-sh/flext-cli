"""FLEXT CLI file operations utilities."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import c, p, r, s, t, u

if TYPE_CHECKING:
    from collections.abc import Sequence


class FlextCliFileTools(s):
    """File operations with r."""

    @staticmethod
    def ensure_dir(file_path: t.Cli.TextPath) -> p.Result[Path]:
        """Create a directory tree when missing and return the path."""
        return u.Cli.ensure_dir(Path(file_path))

    @staticmethod
    def atomic_write_text_file(
        file_path: t.Cli.TextPath, content: str
    ) -> p.Result[bool]:
        """Write text file atomically via the canonical ``u.Cli`` utility surface."""
        return u.Cli.atomic_write_text_file(file_path, content)

    @staticmethod
    def json_read_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        return u.Cli.json_read_files(Path(file_path))

    @staticmethod
    def read_text_file(file_path: t.Cli.TextPath) -> p.Result[str]:
        """Read a UTF-8 text file via the public CLI file surface."""
        return u.Cli.files_read_text(Path(file_path))

    @staticmethod
    def json_read_model[M: t.Cli.ModelLike](
        file_path: t.Cli.TextPath, model_type: t.ModelClass[M]
    ) -> p.Result[M]:
        """Read JSON into the canonical structural model-class contract."""
        return u.Cli.json_read_files_model(Path(file_path), model_type)

    @staticmethod
    def yaml_read_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        normalized_path = u.Cli.normalize_optional_text(file_path)
        if normalized_path is None:
            return r[t.JsonValue].fail(c.Cli.ERR_FILE_PATH_EMPTY)
        return u.Cli.yaml_read_files(Path(normalized_path))

    @staticmethod
    def yaml_read_model[M: t.Cli.ModelLike](
        file_path: t.Cli.TextPath, model_type: t.ModelClass[M]
    ) -> p.Result[M]:
        """Read YAML and validate it once into the requested model type."""
        return u.Cli.yaml_read_files_model(Path(file_path), model_type)

    @staticmethod
    def yaml_read_model_chain[M: t.Cli.ModelLike](
        file_paths: Sequence[t.Cli.TextPath], model_type: t.ModelClass[M]
    ) -> p.Result[M]:
        """Merge ordered YAML sources and validate the final payload once."""
        return u.Cli.yaml_read_files_model_chain(file_paths, model_type)

    @staticmethod
    def json_write_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
        options: p.Cli.JsonWriteOptions | None = None,
    ) -> p.Result[bool]:
        return u.Cli.json_write(Path(file_path), data, options=options)

    @staticmethod
    def yaml_write_file(
        file_path: t.Cli.TextPath, data: t.Cli.JsonWriteData
    ) -> p.Result[bool]:
        return u.Cli.yaml_dump(Path(file_path), data)

    @staticmethod
    def csv_write_file(
        file_path: t.Cli.TextPath, rows: t.SequenceOf[t.StrSequence]
    ) -> p.Result[bool]:
        return u.Cli.csv_write_files(Path(file_path), rows)

    @staticmethod
    def csv_read_file_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[t.StrMapping]]:
        return u.Cli.csv_read_files_with_headers(Path(file_path))

    @staticmethod
    def read_binary_file(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        return u.Cli.files_read_binary(Path(file_path))

    @staticmethod
    def write_binary_file(file_path: t.Cli.TextPath, data: bytes) -> p.Result[bool]:
        return u.Cli.files_write_binary(Path(file_path), data)

    @staticmethod
    def copy_file(
        source_path: t.Cli.TextPath, destination_path: t.Cli.TextPath
    ) -> p.Result[bool]:
        return u.Cli.files_copy(Path(source_path), Path(destination_path))

    @staticmethod
    def detect_file_format(file_path: t.Cli.TextPath) -> p.Result[str]:
        return u.Cli.files_detect_format(Path(file_path))

    @staticmethod
    def delete_path(file_path: t.Cli.TextPath) -> p.Result[bool]:
        """Delete a file or directory via the public CLI file surface."""
        return u.Cli.files_delete(Path(file_path))

    @staticmethod
    def list_directory_names(file_path: t.Cli.TextPath) -> p.Result[Sequence[str]]:
        """Return sorted child directory names for one path."""
        return u.Cli.files_list_directory_names(Path(file_path))

    @staticmethod
    def load_file_auto_dict(file_path: t.Cli.TextPath) -> p.Result[t.JsonMapping]:
        return u.Cli.files_load_auto_mapping(Path(file_path))


__all__: t.MutableSequenceOf[str] = ["FlextCliFileTools"]
