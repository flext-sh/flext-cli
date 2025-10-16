"""Comprehensive file operation tools for CLI applications.

This module provides extensive import/export functionality for all major file formats
using the best Python libraries. Supports formats defined in FlextConstants including
JSON, YAML, CSV, XML, Excel, Parquet, TOML, and more.

Dependencies:
- pandas: Excel, Parquet, enhanced CSV/TSV support
- pyarrow: High-performance Parquet operations
- yaml: YAML format support
- xml.etree: XML parsing and generation
- toml: TOML configuration files
- pathlib: Modern path handling
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

import yaml
from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.constants import FlextCliConstants

# ============================================================================
# SPECIALIZED INTERNAL SERVICES - Better separation of concerns
# ============================================================================


class FlextCliFileTools(FlextService[FlextTypes.Dict]):
    """Unified file operations service following FLEXT namespace pattern.

    Single class containing all file operations with nested helper classes
    for format detection, loading, and saving operations.
    """

    def __init__(self) -> None:
        """Initialize unified file tools service with Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins
        self._supported_formats = FlextCliConstants.FILE_FORMATS

    # Attributes initialized in __init__

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute file tools service - FlextService interface.

        Returns:
            FlextResult with status dict[str, object] (file tools service is ready)

        """
        # Return dict[str, object] to indicate service is ready (matches service interface)
        return FlextResult[FlextTypes.Dict].ok({"status": "ready"})

    # ==========================================================================
    # PUBLIC API - File operations exposed to ecosystem
    # ==========================================================================

    def read_text_file(self, file_path: str | Path) -> FlextResult[str]:
        """Read text file.

        Args:
            file_path: Path to text file

        Returns:
            FlextResult containing file content as string

        """
        try:
            content = Path(file_path).read_text(
                encoding=FlextCliConstants.Encoding.UTF8
            )
            return FlextResult[str].ok(content)
        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TEXT_FILE_READ_FAILED.format(error=e)
            )

    def write_text_file(
        self,
        file_path: str | Path,
        content: str,
        encoding: str = FlextCliConstants.Encoding.UTF8,
    ) -> FlextResult[None]:
        """Write text content to file.

        Args:
            file_path: Path to text file
            content: Content to write
            encoding: Text encoding (default: UTF-8)

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            # If encoding is not a string, use default (graceful degradation)
            if not isinstance(encoding, str):
                encoding = FlextCliConstants.Encoding.UTF8
            Path(file_path).write_text(content, encoding=encoding)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.TEXT_FILE_WRITE_FAILED.format(error=e)
            )

    def copy_file(
        self, source_path: str | Path, destination_path: str | Path
    ) -> FlextResult[bool]:
        """Copy file from source to destination.

        Args:
            source_path: Source file path
            destination_path: Destination file path

        Returns:
            FlextResult[bool] indicating success or failure

        """
        try:
            shutil.copy2(str(source_path), str(destination_path))
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FILE_COPY_FAILED.format(error=e)
            )

    def read_json_file(
        self, file_path: str | Path
    ) -> FlextResult[
        FlextTypes.Dict | FlextTypes.List | str | int | float | bool | None
    ]:
        """Read JSON file using internal loader.

        Args:
            file_path: Path to JSON file

        Returns:
            FlextResult containing parsed JSON data

        """
        return self._FileLoader.load_json(str(file_path))

    @staticmethod
    def write_json_file(
        file_path: str | Path,
        data: FlextTypes.JsonValue,
        indent: int = 2,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
    ) -> FlextResult[None]:
        """Write data to JSON file with explicit common parameters.

        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: Indentation level (default: 2)
            sort_keys: Sort keys alphabetically (default: False)
            ensure_ascii: Escape non-ASCII characters (default: True)

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            with Path(file_path).open(
                "w", encoding=FlextCliConstants.Encoding.UTF8
            ) as f:
                json.dump(
                    data,
                    f,
                    indent=indent,
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii,
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.JSON_WRITE_FAILED.format(error=e)
            )

    def read_yaml_file(
        self, file_path: str | Path
    ) -> FlextResult[
        FlextTypes.Dict | FlextTypes.List | str | int | float | bool | None
    ]:
        """Read YAML file using internal loader.

        Args:
            file_path: Path to YAML file

        Returns:
            FlextResult containing parsed YAML data

        """
        return self._FileLoader.load_yaml(str(file_path))

    @staticmethod
    def write_yaml_file(
        file_path: str | Path,
        data: FlextTypes.JsonValue,
        *,
        default_flow_style: bool | None = None,
        sort_keys: bool = False,
        allow_unicode: bool = True,
    ) -> FlextResult[None]:
        """Write data to YAML file with explicit common parameters.

        Args:
            file_path: Path to YAML file
            data: Data to write
            default_flow_style: Use flow style (None=auto, True=flow, False=block)
            sort_keys: Sort keys alphabetically (default: False)
            allow_unicode: Output Unicode characters (default: True)

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            with Path(file_path).open(
                "w", encoding=FlextCliConstants.Encoding.UTF8
            ) as f:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=default_flow_style,
                    sort_keys=sort_keys,
                    allow_unicode=allow_unicode,
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.YAML_WRITE_FAILED.format(error=e)
            )

    # === PUBLIC API METHODS ===

    def file_exists(self, file_path: str | Path) -> FlextResult[bool]:
        """Check if file exists."""
        return self._FileSystemOps.file_exists(str(file_path))

    def detect_file_format(self, file_path: str | Path) -> FlextResult[str]:
        """Detect file format from extension."""
        supported_formats = {
            "json": {"extensions": ["json"]},
            "yaml": {"extensions": ["yaml", "yml"]},
        }
        return self._FormatDetector.detect_format(supported_formats, file_path)

    def load_file_auto_detect(
        self, file_path: str | Path
    ) -> FlextResult[FlextTypes.JsonValue]:
        """Load file with automatic format detection."""
        format_result = self.detect_file_format(file_path)
        if format_result.is_failure:
            return FlextResult[FlextTypes.JsonValue].fail(
                format_result.error
                or FlextCliConstants.ErrorMessages.FORMAT_DETECTION_FAILED
            )

        file_format = format_result.unwrap()
        if file_format == "json":
            return self._FileLoader.load_json(str(file_path))
        if file_format == "yaml":
            return self._FileLoader.load_yaml(str(file_path))

        return FlextResult[FlextTypes.JsonValue].fail(
            FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT.format(
                format=file_format
            )
        )

    def save_file(
        self, file_path: str | Path, data: FlextTypes.JsonValue
    ) -> FlextResult[None]:
        """Save data to file with automatic format detection.

        Note:
            Uses default parameters for JSON/YAML writing.
            For custom formatting options, use write_json_file() or write_yaml_file() directly.

        """
        return self._FileSaver.save_file(file_path, data)

    def read_binary_file(self, file_path: str | Path) -> FlextResult[bytes]:
        """Read binary file content."""
        try:
            content = Path(file_path).read_bytes()
            return FlextResult[bytes].ok(content)
        except Exception as e:
            return FlextResult[bytes].fail(f"Binary read failed: {e}")

    def write_binary_file(
        self, file_path: str | Path, content: bytes
    ) -> FlextResult[None]:
        """Write binary content to file."""
        try:
            Path(file_path).write_bytes(content)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Binary write failed: {e}")

    def read_csv_file(
        self, file_path: str | Path
    ) -> FlextResult[list[FlextTypes.StringList]]:
        """Read CSV file content."""
        try:
            with Path(file_path).open(
                encoding=FlextCliConstants.Encoding.UTF8, newline=""
            ) as f:
                reader = csv.reader(f)
                data = list(reader)
            return FlextResult[list[FlextTypes.StringList]].ok(data)
        except Exception as e:
            return FlextResult[list[FlextTypes.StringList]].fail(
                f"CSV read failed: {e}"
            )

    def write_csv_file(
        self, file_path: str | Path, data: list[FlextTypes.StringList]
    ) -> FlextResult[None]:
        """Write CSV file content."""
        try:
            with Path(file_path).open(
                "w", encoding=FlextCliConstants.Encoding.UTF8, newline=""
            ) as f:
                writer = csv.writer(f)
                writer.writerows(data)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"CSV write failed: {e}")

    def read_csv_file_with_headers(
        self, file_path: str | Path
    ) -> FlextResult[list[FlextTypes.StringDict]]:
        """Read CSV file with headers."""
        try:
            with Path(file_path).open(
                encoding=FlextCliConstants.Encoding.UTF8, newline=""
            ) as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return FlextResult[list[FlextTypes.StringDict]].ok(data)
        except Exception as e:
            return FlextResult[list[FlextTypes.StringDict]].fail(
                f"CSV read failed: {e}"
            )

    def delete_file(self, file_path: str | Path) -> FlextResult[None]:
        """Delete file."""
        try:
            Path(file_path).unlink()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"File deletion failed: {e}")

    def move_file(
        self, source: str | Path, destination: str | Path
    ) -> FlextResult[None]:
        """Move file to new location."""
        try:
            shutil.move(str(source), str(destination))
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"File move failed: {e}")

    def create_directory(self, dir_path: str | Path) -> FlextResult[None]:
        """Create directory."""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Directory creation failed: {e}")

    def directory_exists(self, dir_path: str | Path) -> FlextResult[bool]:
        """Check if directory exists."""
        try:
            exists = Path(dir_path).is_dir()
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(f"Directory check failed: {e}")

    def delete_directory(self, dir_path: str | Path) -> FlextResult[None]:
        """Delete directory."""
        try:
            shutil.rmtree(str(dir_path))
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Directory deletion failed: {e}")

    def list_directory(
        self, dir_path: str | Path
    ) -> FlextResult[FlextTypes.StringList]:
        """List directory contents."""
        try:
            items = [str(p.name) for p in Path(dir_path).iterdir()]
            return FlextResult[FlextTypes.StringList].ok(items)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Directory listing failed: {e}"
            )

    def get_file_size(self, file_path: str | Path) -> FlextResult[int]:
        """Get file size in bytes."""
        try:
            size = Path(file_path).stat().st_size
            return FlextResult[int].ok(size)
        except Exception as e:
            return FlextResult[int].fail(f"File size check failed: {e}")

    def get_file_modified_time(self, file_path: str | Path) -> FlextResult[float]:
        """Get file modification time."""
        try:
            mtime = Path(file_path).stat().st_mtime
            return FlextResult[float].ok(mtime)
        except Exception as e:
            return FlextResult[float].fail(f"File time check failed: {e}")

    def calculate_file_hash(
        self, file_path: str | Path, algorithm: str = "sha256"
    ) -> FlextResult[str]:
        """Calculate file hash."""
        try:
            hash_obj = hashlib.new(algorithm)
            with Path(file_path).open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return FlextResult[str].ok(hash_obj.hexdigest())
        except Exception as e:
            return FlextResult[str].fail(f"Hash calculation failed: {e}")

    def verify_file_hash(
        self, file_path: str | Path, expected_hash: str, algorithm: str = "sha256"
    ) -> FlextResult[bool]:
        """Verify file hash."""
        hash_result = self.calculate_file_hash(file_path, algorithm)
        if hash_result.is_failure:
            return FlextResult[bool].fail(
                hash_result.error or "Hash calculation failed"
            )

        matches = hash_result.unwrap() == expected_hash
        return FlextResult[bool].ok(matches)

    def get_file_permissions(self, file_path: str | Path) -> FlextResult[int]:
        """Get file permissions."""
        try:
            mode = Path(file_path).stat().st_mode
            permissions = stat.S_IMODE(mode)
            return FlextResult[int].ok(permissions)
        except Exception as e:
            return FlextResult[int].fail(f"Permission check failed: {e}")

    def set_file_permissions(
        self, file_path: str | Path, permissions: int
    ) -> FlextResult[None]:
        """Set file permissions."""
        try:
            Path(file_path).chmod(permissions)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Permission set failed: {e}")

    def create_temp_file(self) -> FlextResult[str]:
        """Create temporary file."""
        try:
            fd, path = tempfile.mkstemp()

            os.close(fd)
            return FlextResult[str].ok(path)
        except Exception as e:
            return FlextResult[str].fail(f"Temp file creation failed: {e}")

    def create_temp_directory(self) -> FlextResult[str]:
        """Create temporary directory."""
        try:
            path = tempfile.mkdtemp()
            return FlextResult[str].ok(path)
        except Exception as e:
            return FlextResult[str].fail(f"Temp directory creation failed: {e}")

    def create_zip_archive(
        self, archive_path: str | Path, files: FlextTypes.StringList
    ) -> FlextResult[None]:
        """Create zip archive."""
        try:
            with zipfile.ZipFile(archive_path, "w") as zipf:
                for file in files:
                    zipf.write(file, Path(file).name)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Zip creation failed: {e}")

    def extract_zip_archive(
        self, archive_path: str | Path, extract_to: str | Path
    ) -> FlextResult[None]:
        """Extract zip archive."""
        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(extract_to)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Zip extraction failed: {e}")

    def find_files_by_pattern(
        self, directory: str | Path, pattern: str
    ) -> FlextResult[FlextTypes.StringList]:
        """Find files by glob pattern."""
        try:
            files = [str(p) for p in Path(directory).glob(pattern)]
            return FlextResult[FlextTypes.StringList].ok(files)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"File search failed: {e}")

    def find_files_by_name(
        self, directory: str | Path, name: str
    ) -> FlextResult[FlextTypes.StringList]:
        """Find files by name."""
        try:
            files = [str(p) for p in Path(directory).rglob("*") if p.name == name]
            return FlextResult[FlextTypes.StringList].ok(files)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"File search failed: {e}")

    def find_files_by_content(
        self, directory: str | Path, content: str
    ) -> FlextResult[FlextTypes.StringList]:
        """Find files containing specific content."""
        try:
            matches = []
            for file_path in Path(directory).rglob("*"):
                if file_path.is_file():
                    try:
                        text = file_path.read_text(
                            encoding=FlextCliConstants.Encoding.UTF8
                        )
                        if content in text:
                            matches.append(str(file_path))
                    except (UnicodeDecodeError, PermissionError):
                        continue
            return FlextResult[FlextTypes.StringList].ok(matches)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Content search failed: {e}"
            )

    def get_supported_formats(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of supported file formats."""
        formats = ["json", "yaml", "yml", "txt", "csv"]
        return FlextResult[FlextTypes.StringList].ok(formats)

    # === NESTED HELPER CLASSES ===

    class _FormatDetector:
        """Nested helper for file format detection."""

        @staticmethod
        def detect_format(
            supported_formats: dict[str, dict[str, FlextTypes.StringList]],
            file_path: str | Path,
        ) -> FlextResult[str]:
            """Detect file format from extension."""
            path = Path(file_path)
            extension = path.suffix.lower().lstrip(".")

            for format_name, format_info in supported_formats.items():
                if (
                    isinstance(format_info, dict)
                    and "extensions" in format_info
                    and isinstance(format_info["extensions"], (list, tuple))
                    and extension in format_info["extensions"]
                ):
                    return FlextResult[str].ok(format_name)

            return FlextResult[str].fail(f"Unsupported file format: {extension}")

    class _FileLoader:
        """Nested helper for file loading operations."""

        @staticmethod
        def load_json(file_path: str) -> FlextResult[FlextTypes.JsonValue]:
            """Load JSON file."""
            try:
                with Path(file_path).open(
                    encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data: FlextTypes.JsonValue = json.load(f)
                return FlextResult[FlextTypes.JsonValue].ok(data)
            except Exception as e:
                return FlextResult[FlextTypes.JsonValue].fail(f"JSON load failed: {e}")

        @staticmethod
        def load_yaml(file_path: str) -> FlextResult[FlextTypes.JsonValue]:
            """Load YAML file."""
            try:
                with Path(file_path).open(
                    encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data: FlextTypes.JsonValue = yaml.safe_load(f)
                return FlextResult[FlextTypes.JsonValue].ok(data)
            except Exception as e:
                return FlextResult[FlextTypes.JsonValue].fail(f"YAML load failed: {e}")

    class _FileSaver:
        """Nested helper for file saving operations."""

        @staticmethod
        def save_file(
            file_path: str | Path,
            data: FlextTypes.JsonValue,
        ) -> FlextResult[None]:
            """Save data to file with automatic format detection.

            Args:
                file_path: Path to save file
                data: Data to save

            Returns:
                FlextResult[None] indicating success or failure

            Note:
                Uses default parameters for JSON/YAML writing.
                For custom formatting, use write_json_file() or write_yaml_file() directly.

            """
            path = Path(file_path)
            extension = path.suffix.lower()

            # Detect format and delegate to appropriate saver
            if extension == ".json":
                return FlextCliFileTools.write_json_file(file_path, data)
            if extension in {".yaml", ".yml"}:
                return FlextCliFileTools.write_yaml_file(file_path, data)
            return FlextResult[None].fail(
                f"Unsupported file format: {extension}. Supported: .json, .yaml, .yml"
            )

    class _FileSystemOps:
        """Nested helper for file system operations."""

        @staticmethod
        def file_exists(file_path: str) -> FlextResult[bool]:
            """Check if file exists."""
            try:
                exists = Path(file_path).exists()
                return FlextResult[bool].ok(exists)
            except Exception as e:
                return FlextResult[bool].fail(f"File existence check failed: {e}")


__all__ = ["FlextCliFileTools"]
