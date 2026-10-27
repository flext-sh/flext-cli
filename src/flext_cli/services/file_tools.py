"""FLEXT CLI file operations utilities.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_cli import m, p, s, t, u


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
