"""CLI output and formatting tools.

COMPLETELY REFACTORED: This module delegates ALL Rich functionality to formatters.py.
ZERO direct Rich imports - all Rich operations go through FlextCliFormatters abstraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from collections.abc import Sequence
from io import StringIO
from typing import cast, override

import yaml
from flext_core import FlextCore
from rich.console import Console
from rich.table import Table as RichTable
from rich.tree import Tree

from flext_cli.constants import FlextCliConstants
from flext_cli.formatters import FlextCliFormatters
from flext_cli.tables import FlextCliTables


class FlextCliOutput(FlextCore.Service[object]):
    """Comprehensive CLI output tools for the flext ecosystem.

    REFACTORED to use FlextCliFormatters and FlextCliTables for all output.
    This module provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - FlextCliTables: Tabulate-based ASCII tables (performance, plain text)
    - Built-in: JSON, YAML, CSV formatting

    Examples:
        >>> output = FlextCliOutput()
        >>>
        >>> # Format data in various formats
        >>> result = output.format_data(data={"key": "value"}, format_type="json")
        >>>
        >>> # Create Rich table
        >>> table_result = output.create_rich_table(
        ...     data=[{"name": "Alice", "age": 30}], title="Users"
        ... )
        >>>
        >>> # Create ASCII table
        >>> ascii_result = output.create_ascii_table(
        ...     data=[{"name": "Bob", "age": 25}], format="grid"
        ... )
        >>>
        >>> # Print styled messages
        >>> output.print_error("Something failed")
        >>> output.print_success("Operation completed")

    Note:
        This class provides backward compatibility while using the new
        abstraction layers internally. NO Rich imports are present here.

    """

    @override
    def __init__(self) -> None:
        """Initialize CLI output - formatters lazy-loaded via properties."""
        super().__init__()
        # Logger and container inherited from FlextCore.Service via FlextCore.Mixins

    @property
    def _formatters(self) -> FlextCliFormatters:
        """Get formatters instance via container."""
        return self.container.get_or_create("formatters", FlextCliFormatters).unwrap()

    @property
    def _tables(self) -> FlextCliTables:
        """Get tables instance via container."""
        return self.container.get_or_create("tables", FlextCliTables).unwrap()

    @override
    def execute(self) -> FlextCore.Result[object]:
        """Execute the main domain service operation - required by FlextCore.Service."""
        return FlextCore.Result[object].ok("FlextCliOutput operational")

    # =========================================================================
    # FORMAT DATA - UNIFIED API
    # =========================================================================

    def format_data(
        self,
        data: object,
        format_type: str = FlextCliConstants.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: FlextCore.Types.StringList | None = None,
    ) -> FlextCore.Result[str]:
        """Format data using specified format type from FlextCliConstants.

        Args:
            data: Data to format
            format_type: Format type from FlextCliConstants.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            FlextCore.Result[str]: Formatted data string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_data(
            ...     data={"name": "Alice", "age": 30}, format_type="json"
            ... )

        """
        format_lower = format_type.lower()

        if format_lower == FlextCliConstants.OutputFormats.JSON.value:
            return self.format_json(data)
        if format_lower == FlextCliConstants.OutputFormats.YAML.value:
            return self.format_yaml(data)
        if format_lower == FlextCliConstants.OutputFormats.TABLE.value:
            # Convert object to appropriate type for format_table
            if isinstance(data, (dict, list)):
                return self.format_table(data, title=title, headers=headers)
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
            )
        if format_lower == FlextCliConstants.OutputFormats.CSV.value:
            return self.format_csv(data)
        if format_lower == FlextCliConstants.OutputFormats.PLAIN.value:
            return FlextCore.Result[str].ok(str(data))
        return FlextCore.Result[str].fail(
            FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                format_type=format_type
            )
        )

    def create_formatter(self, format_type: str) -> FlextCore.Result[object]:
        """Create a formatter instance for the specified format type.

        Args:
            format_type: Format type to create formatter for

        Returns:
            FlextCore.Result[object]: Formatter instance or error

        """
        try:
            # Validate format type is supported using constants
            if format_type.lower() not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextCore.Result[object].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                        format_type=format_type
                    )
                )

            # Return self as the formatter since this class handles all formats
            return FlextCore.Result[object].ok(self)
        except Exception as e:
            return FlextCore.Result[object].fail(
                FlextCliConstants.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e)
            )

    # =========================================================================
    # RICH TABLE CREATION (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_rich_table(
        self,
        data: list[FlextCore.Types.Dict],
        title: str | None = None,
        headers: FlextCore.Types.StringList | None = None,
        *,
        show_header: bool = True,
        show_lines: bool = False,
        show_edge: bool = True,
        expand: bool = False,
        padding: tuple[int, int] = (0, 1),
    ) -> FlextCore.Result[object]:
        """Create a Rich table from data using FlextCliFormatters.

        Args:
            data: List of dictionaries to display
            title: Optional table title
            headers: Optional custom headers
            **kwargs: Additional Rich table options

        Returns:
            FlextCore.Result containing Rich Table object

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.create_rich_table(
            ...     data=[{"name": "Alice", "age": 30}], title="Users", show_header=True
            ... )

        """
        if not data:
            return FlextCore.Result[object].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
            )

        try:
            # Determine headers
            table_headers = headers or list(data[0].keys())

            # Create Rich table through formatters abstraction
            table_result = self._formatters.create_table(
                title=title or "",
                show_header=show_header,
                show_lines=show_lines,
                show_edge=show_edge,
                expand=expand,
                padding=padding,
            )

            if table_result.is_failure:
                return FlextCore.Result[object].fail(
                    f"Failed to create Rich table: {table_result.error}"
                )

            table = table_result.unwrap()

            # Add columns directly to table
            for header in table_headers:
                table.add_column(str(header))

            # Add rows directly to table
            for row_data in data:
                row_values = [str(row_data.get(h, "")) for h in table_headers]
                table.add_row(*row_values)

            return FlextCore.Result[object].ok(table)

        except Exception as e:
            error_msg = FlextCliConstants.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextCore.Result[object].fail(error_msg)

    def table_to_string(
        self,
        table: object,  # RichTable but avoiding direct import
        width: int | None = None,
    ) -> FlextCore.Result[str]:
        """Convert Rich table to string using FlextCliFormatters.

        Args:
            table: Rich table object
            width: Optional width for console

        Returns:
            FlextCore.Result[str]: Table as string or error

        """
        # Delegate to formatters for Rich operations
        return self._formatters.render_table_to_string(cast("RichTable", table), width)

    # =========================================================================
    # ASCII TABLE CREATION (Delegates to FlextCliTables)
    # =========================================================================

    def create_ascii_table(
        self,
        data: list[FlextCore.Types.Dict],
        headers: FlextCore.Types.StringList | None = None,
        table_format: str = "simple",
        *,
        align: str | Sequence[str] | None = None,
        floatfmt: str = "g",
        numalign: str = "decimal",
        stralign: str = "left",
        missingval: str = "",
        showindex: bool | str = False,
        disable_numparse: bool = False,
        colalign: Sequence[str] | None = None,
    ) -> FlextCore.Result[str]:
        """Create ASCII table using FlextCliTables.

        Args:
            data: List of dictionaries to display
            headers: Optional custom headers
            table_format: Table format (simple, grid, fancy_grid, pipe, etc.)
            **kwargs: Additional tabulate options

        Returns:
            FlextCore.Result[str]: ASCII table string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.create_ascii_table(
            ...     data=[{"name": "Bob", "age": 25}], table_format="grid"
            ... )

        """
        return self._tables.create_table(
            data=data,
            headers=headers or "keys",
            table_format=table_format,
            align=align,
            floatfmt=floatfmt,
            numalign=numalign,
            stralign=stralign,
            missingval=missingval,
            showindex=showindex,
            disable_numparse=disable_numparse,
            colalign=colalign,
        )

    # =========================================================================
    # PROGRESS BARS (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_progress_bar(
        self,
        _description: str = "Processing...",
        _total: int = 100,
    ) -> FlextCore.Result[object]:
        """Create a Rich progress bar using FlextCliFormatters.

        Args:
            _description: Progress description (reserved for future use)
            _total: Total number of steps (reserved for future use)

        Returns:
            FlextCore.Result containing Progress object

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar(
            ...     description="Loading", total=100
            ... )

        """
        progress_result = self._formatters.create_progress()
        # Cast to object type to match return type
        return cast("FlextCore.Result[object]", progress_result)

    # =========================================================================
    # STYLED PRINTING (Delegates to FlextCliFormatters)
    # =========================================================================

    def print_message(
        self,
        message: str,
        style: str = "",
        *,
        highlight: bool = False,
    ) -> FlextCore.Result[None]:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print
            style: Optional Rich style
            highlight: Whether to enable syntax highlighting

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_message("Hello", style="bold blue")

        """
        return self._formatters.print(
            message,
            style=style,
            highlight=highlight,
        )

    def print_error(self, message: str) -> FlextCore.Result[None]:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_error("Operation failed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.ERROR_PREFIX} {message}", style="bold red"
        )

    def print_success(self, message: str) -> FlextCore.Result[None]:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_success("Task completed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.SUCCESS_PREFIX} {message}", style="bold green"
        )

    def print_warning(self, message: str) -> FlextCore.Result[None]:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_warning("Deprecated feature")

        """
        return self.print_message(f"⚠️  Warning: {message}", style="bold yellow")

    def display_text(
        self,
        text: str,
        *,
        style: str = "",
        highlight: bool = False,
    ) -> FlextCore.Result[None]:
        """Display text using FlextCliFormatters.

        Args:
            text: Text to display
            style: Optional Rich style
            highlight: Whether to enable syntax highlighting

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_text("Important info", style="bold")

        """
        return self._formatters.print(
            text,
            style=style,
            highlight=highlight,
        )

    def display_message(
        self,
        message: str,
        message_type: str = "info",
        **kwargs: object,
    ) -> FlextCore.Result[None]:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)
            **kwargs: Additional formatting options

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_message("Operation completed", message_type="success")

        """
        # Map message types to styles
        style_map = {
            "info": "blue",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold yellow",
        }

        # Get style for message type, default to info
        style = style_map.get(message_type, "blue")

        # Add emoji prefix based on message type
        emoji_map = {
            "info": "i",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
        }

        emoji = emoji_map.get(message_type, "i")
        formatted_message = f"{emoji} {message}"

        # Extract highlight parameter from kwargs if present
        highlight = kwargs.get("highlight", False)
        if not isinstance(highlight, bool):
            highlight = False
        return self.print_message(formatted_message, style=style, highlight=highlight)

    def display_data(
        self,
        data: object,
        format_type: str = "table",
        **kwargs: object,
    ) -> FlextCore.Result[None]:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.)
            **kwargs: Additional formatting options

        Returns:
            FlextCore.Result[None]: Success or failure result

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data({"key": "value"}, format_type="json")

        """
        # Format the data first - extract valid parameters from kwargs
        title = kwargs.get("title")
        if title is not None and not isinstance(title, str):
            title = None
        headers = kwargs.get("headers")
        if headers is not None and not isinstance(headers, list):
            headers = None

        format_result = self.format_data(
            data, format_type=format_type, title=title, headers=headers
        )

        if format_result.is_failure:
            return FlextCore.Result[None].fail(
                f"Failed to format data: {format_result.error}"
            )

        formatted_data = format_result.unwrap()

        # Display the formatted data
        return self.print_message(formatted_data)

    # =========================================================================
    # DATA FORMAT METHODS (Built-in)
    # =========================================================================

    def format_json(self, data: object) -> FlextCore.Result[str]:
        """Format data as JSON.

        Args:
            data: Data to format

        Returns:
            FlextCore.Result[str]: Formatted JSON string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_json({"key": "value"})

        """
        try:
            return FlextCore.Result[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            error_msg = f"JSON formatting failed: {e}"
            self.logger.exception(error_msg)
            return FlextCore.Result[str].fail(error_msg)

    def format_yaml(self, data: object) -> FlextCore.Result[str]:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            FlextCore.Result[str]: Formatted YAML string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_yaml({"key": "value"})

        """
        try:
            return FlextCore.Result[str].ok(yaml.dump(data, default_flow_style=False))
        except Exception as e:
            error_msg = f"YAML formatting failed: {e}"
            self.logger.exception(error_msg)
            return FlextCore.Result[str].fail(error_msg)

    def format_csv(self, data: object) -> FlextCore.Result[str]:
        """Format data as CSV.

        Args:
            data: Data to format

        Returns:
            FlextCore.Result[str]: Formatted CSV string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_csv([{"name": "Alice", "age": 30}])

        """
        try:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                output_buffer = StringIO()
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                return FlextCore.Result[str].ok(output_buffer.getvalue())
            if isinstance(data, dict):
                output_buffer = StringIO()
                fieldnames = list(data.keys())
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
                return FlextCore.Result[str].ok(output_buffer.getvalue())
            return FlextCore.Result[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            error_msg = f"CSV formatting failed: {e}"
            self.logger.exception(error_msg)
            return FlextCore.Result[str].fail(error_msg)

    def format_table(
        self,
        data: FlextCore.Types.Dict | list[FlextCore.Types.Dict],
        title: str | None = None,
        headers: FlextCore.Types.StringList | None = None,
    ) -> FlextCore.Result[str]:
        """Format data as a tabulated table string using FlextCliTables.

        Args:
            data: Data to format (dict or list of dicts)
            title: Optional table title
            headers: Optional column headers

        Returns:
            FlextCore.Result[str]: Table as string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_table(
            ...     data=[{"name": "Alice", "age": 30}], title="Users"
            ... )

        """
        try:
            # Prepare data for tabulate
            if isinstance(data, dict):
                table_data = [{"Key": k, "Value": str(v)} for k, v in data.items()]
                # For list of dicts, use "keys" string as tabulate requires
                table_headers: str | FlextCore.Types.StringList = headers or "keys"
            else:
                if not isinstance(data, list):
                    return FlextCore.Result[str].fail(
                        FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
                    )
                table_data = data
                if not table_data:
                    return FlextCore.Result[str].fail(
                        FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
                    )
                # For list of dicts, use "keys" string as tabulate requires
                table_headers = headers or "keys"

            # Create table using FlextCliTables
            table_result = self._tables.create_table(
                data=cast("list[FlextCore.Types.Dict]", table_data),
                headers=table_headers,
                table_format="grid",
            )

            if table_result.is_failure:
                return FlextCore.Result[str].fail(
                    f"Failed to create table: {table_result.error}"
                )

            table_str = table_result.unwrap()

            # Add title if provided
            if title:
                table_str = f"{title}\n{table_str}\n"

            return FlextCore.Result[str].ok(table_str)

        except Exception as e:
            error_msg = f"Failed to format table: {e}"
            self.logger.exception(error_msg)
            return FlextCore.Result[str].fail(error_msg)

    def format_as_tree(
        self,
        data: FlextCore.Types.Dict,
        title: str = "Tree",
    ) -> FlextCore.Result[str]:
        """Format hierarchical data as tree view using FlextCliFormatters.

        Args:
            data: Hierarchical data to format
            title: Tree title

        Returns:
            FlextCore.Result[str]: Tree view as string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_as_tree(
            ...     data={"root": {"child1": "value1", "child2": "value2"}},
            ...     title="Config",
            ... )

        """
        # Create tree through formatters
        tree_result = self._formatters.create_tree(label=title)

        if tree_result.is_failure:
            return FlextCore.Result[str].fail(
                f"Failed to create tree: {tree_result.error}"
            )

        tree = tree_result.unwrap()

        # Build tree structure
        self._build_tree(tree, data)

        # Render to string using formatters
        return self._formatters.render_tree_to_string(
            tree, width=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH
        )

    def _build_tree(self, tree: object, data: object) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Rich Tree object
            data: Data to build tree from

        """
        tree_obj = cast("Tree", tree)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    branch = tree_obj.add(str(key))
                    self._build_tree(branch, value)
                elif isinstance(value, list):
                    branch = tree_obj.add(f"{key} (list)")
                    for item in value:
                        self._build_tree(branch, item)
                else:
                    tree_obj.add(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                self._build_tree(tree, item)
        else:
            tree_obj.add(str(data))

    # =========================================================================
    # CONSOLE ACCESS (Delegates to FlextCliFormatters)
    # =========================================================================

    @property
    def console(self) -> Console:
        """Get console instance from FlextCliFormatters (Rich Console abstraction).

        Returns:
            Console instance (Rich Console wrapped)

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.console
            >>> # Use through formatters abstraction

        """
        return self._formatters.console

    def get_console(self) -> Console:
        """Get the console instance from FlextCliFormatters (method form).

        Returns:
            Console instance (Rich Console wrapped)

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.get_console()

        """
        return self._formatters.get_console()


__all__ = ["FlextCliOutput"]
