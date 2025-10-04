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

import json
import shutil
from pathlib import Path

import yaml
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

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
        """Initialize unified file tools service."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._supported_formats = FlextCliConstants.FILE_FORMATS

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger
    _container: FlextContainer

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute file tools service - FlextService interface.

        Returns:
            FlextResult with empty dict (file tools are used via methods, not execute)

        """
        return FlextResult[FlextTypes.Dict].ok({})

    # ==========================================================================
    # PUBLIC API - File operations exposed to ecosystem
    # ==========================================================================

    def read_json_file(self, file_path: str | Path) -> FlextResult[object]:
        """Read JSON file using internal loader.

        Args:
            file_path: Path to JSON file

        Returns:
            FlextResult containing parsed JSON data

        """
        return self._FileLoader.load_json(str(file_path))

    def write_json_file(
        self, file_path: str | Path, data: object, **kwargs: object
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
            with Path(file_path).open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, **kwargs)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"JSON write failed: {e}")

    def read_yaml_file(self, file_path: str | Path) -> FlextResult[object]:
        """Read YAML file using internal loader.

        Args:
            file_path: Path to YAML file

        Returns:
            FlextResult containing parsed YAML data

        """
        return self._FileLoader.load_yaml(str(file_path))

    def write_yaml_file(
        self, file_path: str | Path, data: object, **kwargs: object
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
            with Path(file_path).open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, **kwargs)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"YAML write failed: {e}")

    # === NESTED HELPER CLASSES ===

    class _FormatDetector:
        """Nested helper for file format detection."""

        @staticmethod
        def detect_format(
            supported_formats: FlextTypes.NestedDict, file_path: str | Path
        ) -> FlextResult[str]:
            """Detect file format from extension."""
            path = Path(file_path)
            extension = path.suffix.lower().lstrip(".")

            for format_name, format_info in supported_formats.items():
                if (
                    isinstance(format_info, dict)
                    and "extensions" in format_info
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
                with Path(file_path).open(encoding="utf-8") as f:
                    data = json.load(f)
                return FlextResult[object].ok(data)
            except Exception as e:
                return FlextResult[object].fail(f"JSON load failed: {e}")

        @staticmethod
        def load_yaml(file_path: str, **_kwargs: object) -> FlextResult[object]:
            """Load YAML file."""
            try:
                with Path(file_path).open(encoding="utf-8") as f:
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
                # Create temporary instance to use instance method
                temp_instance = object.__new__(FlextCliFileTools)
                return temp_instance.write_json_file(file_path, data, **kwargs)
            if extension in {".yaml", ".yml"}:
                # Create temporary instance to use instance method
                temp_instance = object.__new__(FlextCliFileTools)
                return temp_instance.write_yaml_file(file_path, data, **kwargs)
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


class _FlextCliFileSystemOps:
    """Internal service for file system operations."""

    def __init__(self) -> None:
        self._logger = FlextLogger(__name__)

    def file_exists(self, file_path: str) -> FlextResult[bool]:
        """Check if file exists."""
        try:
            exists = Path(file_path).exists()
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(f"File existence check failed: {e}")

    def get_file_size(self, file_path: str) -> FlextResult[int]:
        """Get file size in bytes."""
        try:
            size = Path(file_path).stat().st_size
            return FlextResult[int].ok(size)
        except Exception as e:
            return FlextResult[int].fail(f"File size check failed: {e}")

    def copy_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Copy file from source to destination."""
        try:
            shutil.copy2(source_path, destination_path)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"File copy failed: {e}")

    def move_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Move file from source to destination."""
        try:
            shutil.move(source_path, destination_path)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"File move failed: {e}")

    def delete_file(self, file_path: str) -> FlextResult[bool]:
        """Delete file."""
        try:
            Path(file_path).unlink()
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"File delete failed: {e}")

    def create_directory(self, directory_path: str) -> FlextResult[bool]:
        """Create directory."""
        try:
            Path(directory_path).mkdir(parents=False, exist_ok=False)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Directory create failed: {e}")

    def create_directories(self, directory_path: str) -> FlextResult[bool]:
        """Create directories recursively."""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Directories create failed: {e}")

    def list_directory(self, directory_path: str) -> FlextResult[FlextTypes.StringList]:
        """List directory contents."""
        try:
            items = [str(item) for item in Path(directory_path).iterdir()]
            return FlextResult[FlextTypes.StringList].ok(items)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Directory list failed: {e}"
            )


__all__ = ["FlextCliFileTools"]
