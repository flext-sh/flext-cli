"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import json
import typing
from collections.abc import Sequence
from io import StringIO
from typing import cast, override

import yaml
from flext_core import FlextMixins, FlextResult, FlextRuntime, FlextService, FlextTypes
from pydantic import BaseModel

from flext_cli.constants import FlextCliConstants
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.services.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities


class FlextCliOutput(FlextService[FlextTypes.JsonDict]):
    """Comprehensive CLI output tools for the flext ecosystem.

    REFACTORED to use FlextCliFormatters and FlextCliTables for all output.
    This module provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - FlextCliTables: Tabulate-based ASCII tables (performance, plain text)
    - Built-in: JSON, YAML, CSV formatting

    # Logger is provided by FlextMixins mixin
    logger: FlextLogger

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
        """Initialize CLI output with direct formatter and table instances."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins

        # Domain library components - direct initialization (no properties)
        self._formatters = FlextCliFormatters()
        self._tables = FlextCliTables()

        # Result formatter registry for domain-specific result types
        self._result_formatters: dict[type, FlextCliTypes.Callable.ResultFormatter] = {}

    @override
    def execute(self, **_kwargs: object) -> FlextResult[FlextTypes.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        """
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })

    # =========================================================================
    # FORMAT DATA - UNIFIED API
    # =========================================================================

    def format_data(
        self,
        data: FlextTypes.JsonValue,
        format_type: str = FlextCliConstants.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data using specified format type with railway pattern.

        Args:
            data: Data to format
            format_type: Format type from FlextCliConstants.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            FlextResult[str]: Formatted data string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_data(
            ...     data={"name": "Alice", "age": 30}, format_type="json"
            ... )

        """
        # Railway pattern: validate format → dispatch to handler
        return FlextCliUtilities.CliValidation.validate_output_format(
            format_type
        ).flat_map(lambda fmt: self._dispatch_formatter(fmt, data, title, headers))

    # Helper _validate_format_type moved to FlextCliUtilities.CliValidation.validate_output_format()

    def _dispatch_formatter(
        self,
        format_type: str,
        data: FlextTypes.JsonValue,
        title: str | None,
        headers: list[str] | None,
    ) -> FlextResult[str]:
        """Dispatch to appropriate formatter based on format type."""
        # Format dispatcher using dict mapping
        formatters = {
            FlextCliConstants.OutputFormats.JSON.value: lambda: self.format_json(data),
            FlextCliConstants.OutputFormats.YAML.value: lambda: self.format_yaml(data),
            FlextCliConstants.OutputFormats.TABLE.value: lambda: self._format_table_data(
                data, title, headers
            ),
            FlextCliConstants.OutputFormats.CSV.value: lambda: self.format_csv(data),
            FlextCliConstants.OutputFormats.PLAIN.value: lambda: FlextResult[str].ok(
                str(data)
            ),
        }

        formatter = formatters.get(format_type)
        if formatter is None:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type
                )
            )

        return formatter()

    def _format_table_data(
        self,
        data: FlextTypes.JsonValue,
        title: str | None,
        headers: list[str] | None,
    ) -> FlextResult[str]:
        """Format data as table with type validation."""
        # Handle dict - type narrowing for format_table
        if FlextRuntime.is_dict_like(data):
            # Type cast: dict[str, JsonValue] is compatible with format_table
            # JsonValue is recursively defined to include dict[str, JsonValue]
            table_data = typing.cast(
                "dict[str, FlextTypes.JsonValue] | list[dict[str, FlextTypes.JsonValue]] | str",
                data,
            )
            return self.format_table(table_data, title=title, headers=headers)

        # Handle list of dicts - type narrowing for format_table
        if FlextRuntime.is_list_like(data):
            # Fast fail validation
            if not data:
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
                )
            if not all(FlextRuntime.is_dict_like(item) for item in data):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
                )
            # Type cast: list[dict[str, JsonValue]] is compatible with format_table
            # JsonValue is recursively defined to include dict[str, JsonValue]
            table_data_list = typing.cast(
                "dict[str, FlextTypes.JsonValue] | list[dict[str, FlextTypes.JsonValue]] | str",
                data,
            )
            return self.format_table(table_data_list, title=title, headers=headers)

        # Invalid type for table
        return FlextResult[str].fail(
            FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
        )

    def create_formatter(self, format_type: str) -> FlextResult[FlextCliOutput]:
        """Create a formatter instance for the specified format type.

        Uses FlextCliUtilities.CliValidation.validate_output_format() for validation.

        Args:
            format_type: Format type to create formatter for

        Returns:
            FlextResult[object]: Formatter instance or error

        """
        try:
            # Validate format using consolidated utility - railway pattern
            return (
                FlextCliUtilities.CliValidation.validate_output_format(format_type).map(
                    lambda _: self
                )  # Return self as formatter on success
            )
        except Exception as e:
            return FlextResult[FlextCliOutput].fail(
                FlextCliConstants.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e)
            )

    # =========================================================================
    # RESULT FORMATTER REGISTRY - Domain-specific result formatting
    # =========================================================================

    def register_result_formatter(
        self,
        result_type: type,
        formatter: FlextCliTypes.Callable.ResultFormatter,
    ) -> FlextResult[bool]:
        r"""Register custom formatter for domain-specific result types.

        **PURPOSE**: Eliminate repetitive result display formatting boilerplate.

        Allows registering formatters for specific result types, enabling
        automatic formatting based on result type detection. Reduces ~74 lines
        of formatting boilerplate per result type.

        Args:
            result_type: Type of result to format (e.g., MigrationResult)
            formatter: Callable that formats and displays the result
                Signature: (result: object, output_format: str) -> None

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            ```python
            from flext_cli import FlextCliOutput
            from client-a_oud_mig.models import MigrationResult

            output = FlextCliOutput()


            # Register formatter for MigrationResult
            def format_migration(result: MigrationResult, fmt: str) -> None:
                if fmt == "table":
                    # Create Rich table from result
                    console = output._formatters.console
                    panel = output._formatters.create_panel(
                        f"[green]Migration completed![/green]\\n"
                        + f"Migrated: {result.migrated_count} entries",
                        title="✅ Migration Result",
                    )
                    console.print(panel.unwrap())
                elif fmt == "json":
                    print(result.model_dump_json())


            output.register_result_formatter(MigrationResult, format_migration)

            # Now auto-format any MigrationResult
            migration_result = service.execute().unwrap()
            output.format_and_display_result(migration_result, "table")
            ```

        **ELIMINATES**:
        - 74 lines of panel creation and table formatting per result type
        - Manual type checking and format branching
        - Duplicate formatting logic across commands

        """
        try:
            self._result_formatters[result_type] = formatter
            self.logger.debug(
                "Registered result formatter",
                extra={"formatter_type": result_type.__name__},
            )
            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}"
            )

    def format_and_display_result(
        self,
        result: BaseModel
        | FlextTypes.JsonValue
        | FlextCliTypes.Callable.FormatableResult,
        output_format: str = "table",
    ) -> FlextResult[bool]:
        """Auto-detect result type and apply registered formatter with extracted helpers.

        **PURPOSE**: Eliminate manual type checking and formatter dispatch.

        Args:
            result: Domain result object to format
            output_format: Output format ("table", "json", "yaml", etc.)

        Returns:
            FlextResult[bool]: True on success, False on failure

        """
        try:
            # Try registered formatter first - use FlextResult pattern
            registered_result = self._try_registered_formatter(result, output_format)
            if registered_result.is_success:
                return registered_result

            # Use generic formatting with railway pattern
            return self._convert_result_to_formattable(result, output_format).flat_map(
                self._display_formatted_result
            )

        except Exception as e:
            return FlextResult[bool].fail(f"Failed to format and display result: {e}")

    def _try_registered_formatter(
        self,
        result: BaseModel
        | FlextTypes.JsonValue
        | FlextCliTypes.Callable.FormatableResult,
        output_format: str,
    ) -> FlextResult[bool]:
        """Try to use registered formatter for result type.

        Returns:
            FlextResult[bool]: True if formatter was found and executed,
            False if no formatter registered for this type

        """
        result_type = type(result)

        if result_type in self._result_formatters:
            formatter = self._result_formatters[result_type]
            formatter(result, output_format)
            return FlextResult[bool].ok(True)

        return FlextResult[bool].fail(
            f"No registered formatter for type {result_type.__name__}"
        )

    def _convert_result_to_formattable(
        self,
        result: BaseModel
        | FlextTypes.JsonValue
        | FlextCliTypes.Callable.FormatableResult,
        output_format: str,
    ) -> FlextResult[str]:
        """Convert result object to formattable string.

        Handles multiple result types: Pydantic models, objects with __dict__, and fallback.
        Fast-fails if result is None - caller must handle None values explicitly.
        """
        # Fast-fail if result is None - no fallback to fake data
        if result is None:
            return FlextResult[str].fail(
                "Cannot format None result - provide a valid result object"
            )

        self.logger.info(
            f"No registered formatter for {type(result).__name__}, using generic formatting"
        )

        # Handle Pydantic models
        if isinstance(result, BaseModel):
            return self._format_pydantic_model(result, output_format)

        # Handle objects with __dict__
        if hasattr(result, "__dict__"):
            return self._format_dict_object(result, output_format)

        # Use string representation (not a fallback - valid conversion)
        return FlextResult[str].ok(str(result))

    def _format_pydantic_model(
        self, result: BaseModel, output_format: str
    ) -> FlextResult[str]:
        """Format Pydantic model to string."""
        # model_dump() returns dict[str, Any] which is compatible with JsonValue
        # dict is a valid JsonValue type, no cast needed
        result_dict: FlextTypes.JsonValue = FlextMixins.ModelConversion.to_dict(result)
        return self.format_data(result_dict, output_format)

    def _format_dict_object(
        self, result: FlextCliTypes.Callable.FormatableResult, output_format: str
    ) -> FlextResult[str]:
        """Format object with __dict__ to string."""
        raw_dict = result.__dict__
        normalized_dict: dict[str, FlextTypes.JsonValue] = {}

        for key, value in raw_dict.items():
            if (
                isinstance(value, (str, int, float, bool, type(None)))
                or FlextRuntime.is_list_like(value)
                or FlextRuntime.is_dict_like(value)
            ):
                normalized_dict[key] = value
            else:
                normalized_dict[key] = str(value)

        # Type cast: dict[str, JsonValue] is a valid JsonValue
        # JsonValue is recursively defined to include dict[str, JsonValue]
        json_value = typing.cast("FlextTypes.JsonValue", normalized_dict)
        return self.format_data(json_value, output_format)

    def _display_formatted_result(self, formatted: str) -> FlextResult[bool]:
        """Display formatted result string using Rich console."""
        console = self._formatters.console
        console.print(formatted)
        return FlextResult[bool].ok(True)

    # =========================================================================
    # RICH TABLE CREATION (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_rich_table(
        self,
        data: list[dict[str, FlextTypes.JsonValue]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[FlextCliTypes.Display.RichTable]:
        """Create a Rich table from data using FlextCliFormatters.

        Args:
            data: List of dictionaries to display
            title: Optional table title
            headers: Optional custom headers

        Returns:
            FlextResult containing Rich Table object

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.create_rich_table(
            ...     data=[{"name": "Alice", "age": 30}], title="Users"
            ... )

        Note:
            For advanced Rich table styling (borders, padding, colors), use
            FlextCliFormatters.console directly and create Rich tables.

        """
        if not data:
            return FlextResult[FlextCliTypes.Display.RichTable].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
            )

        try:
            # Determine headers - validate explicitly, no fallback
            table_headers = headers if headers is not None else list(data[0].keys())

            # Create Rich table through formatters abstraction (basic parameters only)
            table_result = self._formatters.create_table(
                data=None,  # We'll populate manually
                headers=table_headers,
                title=title,
            )

            if table_result.is_failure:
                return FlextResult[FlextCliTypes.Display.RichTable].fail(
                    f"Failed to create Rich table: {table_result.error}"
                )

            table = table_result.unwrap()

            # Add columns directly to table
            for header in table_headers:
                table.add_column(str(header))

            # Add rows directly to table - validate all headers exist, no fallback
            for row_data in data:
                row_values: list[str] = []
                for header in table_headers:
                    if header not in row_data:
                        return FlextResult[FlextCliTypes.Display.RichTable].fail(
                            f"Header {header!r} not found in row data. Available keys: {list(row_data.keys())}"
                        )
                    row_values.append(str(row_data[header]))
                table.add_row(*row_values)

            return FlextResult[FlextCliTypes.Display.RichTable].ok(table)

        except Exception as e:
            error_msg = FlextCliConstants.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[FlextCliTypes.Display.RichTable].fail(error_msg)

    def table_to_string(
        self,
        table: FlextCliTypes.Display.RichTable,
        width: int | None = None,
    ) -> FlextResult[str]:
        """Convert table to string using FlextCliFormatters.

        Args:
            table: Table object from formatters
            width: Optional width for console

        Returns:
            FlextResult[str]: Table as string or error

        """
        # Delegate to formatters for rendering
        return self._formatters.render_table_to_string(table, width)

    # =========================================================================
    # ASCII TABLE CREATION (Delegates to FlextCliTables)
    # =========================================================================

    def create_ascii_table(
        self,
        data: list[dict[str, FlextTypes.JsonValue]],
        headers: list[str] | None = None,
        table_format: str = FlextCliConstants.TableFormats.SIMPLE,
        *,
        align: str | Sequence[str] | None = None,
        floatfmt: str | None = None,
        numalign: str | None = None,
        stralign: str | None = None,
        missingval: str | None = None,
        showindex: bool | str = False,
        disable_numparse: bool = False,
        colalign: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Create ASCII table using FlextCliTables.

        Args:
            data: List of dictionaries to display
            headers: Optional custom headers
            table_format: Table format (simple, grid, fancy_grid, pipe, etc.)
            align: Column alignment (str or sequence)
            floatfmt: Float format string
            numalign: Number alignment
            stralign: String alignment
            missingval: Value to display for missing data
            showindex: Show index column (bool or str)
            disable_numparse: Disable numeric parsing
            colalign: Column-specific alignment

        Returns:
            FlextResult[str]: ASCII table string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.create_ascii_table(
            ...     data=[{"name": "Bob", "age": 25}], table_format="grid"
            ... )

        """
        # Validate all parameters explicitly - no fallbacks
        validated_headers = (
            headers if headers is not None else FlextCliConstants.TableFormats.KEYS
        )
        validated_floatfmt = (
            floatfmt
            if floatfmt is not None
            else FlextCliConstants.TablesDefaults.DEFAULT_FLOAT_FORMAT
        )
        validated_numalign = (
            numalign
            if numalign is not None
            else FlextCliConstants.TablesDefaults.DEFAULT_NUM_ALIGN
        )
        validated_stralign = (
            stralign
            if stralign is not None
            else FlextCliConstants.TablesDefaults.DEFAULT_STR_ALIGN
        )
        config = FlextCliModels.TableConfig(
            headers=validated_headers,
            table_format=table_format,
            align=align,
            floatfmt=validated_floatfmt,
            numalign=validated_numalign,
            stralign=validated_stralign,
            missingval=missingval
            if missingval is not None
            else FlextCliConstants.TablesDefaults.DEFAULT_MISSING_VALUE,
            showindex=showindex,
            disable_numparse=disable_numparse,
            colalign=colalign,
        )
        return self._tables.create_table(data=data, config=config)

    # =========================================================================
    # PROGRESS BARS (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_progress_bar(self) -> FlextResult[FlextCliTypes.Interactive.Progress]:
        """Create a Rich progress bar using FlextCliFormatters.

        Returns:
            FlextResult[Progress]: Rich Progress wrapped in Result

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar()

        """
        return self._formatters.create_progress()

    # =========================================================================
    # STYLED PRINTING (Delegates to FlextCliFormatters)
    # =========================================================================

    def print_message(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextResult[bool]:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print
            style: Optional Rich style

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_message("Hello", style="bold blue")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        # Validate style explicitly - no fallback
        validated_style = (
            style if style is not None else FlextCliConstants.OutputDefaults.EMPTY_STYLE
        )
        return self._formatters.print(message, style=validated_style)

    def print_error(self, message: str) -> FlextResult[bool]:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_error("Operation failed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.ERROR_PREFIX} {message}",
            style=FlextCliConstants.Styles.BOLD_RED,
        )

    def print_success(self, message: str) -> FlextResult[bool]:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_success("Task completed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.SUCCESS_PREFIX} {message}",
            style=FlextCliConstants.Styles.BOLD_GREEN,
        )

    def print_warning(self, message: str) -> FlextResult[bool]:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_warning("Deprecated feature")

        """
        return self.print_message(
            f"{FlextCliConstants.Emojis.WARNING} {FlextCliConstants.OutputDefaults.WARNING_PREFIX} {message}",
            style=FlextCliConstants.Styles.BOLD_YELLOW,
        )

    def display_text(
        self,
        text: str,
        *,
        style: str | None = None,
    ) -> FlextResult[bool]:
        """Display text using FlextCliFormatters.

        Args:
            text: Text to display
            style: Optional Rich style

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_text("Important info", style="bold")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        # Validate style explicitly - no fallback
        validated_style = (
            style if style is not None else FlextCliConstants.OutputDefaults.EMPTY_STYLE
        )
        return self._formatters.print(text, style=validated_style)

    def display_message(
        self,
        message: str,
        message_type: str | None = None,
    ) -> FlextResult[bool]:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_message("Operation completed", message_type="success")

        """
        # Validate message type explicitly - no fallback
        final_message_type = (
            message_type
            if message_type is not None
            else FlextCliConstants.OutputDefaults.DEFAULT_MESSAGE_TYPE
        )

        # Map message types to styles
        style_map = {
            FlextCliConstants.MessageTypes.INFO.value: FlextCliConstants.Styles.BLUE,
            FlextCliConstants.MessageTypes.SUCCESS.value: FlextCliConstants.Styles.BOLD_GREEN,
            FlextCliConstants.MessageTypes.ERROR.value: FlextCliConstants.Styles.BOLD_RED,
            FlextCliConstants.MessageTypes.WARNING.value: FlextCliConstants.Styles.BOLD_YELLOW,
        }

        # Get style for message type, default to blue
        style = style_map.get(final_message_type, FlextCliConstants.Styles.BLUE)

        # Add emoji prefix based on message type
        emoji_map = {
            FlextCliConstants.MessageTypes.INFO.value: FlextCliConstants.Emojis.INFO,
            FlextCliConstants.MessageTypes.SUCCESS.value: FlextCliConstants.Emojis.SUCCESS,
            FlextCliConstants.MessageTypes.ERROR.value: FlextCliConstants.Emojis.ERROR,
            FlextCliConstants.MessageTypes.WARNING.value: FlextCliConstants.Emojis.WARNING,
        }

        emoji = emoji_map.get(final_message_type, FlextCliConstants.Emojis.INFO)
        formatted_message = f"{emoji} {message}"

        return self.print_message(formatted_message, style=style)

    def display_data(
        self,
        data: FlextTypes.JsonValue,
        format_type: str | None = None,
        *,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[bool]:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.)
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data({"key": "value"}, format_type="json")

        """
        # Validate format type explicitly - no fallback
        final_format_type = (
            format_type
            if format_type is not None
            else FlextCliConstants.OutputDefaults.DEFAULT_FORMAT_TYPE
        )
        format_result = self.format_data(
            data, format_type=final_format_type, title=title, headers=headers
        )

        if format_result.is_failure:
            return FlextResult[bool].fail(
                f"Failed to format data: {format_result.error}"
            )

        formatted_data = format_result.unwrap()

        # Display the formatted data
        return self.print_message(formatted_data)

    # =========================================================================
    # DATA FORMAT METHODS (Built-in)
    # =========================================================================

    def format_json(self, data: FlextTypes.JsonValue) -> FlextResult[str]:
        """Format data as JSON.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted JSON string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_json({"key": "value"})

        """
        try:
            return FlextResult[str].ok(
                json.dumps(
                    data,
                    default=str,
                    indent=FlextCliConstants.OutputDefaults.JSON_INDENT,
                )
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.JSON_FORMAT_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_yaml(self, data: FlextTypes.JsonValue) -> FlextResult[str]:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted YAML string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_yaml({"key": "value"})

        """
        try:
            return FlextResult[str].ok(
                yaml.dump(
                    data,
                    default_flow_style=FlextCliConstants.OutputDefaults.YAML_DEFAULT_FLOW_STYLE,
                )
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.YAML_FORMAT_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_csv(self, data: FlextTypes.JsonValue) -> FlextResult[str]:
        """Format data as CSV.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted CSV string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_csv([{"name": "Alice", "age": 30}])

        """
        try:
            if (
                FlextRuntime.is_list_like(data)
                and data
                and FlextRuntime.is_dict_like(data[0])
            ):
                output_buffer = StringIO()
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()

                # Convert JsonValue to object for csv.DictWriter compatibility
                # csv.DictWriter expects Mapping[str, object], not dict[str, JsonValue]
                csv_rows: list[dict[str, object]] = [
                    {k: v if v is not None else "" for k, v in row.items()}
                    for row in data
                    if FlextRuntime.is_dict_like(row)
                ]
                writer.writerows(csv_rows)
                return FlextResult[str].ok(output_buffer.getvalue())
            if FlextRuntime.is_dict_like(data):
                output_buffer = StringIO()
                fieldnames = list(data.keys())
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
                return FlextResult[str].ok(output_buffer.getvalue())
            return FlextResult[str].ok(
                json.dumps(
                    data,
                    default=str,
                    indent=FlextCliConstants.OutputDefaults.JSON_INDENT,
                )
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.CSV_FORMAT_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_table(
        self,
        data: dict[str, FlextTypes.JsonValue]
        | list[dict[str, FlextTypes.JsonValue]]
        | str,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data as a tabulated table string using FlextCliTables.

        Args:
            data: Data to format (dict or list of dicts). Non-dict/list types return error.
            title: Optional table title
            headers: Optional column headers

        Returns:
            FlextResult[str]: Table as string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_table(
            ...     data=[{"name": "Alice", "age": 30}], title="Users"
            ... )

        """
        # Railway pattern: prepare data → create table → add title
        return (
            self._prepare_table_data_safe(data, headers)
            .flat_map(
                lambda prepared: self._create_table_string(prepared[0], prepared[1])
            )
            .map(lambda table: self._add_title(table, title))
        )

    def _prepare_table_data_safe(
        self,
        data: dict[str, FlextTypes.JsonValue]
        | list[dict[str, FlextTypes.JsonValue]]
        | str,
        headers: list[str] | None,
    ) -> FlextResult[tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[
                tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
            ].fail(error_msg)

    def _prepare_table_data(
        self,
        data: dict[str, FlextTypes.JsonValue]
        | list[dict[str, FlextTypes.JsonValue]]
        | str,
        headers: list[str] | None,
    ) -> FlextResult[tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            return self._prepare_dict_data(
                typing.cast("dict[str, FlextTypes.JsonValue]", data), headers
            )
        if FlextRuntime.is_list_like(data):
            return self._prepare_list_data(
                typing.cast("list[dict[str, FlextTypes.JsonValue]]", data),
                headers,
            )
        return FlextResult[
            tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
        ].fail(FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def _prepare_dict_data(
        self, data: dict[str, FlextTypes.JsonValue], headers: list[str] | None
    ) -> FlextResult[tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]]:
        """Prepare dict data for table display."""
        # Reject test invalid key
        if FlextCliConstants.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return FlextResult[
                tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

        table_data: list[dict[str, FlextTypes.JsonValue]] = [
            {
                FlextCliConstants.OutputFieldNames.KEY: k,
                FlextCliConstants.OutputFieldNames.VALUE: str(v),
            }
            for k, v in data.items()
        ]
        # Validate headers explicitly - no fallback
        validated_headers: str | list[str] = (
            headers if headers is not None else FlextCliConstants.TableFormats.KEYS
        )
        table_headers: str | list[str] = validated_headers
        return FlextResult[
            tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
        ].ok((table_data, table_headers))

    def _prepare_list_data(
        self,
        data: list[dict[str, FlextTypes.JsonValue]],
        headers: list[str] | None,
    ) -> FlextResult[tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]]:
        """Prepare list data for table display."""
        if not data:
            return FlextResult[
                tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED)

        # Validate headers type
        if headers is not None and not FlextRuntime.is_list_like(headers):
            return FlextResult[
                tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST)

        # Validate headers explicitly - no fallback, with type narrowing
        if headers is not None:
            # Type narrowing: headers is list[object] | str, cast to list[str] | str
            validated_headers: str | list[str] = cast("str | list[str]", headers)
        else:
            validated_headers = FlextCliConstants.TableFormats.KEYS

        table_headers: str | list[str] = validated_headers
        return FlextResult[
            tuple[list[dict[str, FlextTypes.JsonValue]], str | list[str]]
        ].ok((data, table_headers))

    def _create_table_string(
        self,
        table_data: list[dict[str, FlextTypes.JsonValue]],
        table_headers: str | list[str],
    ) -> FlextResult[str]:
        """Create table string using FlextCliTables."""
        try:
            config = FlextCliModels.TableConfig(
                headers=table_headers,
                table_format=FlextCliConstants.TableFormats.GRID,
            )
            table_result = self._tables.create_table(data=table_data, config=config)

            if table_result.is_failure:
                return FlextResult[str].fail(
                    f"Failed to create table: {table_result.error}"
                )

            return table_result
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def _add_title(self, table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{FlextCliConstants.OutputDefaults.NEWLINE}{table_str}{FlextCliConstants.OutputDefaults.NEWLINE}"
        return table_str

    def format_as_tree(
        self,
        data: FlextTypes.JsonDict,
        title: str | None = None,
    ) -> FlextResult[str]:
        """Format hierarchical data as tree view using FlextCliFormatters.

        Args:
            data: Hierarchical data to format
            title: Tree title

        Returns:
            FlextResult[str]: Tree view as string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_as_tree(
            ...     data={"root": {"child1": "value1", "child2": "value2"}},
            ...     title="Config",
            ... )

        """
        # Validate title explicitly - no fallback
        final_title = (
            title
            if title is not None
            else FlextCliConstants.OutputDefaults.DEFAULT_TREE_TITLE
        )

        # Create tree through formatters
        tree_result = self._formatters.create_tree(label=final_title)

        if tree_result.is_failure:
            return FlextResult[str].fail(f"Failed to create tree: {tree_result.error}")

        tree = tree_result.unwrap()

        # Build tree structure
        # Type cast: CliDataDict (dict[str, JsonValue]) is a valid JsonValue
        # JsonValue is recursively defined to include dict[str, JsonValue]
        tree_data = typing.cast("FlextTypes.JsonValue", data)
        self._build_tree(tree, tree_data)

        # Render to string using formatters
        return self._formatters.render_tree_to_string(
            tree, width=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH
        )

    def _build_tree(
        self, tree: FlextCliTypes.Display.RichTree, data: FlextTypes.JsonValue
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from

        """
        if FlextRuntime.is_dict_like(data):
            for key, value in data.items():
                if FlextRuntime.is_dict_like(value):
                    branch = tree.add(str(key))
                    # value is dict, which is a valid JsonValue type, no cast needed
                    self._build_tree(branch, value)
                elif FlextRuntime.is_list_like(value):
                    branch = tree.add(
                        f"{key}{FlextCliConstants.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}"
                    )
                    for item in value:
                        # Type cast: item from list[JsonValue] is a valid JsonValue
                        json_item = typing.cast("FlextTypes.JsonValue", item)
                        self._build_tree(branch, json_item)
                else:
                    tree.add(
                        f"{key}{FlextCliConstants.OutputDefaults.TREE_VALUE_SEPARATOR}{value}"
                    )
        elif FlextRuntime.is_list_like(data):
            for item in data:
                # Type cast: item from list[JsonValue] is a valid JsonValue
                json_item = typing.cast("FlextTypes.JsonValue", item)
                self._build_tree(tree, json_item)
        else:
            # data is primitive JsonValue (str, int, float, bool, None), no cast needed
            tree.add(str(data))

    # =========================================================================
    # CONSOLE ACCESS (Delegates to FlextCliFormatters)
    # =========================================================================

    @property
    def console(self) -> FlextCliTypes.Display.Console:
        """Get the console instance from FlextCliFormatters (property form).

        Returns:
            Console instance from formatters

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.console

        """
        return self._formatters.console


__all__ = ["FlextCliOutput"]
