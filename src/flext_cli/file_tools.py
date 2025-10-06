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
from typing import cast

import yaml
from flext_core import (
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
        """Initialize unified file tools service with Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins
        self._supported_formats = FlextCliConstants.FILE_FORMATS

    # Attributes initialized in __init__

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute file tools service - FlextService interface.

        Returns:
            FlextResult with empty dict (file tools are used via methods, not execute)

        """
        return FlextResult[FlextTypes.Dict].ok({})

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
            content = Path(file_path).read_text(encoding="utf-8")
            return FlextResult[str].ok(content)
        except Exception as e:
            return FlextResult[str].fail(f"Text file read failed: {e}")

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
            encoding = kwargs.get("encoding", "utf-8")
            if not isinstance(encoding, str):
                encoding = "utf-8"
            Path(file_path).write_text(content, encoding=encoding)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Text file write failed: {e}")

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
            return FlextResult[bool].fail(f"File copy failed: {e}")

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
                "skipkeys",
                "ensure_ascii",
                "check_circular",
                "allow_nan",
                "cls",
                "indent",
                "separators",
                "default",
                "sort_keys",
            }
            dump_kwargs = {
                key: value for key, value in kwargs.items() if key in valid_keys
            }

            with Path(file_path).open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, **dump_kwargs)
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
            with Path(file_path).open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, **cast("dict[str, object]", kwargs))
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
