"""FLEXT CLI Formatting - Unified formatting service consolidating all CLI output functionality.

Unified formatting service eliminating duplication between formatters.py and formatting_service.py.
Provides comprehensive Rich-based output formatting, multiple format support, and export capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from typing import Protocol

import yaml
from pydantic import BaseModel, ConfigDict, PrivateAttr
from rich.console import Console
from rich.table import Table

from flext_cli.constants import FlextCliConstants
from flext_cli.validations import FlextCliValidations
from flext_core import FlextLogger, FlextResult


class FormatterProtocol(Protocol):
    """Protocol for custom formatters with format method."""

    def format(self, data: object, **kwargs: object) -> str:
        """Format data and return string result."""
        ...


class FlextCliFormatters(BaseModel):
    """Unified CLI formatting service - consolidates all formatting functionality.

    Provides comprehensive output formatting capabilities including:
    - Rich-based table formatting with multiple styles
    - JSON, YAML, CSV output formats
    - Export functionality to files
    - Batch dataset processing
    - Custom formatter registration
    - Console output management

    Follows FLEXT unified class pattern with nested helper classes.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    class FormatterProtocol:
        """Protocol for custom formatters."""

        def format(self, data: object, **kwargs: object) -> str:
            """Format data according to protocol."""
            raise NotImplementedError

        def get_name(self) -> str:
            """Get formatter name."""
            raise NotImplementedError

    class _ConsoleOutput:
        """Nested helper for console output management."""

        def __init__(self) -> None:
            self._console = Console()

        def print_formatted(self, content: str, style: str = "") -> None:
            """Print formatted content with optional style."""
            if style:
                self._console.print(content, style=style)
            else:
                self._console.print(content)

        def get_console(self) -> Console:
            """Get console instance."""
            return self._console

    class _FormatValidationHelper:
        """Nested helper for format validation."""

        @staticmethod
        def validate_format_type(format_type: str) -> FlextResult[str]:
            """Validate format type using centralized validation."""
            return FlextCliValidations.validate_output_format(format_type)

        @staticmethod
        def validate_data_structure(data: object) -> FlextResult[object]:
            """Validate data structure for formatting."""
            if data is None:
                return FlextResult[object].fail("Data cannot be None")
            return FlextResult[object].ok(data)

    class _FilePathHelper:
        """Nested helper for file path operations."""

        @staticmethod
        def ensure_directory_exists(file_path: Path) -> FlextResult[Path]:
            """Ensure parent directory exists for file path."""
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                return FlextResult[Path].ok(file_path)
            except OSError as e:
                return FlextResult[Path].fail(f"Failed to create directory: {e}")

        @staticmethod
        def validate_file_path(file_path: str | Path) -> FlextResult[Path]:
            """Validate and convert file path."""
            try:
                path = Path(file_path)
                return FlextResult[Path].ok(path)
            except Exception as e:
                return FlextResult[Path].fail(f"Invalid file path: {e}")

    class _RichIntegrationHelper:
        """Nested helper for display integration features - abstracted from Rich."""

        def __init__(self) -> None:
            """Initialize display helper using flext-core abstractions."""

        def create_display_table(
            self,
            data: list[dict[str, object]],
            title: str = "",
            *,
            show_header: bool = True,
            show_lines: bool = False,
        ) -> dict[str, object]:
            """Create display table structure from data - Rich abstraction."""
            table_structure = {
                "title": title,
                "show_header": show_header,
                "show_lines": show_lines,
                "columns": [],
                "rows": [],
                "data": data,
            }

            if not data:
                return table_structure

            # Extract columns from first row
            table_structure["columns"] = list(data[0].keys())

            # Extract row data
            rows_list = table_structure["rows"]
            if isinstance(rows_list, list):
                for row in data:
                    rows_list.append(list(row.values()))

            return table_structure

        def display_table_structure(
            self, table_structure: dict[str, object]
        ) -> FlextResult[str]:
            """Display table structure using flext-core formatting - no direct Rich."""
            try:
                # Convert table structure to string representation
                title = table_structure.get("title", "")
                show_header = table_structure.get("show_header", True)
                columns_obj = table_structure.get("columns", [])
                rows_obj = table_structure.get("rows", [])
                columns = columns_obj if isinstance(columns_obj, list) else []
                rows = rows_obj if isinstance(rows_obj, list) else []

                output_lines: list[str] = []

                if title:
                    output_lines.extend((f"=== {title} ===", ""))

                if show_header and columns:
                    header_line = " | ".join(str(col) for col in columns)
                    output_lines.extend((header_line, "-" * len(header_line)))

                for row in rows:
                    row_line = " | ".join(str(cell) for cell in row)
                    output_lines.append(row_line)

                formatted_output = "\n".join(output_lines)
                return FlextResult[str].ok(formatted_output)

            except Exception as e:
                return FlextResult[str].fail(f"Table display failed: {e}")

    # Core attributes - using PrivateAttr for underscore-prefixed fields
    _console: Console = PrivateAttr(default_factory=Console)
    _custom_formatters: dict[str, FormatterProtocol] = PrivateAttr(default_factory=dict)
    _logger: FlextLogger = PrivateAttr(default_factory=lambda: FlextLogger(__name__))

    def __init__(self, **data: object) -> None:
        """Initialize FlextCliFormatters with configuration."""
        super().__init__(**data)

    def execute(self) -> FlextResult[None]:
        """Execute formatting service - FlextDomainService interface."""
        return FlextResult[None].ok(None)

    def create_table(
        self,
        data: list[dict[str, object]],
        title: str = "",
        headers: list[str] | None = None,
        *,
        show_header: bool = True,
        show_lines: bool = False,
    ) -> FlextResult[Table]:
        """Create Rich table with comprehensive options."""
        validation_result = self._FormatValidationHelper.validate_data_structure(data)
        if validation_result.is_failure:
            return FlextResult[Table].fail(
                validation_result.error or "Data validation failed"
            )

        try:
            table = Table(title=title, show_header=show_header, show_lines=show_lines)

            if not data:
                return FlextResult[Table].ok(table)

            # Determine columns
            columns = headers or (list(data[0].keys()) if data else [])

            # Add columns
            for col in columns:
                table.add_column(str(col), style="cyan")

            # Add rows
            for row in data:
                values = []
                for col in columns:
                    value = row.get(col, "")
                    values.append(str(value))
                table.add_row(*values)

            return FlextResult[Table].ok(table)

        except Exception as e:
            return FlextResult[Table].fail(f"Table creation failed: {e}")

    def format_table(
        self,
        data: list[dict[str, object]],
        title: str = "",
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data as table string."""
        table_result = self.create_table(data, title=title, headers=headers)
        if table_result.is_failure:
            return FlextResult[str].fail(table_result.error or "Table creation failed")

        try:
            # Capture table output as string
            with StringIO() as buffer:
                console = Console(file=buffer, width=120)
                console.print(table_result.unwrap())
                return FlextResult[str].ok(buffer.getvalue())
        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e}")

    def format_data(
        self, data: object, format_type: str = "table", **kwargs: object
    ) -> FlextResult[str]:
        """Format data according to specified type."""
        format_validation = self._FormatValidationHelper.validate_format_type(
            format_type
        )
        if format_validation.is_failure:
            return FlextResult[str].fail(
                format_validation.error or "Format validation failed"
            )

        data_validation = self._FormatValidationHelper.validate_data_structure(data)
        if data_validation.is_failure:
            return FlextResult[str].fail(
                data_validation.error or "Data validation failed"
            )

        try:
            if format_type == "table":
                return self._format_as_table(data, **kwargs)
            if format_type == "json":
                return self._format_as_json(data, **kwargs)
            if format_type == "yaml":
                return self._format_as_yaml(data, **kwargs)
            if format_type == "csv":
                return self._format_as_csv(data, **kwargs)
            if format_type == "plain":
                return FlextResult[str].ok(str(data))
            return FlextResult[str].fail(f"Unsupported format: {format_type}")
        except Exception as e:
            return FlextResult[str].fail(f"Data formatting failed: {e}")

    def display_table(
        self,
        data: list[dict[str, object]],
        title: str = "",
        headers: list[str] | None = None,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Display table to console."""
        # Extract valid create_table parameters from kwargs
        valid_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in {"show_header", "show_lines"} and isinstance(v, bool)
        }
        table_result = self.create_table(
            data, title=title, headers=headers, **valid_kwargs
        )
        if table_result.is_failure:
            return FlextResult[None].fail(table_result.error or "Table creation failed")

        try:
            rich_helper = self._RichIntegrationHelper()
            # Display using console directly since display_rich_table doesn't exist
            if hasattr(self._console, "print"):
                self._console.print(table_result.unwrap())
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Table display failed: {e}")

    def display_json(self, data: object, **kwargs: object) -> FlextResult[None]:
        """Display JSON formatted data."""
        json_result = self._format_as_json(data, **kwargs)
        if json_result.is_failure:
            return FlextResult[None].fail(json_result.error or "JSON display failed")

        console_output = self._ConsoleOutput()
        console_output.print_formatted(json_result.unwrap(), "green")
        return FlextResult[None].ok(None)

    def display_message(
        self, message: str, style: str = "", prefix: str = ""
    ) -> FlextResult[None]:
        """Display formatted message with optional styling."""
        try:
            formatted_message = f"{prefix}{message}" if prefix else message
            console_output = self._ConsoleOutput()
            console_output.print_formatted(formatted_message, style)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Message display failed: {e}")

    @property
    def console(self) -> Console:
        """Get console instance."""
        return self._console

    def print_success(self, message: str) -> None:
        """Print success message in green."""
        self._console.print(f"✅ {message}", style="green")

    def print_error(self, message: str) -> None:
        """Print error message in red."""
        self._console.print(f"❌ {message}", style="red")

    def create_formatter(
        self, name: str, format_function: Callable[[object], str]
    ) -> FlextResult[FormatterProtocol]:
        """Create custom formatter."""
        try:

            class CustomFormatter:
                def format(self, data: object, **format_kwargs: object) -> str:
                    return format_function(data, **format_kwargs)

                def get_name(self) -> str:
                    return name

            formatter = CustomFormatter()
            return FlextResult[FormatterProtocol].ok(formatter)
        except Exception as e:
            return FlextResult[FormatterProtocol].fail(f"Formatter creation failed: {e}")

    def register_formatter(
        self, name: str, formatter: FormatterProtocol | Callable[..., object]
    ) -> FlextResult[None]:
        """Register custom formatter."""
        try:
            if callable(formatter) and not hasattr(formatter, "format"):
                # Convert function to FormatterProtocol
                # Cast to the expected type for create_formatter
                from typing import cast
                typed_formatter = cast("Callable[[object], str]", formatter)
                formatter_result = self.create_formatter(name, typed_formatter)
                if formatter_result.is_failure:
                    return FlextResult[None].fail(
                        formatter_result.error or "Formatter creation failed"
                    )
                formatter_obj = formatter_result.unwrap()
                self._custom_formatters[name] = formatter_obj
            else:
                # Cast to FormatterProtocol if it's an object with format method
                from typing import cast
                formatter_obj = cast("FormatterProtocol", formatter)
                self._custom_formatters[name] = formatter_obj
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Formatter registration failed: {e}")

    def format_output(
        self, data: object, format_type: str = "table", **kwargs: object
    ) -> FlextResult[str]:
        """Format output using registered or built-in formatters."""
        # Check for custom formatter first
        if format_type in self._custom_formatters:
            try:
                formatter = self._custom_formatters[format_type]
                if hasattr(formatter, "format"):
                    result = formatter.format(data, **kwargs)
                    return FlextResult[str].ok(result)
                return FlextResult[str].fail("Formatter object missing format method")
            except Exception as e:
                return FlextResult[str].fail(f"Custom formatter failed: {e}")

        # Use built-in formatting
        return self.format_data(data, format_type, **kwargs)

    def list_formats(self) -> FlextResult[list[str]]:
        """List all available formats."""
        built_in_formats = ["table", "json", "yaml", "csv", "plain"]
        custom_formats = list(self._custom_formatters.keys())
        all_formats = built_in_formats + custom_formats
        return FlextResult[list[str]].ok(all_formats)

    # Export functionality
    def export_formatted_data(
        self,
        data: object,
        file_path: str | Path,
        format_type: str = "json",
        **kwargs: object,
    ) -> FlextResult[Path]:
        """Export formatted data to file."""
        # Validate file path
        path_result = self._FilePathHelper.validate_file_path(file_path)
        if path_result.is_failure:
            return FlextResult[Path].fail(path_result.error or "Path validation failed")

        file_path_obj = path_result.unwrap()

        # Ensure directory exists
        dir_result = self._FilePathHelper.ensure_directory_exists(file_path_obj)
        if dir_result.is_failure:
            return FlextResult[Path].fail(
                dir_result.error or "Directory creation failed"
            )

        # Format data
        format_result = self.format_data(data, format_type, **kwargs)
        if format_result.is_failure:
            return FlextResult[Path].fail(
                format_result.error or "Format operation failed"
            )

        try:
            # Write to file using Path.open() (PTH123 fix)
            formatted_content = format_result.unwrap()
            file_path_obj.write_text(formatted_content, encoding="utf-8")

            self._logger.info(f"Data exported to {file_path_obj}")
            return FlextResult[Path].ok(file_path_obj)
        except Exception as e:
            return FlextResult[Path].fail(f"File export failed: {e}")

    def batch_export_datasets(
        self,
        datasets: list[tuple[object, str]],  # (data, filename) pairs
        output_dir: str | Path,
        format_type: str = "json",
        **kwargs: object,
    ) -> FlextResult[list[Path]]:
        """Export multiple datasets to files."""
        # Validate output directory
        dir_path_result = self._FilePathHelper.validate_file_path(output_dir)
        if dir_path_result.is_failure:
            return FlextResult[list[Path]].fail(
                dir_path_result.error or "Directory path processing failed"
            )

        output_dir_path = dir_path_result.unwrap()

        try:
            output_dir_path.mkdir(parents=True, exist_ok=True)
            exported_files = []

            for data, filename in datasets:
                # Validate dataset tuple has expected length (PLR2004 fix)
                if (
                    len((data, filename))
                    != FlextCliConstants.LIMITS.dataset_tuple_length
                ):
                    return FlextResult[list[Path]].fail(
                        f"Invalid dataset tuple: expected length {FlextCliConstants.LIMITS.dataset_tuple_length}"
                    )

                file_path = output_dir_path / filename
                export_result = self.export_formatted_data(
                    data, file_path, format_type, **kwargs
                )

                if export_result.is_failure:
                    return FlextResult[list[Path]].fail(
                        f"Failed to export {filename}: {export_result.error}"
                    )

                exported_files.append(export_result.unwrap())

            return FlextResult[list[Path]].ok(exported_files)
        except Exception as e:
            return FlextResult[list[Path]].fail(f"Batch export failed: {e}")

    def create_formatted_output(
        self,
        data: object,
        format_type: str = "table",
        output_file: str | Path | None = None,
        **kwargs: object,
    ) -> FlextResult[str]:
        """Create formatted output with optional file export."""
        format_result = self.format_output(data, format_type, **kwargs)
        if format_result.is_failure:
            return FlextResult[str].fail(
                format_result.error or "String formatting failed"
            )

        formatted_data = format_result.unwrap()

        # Export to file if specified
        if output_file:
            export_result = self.export_formatted_data(
                data, output_file, format_type, **kwargs
            )
            if export_result.is_failure:
                self._logger.warning(f"File export failed: {export_result.error}")

        return FlextResult[str].ok(formatted_data)

    def get_formatter_info(self) -> FlextResult[dict[str, object]]:
        """Get information about available formatters."""
        try:
            info = {
                "built_in_formats": ["table", "json", "yaml", "csv", "plain"],
                "custom_formatters": list(self._custom_formatters.keys()),
                "total_formatters": len(self._custom_formatters) + 5,
                "rich_integration": True,
                "export_support": True,
            }
            return FlextResult[dict[str, object]].ok(info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Failed to get formatter info: {e}"
            )

    # Private formatting methods
    def _format_as_json(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as JSON."""
        try:
            indent = kwargs.get("indent", 2)
            # Ensure indent is valid type for json.dumps
            if not isinstance(indent, (int, str, type(None))):
                indent = 2
            result = json.dumps(data, indent=indent, ensure_ascii=False)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def _format_as_yaml(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as YAML."""
        try:
            # Use kwargs for YAML formatting options (ARG002 fix)
            default_flow_style = bool(kwargs.get("default_flow_style"))
            allow_unicode = bool(kwargs.get("allow_unicode", True))
            indent_value = kwargs.get("indent", 2)
            indent = int(indent_value) if isinstance(indent_value, (int, str)) else 2

            result = yaml.dump(
                data,
                default_flow_style=default_flow_style,
                allow_unicode=allow_unicode,
                indent=indent,
            )
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def _format_as_csv(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as CSV."""
        try:
            if not isinstance(data, list) or not data:
                return FlextResult[str].fail(
                    "CSV formatting requires non-empty list of dictionaries"
                )

            if not isinstance(data[0], dict):
                return FlextResult[str].fail(
                    "CSV formatting requires list of dictionaries"
                )

            # Use kwargs for CSV formatting options (ARG002 fix)
            delimiter = str(kwargs.get("delimiter", ","))
            quotechar = str(kwargs.get("quotechar", '"'))
            include_header = bool(kwargs.get("include_header", True))

            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=data[0].keys(),
                delimiter=delimiter,
                quotechar=quotechar,
            )

            if include_header:
                writer.writeheader()
            writer.writerows(data)
            return FlextResult[str].ok(output.getvalue())
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

    def _format_as_table(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as table."""
        if not isinstance(data, list):
            data = [{"value": str(data)}]

        # Ensure data is properly typed for format_table
        if not all(isinstance(item, dict) for item in data):
            return FlextResult[str].fail("Data must be a list of dictionaries")

        # At this point, data is guaranteed to be list[dict]
        typed_data: list[dict[str, object]] = data  # type: ignore[assignment]

        # Extract valid format_table parameters from kwargs
        title = kwargs.get("title", "")
        if not isinstance(title, str):
            title = ""

        headers = kwargs.get("headers")
        if headers is not None and not isinstance(headers, list):
            headers = None

        return self.format_table(typed_data, title=title, headers=headers)


__all__ = [
    "FlextCliFormatters",
]
