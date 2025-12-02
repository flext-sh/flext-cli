"""FLEXT CLI File Tools - Comprehensive file operation utilities.

**MODULE**: FlextCliFileTools - Single primary class for file operations
**SCOPE**: File I/O, format detection, directory operations, file search, archive operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
import zipfile
from collections.abc import Callable, Mapping
from pathlib import Path

import yaml
from flext_core import FlextResult, FlextRuntime, FlextTypes

from flext_cli.constants import FlextCliConstants


class FlextCliFileTools:
    """Unified file operations utility following FLEXT namespace pattern.

    Single class containing all stateless file operations with generalized helpers.
    """

    # ==========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # ==========================================================================

    @staticmethod
    def _execute_file_operation[T](
        operation_func: Callable[[], T],
        error_template: str,
    ) -> FlextResult[T]:
        """Generalized file operation helper with error handling."""
        try:
            return FlextResult[T].ok(operation_func())
        except Exception as e:
            return FlextResult[T].fail(error_template.format(error=e))

    @staticmethod
    def _normalize_path(file_path: str | Path) -> Path:
        """Normalize path to Path object."""
        return Path(file_path)

    @staticmethod
    def _get_encoding(encoding: str | int | None) -> str:
        """Normalize encoding to string."""
        return (
            encoding if isinstance(encoding, str) else FlextCliConstants.Encoding.UTF8
        )

    @staticmethod
    def _read_file_with_encoding(
        file_path: Path, encoding: str = FlextCliConstants.Encoding.UTF8
    ) -> str:
        """Generalized text file reader."""
        return file_path.read_text(encoding=encoding)

    @staticmethod
    def _write_file_with_encoding(
        file_path: Path, content: str, encoding: str = FlextCliConstants.Encoding.UTF8
    ) -> None:
        """Generalized text file writer."""
        file_path.write_text(content, encoding=encoding)

    @staticmethod
    def _open_file_for_reading(file_path: Path) -> io.TextIOWrapper:
        """Generalized file opener for reading."""
        return file_path.open(encoding=FlextCliConstants.Encoding.UTF8)

    @staticmethod
    def _open_file_for_writing(file_path: Path) -> io.TextIOWrapper:
        """Generalized file opener for writing."""
        return file_path.open(mode="w", encoding=FlextCliConstants.Encoding.UTF8)

    @staticmethod
    def _get_file_stat_attr(file_path: Path, attr: str) -> int | float:
        """Generalized file stat attribute getter."""
        value = getattr(file_path.stat(), attr)
        if isinstance(value, (int, float)):
            return value
        # Fallback for type safety
        return int(value) if isinstance(value, (bool, str)) else 0

    @staticmethod
    def _detect_format_from_extension(
        file_path: str | Path,
        supported_formats: dict[str, dict[str, list[str]]],
    ) -> FlextResult[str]:
        """Detect file format from extension."""
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(
            FlextCliConstants.FileToolsDefaults.EXTENSION_PREFIX
        )

        for format_name, format_info in supported_formats.items():
            if (
                FlextRuntime.is_dict_like(format_info)
                and FlextCliConstants.FileIODefaults.FORMAT_EXTENSIONS_KEY
                in format_info
            ):
                extensions = format_info[
                    FlextCliConstants.FileIODefaults.FORMAT_EXTENSIONS_KEY
                ]
                if FlextRuntime.is_list_like(extensions) and extension in extensions:
                    return FlextResult[str].ok(format_name)

        return FlextResult[str].fail(
            FlextCliConstants.FileErrorMessages.UNSUPPORTED_FORMAT_GENERIC.format(
                extension=extension
            )
        )

    @staticmethod
    def _load_json_file(file_path: str) -> FlextTypes.GeneralValueType:
        """Load JSON file content."""
        path = Path(file_path)
        with path.open(encoding=FlextCliConstants.Encoding.UTF8) as f:
            data: FlextTypes.GeneralValueType = json.load(f)
            # Type narrowing: json.load returns object, narrow to FlextTypes.GeneralValueType
            if (
                isinstance(data, (str, int, float, bool, type(None)))
                or (isinstance(data, dict) and all(isinstance(k, str) for k in data))
                or isinstance(data, list)
            ):
                return data
            # Fallback: convert to compatible type
            return str(data) if data is not None else None

    @staticmethod
    def _load_yaml_file(file_path: str) -> FlextTypes.GeneralValueType:
        """Load YAML file content."""
        path = Path(file_path)
        with path.open(encoding=FlextCliConstants.Encoding.UTF8) as f:
            data: FlextTypes.GeneralValueType = yaml.safe_load(f)
            # Type narrowing: yaml.safe_load returns object, narrow to FlextTypes.GeneralValueType
            if (
                isinstance(data, (str, int, float, bool, type(None)))
                or (isinstance(data, dict) and all(isinstance(k, str) for k in data))
                or isinstance(data, list)
            ):
                return data
            # Fallback: convert to compatible type
            return str(data) if data is not None else None

    @staticmethod
    def _save_file_by_extension(
        file_path: str | Path, data: FlextTypes.GeneralValueType
    ) -> FlextResult[bool]:
        """Save data to file based on extension."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == FlextCliConstants.FileExtensions.JSON:
            return FlextCliFileTools.write_json_file(file_path, data)

        if extension in FlextCliConstants.FileSupportedFormats.YAML_EXTENSIONS_SET:
            return FlextCliFileTools.write_yaml_file(file_path, data)

        return FlextResult[bool].fail(
            FlextCliConstants.FileErrorMessages.UNSUPPORTED_FORMAT_EXTENSION.format(
                extension=extension
            )
        )

    # ==========================================================================
    # TEXT FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_text_file(file_path: str | Path) -> FlextResult[str]:
        """Read text file."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_file_with_encoding(path),
            FlextCliConstants.ErrorMessages.TEXT_FILE_READ_FAILED,
        )

    @staticmethod
    def write_text_file(
        file_path: str | Path,
        content: str,
        encoding: str | int = FlextCliConstants.Encoding.UTF8,
    ) -> FlextResult[bool]:
        """Write text content to file."""
        path = FlextCliFileTools._normalize_path(file_path)
        validated_encoding = FlextCliFileTools._get_encoding(encoding)
        try:
            FlextCliFileTools._write_file_with_encoding(
                path, content, validated_encoding
            )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.TEXT_FILE_WRITE_FAILED.format(error=e)
            )

    # ==========================================================================
    # BINARY FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_binary_file(file_path: str | Path) -> FlextResult[bytes]:
        """Read binary file content."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.read_bytes,
            FlextCliConstants.FileErrorMessages.BINARY_READ_FAILED,
        )

    @staticmethod
    def write_binary_file(
        file_path: str | Path,
        content: bytes,
    ) -> FlextResult[bool]:
        """Write binary content to file."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            path.write_bytes(content)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.FileErrorMessages.BINARY_WRITE_FAILED.format(error=e)
            )

    # ==========================================================================
    # JSON FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_json_file(
        file_path: str | Path,
    ) -> FlextResult[FlextTypes.GeneralValueType]:
        """Read JSON file."""
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_json_file(str(file_path)),
            FlextCliConstants.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: FlextTypes.GeneralValueType,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
    ) -> FlextResult[bool]:
        """Write data to JSON file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _write_json() -> bool:
            with path.open(mode="w", encoding=FlextCliConstants.Encoding.UTF8) as f:
                json.dump(
                    data,
                    f,
                    indent=indent,
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii,
                )
            return True

        return FlextCliFileTools._execute_file_operation(
            _write_json,
            FlextCliConstants.ErrorMessages.JSON_WRITE_FAILED,
        )

    # ==========================================================================
    # YAML FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_yaml_file(
        file_path: str | Path,
    ) -> FlextResult[FlextTypes.GeneralValueType]:
        """Read YAML file."""
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_yaml_file(str(file_path)),
            FlextCliConstants.FileErrorMessages.YAML_LOAD_FAILED,
        )

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: FlextTypes.GeneralValueType,
        *,
        default_flow_style: bool | None = None,
        sort_keys: bool = False,
        allow_unicode: bool = True,
    ) -> FlextResult[bool]:
        """Write data to YAML file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _write_yaml() -> bool:
            with path.open(mode="w", encoding=FlextCliConstants.Encoding.UTF8) as f:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=default_flow_style,
                    sort_keys=sort_keys,
                    allow_unicode=allow_unicode,
                )
            return True

        return FlextCliFileTools._execute_file_operation(
            _write_yaml,
            FlextCliConstants.ErrorMessages.YAML_WRITE_FAILED,
        )

    # ==========================================================================
    # CSV FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_csv_file(file_path: str | Path) -> FlextResult[list[list[str]]]:
        """Read CSV file content."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: list(
                csv.reader(
                    path.open(
                        encoding=FlextCliConstants.Encoding.UTF8,
                        newline="",
                    )
                )
            ),
            FlextCliConstants.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def write_csv_file(
        file_path: str | Path,
        data: list[list[str]],
    ) -> FlextResult[bool]:
        """Write CSV file content."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            with path.open(
                mode="w",
                encoding=FlextCliConstants.Encoding.UTF8,
                newline="",
            ) as f:
                csv.writer(f).writerows(data)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.FileErrorMessages.CSV_WRITE_FAILED.format(error=e)
            )

    @staticmethod
    def read_csv_file_with_headers(
        file_path: str | Path,
    ) -> FlextResult[list[dict[str, str]]]:
        """Read CSV file with headers."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: list(
                csv.DictReader(
                    path.open(
                        encoding=FlextCliConstants.Encoding.UTF8,
                        newline="",
                    )
                )
            ),
            FlextCliConstants.FileErrorMessages.CSV_READ_FAILED,
        )

    # ==========================================================================
    # FILE SYSTEM OPERATIONS
    # ==========================================================================

    @staticmethod
    def file_exists(file_path: str | Path) -> FlextResult[bool]:
        """Check if file exists."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.exists,
            FlextCliConstants.FileErrorMessages.FILE_EXISTENCE_CHECK_FAILED,
        )

    @staticmethod
    def copy_file(
        source_path: str | Path,
        destination_path: str | Path,
    ) -> FlextResult[bool]:
        """Copy file from source to destination."""

        def _copy() -> bool:
            shutil.copy2(str(source_path), str(destination_path))
            return True

        return FlextCliFileTools._execute_file_operation(
            _copy,
            FlextCliConstants.ErrorMessages.FILE_COPY_FAILED,
        )

    @staticmethod
    def delete_file(file_path: str | Path) -> FlextResult[bool]:
        """Delete file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _delete() -> bool:
            path.unlink()
            return True

        return FlextCliFileTools._execute_file_operation(
            _delete,
            FlextCliConstants.FileErrorMessages.FILE_DELETION_FAILED,
        )

    @staticmethod
    def move_file(
        source: str | Path,
        destination: str | Path,
    ) -> FlextResult[bool]:
        """Move file to new location."""

        def _move() -> bool:
            shutil.move(str(source), str(destination))
            return True

        return FlextCliFileTools._execute_file_operation(
            _move,
            FlextCliConstants.FileErrorMessages.FILE_MOVE_FAILED,
        )

    @staticmethod
    def get_file_size(file_path: str | Path) -> FlextResult[int]:
        """Get file size in bytes."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: int(path.stat().st_size),
            "Failed to get file size for {file_path}: {error}",
        )

    @staticmethod
    def get_file_modified_time(file_path: str | Path) -> FlextResult[float]:
        """Get file modification time as Unix timestamp."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._get_file_stat_attr(path, "st_mtime"),
            "Failed to get modification time for {file_path}: {error}",
        )

    @staticmethod
    def get_file_permissions(file_path: str | Path) -> FlextResult[int]:
        """Get file permissions as integer (Unix-style)."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: path.stat().st_mode & 0o777,
            "Failed to get permissions for {file_path}: {error}",
        )

    @staticmethod
    def set_file_permissions(file_path: str | Path, mode: int) -> FlextResult[bool]:
        """Set file permissions."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _chmod() -> bool:
            path.chmod(mode)
            return True

        return FlextCliFileTools._execute_file_operation(
            _chmod,
            "Failed to set permissions for {file_path}: {error}",
        )

    # ==========================================================================
    # DIRECTORY OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_directory(dir_path: str | Path) -> FlextResult[bool]:
        """Create directory."""
        path = FlextCliFileTools._normalize_path(dir_path)

        def _mkdir() -> bool:
            path.mkdir(parents=True, exist_ok=True)
            return True

        return FlextCliFileTools._execute_file_operation(
            _mkdir,
            FlextCliConstants.FileErrorMessages.DIRECTORY_CREATION_FAILED,
        )

    @staticmethod
    def directory_exists(dir_path: str | Path) -> FlextResult[bool]:
        """Check if directory exists."""
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            path.is_dir,
            FlextCliConstants.FileErrorMessages.DIRECTORY_CHECK_FAILED,
        )

    @staticmethod
    def delete_directory(dir_path: str | Path) -> FlextResult[bool]:
        """Delete directory."""

        def _rmtree() -> bool:
            shutil.rmtree(str(dir_path))
            return True

        return FlextCliFileTools._execute_file_operation(
            _rmtree,
            FlextCliConstants.FileErrorMessages.DIRECTORY_DELETION_FAILED,
        )

    @staticmethod
    def list_directory(dir_path: str | Path) -> FlextResult[list[str]]:
        """List directory contents."""
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p.name) for p in path.iterdir()],
            FlextCliConstants.FileErrorMessages.DIRECTORY_LISTING_FAILED,
        )

    # ==========================================================================
    # FILE FORMAT DETECTION AND AUTO-LOADING
    # ==========================================================================

    @staticmethod
    def detect_file_format(file_path: str | Path) -> FlextResult[str]:
        """Detect file format from extension."""
        # Convert Mapping to dict for _detect_format_from_extension compatibility
        # FILE_FORMATS is Mapping[str, Mapping[str, str | tuple[str, ...]]]
        formats_dict: dict[str, dict[str, list[str]]] = {}
        for key, value in FlextCliConstants.FILE_FORMATS.items():
            # FILE_FORMATS is always Mapping, but isinstance check for type narrowing
            if isinstance(value, Mapping):
                # Convert Mapping values: tuple[str, ...] -> list[str], str -> [str]
                formats_dict[key] = {
                    k: list(v)
                    if isinstance(v, tuple)
                    else [v]
                    if isinstance(v, str)
                    else []
                    for k, v in value.items()
                }
            # Note: else branch is unreachable as FILE_FORMATS is always Mapping,
            # but kept for defensive programming and type narrowing
        return FlextCliFileTools._detect_format_from_extension(
            file_path,
            formats_dict,
        )

    @staticmethod
    def load_file_auto_detect(
        file_path: str | Path,
    ) -> FlextResult[FlextTypes.GeneralValueType]:
        """Load file with automatic format detection."""
        format_result = FlextCliFileTools.detect_file_format(file_path)
        if format_result.is_failure:
            return FlextResult[FlextTypes.GeneralValueType].fail(
                format_result.error
                or FlextCliConstants.ErrorMessages.FORMAT_DETECTION_FAILED
            )

        file_format = format_result.unwrap()
        format_loaders: dict[
            str, Callable[[], FlextResult[FlextTypes.GeneralValueType]]
        ] = {
            FlextCliConstants.FileSupportedFormats.JSON: lambda: FlextCliFileTools.read_json_file(
                file_path
            ),
            FlextCliConstants.FileSupportedFormats.YAML: lambda: FlextCliFileTools.read_yaml_file(
                file_path
            ),
        }

        loader = format_loaders.get(file_format)
        if loader:
            return loader()

        return FlextResult[FlextTypes.GeneralValueType].fail(
            FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT.format(
                format=file_format
            )
        )

    @staticmethod
    def save_file(
        file_path: str | Path,
        data: FlextTypes.GeneralValueType,
    ) -> FlextResult[bool]:
        """Save data to file with automatic format detection."""
        return FlextCliFileTools._save_file_by_extension(file_path, data)

    # ==========================================================================
    # FILE HASH OPERATIONS
    # ==========================================================================

    @staticmethod
    def calculate_file_hash(
        file_path: str | Path,
        algorithm: str = "sha256",
    ) -> FlextResult[str]:
        """Calculate file hash."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            hash_obj = hashlib.new(algorithm)
            with path.open("rb") as f:
                for chunk in iter(
                    lambda: f.read(FlextCliConstants.FileToolsDefaults.CHUNK_SIZE),
                    b"",
                ):
                    hash_obj.update(chunk)
            return FlextResult[str].ok(hash_obj.hexdigest())
        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.FileErrorMessages.HASH_CALCULATION_FAILED.format(
                    error=e
                )
            )

    @staticmethod
    def verify_file_hash(
        file_path: str | Path,
        expected_hash: str,
        algorithm: str = "sha256",
    ) -> FlextResult[bool]:
        """Verify file hash."""
        hash_result = FlextCliFileTools.calculate_file_hash(file_path, algorithm)
        if hash_result.is_failure:
            return FlextResult[bool].fail(
                hash_result.error
                or FlextCliConstants.FileErrorMessages.HASH_CALCULATION_FAILED_NO_ERROR
            )

        return FlextResult[bool].ok(hash_result.unwrap() == expected_hash)

    # ==========================================================================
    # TEMPORARY FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_temp_file() -> FlextResult[str]:
        """Create temporary file."""
        try:
            fd, path = tempfile.mkstemp()
            os.close(fd)
            return FlextResult[str].ok(path)
        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.FileErrorMessages.TEMP_FILE_CREATION_FAILED.format(
                    error=e
                )
            )

    @staticmethod
    def create_temp_directory() -> FlextResult[str]:
        """Create temporary directory."""
        return FlextCliFileTools._execute_file_operation(
            tempfile.mkdtemp,
            FlextCliConstants.FileErrorMessages.TEMP_DIR_CREATION_FAILED,
        )

    # ==========================================================================
    # ARCHIVE OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_zip_archive(
        archive_path: str | Path,
        files: list[str],
    ) -> FlextResult[bool]:
        """Create zip archive."""
        try:
            with zipfile.ZipFile(
                archive_path,
                FlextCliConstants.FileIODefaults.ZIP_WRITE_MODE,
            ) as zipf:
                for file in files:
                    zipf.write(file, Path(file).name)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.FileErrorMessages.ZIP_CREATION_FAILED.format(error=e)
            )

    @staticmethod
    def extract_zip_archive(
        archive_path: str | Path,
        extract_to: str | Path,
    ) -> FlextResult[bool]:
        """Extract zip archive."""
        try:
            with zipfile.ZipFile(
                archive_path,
                FlextCliConstants.FileIODefaults.ZIP_READ_MODE,
            ) as zipf:
                zipf.extractall(extract_to)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.FileErrorMessages.ZIP_EXTRACTION_FAILED.format(
                    error=e
                )
            )

    # ==========================================================================
    # FILE SEARCH OPERATIONS
    # ==========================================================================

    @staticmethod
    def find_files_by_pattern(
        directory: str | Path,
        pattern: str,
    ) -> FlextResult[list[str]]:
        """Find files by glob pattern."""
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p) for p in path.glob(pattern)],
            FlextCliConstants.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_name(
        directory: str | Path,
        name: str,
    ) -> FlextResult[list[str]]:
        """Find files by name."""
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [
                str(p)
                for p in path.rglob(FlextCliConstants.FileIODefaults.GLOB_PATTERN_ALL)
                if p.name == name
            ],
            FlextCliConstants.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_content(
        directory: str | Path,
        content: str,
    ) -> FlextResult[list[str]]:
        """Find files containing specific content."""
        path = FlextCliFileTools._normalize_path(directory)
        try:
            matches = []
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        text = file_path.read_text(
                            encoding=FlextCliConstants.Encoding.UTF8
                        )
                        if content in text:
                            matches.append(str(file_path))
                    except (UnicodeDecodeError, PermissionError):
                        continue
            return FlextResult[list[str]].ok(matches)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.FileErrorMessages.CONTENT_SEARCH_FAILED.format(
                    error=e
                )
            )

    # ==========================================================================
    # FORMAT INFORMATION
    # ==========================================================================

    @staticmethod
    def get_supported_formats() -> FlextResult[list[str]]:
        """Get list of supported file formats."""
        return FlextResult[list[str]].ok(
            FlextCliConstants.FileSupportedFormats.SUPPORTED_FORMATS
        )


__all__ = ["FlextCliFileTools"]
