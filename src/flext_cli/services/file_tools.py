"""FLEXT CLI file operations utilities.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_cli import c, m, p, r, s, t, u


class FlextCliFileTools(s[p.Cli.RuntimeStatus]):
    """File operations with r."""

    @staticmethod
    def read_json_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        """Read one JSON file into a validated JSON-compatible value.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            The resulting ``p.Result[t.JsonValue]``.

        """
        return u.Cli.files_read_json(Path(file_path))

    @staticmethod
    def read_text_file(file_path: t.Cli.TextPath) -> p.Result[str]:
        """Read a UTF-8 text file via the public CLI file surface.

        Args:
            file_path: Path to the text file to read.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return u.Cli.files_read_text(Path(file_path))

    @staticmethod
    def read_json_model[M: t.Cli.ModelLike](
        file_path: t.Cli.TextPath,
        model_type: t.ModelClass[M],
    ) -> p.Result[M]:
        """Read JSON into the canonical structural model-class contract.

        Args:
            file_path: Path to the JSON file to read.
            model_type: Model class that the parsed payload must validate into.

        Returns:
            The resulting ``p.Result[M]``.

        """
        return u.Cli.files_read_json_model(Path(file_path), model_type)

    @staticmethod
    def read_yaml_file(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        """Read one YAML file into a validated JSON-compatible value.

        Args:
            file_path: Path to the YAML file to read.

        Returns:
            The resulting ``p.Result[t.JsonValue]``.

        """
        normalized_path = u.Cli.normalize_optional_text(file_path)
        if normalized_path is None:
            return r[t.JsonValue].fail(c.Cli.ERR_FILE_PATH_EMPTY)
        return u.Cli.files_read_yaml(Path(normalized_path))

    @staticmethod
    def read_yaml_model[M: t.Cli.ModelLike](
        file_path: t.Cli.TextPath,
        model_type: t.ModelClass[M],
    ) -> p.Result[M]:
        """Read YAML and validate it once into the requested model type.

        Args:
            file_path: Path to the YAML file to read.
            model_type: Model class that the parsed payload must validate into.

        Returns:
            The resulting ``p.Result[M]``.

        """
        return u.Cli.files_read_yaml_model(Path(file_path), model_type)

    @staticmethod
    def read_yaml_model_chain[M: t.Cli.ModelLike](
        file_paths: Sequence[t.Cli.TextPath],
        model_type: t.ModelClass[M],
    ) -> p.Result[M]:
        """Merge ordered YAML sources and validate the final payload once.

        Args:
            file_paths: Ordered paths whose YAML payloads merge front to back.
            model_type: Model class that the merged payload must validate into.

        Returns:
            The resulting ``p.Result[M]``.

        """
        return u.Cli.files_read_yaml_model_chain(file_paths, model_type)

    @staticmethod
    def write_json_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
        options: m.Cli.JsonWriteOptions | None = None,
    ) -> p.Result[bool]:
        """Write JSON data using the canonical serialization options.

        Args:
            file_path: Path of the JSON file to write.
            data: JSON-compatible payload to serialize.
            options: Optional serialization options; defaults apply when omitted.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.json_write(Path(file_path), data, options=options)

    @staticmethod
    def write_yaml_file(
        file_path: t.Cli.TextPath,
        data: t.Cli.JsonWriteData,
    ) -> p.Result[bool]:
        """Write JSON-compatible data as YAML.

        Args:
            file_path: Path of the YAML file to write.
            data: JSON-compatible payload to serialize.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.yaml_dump(Path(file_path), data)

    @staticmethod
    def write_csv_file(
        file_path: t.Cli.TextPath,
        rows: t.SequenceOf[t.StrSequence],
    ) -> p.Result[bool]:
        """Write rows to a CSV file.

        Args:
            file_path: Path of the CSV file to write.
            rows: Ordered rows of string cells to write.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.files_write_csv(Path(file_path), rows)

    @staticmethod
    def read_csv_file_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[t.StrMapping]]:
        """Read CSV rows as string mappings keyed by the header row.

        Args:
            file_path: Path to the CSV file to read.

        Returns:
            The resulting ``p.Result[t.SequenceOf[t.StrMapping]]``.

        """
        return u.Cli.files_read_csv_with_headers(Path(file_path))

    @staticmethod
    def read_binary_file(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        """Read a file as bytes.

        Args:
            file_path: Path to the file to read.

        Returns:
            The resulting ``p.Result[bytes]``.

        """
        return u.Cli.files_read_binary(Path(file_path))

    @staticmethod
    def write_binary_file(file_path: t.Cli.TextPath, data: bytes) -> p.Result[bool]:
        """Write bytes to a file.

        Args:
            file_path: Path of the file to write.
            data: Bytes to write.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.files_write_binary(Path(file_path), data)

    @staticmethod
    def copy_file(
        source_path: t.Cli.TextPath,
        destination_path: t.Cli.TextPath,
    ) -> p.Result[bool]:
        """Copy one file to another path.

        Args:
            source_path: Path of the file to copy.
            destination_path: Path that receives the copied file.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.files_copy(Path(source_path), Path(destination_path))

    @staticmethod
    def detect_file_format(file_path: t.Cli.TextPath) -> p.Result[str]:
        """Detect the supported serialization format for a file.

        Args:
            file_path: Path whose format is detected.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return u.Cli.files_detect_format(Path(file_path))

    @staticmethod
    def delete_path(file_path: t.Cli.TextPath) -> p.Result[bool]:
        """Delete a file or directory via the public CLI file surface.

        Args:
            file_path: Path to delete.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.files_delete(Path(file_path))

    @staticmethod
    def list_directory_names(file_path: t.Cli.TextPath) -> p.Result[Sequence[str]]:
        """Return sorted child directory names for one path.

        Args:
            file_path: Directory path to list.

        Returns:
            Sorted child directory names for one path.

        """
        return u.Cli.files_list_directory_names(Path(file_path))

    @staticmethod
    def load_file_auto_dict(file_path: t.Cli.TextPath) -> p.Result[t.JsonMapping]:
        """Load a supported file format as a JSON-compatible mapping.

        Args:
            file_path: Path to the file to load.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        return u.Cli.files_load_auto_mapping(Path(file_path))


__all__: t.MutableSequenceOf[str] = ["FlextCliFileTools"]
