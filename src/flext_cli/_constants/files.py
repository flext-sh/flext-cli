"""FLEXT CLI file and format constants.

Owns file-format detection, extension mapping, and generic file metadata
constants reused across CLI and test infrastructure.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique
from types import MappingProxyType
from typing import ClassVar

from flext_core import t

from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead


class FlextCliConstantsFiles:
    """File format and filesystem metadata constants for CLI consumers."""

    IDENTITY_COMPONENT_COUNT: ClassVar[int] = 2
    "A strict file identity is one non-negative device and inode pair."

    READ_FLAGS: ClassVar[int] = FlextCliUtilitiesAtomicFileRead.READ_FLAGS
    "Open flags for authenticated read-only descriptors of atomic files."

    @unique
    class WriteDurability(StrEnum):
        """Caller-declared durability of one atomic file publication.

        ``DURABLE`` syncs the staged inode and every changed directory before
        success. ``SCRATCH`` keeps the same atomic rename and physical checks
        but skips every ``fsync`` for throwaway trees no consumer recovers
        after a crash.
        """

        DURABLE = "durable"
        SCRATCH = "scratch"

    @unique
    class FileFormat(StrEnum):
        """Canonical file format labels."""

        AUTO = "auto"
        TEXT = "text"
        BIN = "bin"
        JSON = "json"
        YAML = "yaml"
        TOML = "toml"
        CSV = "csv"
        UNKNOWN = "unknown"

    FILE_FORMAT_AUTO: ClassVar[FileFormat] = FileFormat.AUTO
    FILE_FORMAT_TEXT: ClassVar[FileFormat] = FileFormat.TEXT
    FILE_FORMAT_BIN: ClassVar[FileFormat] = FileFormat.BIN
    FILE_FORMAT_JSON: ClassVar[FileFormat] = FileFormat.JSON
    FILE_FORMAT_YAML: ClassVar[FileFormat] = FileFormat.YAML
    FILE_FORMAT_TOML: ClassVar[FileFormat] = FileFormat.TOML
    FILE_FORMAT_CSV: ClassVar[FileFormat] = FileFormat.CSV
    FILE_FORMAT_UNKNOWN: ClassVar[FileFormat] = FileFormat.UNKNOWN

    KNOWN_FORMATS: ClassVar[frozenset[str]] = frozenset({
        FileFormat.AUTO,
        FileFormat.TEXT,
        FileFormat.BIN,
        FileFormat.JSON,
        FileFormat.YAML,
        FileFormat.CSV,
    })

    EXT_TO_FMT: ClassVar[t.StrMapping] = MappingProxyType({
        ".txt": FileFormat.TEXT,
        ".log": FileFormat.TEXT,
        ".md": FileFormat.TEXT,
        ".rst": FileFormat.TEXT,
        ".bin": FileFormat.BIN,
        ".dat": FileFormat.BIN,
        ".json": FileFormat.JSON,
        ".yaml": FileFormat.YAML,
        ".yml": FileFormat.YAML,
        ".csv": FileFormat.CSV,
        ".tsv": FileFormat.CSV,
    })

    DEFAULT_FILENAME: ClassVar[str] = "file"
    DEFAULT_EXTENSION: ClassVar[str] = ".txt"
    DEFAULT_JSON_INDENT: ClassVar[int] = 2
    DEFAULT_CSV_DELIMITER: ClassVar[str] = ","

    SIZE_UNITS: ClassVar[t.StrSequence] = ("B", "KB", "MB", "GB", "TB", "PB")
    SIZE_THRESHOLD: ClassVar[int] = 1024

    @classmethod
    def format_size(cls, size: int) -> str:
        """Return a human-readable byte size string.

        Args:
            size: Size in bytes.

        Returns:
            Human-readable size like ``"1.2 KB"``.

        """
        for unit in cls.SIZE_UNITS:
            if size < cls.SIZE_THRESHOLD:
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
            size //= cls.SIZE_THRESHOLD
        return f"{size:.1f} PB"

    @classmethod
    def format_for_extension(cls, extension: str) -> str:
        """Return the canonical format label for a file extension.

        Args:
            extension: File extension, e.g. ``".json"``.

        Returns:
            Format label or ``c.Cli.FileFormat.TEXT`` as the default.

        """
        format_name = cls.EXT_TO_FMT.get(extension.lower())
        return format_name if isinstance(format_name, str) else cls.FileFormat.TEXT


__all__: list[str] = ["FlextCliConstantsFiles"]
