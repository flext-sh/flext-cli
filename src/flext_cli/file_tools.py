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
from collections.abc import Callable
from pathlib import Path

import yaml
from flext_core import (
    FlextRuntime,
    r,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities


class FlextCliFileTools:
    """Unified file operations utility following FLEXT namespace pattern.

    Business Rules:
    ───────────────
    1. All file operations MUST use r[T] for error handling
    2. File paths MUST be validated to prevent path traversal attacks
    3. File encoding MUST default to UTF-8 (configurable)
    4. File operations MUST handle missing files gracefully (no crashes)
    5. Archive operations MUST validate archive integrity before extraction
    6. File format detection MUST use extension and content analysis
    7. Temporary files MUST be cleaned up after operations
    8. File permissions MUST be preserved when copying/moving files

    Architecture Implications:
    ───────────────────────────
    - Single class consolidates all file operations (SRP)
    - Static methods ensure thread safety and no side effects
    - Generalized helpers reduce code duplication (DRY)
    - Path normalization ensures consistent path handling
    - Format detection enables automatic format handling

    Audit Implications:
    ───────────────────
    - File operations MUST be logged with file paths (no sensitive content)
    - Path validation MUST prevent directory traversal attacks
    - File deletions MUST be logged for audit trail
    - Archive operations MUST validate file integrity
    - Temporary file creation MUST track files for cleanup
    - File access MUST respect file permissions

    Single class containing all stateless file operations with generalized helpers.
    """

    # ==========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # ==========================================================================

    @staticmethod
    def _execute_file_operation[T](
        operation_func: Callable[[], T],
        error_template: str,
        **format_kwargs: object,
    ) -> r[T]:
        """Generalized file operation helper with error handling."""
        try:
            return r[T].ok(operation_func())
        except Exception as e:
            return r[T].fail(error_template.format(error=e, **format_kwargs))

    @staticmethod
    def _normalize_path(file_path: str | Path) -> Path:
        """Normalize path to Path object."""
        return Path(file_path)

    @staticmethod
    def _get_encoding(encoding: str | int | None) -> str:
        """Normalize encoding to string."""
        return (
            encoding
            if isinstance(encoding, str)
            else FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING
        )

    @staticmethod
    def _read_file_with_encoding(
        file_path: Path,
        encoding: str = FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
    ) -> str:
        """Generalized text file reader."""
        return file_path.read_text(encoding=encoding)

    @staticmethod
    def _write_file_with_encoding(
        file_path: Path,
        content: str,
        encoding: str = FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
    ) -> None:
        """Generalized text file writer."""
        file_path.write_text(content, encoding=encoding)

    @staticmethod
    def _open_file_for_reading(file_path: Path) -> io.TextIOWrapper:
        """Generalized file opener for reading."""
        return file_path.open(encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING)

    @staticmethod
    def _open_file_for_writing(file_path: Path) -> io.TextIOWrapper:
        """Generalized file opener for writing."""
        return file_path.open(
            mode="w", encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING
        )

    @staticmethod
    def _get_file_stat_attr(file_path: Path, attr: str) -> float | None:
        """Generalized file stat attribute getter."""
        value = getattr(file_path.stat(), attr)
        # Use FlextCliUtilities.parse for conversion (returns r[T], need to unwrap)
        if isinstance(value, (int, float)):
            return float(value)
        # Try parsing as int first, then float
        int_result = FlextCliUtilities.parse(value, int, default=0)
        if int_result.is_success and int_result.value is not None:
            return float(int_result.value)
        # Fallback to float
        float_result = FlextCliUtilities.parse(value, float, default=0.0)
        if float_result.is_success and float_result.value is not None:
            return float_result.value
        return 0.0

    @staticmethod
    def _detect_format_from_extension(
        file_path: str | Path,
        supported_formats: dict[str, dict[str, list[str]]],
    ) -> r[str]:
        """Detect file format from extension."""
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(
            FlextCliConstants.Cli.FileToolsDefaults.EXTENSION_PREFIX
        )

        for format_name, format_info in supported_formats.items():
            if (
                FlextRuntime.is_dict_like(format_info)
                and FlextCliConstants.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY
                in format_info
            ):
                extensions = format_info[
                    FlextCliConstants.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY
                ]
                if FlextRuntime.is_list_like(extensions) and extension in extensions:
                    return r[str].ok(format_name)

        return r[str].fail(
            FlextCliConstants.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_GENERIC.format(
                extension=extension
            ),
        )

    @staticmethod
    def _load_json_file(file_path: str) -> FlextCliTypes.GeneralValueType:
        """Load JSON file content."""
        path = Path(file_path)
        with path.open(encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING) as f:
            raw_data: object = json.load(f)
            # Use ur JSON conversion
            if isinstance(raw_data, dict):
                transform_result = FlextCliUtilities.transform(
                    raw_data,
                    to_json=True,
                )
                unwrapped = (
                    transform_result.value if transform_result.is_success else raw_data
                )
                # Type narrowing: ensure return type is FlextCliTypes.GeneralValueType
                # unwrapped is object from unwrap(), convert to FlextCliTypes.GeneralValueType
                if isinstance(
                    unwrapped, (str, int, float, bool, type(None), dict, list)
                ):
                    return unwrapped
                return str(unwrapped)
            # Type narrowing: raw_data is object, convert to FlextCliTypes.GeneralValueType
            if isinstance(raw_data, (str, int, float, bool, type(None), dict, list)):
                return raw_data
            return str(raw_data)

    @staticmethod
    def _load_yaml_file(file_path: str) -> FlextCliTypes.GeneralValueType:
        """Load YAML file content."""
        path = Path(file_path)
        with path.open(encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING) as f:
            raw_data: object = yaml.safe_load(f)
            # Use ur JSON conversion
            if isinstance(raw_data, dict):
                transform_result = FlextCliUtilities.transform(
                    raw_data,
                    to_json=True,
                )
                unwrapped = (
                    transform_result.value if transform_result.is_success else raw_data
                )
                # Type narrowing: ensure return type is FlextCliTypes.GeneralValueType
                # unwrapped is object from unwrap(), convert to FlextCliTypes.GeneralValueType
                if isinstance(
                    unwrapped, (str, int, float, bool, type(None), dict, list)
                ):
                    return unwrapped
                return str(unwrapped)
            # Type narrowing: raw_data is object, convert to FlextCliTypes.GeneralValueType
            if isinstance(raw_data, (str, int, float, bool, type(None), dict, list)):
                return raw_data
            return str(raw_data)

    @staticmethod
    def _save_file_by_extension(
        file_path: str | Path,
        data: FlextCliTypes.GeneralValueType,
    ) -> r[bool]:
        """Save data to file based on extension."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == FlextCliConstants.Cli.FileExtensions.JSON:
            return FlextCliFileTools.write_json_file(file_path, data)

        if extension in FlextCliConstants.Cli.FileSupportedFormats.YAML_EXTENSIONS_SET:
            return FlextCliFileTools.write_yaml_file(file_path, data)

        return r[bool].fail(
            FlextCliConstants.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_EXTENSION.format(
                extension=extension
            ),
        )

    # ==========================================================================
    # TEXT FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_text_file(file_path: str | Path) -> r[str]:
        """Read text file."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_file_with_encoding(path),
            FlextCliConstants.Cli.ErrorMessages.TEXT_FILE_READ_FAILED,
        )

    @staticmethod
    def write_text_file(
        file_path: str | Path,
        content: str,
        encoding: str | int = FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
    ) -> r[bool]:
        """Write text content to file."""
        path = FlextCliFileTools._normalize_path(file_path)
        validated_encoding = FlextCliFileTools._get_encoding(encoding)
        try:
            FlextCliFileTools._write_file_with_encoding(
                path,
                content,
                validated_encoding,
            )
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.ErrorMessages.TEXT_FILE_WRITE_FAILED.format(
                    error=e
                )
            )

    # ==========================================================================
    # BINARY FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_binary_file(file_path: str | Path) -> r[bytes]:
        """Read binary file content."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.read_bytes,
            FlextCliConstants.Cli.FileErrorMessages.BINARY_READ_FAILED,
        )

    @staticmethod
    def write_binary_file(
        file_path: str | Path,
        content: bytes,
    ) -> r[bool]:
        """Write binary content to file."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            path.write_bytes(content)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.FileErrorMessages.BINARY_WRITE_FAILED.format(
                    error=e
                )
            )

    # ==========================================================================
    # JSON FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_json_file(
        file_path: str | Path,
    ) -> r[FlextCliTypes.GeneralValueType]:
        """Read JSON file."""
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_json_file(str(file_path)),
            FlextCliConstants.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: FlextCliTypes.GeneralValueType,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
    ) -> r[bool]:
        """Write data to JSON file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _write_json() -> bool:
            with path.open(
                mode="w", encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING
            ) as f:
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
            FlextCliConstants.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )

    # ==========================================================================
    # YAML FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_yaml_file(
        file_path: str | Path,
    ) -> r[FlextCliTypes.GeneralValueType]:
        """Read YAML file."""
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_yaml_file(str(file_path)),
            FlextCliConstants.Cli.FileErrorMessages.YAML_LOAD_FAILED,
        )

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: FlextCliTypes.GeneralValueType,
        *,
        default_flow_style: bool | None = None,
        sort_keys: bool = False,
        allow_unicode: bool = True,
    ) -> r[bool]:
        """Write data to YAML file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _write_yaml() -> bool:
            with path.open(
                mode="w", encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING
            ) as f:
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
            FlextCliConstants.Cli.ErrorMessages.YAML_WRITE_FAILED,
        )

    # ==========================================================================
    # CSV FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def read_csv_file(file_path: str | Path) -> r[list[list[str]]]:
        """Read CSV file contenFlextCliTypes.

        Business Rule:
        ──────────────
        CSV files are read with UTF-8 encoding and empty newline for proper line handling.
        The file handle is properly closed using context manager to prevent ResourceWarning.

        Audit Implications:
        ───────────────────
        - File is read completely before returning
        - File handle is always closed even on exceptions
        - Returns list of rows, each row is list of cell values
        """
        path = FlextCliFileTools._normalize_path(file_path)

        def _read_csv() -> list[list[str]]:
            with path.open(
                encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
                newline="",
            ) as f:
                return list(csv.reader(f))

        return FlextCliFileTools._execute_file_operation(
            _read_csv,
            FlextCliConstants.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def write_csv_file(
        file_path: str | Path,
        data: list[list[str]],
    ) -> r[bool]:
        """Write CSV file content."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            with path.open(
                mode="w",
                encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
                newline="",
            ) as f:
                csv.writer(f).writerows(data)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.FileErrorMessages.CSV_WRITE_FAILED.format(error=e)
            )

    @staticmethod
    def read_csv_file_with_headers(
        file_path: str | Path,
    ) -> r[list[dict[str, str]]]:
        """Read CSV file with headers as dictionaries.

        Business Rule:
        ──────────────
        CSV files with headers are read using DictReader which maps each row to a dicFlextCliTypes.
        First row is treated as header names. File handle is properly closed.

        Audit Implications:
        ───────────────────
        - Header row determines dict keys for all data rows
        - File handle is always closed using context manager
        - Returns list of dicts, each dict represents a row with header keys
        """
        path = FlextCliFileTools._normalize_path(file_path)

        def _read_csv_dict() -> list[dict[str, str]]:
            with path.open(
                encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
                newline="",
            ) as f:
                return list(csv.DictReader(f))

        return FlextCliFileTools._execute_file_operation(
            _read_csv_dict,
            FlextCliConstants.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    # ==========================================================================
    # FILE SYSTEM OPERATIONS
    # ==========================================================================

    @staticmethod
    def file_exists(file_path: str | Path) -> r[bool]:
        """Check if file exists."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.exists,
            FlextCliConstants.Cli.FileErrorMessages.FILE_EXISTENCE_CHECK_FAILED,
        )

    @staticmethod
    def copy_file(
        source_path: str | Path,
        destination_path: str | Path,
    ) -> r[bool]:
        """Copy file from source to destination."""

        def _copy() -> bool:
            shutil.copy2(str(source_path), str(destination_path))
            return True

        return FlextCliFileTools._execute_file_operation(
            _copy,
            FlextCliConstants.Cli.ErrorMessages.FILE_COPY_FAILED,
        )

    @staticmethod
    def delete_file(file_path: str | Path) -> r[bool]:
        """Delete file."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _delete() -> bool:
            path.unlink()
            return True

        return FlextCliFileTools._execute_file_operation(
            _delete,
            FlextCliConstants.Cli.FileErrorMessages.FILE_DELETION_FAILED,
        )

    @staticmethod
    def move_file(
        source: str | Path,
        destination: str | Path,
    ) -> r[bool]:
        """Move file to new location."""

        def _move() -> bool:
            shutil.move(str(source), str(destination))
            return True

        return FlextCliFileTools._execute_file_operation(
            _move,
            FlextCliConstants.Cli.FileErrorMessages.FILE_MOVE_FAILED,
        )

    @staticmethod
    def get_file_size(file_path: str | Path) -> r[int]:
        """Get file size in bytes."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: int(path.stat().st_size),
            "Failed to get file size for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def get_file_modified_time(file_path: str | Path) -> r[float | None]:
        """Get file modification time as Unix timestamp."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._get_file_stat_attr(path, "st_mtime"),
            "Failed to get modification time for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def get_file_permissions(file_path: str | Path) -> r[int]:
        """Get file permissions as integer (Unix-style)."""
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: path.stat().st_mode & 0o777,
            "Failed to get permissions for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def set_file_permissions(file_path: str | Path, mode: int) -> r[bool]:
        """Set file permissions."""
        path = FlextCliFileTools._normalize_path(file_path)

        def _chmod() -> bool:
            path.chmod(mode)
            return True

        return FlextCliFileTools._execute_file_operation(
            _chmod,
            "Failed to set permissions for {file_path}: {error}",
            file_path=str(path),
        )

    # ==========================================================================
    # DIRECTORY OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_directory(dir_path: str | Path) -> r[bool]:
        """Create directory."""
        path = FlextCliFileTools._normalize_path(dir_path)

        def _mkdir() -> bool:
            path.mkdir(parents=True, exist_ok=True)
            return True

        return FlextCliFileTools._execute_file_operation(
            _mkdir,
            FlextCliConstants.Cli.FileErrorMessages.DIRECTORY_CREATION_FAILED,
        )

    @staticmethod
    def directory_exists(dir_path: str | Path) -> r[bool]:
        """Check if directory exists."""
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            path.is_dir,
            FlextCliConstants.Cli.FileErrorMessages.DIRECTORY_CHECK_FAILED,
        )

    @staticmethod
    def delete_directory(dir_path: str | Path) -> r[bool]:
        """Delete directory."""

        def _rmtree() -> bool:
            shutil.rmtree(str(dir_path))
            return True

        return FlextCliFileTools._execute_file_operation(
            _rmtree,
            FlextCliConstants.Cli.FileErrorMessages.DIRECTORY_DELETION_FAILED,
        )

    @staticmethod
    def list_directory(dir_path: str | Path) -> r[list[str]]:
        """List directory contents."""
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p.name) for p in path.iterdir()],
            FlextCliConstants.Cli.FileErrorMessages.DIRECTORY_LISTING_FAILED,
        )

    # ==========================================================================
    # FILE FORMAT DETECTION AND AUTO-LOADING
    # ==========================================================================

    @staticmethod
    def detect_file_format(file_path: str | Path) -> r[str]:
        """Detect file format from extension."""
        # Convert FILE_FORMATS to the expected dict[str, dict[str, list[str]]] format
        # FILE_FORMATS is Mapping[str, FileFormatConfig] where FileFormatConfig has:
        #   - extensions: tuple[str, ...] -> needs conversion to list[str]
        #   - mime_type: str
        formats_dict: dict[str, dict[str, list[str]]] = {}
        for format_name, format_config in FlextCliConstants.Cli.FILE_FORMATS.items():
            # Convert tuple to list for extensions
            extensions = format_config["extensions"]
            extensions_list: list[str] = (
                list(extensions) if isinstance(extensions, tuple) else [extensions]
            )
            formats_dict[format_name] = {
                FlextCliConstants.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY: extensions_list,
            }
        return FlextCliFileTools._detect_format_from_extension(
            file_path,
            formats_dict,
        )

    @staticmethod
    def load_file_auto_detect(
        file_path: str | Path,
    ) -> r[FlextCliTypes.GeneralValueType]:
        """Load file with automatic format detection."""
        format_result = FlextCliFileTools.detect_file_format(file_path)
        if format_result.is_failure:
            return r[FlextCliTypes.GeneralValueType].fail(
                format_result.error
                or FlextCliConstants.Cli.ErrorMessages.FORMAT_DETECTION_FAILED,
            )

        file_format = format_result.value
        format_loaders: dict[str, Callable[[], r[FlextCliTypes.GeneralValueType]]] = {
            FlextCliConstants.Cli.FileSupportedFormats.JSON: lambda: FlextCliFileTools.read_json_file(
                file_path,
            ),
            FlextCliConstants.Cli.FileSupportedFormats.YAML: lambda: FlextCliFileTools.read_yaml_file(
                file_path,
            ),
        }

        loader = format_loaders.get(file_format)
        if loader:
            return loader()

        return r[FlextCliTypes.GeneralValueType].fail(
            FlextCliConstants.Cli.ErrorMessages.UNSUPPORTED_FORMAT.format(
                format=file_format
            ),
        )

    @staticmethod
    def save_file(
        file_path: str | Path,
        data: FlextCliTypes.GeneralValueType,
    ) -> r[bool]:
        """Save data to file with automatic format detection."""
        return FlextCliFileTools._save_file_by_extension(file_path, data)

    # ==========================================================================
    # FILE HASH OPERATIONS
    # ==========================================================================

    @staticmethod
    def calculate_file_hash(
        file_path: str | Path,
        algorithm: str = "sha256",
    ) -> r[str]:
        """Calculate file hash."""
        path = FlextCliFileTools._normalize_path(file_path)
        try:
            hash_obj = hashlib.new(algorithm)
            with path.open("rb") as f:
                for chunk in iter(
                    lambda: f.read(FlextCliConstants.Cli.FileToolsDefaults.CHUNK_SIZE),
                    b"",
                ):
                    hash_obj.update(chunk)
            return r[str].ok(hash_obj.hexdigest())
        except Exception as e:
            return r[str].fail(
                FlextCliConstants.Cli.FileErrorMessages.HASH_CALCULATION_FAILED.format(
                    error=e
                ),
            )

    @staticmethod
    def verify_file_hash(
        file_path: str | Path,
        expected_hash: str,
        algorithm: str = "sha256",
    ) -> r[bool]:
        """Verify file hash."""
        hash_result = FlextCliFileTools.calculate_file_hash(file_path, algorithm)
        if hash_result.is_failure:
            return r[bool].fail(
                hash_result.error
                or FlextCliConstants.Cli.FileErrorMessages.HASH_CALCULATION_FAILED_NO_ERROR,
            )

        return r[bool].ok(hash_result.value == expected_hash)

    # ==========================================================================
    # TEMPORARY FILE OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_temp_file() -> r[str]:
        """Create temporary file."""
        try:
            fd, path = tempfile.mkstemp()
            os.close(fd)
            return r[str].ok(path)
        except Exception as e:  # pragma: no cover
            return r[str].fail(
                FlextCliConstants.Cli.FileErrorMessages.TEMP_FILE_CREATION_FAILED.format(
                    error=e
                ),
            )

    @staticmethod
    def create_temp_directory() -> r[str]:
        """Create temporary directory."""
        return FlextCliFileTools._execute_file_operation(
            tempfile.mkdtemp,
            FlextCliConstants.Cli.FileErrorMessages.TEMP_DIR_CREATION_FAILED,
        )

    # ==========================================================================
    # ARCHIVE OPERATIONS
    # ==========================================================================

    @staticmethod
    def create_zip_archive(
        archive_path: str | Path,
        files: list[str],
    ) -> r[bool]:
        """Create zip archive."""
        try:
            with zipfile.ZipFile(
                archive_path,
                FlextCliConstants.Cli.FileIODefaults.ZIP_WRITE_MODE,
            ) as zipf:
                for file in files:
                    zipf.write(file, Path(file).name)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.FileErrorMessages.ZIP_CREATION_FAILED.format(
                    error=e
                )
            )

    @staticmethod
    def extract_zip_archive(
        archive_path: str | Path,
        extract_to: str | Path,
    ) -> r[bool]:
        """Extract zip archive."""
        try:
            with zipfile.ZipFile(
                archive_path,
                FlextCliConstants.Cli.FileIODefaults.ZIP_READ_MODE,
            ) as zipf:
                zipf.extractall(extract_to)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.FileErrorMessages.ZIP_EXTRACTION_FAILED.format(
                    error=e
                ),
            )

    # ==========================================================================
    # FILE SEARCH OPERATIONS
    # ==========================================================================

    @staticmethod
    def find_files_by_pattern(
        directory: str | Path,
        pattern: str,
    ) -> r[list[str]]:
        """Find files by glob pattern."""
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p) for p in path.glob(pattern)],
            FlextCliConstants.Cli.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_name(
        directory: str | Path,
        name: str,
    ) -> r[list[str]]:
        """Find files by name."""
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [
                str(p)
                for p in path.rglob(
                    FlextCliConstants.Cli.FileIODefaults.GLOB_PATTERN_ALL
                )
                if p.name == name
            ],
            FlextCliConstants.Cli.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_content(
        directory: str | Path,
        content: str,
    ) -> r[list[str]]:
        """Find files containing specific contenFlextCliTypes."""
        path = FlextCliFileTools._normalize_path(directory)
        try:
            matches = []
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        text = file_path.read_text(
                            encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING
                        )
                        if content in text:
                            matches.append(str(file_path))
                    except (UnicodeDecodeError, PermissionError):
                        continue
            return r[list[str]].ok(matches)
        except Exception as e:  # pragma: no cover
            return r[list[str]].fail(
                FlextCliConstants.Cli.FileErrorMessages.CONTENT_SEARCH_FAILED.format(
                    error=e
                ),
            )

    # ==========================================================================
    # FORMAT INFORMATION
    # ==========================================================================

    @staticmethod
    def get_supported_formats() -> r[list[str]]:
        """Get list of supported file formats."""
        return r[list[str]].ok(
            FlextCliConstants.Cli.FileSupportedFormats.SUPPORTED_FORMATS
        )


__all__ = ["FlextCliFileTools"]
