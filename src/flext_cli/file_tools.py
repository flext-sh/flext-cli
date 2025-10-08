"""Comprehensive file operation tools for CLI applications.

This module provides extensive import/export functionality for all major file formats
using the best Python libraries. Supports formats defined in FlextCore.Constants including
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
from flext_core import FlextCore, FlextResult

from flext_cli.constants import FlextCliConstants

# ============================================================================
# SPECIALIZED INTERNAL SERVICES - Better separation of concerns
# ============================================================================


class FlextCliFileTools(FlextCore.Service[FlextCore.Types.Dict]):
    """Unified file operations service following FLEXT namespace pattern.

    Single class containing all file operations with nested helper classes
    for format detection, loading, and saving operations.
    """

    def __init__(self) -> None:
        """Initialize unified file tools service with Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextCore.Service via FlextMixins
        self._supported_formats = FlextCliConstants.FILE_FORMATS

    # Attributes initialized in __init__

    def execute(self) -> FlextResult[FlextCore.Types.Dict]:
        """Execute file tools service - FlextCore.Service interface.

        Returns:
            FlextResult with status dict (file tools service is ready)

        """
        # Return dict to indicate service is ready (matches service interface)
        return FlextResult[FlextCore.Types.Dict].ok({"status": "ready"})

    # ==========================================================================
    # PUBLIC API - File operations exposed to ecosystem
    # ==========================================================================

    def write_json(
        self, data: object, path: str | Path, **kwargs: object
    ) -> FlextResult[None]:
        """Write JSON data to file (alias for write_json_file).

        Args:
            data: Data to write
            path: File path
            **kwargs: Additional options

        Returns:
            FlextResult[None]: Success or failure

        """
        return self.write_json_file(path, data, **kwargs)

    def read_json(self, path: str | Path) -> FlextResult[object]:
        """Read JSON data from file (alias for read_json_file).

        Args:
            path: File path

        Returns:
            FlextResult[object]: Parsed data or error

        """
        return self.read_json_file(path)

    def write_yaml(
        self, data: object, path: str | Path, **kwargs: object
    ) -> FlextResult[None]:
        """Write YAML data to file (alias for write_yaml_file).

        Args:
            data: Data to write
            path: File path
            **kwargs: Additional options

        Returns:
            FlextResult[None]: Success or failure

        """
        return self.write_yaml_file(path, data, **kwargs)

    def read_yaml(self, path: str | Path) -> FlextResult[object]:
        """Read YAML data from file (alias for read_yaml_file).

        Args:
            path: File path

        Returns:
            FlextResult[object]: Parsed data or error

        """
        return self.read_yaml_file(path)

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
        self, file_path: str | Path, content: str, **kwargs: object
    ) -> FlextResult[None]:
        """Write text content to file.

        Args:
            file_path: Path to text file
            content: Content to write
            **kwargs: Additional options (encoding, etc.)

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            encoding = kwargs.get("encoding", FlextCliConstants.Encoding.UTF8)
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

    def read_json_file(self, file_path: str | Path) -> FlextResult[object]:
        """Read JSON file using internal loader.

        Args:
            file_path: Path to JSON file

        Returns:
            FlextResult containing parsed JSON data

        """
        return self._FileLoader.load_json(str(file_path))

    @staticmethod
    def write_json_file(
        file_path: str | Path, data: object, **kwargs: object
    ) -> FlextResult[None]:
        """Write data to JSON file.

        Args:
            file_path: Path to JSON file
            data: Data to write
            **kwargs: Additional JSON dump options

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            # Filter kwargs to only valid json.dump parameters
            valid_keys = {
                FlextCliConstants.JsonOptions.SKIPKEYS,
                FlextCliConstants.JsonOptions.ENSURE_ASCII,
                FlextCliConstants.JsonOptions.CHECK_CIRCULAR,
                FlextCliConstants.JsonOptions.ALLOW_NAN,
                FlextCliConstants.JsonOptions.CLS,
                FlextCliConstants.JsonOptions.INDENT,
                FlextCliConstants.JsonOptions.SEPARATORS,
                "default",
                FlextCliConstants.JsonOptions.SORT_KEYS,
            }
            dump_kwargs: dict[str, object] = {
                key: value for key, value in kwargs.items() if key in valid_keys
            }

            with Path(file_path).open(
                "w", encoding=FlextCliConstants.Encoding.UTF8
            ) as f:
                # Use type: ignore to avoid type checker issues with **kwargs
                json.dump(data, f, indent=2, **dump_kwargs)  # type: ignore[arg-type]
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.JSON_WRITE_FAILED.format(error=e)
            )

    def read_yaml_file(self, file_path: str | Path) -> FlextResult[object]:
        """Read YAML file using internal loader.

        Args:
            file_path: Path to YAML file

        Returns:
            FlextResult containing parsed YAML data

        """
        return self._FileLoader.load_yaml(str(file_path))

    @staticmethod
    def write_yaml_file(
        file_path: str | Path, data: object, **kwargs: object
    ) -> FlextResult[None]:
        """Write data to YAML file.

        Args:
            file_path: Path to YAML file
            data: Data to write
            **kwargs: Additional YAML dump options

        Returns:
            FlextResult[None] indicating success or failure

        """
        try:
            # Filter kwargs to only valid yaml.safe_dump parameters
            valid_keys = {
                "default_style",
                "default_flow_style",
                "canonical",
                FlextCliConstants.JsonOptions.INDENT,
                "width",
                "allow_unicode",
                "line_break",
                "encoding",
                "explicit_start",
                "explicit_end",
                "version",
                "tags",
                FlextCliConstants.JsonOptions.SORT_KEYS,
            }
            dump_kwargs: dict[str, object] = {
                key: value for key, value in kwargs.items() if key in valid_keys
            }

            with Path(file_path).open(
                "w", encoding=FlextCliConstants.Encoding.UTF8
            ) as f:
                # Use type: ignore to avoid type checker issues with **kwargs
                yaml.safe_dump(data, f, **dump_kwargs)  # type: ignore[arg-type]
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
        self, file_path: str | Path, **kwargs: object
    ) -> FlextResult[object]:
        """Load file with automatic format detection."""
        format_result = self.detect_file_format(file_path)
        if format_result.is_failure:
            return FlextResult[object].fail(
                format_result.error
                or FlextCliConstants.ErrorMessages.FORMAT_DETECTION_FAILED
            )

        file_format = format_result.unwrap()
        if file_format == "json":
            return self._FileLoader.load_json(str(file_path), **kwargs)
        if file_format == "yaml":
            return self._FileLoader.load_yaml(str(file_path), **kwargs)

        return FlextResult[object].fail(
            FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT.format(
                format=file_format
            )
        )

    def save_file(
        self, file_path: str | Path, data: object, **kwargs: object
    ) -> FlextResult[None]:
        """Save data to file with automatic format detection."""
        return self._FileSaver.save_file(file_path, data, **kwargs)

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

    def read_csv_file(self, file_path: str | Path) -> FlextResult[list[list[str]]]:
        """Read CSV file content."""
        try:
            with Path(file_path).open(
                encoding=FlextCliConstants.Encoding.UTF8, newline=""
            ) as f:
                reader = csv.reader(f)
                data = list(reader)
            return FlextResult[list[list[str]]].ok(data)
        except Exception as e:
            return FlextResult[list[list[str]]].fail(f"CSV read failed: {e}")

    def write_csv_file(
        self, file_path: str | Path, data: list[list[str]]
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
    ) -> FlextResult[list[dict[str, str]]]:
        """Read CSV file with headers."""
        try:
            with Path(file_path).open(
                encoding=FlextCliConstants.Encoding.UTF8, newline=""
            ) as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return FlextResult[list[dict[str, str]]].ok(data)
        except Exception as e:
            return FlextResult[list[dict[str, str]]].fail(f"CSV read failed: {e}")

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

    def list_directory(self, dir_path: str | Path) -> FlextResult[list[str]]:
        """List directory contents."""
        try:
            items = [str(p.name) for p in Path(dir_path).iterdir()]
            return FlextResult[list[str]].ok(items)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Directory listing failed: {e}")

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
        self, archive_path: str | Path, files: list[str]
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
    ) -> FlextResult[list[str]]:
        """Find files by glob pattern."""
        try:
            files = [str(p) for p in Path(directory).glob(pattern)]
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"File search failed: {e}")

    def find_files_by_name(
        self, directory: str | Path, name: str
    ) -> FlextResult[list[str]]:
        """Find files by name."""
        try:
            files = [str(p) for p in Path(directory).rglob("*") if p.name == name]
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"File search failed: {e}")

    def find_files_by_content(
        self, directory: str | Path, content: str
    ) -> FlextResult[list[str]]:
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
            return FlextResult[list[str]].ok(matches)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Content search failed: {e}")

    def get_supported_formats(self) -> FlextResult[list[str]]:
        """Get list of supported file formats."""
        formats = ["json", "yaml", "yml", "txt", "csv"]
        return FlextResult[list[str]].ok(formats)

    def create_directories(self, dir_path: str | Path) -> FlextResult[None]:
        """Create directories (alias for create_directory)."""
        return self.create_directory(dir_path)

    # === NESTED HELPER CLASSES ===

    class _FormatDetector:
        """Nested helper for file format detection."""

        @staticmethod
        def detect_format(
            supported_formats: dict[str, dict[str, list[str]]], file_path: str | Path
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
        def load_json(file_path: str, **_kwargs: object) -> FlextResult[object]:
            """Load JSON file."""
            try:
                with Path(file_path).open(
                    encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = json.load(f)
                return FlextResult[object].ok(data)
            except Exception as e:
                return FlextResult[object].fail(f"JSON load failed: {e}")

        @staticmethod
        def load_yaml(file_path: str, **_kwargs: object) -> FlextResult[object]:
            """Load YAML file."""
            try:
                with Path(file_path).open(
                    encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = yaml.safe_load(f)
                return FlextResult[object].ok(data)
            except Exception as e:
                return FlextResult[object].fail(f"YAML load failed: {e}")

    class _FileSaver:
        """Nested helper for file saving operations."""

        @staticmethod
        def save_file(
            file_path: str | Path,
            data: object,
            **kwargs: object,
        ) -> FlextResult[None]:
            """Save data to file with automatic format detection.

            Args:
                file_path: Path to save file
                data: Data to save
                **kwargs: Additional options for the specific format

            Returns:
                FlextResult[bool] indicating success or failure

            """
            path = Path(file_path)
            extension = path.suffix.lower()

            # Detect format and delegate to appropriate saver
            if extension == ".json":
                return FlextCliFileTools.write_json_file(file_path, data, **kwargs)
            if extension in {".yaml", ".yml"}:
                return FlextCliFileTools.write_yaml_file(file_path, data, **kwargs)
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
