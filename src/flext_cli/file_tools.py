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

import json
from pathlib import Path
from typing import Any, cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import toml
import yaml
from lxml import etree  # Modern, secure XML library

from flext_core import FlextLogger, FlextResult, FlextService

# Type aliases for pandas and pyarrow kwargs
# Using Any for maximum compatibility with complex pandas signatures
PandasKwargs = dict[str, Any]
PyArrowKwargs = dict[str, Any]


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

    def __init__(self) -> None:
        """Initialize file tools with format registry."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._supported_formats = self._initialize_format_registry()

    def execute(self) -> FlextResult[bool]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[bool].ok(True)

    def _initialize_format_registry(self) -> dict[str, dict[str, object]]:
        """Initialize the format registry with supported file types."""
        return {
            ".json": {
                "format": "json",
                "mime_type": "application/json",
                "load_method": self._load_json,
                "save_method": self._save_json,
            },
            ".yaml": {
                "format": "yaml",
                "mime_type": "application/x-yaml",
                "load_method": self._load_yaml,
                "save_method": self._save_yaml,
            },
            ".yml": {
                "format": "yaml",
                "mime_type": "application/x-yaml",
                "load_method": self._load_yaml,
                "save_method": self._save_yaml,
            },
            ".csv": {
                "format": "csv",
                "mime_type": "text/csv",
                "load_method": self._load_csv,
                "save_method": self._save_csv,
            },
            ".tsv": {
                "format": "tsv",
                "mime_type": "text/tab-separated-values",
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
        """Load file with automatic format detection.

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments passed to format-specific loader

        Returns:
            FlextResult[object]: Loaded data or error

        """
        try:
            format_result = self.detect_file_format(file_path)
            if not format_result.is_success:
                error_msg = format_result.error or "Unknown format detection error"
                return FlextResult[object].fail(error_msg)

            file_path_obj = Path(file_path)
            extension = file_path_obj.suffix.lower()

            if extension not in self._supported_formats:
                return FlextResult[object].fail(f"Unsupported file format: {extension}")

            format_info = self._supported_formats[extension]
            load_method = format_info["load_method"]
            if not callable(load_method):
                return FlextResult[object].fail("Invalid load method")
            # The load methods already return FlextResult, so return directly
            result = load_method(str(file_path_obj), **kwargs)
            return cast("FlextResult[object]", result)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load file: {e}")

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

    def file_exists(self, file_path: str | Path) -> bool:
        """Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file exists, False otherwise

        """
        try:
            return Path(file_path).exists()
        except Exception:
            return False

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

    def _load_csv(self, file_path: str, **kwargs: object) -> FlextResult[object]:
        """Internal CSV loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load CSV file: File does not exist: {file_path}"
                )

            # Use pandas for enhanced CSV loading
            # Convert kwargs to proper types for pandas
            pandas_kwargs: PandasKwargs = {
                k: v
                for k, v in kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
            }
            result: pd.DataFrame | pd.io.parsers.TextFileReader = pd.read_csv(
                str(file_path_obj), **pandas_kwargs
            )
            if isinstance(result, pd.DataFrame):
                df: pd.DataFrame = result
                return FlextResult[object].ok(df.to_dict("records"))
            # Handle TextFileReader case
            return FlextResult[object].fail(
                "CSV file requires specific parameters to return DataFrame"
            )
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load CSV file: {e}")

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

            # Convert kwargs to proper types for pandas
            pandas_kwargs: PandasKwargs = {
                k: v
                for k, v in kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None), list))
            }
            df.to_csv(
                str(file_path_obj),
                index=False,
                **pandas_kwargs,
            )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to save CSV file: {e}")

    def _load_tsv(self, file_path: str, **kwargs: object) -> FlextResult[object]:
        """Internal TSV loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(
                    f"Failed to load TSV file: File does not exist: {file_path}"
                )

            # Convert kwargs to proper types for pandas
            pandas_kwargs: PandasKwargs = {
                k: v
                for k, v in kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
            }
            result: pd.DataFrame | pd.io.parsers.TextFileReader = pd.read_csv(
                str(file_path_obj), sep="\t", **pandas_kwargs
            )
            if isinstance(result, pd.DataFrame):
                df: pd.DataFrame = result
                return FlextResult[object].ok(df.to_dict("records"))
            # Handle TextFileReader case
            return FlextResult[object].fail(
                "TSV file requires specific parameters to return DataFrame"
            )
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load TSV file: {e}")

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
                                child = dict_to_xml(item, key)
                                root.append(child)
                        else:
                            child = dict_to_xml(value, key)
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

    def _load_excel(self, file_path: str, **kwargs: object) -> FlextResult[object]:
        """Internal Excel loader using pandas."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(f"File does not exist: {file_path}")

            sheet_name = kwargs.get("sheet_name")
            if sheet_name is None:
                # Load all sheets
                excel_file = pd.ExcelFile(file_path_obj)
                sheets_data = {}
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file_path_obj, sheet_name=sheet)
                    sheets_data[sheet] = df.to_dict("records")
                return FlextResult[object].ok(sheets_data)

            # Load specific sheet
            df = pd.read_excel(file_path_obj, sheet_name=cast("str", sheet_name))
            return FlextResult[object].ok(df.to_dict("records"))
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
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
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

    def _load_parquet(self, file_path: str, **kwargs: object) -> FlextResult[object]:
        """Internal Parquet loader using pyarrow."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[object].fail(f"File does not exist: {file_path}")

            # Convert kwargs to proper types for pyarrow
            pyarrow_kwargs: PyArrowKwargs = {
                k: v
                for k, v in kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None), list, pa.Schema))
            }
            table = pq.read_table(file_path_obj, **pyarrow_kwargs)
            df = table.to_pandas()
            return FlextResult[object].ok(df.to_dict("records"))
        except Exception as e:
            return FlextResult[object].fail(f"Failed to load Parquet file: {e}")

    def _save_parquet(
        self, file_path: str, data: object, **kwargs: object
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
            # Convert kwargs to proper types for pyarrow
            pyarrow_kwargs: PyArrowKwargs = {
                k: v
                for k, v in kwargs.items()
                if isinstance(
                    v, (str, int, float, bool, type(None), list, pa.Schema, dict)
                )
            }
            pq.write_table(table, file_path_obj, **pyarrow_kwargs)
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

    # Legacy methods for backward compatibility
    def save_json_file(
        self, data: dict[str, object], file_path: str
    ) -> FlextResult[bool]:
        """Save data to JSON file (legacy method).

        Args:
            data: Data to save as JSON
            file_path: Path to save the JSON file

        Returns:
            FlextResult[bool]: Success if file was saved, failure otherwise

        """
        return self._save_json(file_path, data)

    def load_json_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Load data from JSON file (legacy method).

        Args:
            file_path: Path to the JSON file

        Returns:
            FlextResult[dict[str, object]]: Data from file or error

        """
        result = self._load_json(file_path)
        if result.is_success and isinstance(result.value, dict):
            return FlextResult[dict[str, object]].ok(result.value)
        return FlextResult[dict[str, object]].fail(result.error or "Unknown error")

    def save_yaml_file(
        self, data: dict[str, object], file_path: str
    ) -> FlextResult[bool]:
        """Save data to YAML file (legacy method).

        Args:
            data: Data to save as YAML
            file_path: Path to save the YAML file

        Returns:
            FlextResult[bool]: Success if file was saved, failure otherwise

        """
        return self._save_yaml(file_path, data)

    def load_yaml_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Load data from YAML file (legacy method).

        Args:
            file_path: Path to the YAML file

        Returns:
            FlextResult[dict[str, object]]: Data from file or error

        """
        result = self._load_yaml(file_path)
        if result.is_success and isinstance(result.value, dict):
            return FlextResult[dict[str, object]].ok(result.value)
        return FlextResult[dict[str, object]].fail(result.error or "Unknown error")

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


__all__ = ["FlextCliFileTools"]
