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
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TextIO, TypeGuard

import yaml
from flext_core import r

from flext_cli.constants import c
from flext_cli.typings import t
from flext_cli.utilities import u


def _is_json_mapping(value: t.JsonValue) -> TypeGuard[Mapping[str, t.JsonValue]]:
    """Narrow JsonValue to mapping for structured file load."""
    return isinstance(value, Mapping)


class FlextCliFileTools:
    @staticmethod
    def _execute_file_operation[T](
        operation_func: Callable[[], T],
        error_template: str,
        **format_kwargs: t.JsonValue,
    ) -> r[T]:
        try:
            return r[T].ok(operation_func())
        except Exception as e:
            return r[T].fail(error_template.format(error=e, **format_kwargs))

    @staticmethod
    def _run_bool_operation(
        operation_func: Callable[[], object],
        error_template: str,
        **format_kwargs: t.JsonValue,
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
    def _get_encoding(encoding: str | None) -> str:
        return encoding or c.Cli.Utilities.DEFAULT_ENCODING

    @staticmethod
    def _detect_format_from_extension(
        file_path: str | Path,
        supported_formats: Mapping[str, Mapping[str, list[str]]],
    ) -> r[str]:
        ext = (
            Path(file_path)
            .suffix.lower()
            .lstrip(c.Cli.FileToolsDefaults.EXTENSION_PREFIX)
        )
        for fmt_name, fmt_info in supported_formats.items():
            if (
                u.is_dict_like(fmt_info)
                and c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY in fmt_info
            ):
                exts = fmt_info[c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY]
                if u.is_list_like(exts) and ext in exts:
                    return r[str].ok(fmt_name)
        return r[str].fail(
            c.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_GENERIC.format(extension=ext)
        )

    @staticmethod
    def _load_structured_file(
        file_path: str,
        loader: Callable[[TextIO], t.JsonValue],
    ) -> t.JsonValue:
        with Path(file_path).open(encoding=c.Cli.Utilities.DEFAULT_ENCODING) as f:
            loaded: t.JsonValue = loader(f)
        if _is_json_mapping(loaded):
            loaded_dict: dict[str, t.JsonValue] = dict(loaded)
            return u.transform(loaded_dict, to_json=True).map_or(loaded_dict)
        return loaded

    @staticmethod
    def _save_file_by_extension(file_path: str | Path, data: t.JsonValue) -> r[bool]:
        ext = Path(file_path).suffix.lower()
        if ext == c.Cli.FileExtensions.JSON:
            return FlextCliFileTools.write_json_file(file_path, data)
        if ext in c.Cli.FileSupportedFormats.YAML_EXTENSIONS_SET:
            return FlextCliFileTools.write_yaml_file(file_path, data)
        return r[bool].fail(
            c.Cli.FileErrorMessages.UNSUPPORTED_FORMAT_EXTENSION.format(extension=ext)
        )

    @staticmethod
    def _write_structured_file(
        file_path: str | Path,
        writer: Callable[[TextIO], None],
        error_template: str,
    ) -> r[bool]:
        path = Path(file_path)

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
    def _read_csv_dict_rows(file_path: Path) -> list[Mapping[str, str]]:
        with file_path.open(encoding=c.Cli.Utilities.DEFAULT_ENCODING, newline="") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def read_text_file(file_path: str | Path) -> r[str]:
        p = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: p.read_text(encoding=c.Cli.Utilities.DEFAULT_ENCODING),
            c.Cli.ErrorMessages.TEXT_FILE_READ_FAILED,
        )

    @staticmethod
    def write_text_file(
        file_path: str | Path,
        content: str,
        encoding: str | None = c.Cli.Utilities.DEFAULT_ENCODING,
    ) -> r[bool]:
        p = Path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: p.write_text(
                content, encoding=FlextCliFileTools._get_encoding(encoding)
            ),
            c.Cli.ErrorMessages.TEXT_FILE_WRITE_FAILED,
        )

    @staticmethod
    def read_binary_file(file_path: str | Path) -> r[bytes]:
        p = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            p.read_bytes, c.Cli.FileErrorMessages.BINARY_READ_FAILED
        )

    @staticmethod
    def write_binary_file(file_path: str | Path, content: bytes) -> r[bool]:
        p = Path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: p.write_bytes(content), c.Cli.FileErrorMessages.BINARY_WRITE_FAILED
        )

    @staticmethod
    def read_json_file(file_path: str | Path) -> r[t.JsonValue]:
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_structured_file(str(file_path), json.load),
            c.Cli.FileErrorMessages.JSON_LOAD_FAILED,
        )

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: t.JsonValue,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
    ) -> r[bool]:
        return FlextCliFileTools._write_structured_file(
            file_path,
            lambda f: json.dump(
                data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii
            ),
            c.Cli.ErrorMessages.JSON_WRITE_FAILED,
        )

    @staticmethod
    def read_yaml_file(file_path: str | Path) -> r[t.JsonValue]:
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_structured_file(
                str(file_path),
                yaml.safe_load,
            ),
            c.Cli.FileErrorMessages.YAML_LOAD_FAILED,
        )

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: t.JsonValue,
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
        path = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_csv_rows(path),
            c.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def write_csv_file(file_path: str | Path, data: list[list[str]]) -> r[bool]:
        path = Path(file_path)

        def _write() -> None:
            with path.open(
                mode="w", encoding=c.Cli.Utilities.DEFAULT_ENCODING, newline=""
            ) as f:
                csv.writer(f).writerows(data)

        return FlextCliFileTools._run_bool_operation(
            _write, c.Cli.FileErrorMessages.CSV_WRITE_FAILED
        )

    @staticmethod
    def read_csv_file_with_headers(file_path: str | Path) -> r[list[Mapping[str, str]]]:
        path = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._read_csv_dict_rows(path),
            c.Cli.FileErrorMessages.CSV_READ_FAILED,
        )

    @staticmethod
    def file_exists(file_path: str | Path) -> r[bool]:
        path = Path(file_path)
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
        path = Path(file_path)
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
        p = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: int(p.stat().st_size),
            "Failed to get file size for {file_path}: {error}",
            file_path=str(p),
        )

    @staticmethod
    def get_file_modified_time(file_path: str | Path) -> r[float | None]:
        p = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: float(p.stat().st_mtime),
            "Failed to get modification time for {file_path}: {error}",
            file_path=str(p),
        )

    @staticmethod
    def get_file_permissions(file_path: str | Path) -> r[int]:
        p = Path(file_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: p.stat().st_mode & 0o777,
            "Failed to get permissions for {file_path}: {error}",
            file_path=str(p),
        )

    @staticmethod
    def set_file_permissions(file_path: str | Path, mode: int) -> r[bool]:
        p = Path(file_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: p.chmod(mode),
            "Failed to set permissions for {file_path}: {error}",
            file_path=str(p),
        )

    @staticmethod
    def create_directory(dir_path: str | Path) -> r[bool]:
        path = Path(dir_path)
        return FlextCliFileTools._run_bool_operation(
            lambda: path.mkdir(parents=True, exist_ok=True),
            c.Cli.FileErrorMessages.DIRECTORY_CREATION_FAILED,
        )

    @staticmethod
    def directory_exists(dir_path: str | Path) -> r[bool]:
        path = Path(dir_path)
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
        path = Path(dir_path)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p.name) for p in path.iterdir()],
            c.Cli.FileErrorMessages.DIRECTORY_LISTING_FAILED,
        )

    @staticmethod
    def detect_file_format(file_path: str | Path) -> r[str]:
        fmts: dict[str, dict[str, list[str]]] = {
            name: {c.Cli.FileIODefaults.FORMAT_EXTENSIONS_KEY: list(cfg["extensions"])}
            for name, cfg in c.Cli.FILE_FORMATS.items()
        }
        return FlextCliFileTools._detect_format_from_extension(file_path, fmts)

    @staticmethod
    def load_file_auto_detect(file_path: str | Path) -> r[t.JsonValue]:
        format_result = FlextCliFileTools.detect_file_format(file_path)
        if format_result.is_failure:
            return r[t.JsonValue].fail(
                format_result.error or c.Cli.ErrorMessages.FORMAT_DETECTION_FAILED
            )
        fmt = format_result.value
        if fmt == c.Cli.FileSupportedFormats.JSON:
            return FlextCliFileTools.read_json_file(file_path)
        if fmt == c.Cli.FileSupportedFormats.YAML:
            return FlextCliFileTools.read_yaml_file(file_path)
        return r[t.JsonValue].fail(
            c.Cli.ErrorMessages.UNSUPPORTED_FORMAT.format(format=fmt)
        )

    @staticmethod
    def save_file(file_path: str | Path, data: t.JsonValue) -> r[bool]:
        return FlextCliFileTools._save_file_by_extension(file_path, data)

    @staticmethod
    def calculate_file_hash(file_path: str | Path, algorithm: str = "sha256") -> r[str]:
        path = Path(file_path)

        def _calculate() -> str:
            h = hashlib.new(algorithm)
            with path.open("rb") as f:
                for chunk in iter(
                    lambda: f.read(c.Cli.FileToolsDefaults.CHUNK_SIZE), b""
                ):
                    h.update(chunk)
            return h.hexdigest()

        return FlextCliFileTools._execute_file_operation(
            _calculate, c.Cli.FileErrorMessages.HASH_CALCULATION_FAILED
        )

    @staticmethod
    def verify_file_hash(
        file_path: str | Path, expected_hash: str, algorithm: str = "sha256"
    ) -> r[bool]:
        hash_result = FlextCliFileTools.calculate_file_hash(file_path, algorithm)
        if hash_result.is_failure:
            return r[bool].fail(
                hash_result.error
                or c.Cli.FileErrorMessages.HASH_CALCULATION_FAILED_NO_ERROR
            )
        return r[bool].ok(hash_result.value == expected_hash)

    @staticmethod
    def create_temp_file() -> r[str]:
        def _create() -> str:
            fd, path = tempfile.mkstemp()
            os.close(fd)
            return path

        return FlextCliFileTools._execute_file_operation(
            _create, c.Cli.FileErrorMessages.TEMP_FILE_CREATION_FAILED
        )

    @staticmethod
    def create_temp_directory() -> r[str]:
        return FlextCliFileTools._execute_file_operation(
            tempfile.mkdtemp, c.Cli.FileErrorMessages.TEMP_DIR_CREATION_FAILED
        )

    @staticmethod
    def create_zip_archive(archive_path: str | Path, files: list[str]) -> r[bool]:
        def _create() -> None:
            with zipfile.ZipFile(
                archive_path, c.Cli.FileIODefaults.ZIP_WRITE_MODE
            ) as zf:
                for file in files:
                    zf.write(file, Path(file).name)

        return FlextCliFileTools._run_bool_operation(
            _create, c.Cli.FileErrorMessages.ZIP_CREATION_FAILED
        )

    @staticmethod
    def extract_zip_archive(
        archive_path: str | Path, extract_to: str | Path
    ) -> r[bool]:
        def _extract() -> None:
            with zipfile.ZipFile(
                archive_path, c.Cli.FileIODefaults.ZIP_READ_MODE
            ) as zf:
                zf.extractall(extract_to)

        return FlextCliFileTools._run_bool_operation(
            _extract, c.Cli.FileErrorMessages.ZIP_EXTRACTION_FAILED
        )

    @staticmethod
    def find_files_by_pattern(directory: str | Path, pattern: str) -> r[list[str]]:
        path = Path(directory)
        return FlextCliFileTools._execute_file_operation(
            lambda: [str(p) for p in path.glob(pattern)],
            c.Cli.FileErrorMessages.FILE_SEARCH_FAILED,
        )

    @staticmethod
    def find_files_by_name(directory: str | Path, name: str) -> r[list[str]]:
        path = Path(directory)
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
        path = Path(directory)

        def _search() -> list[str]:
            matches: list[str] = []
            for fp in path.rglob(c.Cli.FileIODefaults.GLOB_PATTERN_ALL):
                if not fp.is_file():
                    continue
                try:
                    if content in fp.read_text(
                        encoding=c.Cli.Utilities.DEFAULT_ENCODING
                    ):
                        matches.append(str(fp))
                except (UnicodeDecodeError, PermissionError):
                    continue
            return matches

        return FlextCliFileTools._execute_file_operation(
            _search, c.Cli.FileErrorMessages.CONTENT_SEARCH_FAILED
        )

    @staticmethod
    def get_supported_formats() -> r[list[str]]:
        return r[list[str]].ok(c.Cli.FileSupportedFormats.SUPPORTED_FORMATS)


__all__ = ["FlextCliFileTools"]
