"""FLEXT CLI file operations utilities."""

from __future__ import annotations

# ruff: noqa: D101, D102
import csv
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

import yaml
from flext_core import FlextRuntime, r

from flext_cli.constants import c
from flext_cli.typings import t
from flext_cli.utilities import u


class FlextCliFileTools:
    @staticmethod
    def _execute_file_operation[T](
        operation_func: Callable[[], T],
        error_template: str,
        **format_kwargs: t.GeneralValueType,
    ) -> r[T]:
        try:
            return r[T].ok(operation_func())
        except Exception as e:
            return r[T].fail(error_template.format(error=e, **format_kwargs))

    @staticmethod
    def _run_bool_operation(
        operation_func: Callable[[], object],
        error_template: str,
        **format_kwargs: t.GeneralValueType,
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
    def _normalize_path(file_path: str | Path) -> Path:
        return Path(file_path)

    @staticmethod
    def _get_encoding(encoding: str | int | None) -> str:
        return (
            encoding if isinstance(encoding, str) else c.Cli.Utilities.DEFAULT_ENCODING
        )

    @staticmethod
    def _get_file_stat_attr(file_path: Path, attr: str) -> float | None:
        if attr == "st_mtime":
            return float(file_path.stat().st_mtime)
        return 0.0

    @staticmethod
    def _detect_format_from_extension(
        file_path: str | Path,
        supported_formats: dict[str, dict[str, list[str]]],
    ) -> r[str]:
        extension = (
            Path(file_path)
            .suffix.lower()
            .lstrip(c.Cli.FileToolsDefaults.EXTENSION_PREFIX)
        )
        for format_name, format_info in supported_formats.items():
            if (
                FlextRuntime.is_dict_like(format_info)
                and c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY in format_info
            ):
                extensions = format_info[c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY]
                if FlextRuntime.is_list_like(extensions) and extension in extensions:
                    return r[str].ok(format_name)
        return r[str].fail(
            c.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_GENERIC.format(
                extension=extension
            ),
        )

    @staticmethod
    def _load_json_file(file_path: str) -> t.GeneralValueType:
        with Path(file_path).open(encoding=c.Cli.Utilities.DEFAULT_ENCODING) as f:
            loaded = json.load(f)
        if isinstance(loaded, dict | list | str | int | float | bool) or loaded is None:
            raw_data: t.GeneralValueType = loaded
        else:
            raw_data = None
        if isinstance(raw_data, dict):
            return u.transform(raw_data, to_json=True).map_or(raw_data)
        return raw_data

    @staticmethod
    def _load_yaml_file(file_path: str) -> t.GeneralValueType:
        with Path(file_path).open(encoding=c.Cli.Utilities.DEFAULT_ENCODING) as f:
            loaded = yaml.safe_load(f)
        if isinstance(loaded, dict | list | str | int | float | bool) or loaded is None:
            raw_data: t.GeneralValueType = loaded
        else:
            raw_data = None
        if isinstance(raw_data, dict):
            return u.transform(raw_data, to_json=True).map_or(raw_data)
        return raw_data

    @staticmethod
    def _save_file_by_extension(
        file_path: str | Path, data: t.GeneralValueType
    ) -> r[bool]:
        extension = Path(file_path).suffix.lower()
        if extension == c.Cli.FileExtensions.JSON:
            return FlextCliFileTools.write_json_file(file_path, data)
        if extension in c.Cli.FileSupportedFormats.YAML_EXTENSIONS_SET:
            return FlextCliFileTools.write_yaml_file(file_path, data)
        return r[bool].fail(
            c.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_EXTENSION.format(
                extension=extension
            ),
        )

    @staticmethod
    def _write_structured_file(
        file_path: str | Path,
        writer: Callable[[TextIO], None],
        error_template: str,
    ) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)

        def _write() -> bool:
            with path.open(mode="w", encoding=c.Cli.Utilities.DEFAULT_ENCODING) as f:
                writer(f)
            return True
        return FlextCliFileTools._execute_file_operation(_write, error_template)

    @staticmethod
    def _read_csv_rows(file_path: Path) -> list[list[str]]:
        with file_path.open(encoding=c.Cli.Utilities.DEFAULT_ENCODING, newline="") as f:
            return list(csv.reader(f))

    @staticmethod
    def _read_csv_dict_rows(file_path: Path) -> list[dict[str, str]]:
        with file_path.open(encoding=c.Cli.Utilities.DEFAULT_ENCODING, newline="") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def read_text_file(file_path: str | Path) -> r[str]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: path.read_text(encoding=c.Cli.Utilities.DEFAULT_ENCODING),
            c.Cli.ErrorMessages.TEXT_FILE_READ_FAILED,
        )

    @staticmethod
    def write_text_file(
        file_path: str | Path,
        content: str,
        encoding: str | int = c.Cli.Utilities.DEFAULT_ENCODING,
    ) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: path.write_text(
                content,
                encoding=FlextCliFileTools._get_encoding(encoding),
            ),
            c.Cli.ErrorMessages.TEXT_FILE_WRITE_FAILED,
        )

    @staticmethod
    def read_binary_file(file_path: str | Path) -> r[bytes]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.read_bytes,
            c.Cli.FileErrorMessages.BINARY_READ_FAILED,
        )

    @staticmethod
    def write_binary_file(file_path: str | Path, content: bytes) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: path.write_bytes(content),
            c.Cli.FileErrorMessages.BINARY_WRITE_FAILED,
        )

    @staticmethod
    def read_json_file(file_path: str | Path) -> r[t.GeneralValueType]:
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_json_file(str(file_path)),
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: t.GeneralValueType,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
    ) -> r[bool]:
        return FlextCliFileTools._write_structured_file(
            file_path,
            lambda f: json.dump(
                data,
                f,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
            ),
            c.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )

    @staticmethod
    def read_yaml_file(file_path: str | Path) -> r[t.GeneralValueType]:
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_yaml_file(str(file_path)),
            c.Cli.FileErrorMessages.YAML_LOAD_FAILED,
        )

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: t.GeneralValueType,
        *,
        default_flow_style: bool | None = None,
        sort_keys: bool = False,
        allow_unicode: bool = True,
    ) -> r[bool]:
        return FlextCliFileTools._write_structured_file(
            file_path,
            lambda f: yaml.safe_dump(
                data,
                f,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=allow_unicode,
            ),
            c.Cli.ErrorMessages.YAML_WRITE_FAILED,
        )

    @staticmethod
    def read_csv_file(file_path: str | Path) -> r[list[list[str]]]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_csv_rows(path),
            c.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def write_csv_file(file_path: str | Path, data: list[list[str]]) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)

        def _write_csv() -> object:
            with path.open(
                mode="w", encoding=c.Cli.Utilities.DEFAULT_ENCODING, newline=""
            ) as f:
                csv.writer(f).writerows(data)
        return FlextCliFileTools._run_bool_operation(
            _write_csv,
            c.Cli.FileErrorMessages.CSV_WRITE_FAILED,
        )

    @staticmethod
    def read_csv_file_with_headers(file_path: str | Path) -> r[list[dict[str, str]]]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_csv_dict_rows(path),
            c.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def file_exists(file_path: str | Path) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            path.exists,
            c.Cli.FileErrorMessages.FILE_EXISTENCE_CHECK_FAILED,
        )

    @staticmethod
    def copy_file(source_path: str | Path, destination_path: str | Path) -> r[bool]:
        return FlextCliFileTools._run_bool_operation(
            lambda: shutil.copy2(str(source_path), str(destination_path)),
            c.Cli.ErrorMessages.FILE_COPY_FAILED,
        )

    @staticmethod
    def delete_file(file_path: str | Path) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._run_bool_operation(
            path.unlink,
            c.Cli.FileErrorMessages.FILE_DELETION_FAILED,
        )

    @staticmethod
    def move_file(source: str | Path, destination: str | Path) -> r[bool]:
        return FlextCliFileTools._run_bool_operation(
            lambda: shutil.move(str(source), str(destination)),
            c.Cli.FileErrorMessages.FILE_MOVE_FAILED,
        )

    @staticmethod
    def get_file_size(file_path: str | Path) -> r[int]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: int(path.stat().st_size),
            "Failed to get file size for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def get_file_modified_time(file_path: str | Path) -> r[float | None]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._get_file_stat_attr(path, "st_mtime"),
            "Failed to get modification time for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def get_file_permissions(file_path: str | Path) -> r[int]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: path.stat().st_mode & 0o777,
            "Failed to get permissions for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def set_file_permissions(file_path: str | Path, mode: int) -> r[bool]:
        path = FlextCliFileTools._normalize_path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: path.chmod(mode),
            "Failed to set permissions for {file_path}: {error}",
            file_path=str(path),
        )

    @staticmethod
    def create_directory(dir_path: str | Path) -> r[bool]:
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: path.mkdir(parents=True, exist_ok=True),
            c.Cli.FileErrorMessages.DIRECTORY_CREATION_FAILED,
        )

    @staticmethod
    def directory_exists(dir_path: str | Path) -> r[bool]:
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            path.is_dir,
            c.Cli.FileErrorMessages.DIRECTORY_CHECK_FAILED,
        )

    @staticmethod
    def delete_directory(dir_path: str | Path) -> r[bool]:
        return FlextCliFileTools._run_bool_operation(
            lambda: shutil.rmtree(str(dir_path)),
            c.Cli.FileErrorMessages.DIRECTORY_DELETION_FAILED,
        )

    @staticmethod
    def list_directory(dir_path: str | Path) -> r[list[str]]:
        path = FlextCliFileTools._normalize_path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p.name) for p in path.iterdir()],
            c.Cli.FileErrorMessages.DIRECTORY_LISTING_FAILED,
        )

    @staticmethod
    def detect_file_format(file_path: str | Path) -> r[str]:
        formats_dict: dict[str, dict[str, list[str]]] = {
            format_name: {
                c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY: list(
                    format_config.extensions
                ),
            }
            for format_name, format_config in c.Cli.FILE_FORMATS.items()
        }
        return FlextCliFileTools._detect_format_from_extension(file_path, formats_dict)

    @staticmethod
    def load_file_auto_detect(file_path: str | Path) -> r[t.GeneralValueType]:
        format_result = FlextCliFileTools.detect_file_format(file_path)
        if format_result.is_failure:
            return r[t.GeneralValueType].fail(
                format_result.error or c.Cli.ErrorMessages.FORMAT_DETECTION_FAILED,
            )
        file_format = format_result.value
        if file_format == c.Cli.FileSupportedFormats.JSON:
            return FlextCliFileTools.read_json_file(file_path)
        if file_format == c.Cli.FileSupportedFormats.YAML:
            return FlextCliFileTools.read_yaml_file(file_path)
        return r[t.GeneralValueType].fail(
            c.Cli.ErrorMessages.UNSUPPORTED_FORMAT.format(format=file_format),
        )

    @staticmethod
    def save_file(file_path: str | Path, data: t.GeneralValueType) -> r[bool]:
        return FlextCliFileTools._save_file_by_extension(file_path, data)

    @staticmethod
    def calculate_file_hash(file_path: str | Path, algorithm: str = "sha256") -> r[str]:
        path = FlextCliFileTools._normalize_path(file_path)

        def _calculate() -> str:
            hash_obj = hashlib.new(algorithm)
            with path.open("rb") as f:
                for chunk in iter(
                    lambda: f.read(c.Cli.FileToolsDefaults.CHUNK_SIZE), b""
                ):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        return FlextCliFileTools._execute_file_operation(
            _calculate,
            c.Cli.FileErrorMessages.HASH_CALCULATION_FAILED,
        )

    @staticmethod
    def verify_file_hash(
        file_path: str | Path,
        expected_hash: str,
        algorithm: str = "sha256",
    ) -> r[bool]:
        hash_result = FlextCliFileTools.calculate_file_hash(file_path, algorithm)
        if hash_result.is_failure:
            return r[bool].fail(
                hash_result.error
                or c.Cli.FileErrorMessages.HASH_CALCULATION_FAILED_NO_ERROR,
            )
        return r[bool].ok(hash_result.value == expected_hash)

    @staticmethod
    def create_temp_file() -> r[str]:
        def _create() -> str:
            fd, path = tempfile.mkstemp()
            os.close(fd)
            return path
        return FlextCliFileTools._execute_file_operation(
            _create,
            c.Cli.FileErrorMessages.TEMP_FILE_CREATION_FAILED,
        )

    @staticmethod
    def create_temp_directory() -> r[str]:
        return FlextCliFileTools._execute_file_operation(
            tempfile.mkdtemp,
            c.Cli.FileErrorMessages.TEMP_DIR_CREATION_FAILED,
        )

    @staticmethod
    def create_zip_archive(archive_path: str | Path, files: list[str]) -> r[bool]:
        def _create() -> object:
            with zipfile.ZipFile(
                archive_path, c.Cli.FileIODefaults.ZIP_WRITE_MODE
            ) as zipf:
                for file in files:
                    zipf.write(file, Path(file).name)
        return FlextCliFileTools._run_bool_operation(
            _create,
            c.Cli.FileErrorMessages.ZIP_CREATION_FAILED,
        )

    @staticmethod
    def extract_zip_archive(
        archive_path: str | Path, extract_to: str | Path
    ) -> r[bool]:
        def _extract() -> object:
            with zipfile.ZipFile(
                archive_path, c.Cli.FileIODefaults.ZIP_READ_MODE
            ) as zipf:
                zipf.extractall(extract_to)
        return FlextCliFileTools._run_bool_operation(
            _extract,
            c.Cli.FileErrorMessages.ZIP_EXTRACTION_FAILED,
        )

    @staticmethod
    def find_files_by_pattern(directory: str | Path, pattern: str) -> r[list[str]]:
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p) for p in path.glob(pattern)],
            c.Cli.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_name(directory: str | Path, name: str) -> r[list[str]]:
        path = FlextCliFileTools._normalize_path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [
                str(p)
                for p in path.rglob(c.Cli.FileIODefaults.GLOB_PATTERN_ALL)
                if p.name == name
            ],
            c.Cli.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_content(directory: str | Path, content: str) -> r[list[str]]:
        path = FlextCliFileTools._normalize_path(directory)

        def _search() -> list[str]:
            matches: list[str] = []
            for file_path in path.rglob(c.Cli.FileIODefaults.GLOB_PATTERN_ALL):
                if not file_path.is_file():
                    continue
                try:
                    if content in file_path.read_text(
                        encoding=c.Cli.Utilities.DEFAULT_ENCODING
                    ):
                        matches.append(str(file_path))
                except (UnicodeDecodeError, PermissionError):
                    continue
            return matches
        return FlextCliFileTools._execute_file_operation(
            _search,
            c.Cli.FileErrorMessages.CONTENT_SEARCH_FAILED,
        )

    @staticmethod
    def get_supported_formats() -> r[list[str]]:
        return r[list[str]].ok(c.Cli.FileSupportedFormats.SUPPORTED_FORMATS)


__all__ = ["FlextCliFileTools"]
