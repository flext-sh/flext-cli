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
from typing import Protocol, cast

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
            """Format data according to protocol.

            Returns:
            str: Description of return value.

            """
            raise NotImplementedError

        def get_name(self) -> str:
            """Get formatter name.

            Returns:
            str: Description of return value.

            """
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
            """Get console instance.

            Returns:
            Console: Description of return value.

            """
            return self._console

    class _FormatValidationHelper:
        """Nested helper for format validation."""

        @staticmethod
        def validate_format_type(format_type: str) -> FlextResult[str]:
            """Validate format type using centralized validation.

            Returns:
            FlextResult[str]: Description of return value.

            """
            return FlextCliValidations.validate_output_format(format_type)

        @staticmethod
        def validate_data_structure(data: object) -> FlextResult[object]:
            """Validate data structure for formatting.

            Returns:
            FlextResult[object]: Description of return value.

            """
            if data is None:
                return FlextResult[object].fail("Data cannot be None")
            return FlextResult[object].ok(data)

    class _FilePathHelper:
        """Nested helper for file path operations."""

        def ensure_directory_exists(self, file_path: Path) -> FlextResult[Path]:
            """Ensure parent directory exists for file path using explicit error handling.

            Returns:
            FlextResult[Path]: Description of return value.

            """

            def create_parent_dirs() -> Path:
                """Create parent directories - used by safe_call.

                Returns:
                Path: Description of return value.

                """
                file_path.parent.mkdir(parents=True, exist_ok=True)
                return file_path

            result = FlextResult.safe_call(create_parent_dirs)
            if result.is_failure:
                return FlextResult[Path].fail(
                    f"Directory creation failed: {result.error}"
                )

            return result

        @staticmethod
        def validate_file_path(file_path: str | Path) -> FlextResult[Path]:
            """Validate and convert file path using explicit error handling.

            Returns:
            FlextResult[Path]: Description of return value.

            """
            if not file_path:
                return FlextResult[Path].fail("File path cannot be empty")

            def convert_to_path() -> Path:
                """Convert string/Path to Path object - used by safe_call.

                Returns:
                Path: Description of return value.

                """
                return Path(file_path)

            result = FlextResult.safe_call(convert_to_path)
            if result.is_failure:
                return FlextResult[Path].fail(f"Invalid file path: {result.error}")

            return result

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
            """Create display table structure from data - Rich abstraction.

            Returns:
            dict[str, object]: Description of return value.

            """
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
            """Display table structure using flext-core formatting - no direct Rich.

            Returns:
            FlextResult[str]: Description of return value.

            """

            def format_table_structure() -> str:
                """Format table structure - used by safe_call.

                Returns:
                str: Description of return value.

                """
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

                return "\n".join(output_lines)

            result = FlextResult.safe_call(format_table_structure)
            if result.is_failure:
                return FlextResult[str].fail(f"Table display failed: {result.error}")

            return result

    # Core attributes - using PrivateAttr for underscore-prefixed fields
    _console: Console = PrivateAttr(default_factory=Console)
    _custom_formatters: dict[str, FlextCliFormatters.FormatterProtocol] = PrivateAttr(
        default_factory=dict
    )
    _logger: FlextLogger = PrivateAttr(default_factory=lambda: FlextLogger(__name__))

    def __init__(self, **data: object) -> None:
        """Initialize FlextCliFormatters with configuration."""
        super().__init__(**data)

    def execute(self) -> FlextResult[None]:
        """Execute formatting service - FlextDomainService interface.

        Returns:
            FlextResult[None]: Description of return value.

        """
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
        """Create Rich table with comprehensive options.

        Returns:
            FlextResult[Table]: Description of return value.

        """
        validation_result = self._FormatValidationHelper.validate_data_structure(data)
        if validation_result.is_failure:
            return FlextResult[Table].fail(
                validation_result.error or "Data validation failed"
            )

        def create_rich_table() -> Table:
            """Create Rich table - used by safe_call.

            Returns:
            Table: Description of return value.

            """
            table = Table(title=title, show_header=show_header, show_lines=show_lines)

            if not data:
                return table

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

            return table

        result = FlextResult.safe_call(create_rich_table)
        if result.is_failure:
            return FlextResult[Table].fail(f"Table creation failed: {result.error}")

        return result

    def format_table(
        self,
        data: list[dict[str, object]],
        title: str = "",
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data as table string.

        Returns:
            FlextResult[str]: Description of return value.

        """
        table_result = self.create_table(data, title=title, headers=headers)
        if table_result.is_failure:
            return FlextResult[str].fail(table_result.error or "Table creation failed")

        def capture_table_output() -> str:
            """Capture table output as string - used by safe_call.

            Returns:
            str: Description of return value.

            """
            with StringIO() as buffer:
                console = Console(file=buffer, width=120)
                console.print(table_result.unwrap())
                return buffer.getvalue()

        result = FlextResult.safe_call(capture_table_output)
        if result.is_failure:
            return FlextResult[str].fail(f"Table formatting failed: {result.error}")

        return result

    def format_data(
        self, data: object, format_type: str = "table", **kwargs: object
    ) -> FlextResult[str]:
        """Format data according to specified type using validation chaining.

        Returns:
            FlextResult[str]: Description of return value.

        """

        def perform_formatting(validated_data: object) -> FlextResult[str]:
            """Perform the actual formatting after validation using explicit routing.

            Returns:
            FlextResult[str]: Description of return value.

            """
            if format_type == "table":
                return self._format_as_table(validated_data, **kwargs)
            if format_type == "json":
                return self._format_as_json(validated_data, **kwargs)
            if format_type == "yaml":
                return self._format_as_yaml(validated_data, **kwargs)
            if format_type == "csv":
                return self._format_as_csv(validated_data, **kwargs)
            if format_type == "plain":
                return FlextResult[str].ok(str(validated_data))
            return FlextResult[str].fail(f"Unsupported format: {format_type}")

        # Railway pattern: format validation → data validation → formatting
        return (
            self._FormatValidationHelper.validate_format_type(format_type)
            .flat_map(
                lambda _: self._FormatValidationHelper.validate_data_structure(data)
            )
            .flat_map(perform_formatting)
        )

    def display_table(
        self,
        data: list[dict[str, object]],
        title: str = "",
        headers: list[str] | None = None,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Display table to console.

        Returns:
            FlextResult[None]: Description of return value.

        """
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

        def display_table_to_console() -> None:
            """Display table to console - used by safe_call."""
            self._RichIntegrationHelper()
            # Display using console directly since display_rich_table doesn't exist
            if hasattr(self._console, "print"):
                self._console.print(table_result.unwrap())

        result = FlextResult.safe_call(display_table_to_console)
        if result.is_failure:
            return FlextResult[None].fail(f"Table display failed: {result.error}")

        return FlextResult[None].ok(None)

    def display_json(self, data: object, **kwargs: object) -> FlextResult[None]:
        """Display JSON formatted data.

        Returns:
            FlextResult[None]: Description of return value.

        """
        json_result = self._format_as_json(data, **kwargs)
        if json_result.is_failure:
            return FlextResult[None].fail(json_result.error or "JSON display failed")

        console_output = self._ConsoleOutput()
        console_output.print_formatted(json_result.unwrap(), "green")
        return FlextResult[None].ok(None)

    def display_message(
        self, message: str, style: str = "", prefix: str = ""
    ) -> FlextResult[None]:
        """Display formatted message with optional styling.

        Returns:
            FlextResult[None]: Description of return value.

        """

        def display_formatted_message() -> None:
            """Display formatted message - used by safe_call."""
            formatted_message = f"{prefix}{message}" if prefix else message
            console_output = self._ConsoleOutput()
            console_output.print_formatted(formatted_message, style)

        result = FlextResult.safe_call(display_formatted_message)
        if result.is_failure:
            return FlextResult[None].fail(f"Message display failed: {result.error}")

        return FlextResult[None].ok(None)

    @property
    def console(self) -> Console:
        """Get console instance.

        Returns:
            Console: Description of return value.

        """
        return self._console

    def print_success(self, message: str) -> None:
        """Print success message in green."""
        self._console.print(f"✅ {message}", style="green")

    def print_error(self, message: str) -> None:
        """Print error message in red."""
        self._console.print(f"❌ {message}", style="red")

    def create_formatter(
        self, name: str, format_function: Callable[[object], str]
    ) -> FlextResult[FlextCliFormatters.FormatterProtocol]:
        """Create custom formatter using explicit error handling.

        Returns:
            FlextResult[FlextCliFormatters.FormatterProtocol]: Description of return value.

        """

        def create_custom_formatter() -> FlextCliFormatters.FormatterProtocol:
            """Create custom formatter - used by safe_call.

            Returns:
            FlextCliFormatters.FormatterProtocol: Description of return value.

            """

            class CustomFormatter:
                def format(self, data: object, **format_kwargs: object) -> str:
                    return format_function(data, **format_kwargs)

                def get_name(self) -> str:
                    return name

            formatter = CustomFormatter()
            # Cast to the inner FormatterProtocol type
            return cast("FlextCliFormatters.FormatterProtocol", formatter)

        result = FlextResult.safe_call(create_custom_formatter)
        if result.is_failure:
            return FlextResult["FlextCliFormatters.FormatterProtocol"].fail(
                f"Formatter creation failed: {result.error}"
            )

        return result

    def register_formatter(
        self, name: str, formatter: FormatterProtocol | Callable[..., object]
    ) -> FlextResult[None]:
        """Register custom formatter using explicit error handling.

        Returns:
            FlextResult[None]: Description of return value.

        """
        if callable(formatter) and not hasattr(formatter, "format"):
            # Convert function to FormatterProtocol
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
            formatter_obj = cast("FlextCliFormatters.FormatterProtocol", formatter)
            self._custom_formatters[name] = formatter_obj

        return FlextResult[None].ok(None)

    def format_output(
        self, data: object, format_type: str = "table", **kwargs: object
    ) -> FlextResult[str]:
        """Format output using registered or built-in formatters.

        Returns:
            FlextResult[str]: Description of return value.

        """
        # Check for custom formatter first
        if format_type in self._custom_formatters:
            formatter = self._custom_formatters[format_type]
            if not hasattr(formatter, "format"):
                return FlextResult[str].fail("Formatter object missing format method")

            def apply_custom_formatter() -> str:
                """Apply custom formatter - used by safe_call.

                Returns:
                str: Description of return value.

                """
                return formatter.format(data, **kwargs)

            result = FlextResult.safe_call(apply_custom_formatter)
            if result.is_failure:
                return FlextResult[str].fail(f"Custom formatter failed: {result.error}")

            return result

        # Use built-in formatting
        return self.format_data(data, format_type, **kwargs)

    def list_formats(self) -> FlextResult[list[str]]:
        """List all available formats.

        Returns:
            FlextResult[list[str]]: Description of return value.

        """
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
        """Export formatted data to file using railway pattern.

        Returns:
            FlextResult[Path]: Description of return value.

        """

        def write_formatted_content(file_path_obj: Path) -> FlextResult[Path]:
            """Write formatted content to validated file path.

            Returns:
            FlextResult[Path]: Description of return value.

            """
            return self.format_data(data, format_type, **kwargs).flat_map(
                lambda formatted_content: self._write_content_to_file(
                    file_path_obj, formatted_content
                )
            )

        # Railway pattern: validation → directory creation → formatting → writing
        file_helper = self._FilePathHelper()
        return (
            self._FilePathHelper.validate_file_path(file_path)
            .flat_map(file_helper.ensure_directory_exists)
            .flat_map(write_formatted_content)
        )

    def _write_content_to_file(
        self, file_path: Path, content: str
    ) -> FlextResult[Path]:
        """Write content to file using explicit error handling.

        Returns:
            FlextResult[Path]: Description of return value.

        """

        def write_text_to_file() -> Path:
            """Write text to file - used by safe_call.

            Returns:
            Path: Description of return value.

            """
            file_path.write_text(content, encoding="utf-8")
            self._logger.info(f"Data exported to {file_path}")
            return file_path

        result = FlextResult.safe_call(write_text_to_file)
        if result.is_failure:
            return FlextResult[Path].fail(f"File write failed: {result.error}")

        return result

    def batch_export_datasets(
        self,
        datasets: list[tuple[object, str]],  # (data, filename) pairs
        output_dir: str | Path,
        format_type: str = "json",
        **kwargs: object,
    ) -> FlextResult[list[Path]]:
        """Export multiple datasets to files.

        Returns:
            FlextResult[list[Path]]: List of exported file paths or error result.

        """
        # Validate output directory
        dir_path_result = self._FilePathHelper.validate_file_path(output_dir)
        if dir_path_result.is_failure:
            return FlextResult[list[Path]].fail(
                dir_path_result.error or "Directory path processing failed"
            )

        output_dir_path = dir_path_result.unwrap()

        def perform_batch_export() -> list[Path]:
            """Perform batch export operations - used by safe_call.

            Raises:
                ValueError: If dataset validation fails.
                RuntimeError: If export operation fails.

            Returns:
            list[Path]: Description of return value.

            """
            output_dir_path.mkdir(parents=True, exist_ok=True)
            exported_files = []

            for data, filename in datasets:
                # Validate dataset tuple has expected length (PLR2004 fix)
                if (
                    len((data, filename))
                    != FlextCliConstants.LIMITS.dataset_tuple_length
                ):
                    msg = f"Invalid dataset tuple: expected length {FlextCliConstants.LIMITS.dataset_tuple_length}"
                    raise ValueError(msg)

                file_path = output_dir_path / filename
                export_result = self.export_formatted_data(
                    data, file_path, format_type, **kwargs
                )

                if export_result.is_failure:
                    msg = f"Failed to export {filename}: {export_result.error}"
                    raise RuntimeError(msg)

                exported_files.append(export_result.unwrap())

            return exported_files

        result = FlextResult.safe_call(perform_batch_export)
        if result.is_failure:
            return FlextResult[list[Path]].fail(f"Batch export failed: {result.error}")

        return result

    def create_formatted_output(
        self,
        data: object,
        format_type: str = "table",
        output_file: str | Path | None = None,
        **kwargs: object,
    ) -> FlextResult[str]:
        """Create formatted output with optional file export.

        Returns:
            FlextResult[str]: Description of return value.

        """
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
        """Get information about available formatters using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """

        def build_formatter_info() -> dict[str, object]:
            """Build formatter information dictionary - used for explicit error handling.

            Returns:
            dict[str, object]: Description of return value.

            """
            return {
                "built_in_formats": ["table", "json", "yaml", "csv", "plain"],
                "custom_formatters": list(self._custom_formatters.keys()),
                "total_formatters": len(self._custom_formatters) + 5,
                "rich_integration": True,
                "export_support": True,
            }

        result = FlextResult.safe_call(build_formatter_info)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Failed to get formatter info: {result.error}"
            )

        return result

    # Private formatting methods
    def _format_as_json(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as JSON using explicit error handling.

        Returns:
            FlextResult[str]: Description of return value.

        """
        indent = kwargs.get("indent", 2)
        # Ensure indent is valid type for json.dumps
        if not isinstance(indent, (int, str, type(None))):
            indent = 2

        result = FlextResult.safe_call(
            lambda: json.dumps(data, indent=indent, ensure_ascii=False)
        )
        if result.is_failure:
            return FlextResult[str].fail(f"JSON formatting failed: {result.error}")
        return result

    def _format_as_yaml(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as YAML using explicit error handling.

        Returns:
            FlextResult[str]: Description of return value.

        """
        # Use kwargs for YAML formatting options (ARG002 fix)
        default_flow_style = bool(kwargs.get("default_flow_style"))
        allow_unicode = bool(kwargs.get("allow_unicode", True))
        indent_value = kwargs.get("indent", 2)
        indent = int(indent_value) if isinstance(indent_value, (int, str)) else 2

        result = FlextResult.safe_call(
            lambda: yaml.dump(
                data,
                default_flow_style=default_flow_style,
                allow_unicode=allow_unicode,
                indent=indent,
            )
        )
        if result.is_failure:
            return FlextResult[str].fail(f"YAML formatting failed: {result.error}")
        return result

    def _format_as_csv(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as CSV using explicit error handling.

        Returns:
            FlextResult[str]: Description of return value.

        """
        # Validate input data
        if not isinstance(data, list) or not data:
            return FlextResult[str].fail(
                "CSV formatting requires non-empty list of dictionaries"
            )

        if not isinstance(data[0], dict):
            return FlextResult[str].fail("CSV formatting requires list of dictionaries")

        # Use kwargs for CSV formatting options (ARG002 fix)
        delimiter = str(kwargs.get("delimiter", ","))
        quotechar = str(kwargs.get("quotechar", '"'))
        include_header = bool(kwargs.get("include_header", True))

        def write_csv_content() -> str:
            """Write CSV content - used by safe_call.

            Returns:
            str: Description of return value.

            """
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
            return output.getvalue()

        result = FlextResult.safe_call(write_csv_content)
        if result.is_failure:
            return FlextResult[str].fail(f"CSV formatting failed: {result.error}")
        return result

    def _format_as_table(self, data: object, **kwargs: object) -> FlextResult[str]:
        """Format data as table.

        Returns:
            FlextResult[str]: Description of return value.

        """
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
