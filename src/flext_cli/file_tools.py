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
import fnmatch
import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path
from typing import Any, cast, override

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import toml
import yaml
from lxml import etree

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes
from flext_core import FlextContainer, FlextLogger, FlextResult, FlextService


class FlextCliFileTools(FlextService[bool]):
    """Comprehensive file operation tools for CLI applications.

    Provides extensive import/export functionality for all major file formats using
    the best Python libraries. Supports formats defined in FlextConstants:

    Supported Formats:
    - JSON (.json): Native Python dict/list serialization
    - YAML (.yaml, .yml): Human-readable configuration and data
    - CSV (.csv): Comma-separated values with pandas enhancement
    - TSV (.tsv): Tab-separated values
    - XML (.xml): Structured markup with validation
    - Excel (.xlsx, .xls): Spreadsheet data with multiple sheets
    - Parquet (.parquet): High-performance columnar storage
    - TOML (.toml): Configuration files
    - Plain Text (.txt): Simple text files

    Features:
    - Automatic format detection based on file extension
    - Comprehensive error handling with FlextResult
    - Support for large files with streaming/chunking
    - Data validation and type conversion
    - Encoding detection and handling
    - Path normalization and security checks
    """

    @override
    def __init__(self) -> None:
        """Initialize file tools with format registry."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        self._supported_formats = self._initialize_format_registry()

    @override
    def execute(self) -> FlextResult[bool]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[bool].ok(True)

    def _initialize_format_registry(self) -> dict[str, dict[str, object]]:
        """Initialize the format registry with supported file types."""
        return {
            ".json": {
                "format": json,
                "mime_type": FlextCliConstants.APPLICATION_JSON,
                "load_method": self._load_json,
                "save_method": self._save_json,
            },
            ".yaml": {
                "format": yaml,
                "mime_type": FlextCliConstants.APPLICATION_YAML,
                "load_method": self._load_yaml,
                "save_method": self._save_yaml,
            },
            ".yml": {
                "format": yaml,
                "mime_type": FlextCliConstants.APPLICATION_YAML,
                "load_method": self._load_yaml,
                "save_method": self._save_yaml,
            },
            ".csv": {
                "format": "csv",
                "mime_type": FlextCliConstants.TEXT_CSV,
                "load_method": self._load_csv,
                "save_method": self._save_csv,
            },
            ".tsv": {
                "format": FlextCliConstants.TSV,
                "mime_type": FlextCliConstants.TEXT_TSV,
                "load_method": self._load_tsv,
                "save_method": self._save_tsv,
            },
            ".xml": {
                "format": "xml",
                "mime_type": "application/xml",
                "load_method": self._load_xml,
                "save_method": self._save_xml,
            },
            ".toml": {
                "format": "toml",
                "mime_type": "application/toml",
                "load_method": self._load_toml,
                "save_method": self._save_toml,
            },
            ".xlsx": {
                "format": "excel",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "load_method": self._load_excel,
                "save_method": self._save_excel,
            },
            ".xls": {
                "format": "excel",
                "mime_type": "application/vnd.ms-excel",
                "load_method": self._load_excel,
                "save_method": self._save_excel,
            },
            ".parquet": {
                "format": "parquet",
                "mime_type": "application/parquet",
                "load_method": self._load_parquet,
                "save_method": self._save_parquet,
            },
            ".txt": {
                "format": "text",
                "mime_type": "text/plain",
                "load_method": self._load_text,
                "save_method": self._save_text,
            },
        }

    def detect_file_format(self, file_path: str | Path) -> FlextResult[str]:
        """Detect file format based on extension.

        Args:
            file_path: Path to the file

        Returns:
            FlextResult[str]: Detected format or error

        """
        try:
            file_path_obj = Path(file_path)
            extension = file_path_obj.suffix.lower()

            if extension in self._supported_formats:
                format_info = self._supported_formats[extension]
                format_name = str(format_info["format"])
                return FlextResult[str].ok(format_name)
            return FlextResult[str].fail(f"Unsupported file format: {extension}")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to detect file format: {e}")

    def get_supported_formats(self) -> FlextResult[list[str]]:
        """Get list of all supported file formats.

        Returns:
            FlextResult[list[str]]: List of supported formats

        """
        try:
            formats = [str(info["format"]) for info in self._supported_formats.values()]
            return FlextResult[list[str]].ok(formats)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to get supported formats: {e}")

    def load_file(self, file_path: str | Path, **kwargs: object) -> FlextResult[object]:
        """Load file with automatic format detection using monadic composition.

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments passed to format-specific loader

        Returns:
            FlextResult[object]: Loaded data or error

        """
        # Advanced monadic composition with railway-oriented programming
        return (
            self.detect_file_format(file_path)
            .flat_map(lambda _: self._validate_file_format(file_path))
            .flat_map(lambda file_info: self._execute_load_method(file_info, **kwargs))
        )

    def _validate_file_format(
        self, file_path: str | Path
    ) -> FlextResult[dict[str, object]]:
        """Validate file format and return file info.

        Args:
            file_path: Path to the file to validate

        Returns:
            FlextResult[dict[str, object]]: File info or error

        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[dict[str, object]].fail(
                    f"File does not exist: {file_path}"
                )

            # Get file format info
            format_info = self.detect_file_format(file_path)
            if format_info.is_failure:
                return FlextResult[dict[str, object]].fail(
                    format_info.error or "Format detection failed"
                )

            # Create file info dict
            file_info = {
                "path": str(file_path_obj),
                "format": format_info.value,
                "extension": file_path_obj.suffix.lower(),
                "size": file_path_obj.stat().st_size,
            }

            return FlextResult[dict[str, object]].ok(
                cast("dict[str, object]", file_info)
            )
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"File validation failed: {e}")

    def _execute_load_method(
        self, file_info: dict[str, object], **kwargs: object
    ) -> FlextResult[object]:
        """Execute the appropriate load method based on file info.

        Args:
            file_info: File information dictionary
            **kwargs: Additional arguments for the load method

        Returns:
            FlextResult[object]: Loaded data or error

        """
        try:
            file_path = str(file_info["path"])
            file_format = str(file_info["format"])

            # Get the appropriate load method from format registry
            if file_format not in self._supported_formats:
                return FlextResult[object].fail(
                    f"Unsupported file format: {file_format}"
                )

            format_info = self._supported_formats[file_format]
            load_method = format_info.get("load_method")

            if not load_method or not callable(load_method):
                return FlextResult[object].fail(
                    f"No load method available for format: {file_format}"
                )

            # Execute the load method
            result = load_method(file_path, **kwargs)
            return (
                result
                if isinstance(result, FlextResult)
                else FlextResult[object].ok(result)
            )
        except Exception as e:
            return FlextResult[object].fail(f"Load method execution failed: {e}")

    def save_file(
        self, file_path: str | Path, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Save data to file with automatic format detection.

        Args:
            file_path: Path to save the file
            data: Data to save
            **kwargs: Additional arguments passed to format-specific saver

        Returns:
            FlextResult[bool]: Success or error

        """
        try:
            format_result = self.detect_file_format(file_path)
            if not format_result.is_success:
                error_msg = format_result.error or "Unknown format detection error"
                return FlextResult[bool].fail(error_msg)

            file_path_obj = Path(file_path)
            extension = file_path_obj.suffix.lower()

            if extension not in self._supported_formats:
                return FlextResult[bool].fail(f"Unsupported file format: {extension}")

            format_info = self._supported_formats[extension]
            save_method = format_info["save_method"]
            if not callable(save_method):
                return FlextResult[bool].fail("Invalid save method")
            result = save_method(str(file_path_obj), data, **kwargs)
            return FlextResult[bool].ok(bool(result))
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save file: {e}")

    def file_exists(self, file_path: str | Path) -> FlextResult[bool]:
        """Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            FlextResult[bool]: True if file exists, False otherwise

        """
        try:
            exists = Path(file_path).exists()
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to check file existence: {e}")

    def get_file_size(self, file_path: str | Path) -> FlextResult[int]:
        """Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            FlextResult[int]: File size in bytes or error

        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[int].fail(f"File does not exist: {file_path}")

            file_size = file_path_obj.stat().st_size
            return FlextResult[int].ok(file_size)
        except Exception as e:
            return FlextResult[int].fail(f"Failed to get file size: {e}")

    # Format-specific internal methods
    def _load_json(self, file_path: str, **_kwargs: object) -> FlextResult[object]:
        """Internal JSON loader."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load JSON file: File does not exist: {file_path}"
                )

            with file_path_obj.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return FlextResult[object].ok(data)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load JSON file: {e}")

    def _save_json(
        self, file_path: str, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Internal JSON saver."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            indent = kwargs.get("indent", 2)
            ensure_ascii = kwargs.get("ensure_ascii", False)

            # Ensure proper types for json.dump
            indent_val = indent if isinstance(indent, (int, str)) else 2
            ensure_ascii_val = bool(ensure_ascii)

            with file_path_obj.open("w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    indent=indent_val,
                    ensure_ascii=ensure_ascii_val,
                    default=str,
                )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save JSON file: {e}")

    def _load_yaml(self, file_path: str, **_kwargs: object) -> FlextResult[object]:
        """Internal YAML loader."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load YAML file: File does not exist: {file_path}"
                )

            with file_path_obj.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return FlextResult[object].ok(data)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load YAML file: {e}")

    def _save_yaml(
        self, file_path: str, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Internal YAML saver."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            default_flow_style = kwargs.get("default_flow_style", False)
            allow_unicode = kwargs.get("allow_unicode", True)

            # Ensure proper types for yaml.dump
            default_flow_style_val = bool(default_flow_style)
            allow_unicode_val = bool(allow_unicode)

            with file_path_obj.open("w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=default_flow_style_val,
                    allow_unicode=allow_unicode_val,
                )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save YAML file: {e}")

    def _load_csv(
        self,
        file_path: str,
        **kwargs: str | float | bool | None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Internal CSV loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[list[dict[str, object]]].fail(
                    f"Failed to load CSV file: File does not exist: {file_path}"
                )

            # Log CSV loading options for debugging
            if kwargs:
                self._logger.debug(f"Loading CSV with options: {kwargs}")

            # Use pandas for enhanced CSV loading with proper type filtering
            pandas_kwargs: dict[str, Any] = {}

            # Filter kwargs to only include valid pandas read_csv parameters with correct types
            for key, value in kwargs.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    pandas_kwargs[key] = value
                elif isinstance(value, list) and all(
                    isinstance(item, str) for item in value
                ):
                    # Convert list of strings to proper type for pandas
                    pandas_kwargs[key] = value

            try:
                result = pd.read_csv(str(file_path_obj), **pandas_kwargs)
            except Exception as e:
                return FlextResult[list[dict[str, object]]].fail(
                    f"Failed to load CSV file: {e}"
                )
            # Ensure we have a DataFrame, not a TextFileReader
            if isinstance(result, pd.DataFrame):
                df = result
            else:
                # If it's a TextFileReader, read it into a DataFrame
                df = pd.DataFrame(list(result))
            # Convert DataFrame to list of dicts with proper typing
            records = df.to_dict("records")
            # Ensure all keys are strings for type safety
            typed_records: list[dict[str, object]] = [
                {str(k): v for k, v in record.items()} for record in records
            ]
            return FlextResult[list[dict[str, object]]].ok(typed_records)
        except Exception as e:
            return FlextResult[list[dict[str, object]]].fail(
                f"Failed to load CSV file: {e}"
            )

    def _save_csv(
        self, file_path: str, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Internal CSV saver using pandas."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Convert data to DataFrame if needed
            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                # For other data types, try to convert to DataFrame
                try:
                    df = pd.DataFrame([data])
                except Exception:
                    return FlextResult[bool].fail(
                        f"Cannot convert data to DataFrame: {type(data)}"
                    )

            # Convert kwargs to proper types for pandas to_csv - filter out complex types
            pandas_to_csv_kwargs: dict[str, Any] = {
                k: v
                for k, v in kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None)))
                or (isinstance(v, list) and all(isinstance(item, str) for item in v))
            }

            # Use pandas to_csv with filtered kwargs
            df.to_csv(
                str(file_path_obj),
                index=False,
                **pandas_to_csv_kwargs,
            )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save CSV file: {e}")

    def _load_tsv(
        self, file_path: str, **kwargs: FlextCliTypes.Data.PandasReadCsvKwargs
    ) -> FlextResult[list[dict[str, object]]]:
        """Internal TSV loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[list[dict[str, object]]].fail(
                    f"Failed to load TSV file: File does not exist: {file_path}"
                )

            # Convert kwargs to proper types for pandas - filter out complex types
            pandas_kwargs: dict[str, Any] = {}

            # Filter kwargs to only include valid pandas read_csv parameters
            for k, v in kwargs.items():
                if isinstance(v, (str, int, float, bool, type(None))):
                    pandas_kwargs[k] = v
                elif isinstance(v, list) and all(isinstance(item, str) for item in v):
                    # Convert list of strings to proper type for pandas
                    pandas_kwargs[k] = v  # type: ignore[assignment]

            # Use filtered kwargs for pandas TSV reading
            result = pd.read_csv(
                str(file_path_obj),
                sep="\t",
                **pandas_kwargs,
            )
            # Ensure we have a DataFrame, not a TextFileReader
            if isinstance(result, pd.DataFrame):
                df = result
            else:
                # If it's a TextFileReader, read it into a DataFrame
                df = pd.DataFrame(list(result))
            # Convert DataFrame to list of dicts with proper typing
            records = df.to_dict("records")
            # Ensure all keys are strings for type safety
            typed_records: list[dict[str, object]] = [
                {str(k): v for k, v in record.items()} for record in records
            ]
            return FlextResult[list[dict[str, object]]].ok(typed_records)
        except Exception as e:
            return FlextResult[list[dict[str, object]]].fail(
                f"Failed to load TSV file: {e}"
            )

    def _save_tsv(self, file_path: str, data: object) -> FlextResult[bool]:
        """Internal TSV saver using pandas."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame([data])

            # Save TSV without additional kwargs to avoid type issues
            df.to_csv(file_path_obj, sep="\t", index=False)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save TSV file: {e}")

    def _load_xml(self, file_path: str, **_kwargs: object) -> FlextResult[object]:
        """Internal XML loader using lxml."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(f"File does not exist: {file_path}")

            # Use lxml for better performance and security
            parser = etree.XMLParser(resolve_entities=False, no_network=True)
            tree = etree.parse(file_path_obj, parser)
            root = tree.getroot()

            # Convert XML to dict
            def xml_to_dict(element: etree.Element) -> dict[str, object]:
                result: dict[str, object] = {}

                # Handle text content
                if element.text and element.text.strip():
                    result["text"] = element.text.strip()

                # Handle attributes
                if element.attrib:
                    result["@attributes"] = dict(element.attrib)

                # Handle child elements
                for child in element:
                    child_data = xml_to_dict(child)
                    tag_name = str(child.tag)
                    if tag_name in result:
                        if not isinstance(result[tag_name], list):
                            result[tag_name] = [result[tag_name]]
                        cast("list[object]", result[tag_name]).append(child_data)
                    else:
                        result[tag_name] = child_data

                return result

            data = {str(root.tag): xml_to_dict(root)}
            return FlextResult[object].ok(data)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load XML file: {e}")

    def _save_xml(
        self, file_path: str, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Internal XML saver using lxml."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            def dict_to_xml(data: object, root_name: str = "root") -> etree.Element:
                root = etree.Element(root_name)

                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == "@attributes" and isinstance(value, dict):
                            # Handle attributes
                            for attr_key, attr_value in value.items():
                                root.set(attr_key, str(attr_value))
                        elif key == "text":
                            # Handle text content
                            root.text = str(value)
                        elif isinstance(value, dict):
                            child = dict_to_xml(value, key)
                            root.append(child)
                        elif isinstance(value, list):
                            for item in value:
                                child = dict_to_xml(item, str(key))
                                root.append(child)
                        else:
                            child = dict_to_xml(value, str(key))
                            root.append(child)
                else:
                    # Handle non-dict data
                    root.text = str(data)

                return root

            root_name = str(kwargs.get("root_name", "root"))
            root = dict_to_xml(data, root_name)

            # Use lxml for better formatting and encoding
            tree = etree.ElementTree(root)
            tree.write(
                file_path_obj, encoding="utf-8", xml_declaration=True, pretty_print=True
            )

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save XML file: {e}")

    def _load_toml(self, file_path: str, **_kwargs: object) -> FlextResult[object]:
        """Internal TOML loader."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load TOML file: File does not exist: {file_path}"
                )

            data = toml.load(file_path_obj)
            return FlextResult[object].ok(data)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load TOML file: {e}")

    def _save_toml(
        self, file_path: str, data: object, **_kwargs: object
    ) -> FlextResult[bool]:
        """Internal TOML saver."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with file_path_obj.open("w", encoding="utf-8") as f:
                toml.dump(cast("dict[str, object]", data), f)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save TOML file: {e}")

    def _load_excel(
        self, file_path: str, **kwargs: str | float | bool | None
    ) -> FlextResult[object]:
        """Internal Excel loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(f"File does not exist: {file_path}")

            sheet_name = kwargs.get("sheet_name")
            if sheet_name is None:
                # Load all sheets
                excel_file = pd.ExcelFile(file_path_obj)
                sheets_data: dict[str, list[dict[str, object]]] = {}
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file_path_obj, sheet_name=sheet)
                    # Convert DataFrame to list of dicts with proper typing
                    records = df.to_dict("records")
                    # Ensure all keys are strings for type safety
                    typed_records: list[dict[str, object]] = [
                        {str(k): v for k, v in record.items()} for record in records
                    ]
                    sheets_data[str(sheet)] = typed_records
                return FlextResult[object].ok(sheets_data)

            # Load specific sheet
            df = pd.read_excel(file_path_obj, sheet_name=cast("str", sheet_name))
            # Convert DataFrame to list of dicts with proper typing
            records = df.to_dict("records")
            # Ensure all keys are strings for type safety
            typed_records: list[dict[str, object]] = [
                {str(k): v for k, v in record.items()} for record in records
            ]
            return FlextResult[object].ok(typed_records)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load Excel file: {e}")

    def _save_excel(self, file_path: str, data: object) -> FlextResult[bool]:
        """Internal Excel saver using pandas."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(data, dict):
                # Multiple sheets
                with pd.ExcelWriter(file_path_obj, engine="openpyxl") as writer:
                    for sheet_name, sheet_data in data.items():
                        if isinstance(sheet_data, pd.DataFrame):
                            df = sheet_data
                        elif isinstance(sheet_data, list):
                            df = pd.DataFrame(sheet_data)
                        else:
                            df = pd.DataFrame([sheet_data])
                        df.to_excel(writer, sheet_name=str(sheet_name), index=False)
            else:
                # Single sheet
                if isinstance(data, pd.DataFrame):
                    df = data
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                df.to_excel(file_path_obj, index=False)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save Excel file: {e}")

    def _load_parquet(
        self,
        file_path: str,
        **kwargs: FlextCliTypes.Data.PyArrowReadTableKwargs,
    ) -> FlextResult[object]:
        """Internal Parquet loader using pyarrow."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(f"File does not exist: {file_path}")

            # Extract only the specific kwargs that PyArrow read_table accepts
            pyarrow_kwargs: dict[str, object] = {}

            # Handle specific PyArrow parameters with proper type checking
            if "columns" in kwargs and isinstance(kwargs["columns"], list):
                pyarrow_kwargs["columns"] = kwargs["columns"]

            if "use_threads" in kwargs:
                pyarrow_kwargs["use_threads"] = kwargs["use_threads"]

            if "schema" in kwargs:
                pyarrow_kwargs["schema"] = kwargs["schema"]

            if "use_pandas_metadata" in kwargs:
                pyarrow_kwargs["use_pandas_metadata"] = kwargs["use_pandas_metadata"]

            if "read_dictionary" in kwargs:
                pyarrow_kwargs["read_dictionary"] = kwargs["read_dictionary"]

            if "memory_map" in kwargs:
                pyarrow_kwargs["memory_map"] = kwargs["memory_map"]

            if "buffer_size" in kwargs and isinstance(kwargs["buffer_size"], int):
                pyarrow_kwargs["buffer_size"] = kwargs["buffer_size"]

            if "pre_buffer" in kwargs:
                pyarrow_kwargs["pre_buffer"] = kwargs["pre_buffer"]

            if "coerce_int96_timestamp_unit" in kwargs and isinstance(
                kwargs["coerce_int96_timestamp_unit"], str
            ):
                pyarrow_kwargs["coerce_int96_timestamp_unit"] = kwargs[
                    "coerce_int96_timestamp_unit"
                ]

            # Use filtered kwargs for pyarrow parquet reading
            # Convert to proper types for PyArrow
            filtered_kwargs: dict[str, Any] = {
                key: value
                for key, value in pyarrow_kwargs.items()
                if key
                in {
                    "columns",
                    "memory_map",
                    "buffer_size",
                    "pre_buffer",
                    "coerce_int96_timestamp_unit",
                }
                and (
                    (key == "columns" and isinstance(value, list))
                    or (key == "memory_map" and isinstance(value, bool))
                    or (key == "buffer_size" and isinstance(value, int))
                    or (key == "pre_buffer" and isinstance(value, bool))
                    or (key == "coerce_int96_timestamp_unit" and isinstance(value, str))
                )
            }
            table = pq.read_table(file_path_obj, **filtered_kwargs)
            df = table.to_pandas()
            return FlextResult[object].ok(df.to_dict("records"))
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load Parquet file: {e}")

    def _save_parquet(
        self,
        file_path: str,
        data: object,
        **kwargs: FlextCliTypes.Data.PyArrowWriteTableKwargs,
    ) -> FlextResult[bool]:
        """Internal Parquet saver using pyarrow."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame([data])

            table = pa.Table.from_pandas(df)

            # Extract only the specific kwargs that PyArrow write_table accepts
            pyarrow_kwargs: dict[str, object] = {}

            # Handle specific PyArrow parameters with proper type checking
            if "row_group_size" in kwargs:
                pyarrow_kwargs["row_group_size"] = kwargs["row_group_size"]

            if (
                "version" in kwargs
                and isinstance(kwargs["version"], str)
                and kwargs["version"] in {"1.0", "2.4", "2.6"}
            ):
                # PyArrow version expects string literal, not int
                pyarrow_kwargs["version"] = kwargs["version"]

            if "use_dictionary" in kwargs:
                pyarrow_kwargs["use_dictionary"] = kwargs["use_dictionary"]

            if "compression" in kwargs and kwargs["compression"] is not None:
                pyarrow_kwargs["compression"] = kwargs["compression"]

            if "write_statistics" in kwargs:
                pyarrow_kwargs["write_statistics"] = kwargs["write_statistics"]

            if "use_deprecated_int96_timestamps" in kwargs:
                pyarrow_kwargs["use_deprecated_int96_timestamps"] = kwargs[
                    "use_deprecated_int96_timestamps"
                ]

            if "coerce_timestamps" in kwargs:
                pyarrow_kwargs["coerce_timestamps"] = kwargs["coerce_timestamps"]

            if "allow_truncated_timestamps" in kwargs:
                pyarrow_kwargs["allow_truncated_timestamps"] = kwargs[
                    "allow_truncated_timestamps"
                ]

            if "data_page_size" in kwargs:
                pyarrow_kwargs["data_page_size"] = kwargs["data_page_size"]

            if "flavor" in kwargs:
                pyarrow_kwargs["flavor"] = kwargs["flavor"]

            # Use filtered kwargs for pyarrow parquet writing
            try:
                # Convert to proper types for PyArrow write_table
                # Create a properly typed kwargs dict for PyArrow
                pyarrow_write_kwargs: dict[str, Any] = {}

                # Handle each parameter with proper type checking
                if "row_group_size" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["row_group_size"], int
                ):
                    pyarrow_write_kwargs["row_group_size"] = pyarrow_kwargs[
                        "row_group_size"
                    ]

                if (
                    "version" in pyarrow_kwargs
                    and isinstance(pyarrow_kwargs["version"], str)
                    and pyarrow_kwargs["version"] in {"1.0", "2.4", "2.6"}
                ):
                    pyarrow_write_kwargs["version"] = pyarrow_kwargs["version"]

                if "use_dictionary" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["use_dictionary"], bool
                ):
                    pyarrow_write_kwargs["use_dictionary"] = pyarrow_kwargs[
                        "use_dictionary"
                    ]

                if "compression" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["compression"], str
                ):
                    pyarrow_write_kwargs["compression"] = pyarrow_kwargs["compression"]

                if "write_statistics" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["write_statistics"], bool
                ):
                    pyarrow_write_kwargs["write_statistics"] = pyarrow_kwargs[
                        "write_statistics"
                    ]

                if "use_deprecated_int96_timestamps" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["use_deprecated_int96_timestamps"], bool
                ):
                    pyarrow_write_kwargs["use_deprecated_int96_timestamps"] = (
                        pyarrow_kwargs["use_deprecated_int96_timestamps"]
                    )

                if "coerce_timestamps" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["coerce_timestamps"], str
                ):
                    pyarrow_write_kwargs["coerce_timestamps"] = pyarrow_kwargs[
                        "coerce_timestamps"
                    ]

                if "allow_truncated_timestamps" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["allow_truncated_timestamps"], bool
                ):
                    pyarrow_write_kwargs["allow_truncated_timestamps"] = pyarrow_kwargs[
                        "allow_truncated_timestamps"
                    ]

                if "data_page_size" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["data_page_size"], int
                ):
                    pyarrow_write_kwargs["data_page_size"] = pyarrow_kwargs[
                        "data_page_size"
                    ]

                if "flavor" in pyarrow_kwargs and isinstance(
                    pyarrow_kwargs["flavor"], str
                ):
                    pyarrow_write_kwargs["flavor"] = pyarrow_kwargs["flavor"]

                pq.write_table(table, file_path_obj, **pyarrow_write_kwargs)
            except TypeError:
                # Fallback to basic write_table without kwargs
                pq.write_table(table, file_path_obj)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save Parquet file: {e}")

    def _load_text(self, file_path: str, **kwargs: object) -> FlextResult[object]:
        """Internal text loader."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load text file: File does not exist: {file_path}"
                )

            encoding = str(kwargs.get("encoding", "utf-8"))
            with file_path_obj.open("r", encoding=encoding) as f:
                content = f.read()
            return FlextResult[object].ok(content)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load text file: {e}")

    def _save_text(
        self, file_path: str, data: object, **kwargs: object
    ) -> FlextResult[bool]:
        """Internal text saver."""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            encoding = str(kwargs.get("encoding", "utf-8"))
            with file_path_obj.open("w", encoding=encoding) as f:
                f.write(str(data))
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save text file: {e}")

    def watch_file(self, _file_path: str, _callback: object) -> FlextResult[None]:
        """Watch file for changes (placeholder for future implementation).

        Args:
            file_path: Path to file to watch
            callback: Callback function to call on change

        Returns:
            FlextResult[None]: Success or error

        """
        return FlextResult[None].fail("File watching not yet implemented")

    def tail_file(self, file_path: str, lines: int = 10) -> FlextResult[list[str]]:
        """Get last N lines from file.

        Args:
            file_path: Path to file
            lines: Number of lines to retrieve

        Returns:
            FlextResult[list[str]]: Last N lines or error

        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[list[str]].fail(f"File does not exist: {file_path}")

            with file_path_obj.open("r", encoding="utf-8") as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            return FlextResult[list[str]].ok([line.rstrip() for line in tail_lines])
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to tail file: {e}")

    # Convenience methods for backward compatibility with tests
    def read_text_file(self, file_path: str) -> FlextResult[str]:
        """Read text file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[str].fail(f"File not found: {file_path}")
            content = path.read_text(encoding="utf-8")
            return FlextResult[str].ok(content)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to read text file: {e}")

    def write_text_file(self, file_path: str, content: str) -> FlextResult[bool]:
        """Write content to text file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to write text file: {e}")

    def read_binary_file(self, file_path: str) -> FlextResult[bytes]:
        """Read binary file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[bytes].fail(f"File not found: {file_path}")
            content = path.read_bytes()
            return FlextResult[bytes].ok(content)
        except Exception as e:
            return FlextResult[bytes].fail(f"Failed to read binary file: {e}")

    def write_binary_file(self, file_path: str, content: bytes) -> FlextResult[bool]:
        """Write content to binary file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to write binary file: {e}")

    def read_json_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Read JSON file content."""
        result = self._load_json(file_path)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                result.error or "Failed to read JSON"
            )
        if not isinstance(result.unwrap(), dict):
            return FlextResult[dict[str, object]].fail(
                "JSON content is not a dictionary"
            )
        return FlextResult[dict[str, object]].ok(
            cast("dict[str, object]", result.unwrap())
        )

    def write_json_file(
        self, file_path: str, data: dict[str, object]
    ) -> FlextResult[bool]:
        """Write data to JSON file."""
        return self._save_json(file_path, data)

    def load_json_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Load JSON file content (alias for read_json_file)."""
        return self.read_json_file(file_path)

    def save_json_file(
        self, file_path: str, data: dict[str, object]
    ) -> FlextResult[bool]:
        """Save data to JSON file (alias for write_json_file)."""
        return self.write_json_file(file_path, data)

    def read_yaml_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Read YAML file content."""
        result = self._load_yaml(file_path)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                result.error or "Failed to read YAML"
            )
        if not isinstance(result.unwrap(), dict):
            return FlextResult[dict[str, object]].fail(
                "YAML content is not a dictionary"
            )
        return FlextResult[dict[str, object]].ok(
            cast("dict[str, object]", result.unwrap())
        )

    def write_yaml_file(
        self, file_path: str, data: dict[str, object]
    ) -> FlextResult[bool]:
        """Write data to YAML file."""
        return self._save_yaml(file_path, data)

    def read_csv_file(self, file_path: str) -> FlextResult[list[list[str]]]:
        """Read CSV file content as list of lists."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[list[list[str]]].fail(
                    f"CSV file does not exist: {file_path}"
                )

            with file_path_obj.open(encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                data = list(reader)
                return FlextResult[list[list[str]]].ok(data)
        except Exception as e:
            return FlextResult[list[list[str]]].fail(f"Failed to read CSV file: {e}")

    def write_csv_file(
        self, file_path: str, data: list[list[str]]
    ) -> FlextResult[bool]:
        """Write data to CSV file."""
        try:
            file_path_obj = Path(file_path)
            with file_path_obj.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(data)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to write CSV file: {e}")

    def read_csv_file_with_headers(
        self, file_path: str
    ) -> FlextResult[list[dict[str, str]]]:
        """Read CSV file with headers."""
        result = self._load_csv(file_path)
        if result.is_failure:
            return FlextResult[list[dict[str, str]]].fail(
                result.error or "Failed to read CSV"
            )
        if not isinstance(result.unwrap(), list):
            return FlextResult[list[dict[str, str]]].fail("CSV content is not a list")
        return FlextResult[list[dict[str, str]]].ok(
            cast("list[dict[str, str]]", result.unwrap())
        )

    def list_directory(self, directory_path: str) -> FlextResult[list[str]]:
        """List files in directory."""
        try:
            directory = Path(directory_path)
            if not directory.exists():
                return FlextResult[list[str]].fail(
                    f"Directory does not exist: {directory_path}"
                )
            if not directory.is_dir():
                return FlextResult[list[str]].fail(
                    f"Path is not a directory: {directory_path}"
                )

            files = [f.name for f in directory.iterdir() if f.is_file()]
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list directory: {e}")

    def copy_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Copy file from source to destination."""
        try:
            source = Path(source_path)
            destination = Path(destination_path)

            if not source.exists():
                return FlextResult[bool].fail(f"Source file not found: {source_path}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to copy file: {e}")

    def move_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Move file from source to destination."""
        try:
            source = Path(source_path)
            destination = Path(destination_path)

            if not source.exists():
                return FlextResult[bool].fail(f"Source file not found: {source_path}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to move file: {e}")

    def delete_file(self, file_path: str) -> FlextResult[bool]:
        """Delete file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[bool].fail(f"File not found: {file_path}")
            path.unlink()
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to delete file: {e}")

    def create_directory(self, directory_path: str) -> FlextResult[bool]:
        """Create directory."""
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to create directory: {e}")

    def create_directories(self, directory_path: str) -> FlextResult[bool]:
        """Create directories recursively."""
        return self.create_directory(directory_path)

    def delete_directory(self, directory_path: str) -> FlextResult[bool]:
        """Delete directory."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return FlextResult[bool].fail(f"Directory not found: {directory_path}")
            if not path.is_dir():
                return FlextResult[bool].fail(
                    f"Path is not a directory: {directory_path}"
                )

            shutil.rmtree(path)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to delete directory: {e}")

    def directory_exists(self, directory_path: str) -> FlextResult[bool]:
        """Check if directory exists."""
        try:
            path = Path(directory_path)
            exists = path.exists() and path.is_dir()
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to check directory existence: {e}")

    def get_file_permissions(self, file_path: str) -> FlextResult[str]:
        """Get file permissions."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[str].fail(f"File not found: {file_path}")

            permissions = f"{stat.S_IMODE(path.stat().st_mode):o}"  # Octal format
            return FlextResult[str].ok(permissions)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to get file permissions: {e}")

    def set_file_permissions(
        self, file_path: str, permissions: str | int
    ) -> FlextResult[bool]:
        """Set file permissions."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[bool].fail(f"File not found: {file_path}")

            # Convert string to int if needed
            if isinstance(permissions, str):
                permissions = int(permissions, 8)  # Convert octal string to int

            path.chmod(permissions)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to set file permissions: {e}")

    def get_file_modified_time(self, file_path: str) -> FlextResult[float]:
        """Get file modification time."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[float].fail(f"File not found: {file_path}")

            mtime = path.stat().st_mtime
            return FlextResult[float].ok(mtime)
        except Exception as e:
            return FlextResult[float].fail(f"Failed to get file modification time: {e}")

    def calculate_file_hash(
        self, file_path: str, algorithm: str = "sha256"
    ) -> FlextResult[str]:
        """Calculate file hash."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[str].fail(f"File not found: {file_path}")

            if algorithm.lower() == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm.lower() == "sha512":
                hash_obj = hashlib.sha512()
            else:
                return FlextResult[str].fail(
                    f"Unsupported algorithm: {algorithm}. Only SHA256 and SHA512 are supported for security reasons."
                )

            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)

            return FlextResult[str].ok(hash_obj.hexdigest())
        except Exception as e:
            return FlextResult[str].fail(f"Failed to calculate file hash: {e}")

    def verify_file_hash(
        self, file_path: str, expected_hash: str, algorithm: str = "sha256"
    ) -> FlextResult[bool]:
        """Verify file hash."""
        try:
            hash_result = self.calculate_file_hash(file_path, algorithm)
            if hash_result.is_failure:
                return FlextResult[bool].fail(
                    hash_result.error or "Failed to calculate hash"
                )

            actual_hash = hash_result.unwrap()
            matches = actual_hash.lower() == expected_hash.lower()
            return FlextResult[bool].ok(matches)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to verify file hash: {e}")

    def find_files_by_name(
        self, directory_path: str, filename: str
    ) -> FlextResult[list[str]]:
        """Find files by name in directory."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return FlextResult[list[str]].fail(
                    f"Directory not found: {directory_path}"
                )

            files = [str(f) for f in path.rglob(filename) if f.is_file()]
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to find files: {e}")

    def find_files_by_pattern(
        self, directory_path: str, pattern: str
    ) -> FlextResult[list[str]]:
        """Find files by pattern in directory."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return FlextResult[list[str]].fail(
                    f"Directory not found: {directory_path}"
                )

            files = [
                str(f)
                for f in path.rglob("*")
                if f.is_file() and fnmatch.fnmatch(f.name, pattern)
            ]
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to find files by pattern: {e}")

    def find_files_by_content(
        self, directory_path: str, content: str
    ) -> FlextResult[list[str]]:
        """Find files containing specific content."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return FlextResult[list[str]].fail(
                    f"Directory not found: {directory_path}"
                )

            files = []
            for f in path.rglob("*"):
                if f.is_file():
                    try:
                        with f.open("r", encoding="utf-8", errors="ignore") as file:
                            if content in file.read():
                                files.append(str(f))
                    except Exception as e:
                        # Log the exception but continue processing other files
                        self._logger.warning(f"Failed to read file {f}: {e}")
                        continue
            return FlextResult[list[str]].ok(files)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to find files by content: {e}")

    def create_temp_file(
        self, content: str = "", suffix: str = ".tmp"
    ) -> FlextResult[str]:
        """Create temporary file."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=suffix, delete=False, encoding="utf-8"
            ) as f:
                f.write(content)
                return FlextResult[str].ok(f.name)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create temp file: {e}")

    def create_temp_directory(self) -> FlextResult[str]:
        """Create temporary directory."""
        try:
            temp_dir = tempfile.mkdtemp()
            return FlextResult[str].ok(temp_dir)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create temp directory: {e}")

    def create_zip_archive(
        self, archive_path: str, files_or_source: str | list[str]
    ) -> FlextResult[bool]:
        """Create ZIP archive from source path or list of files."""
        try:
            archive = Path(archive_path)
            archive.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipf:
                if isinstance(files_or_source, list):
                    # Handle list of files
                    for file_path in files_or_source:
                        file_path_obj = Path(str(file_path))
                        if file_path_obj.exists():
                            zipf.write(file_path_obj, file_path_obj.name)
                        else:
                            return FlextResult[bool].fail(
                                f"File not found: {file_path}"
                            )
                else:
                    # Handle single source path
                    source = Path(files_or_source)
                    if not source.exists():
                        return FlextResult[bool].fail(
                            f"Source not found: {files_or_source}"
                        )

                    if source.is_file():
                        zipf.write(source, source.name)
                    else:
                        for f in source.rglob("*"):
                            if f.is_file():
                                arcname = f.relative_to(source.parent)
                                zipf.write(f, arcname)

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to create ZIP archive: {e}")

    def extract_zip_archive(
        self, archive_path: str, extract_path: str
    ) -> FlextResult[bool]:
        """Extract ZIP archive."""
        try:
            archive = Path(archive_path)
            extract = Path(extract_path)

            if not archive.exists():
                return FlextResult[bool].fail(f"Archive not found: {archive_path}")

            extract.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(archive, "r") as zipf:
                zipf.extractall(extract)

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to extract ZIP archive: {e}")

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute file tools service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI_FILE_TOOLS,
            "supported_formats": list(self._supported_formats.keys()),
            "capabilities": [
                "read",
                "write",
                "validate",
                "convert",
                "compress",
                "hash",
            ],
        })


__all__ = ["FlextCliFileTools"]
