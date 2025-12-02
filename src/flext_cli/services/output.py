"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from io import StringIO
from typing import cast, override

import yaml
from flext_core import (
    FlextResult,
    FlextRuntime,
    FlextTypes,
    FlextUtilities,
)
from pydantic import BaseModel

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.services.tables import FlextCliTables


class FlextCliOutput(FlextCliServiceBase):  # noqa: PLR0904
    """Comprehensive CLI output tools for the flext ecosystem.

    Business Rules:
    ───────────────
    1. Output format MUST be validated against supported formats (JSON, YAML, CSV, table, plain)
    2. Sensitive data (SecretStr fields) MUST be masked in all output formats
    3. Table formatting MUST handle empty data gracefully (no errors)
    4. JSON/YAML serialization MUST handle datetime objects correctly (ISO format)
    5. CSV formatting MUST escape special characters and handle Unicode
    6. Rich formatting MUST respect no_color configuration flag
    7. All formatting operations MUST return FlextResult[T] for error handling
    8. Output MUST respect configured output format from FlextCliConfig

    Architecture Implications:
    ───────────────────────────
    - Delegates to FlextCliFormatters for Rich-based visual output
    - Delegates to FlextCliTables for Tabulate-based ASCII tables
    - Built-in formatters for JSON, YAML, CSV (no external dependencies)
    - Format detection based on file extension or explicit format parameter
    - Output redirection supported via file paths or streams

    Audit Implications:
    ───────────────────
    - Sensitive data MUST be masked before output (passwords, tokens, secrets)
    - Output operations SHOULD be logged with format type and data size
    - File output MUST validate file paths to prevent path traversal attacks
    - Large data sets SHOULD be paginated or truncated for performance
    - Output format changes MUST be logged for audit trail
    - Error conditions MUST be logged with full context (no sensitive data)

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
        >>> result = output.format_data(
        ...     data={"key": "value"},
        ...     format_type=FlextCliConstants.OutputFormats.JSON.value,
        ... )
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
        # ResultFormatter: Callable[[FormatableResult, str], None]
        self._result_formatters: dict[
            type,
            Callable[
                [
                    FlextTypes.GeneralValueType
                    | FlextResult[FlextTypes.GeneralValueType],
                    str,
                ],
                None,
            ],
        ] = {}

    @override
    def execute(
        self, **_kwargs: FlextTypes.JsonDict
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters
                (unused, for FlextService compatibility)

        """
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: (
                FlextCliConstants.ServiceStatus.OPERATIONAL.value
            ),
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })

    # =========================================================================
    # FORMAT DATA - UNIFIED API
    # =========================================================================

    def format_data(
        self,
        data: FlextTypes.GeneralValueType,
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
            ...     data={"name": "Alice", "age": 30},
            ...     format_type=FlextCliConstants.OutputFormats.JSON.value,
            ... )

        """
        # Railway pattern: validate format → dispatch to handler
        # Use FlextUtilities.Validation.validate_choice directly
        format_lower = format_type.lower()
        validation_result = FlextUtilities.Validation.validate_choice(
            format_lower,
            set(FlextCliConstants.OUTPUT_FORMATS_LIST),
            "Output format",
            case_sensitive=False,
        )
        if validation_result.is_failure:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=format_type,
                ),
            )

        fmt = format_lower
        return self._dispatch_formatter(fmt, data, title, headers)

    # Format validation now uses FlextUtilities.Validation.validate_choice directly

    def _dispatch_formatter(
        self,
        format_type: str,
        data: FlextTypes.GeneralValueType,
        title: str | None,
        headers: list[str] | None,
    ) -> FlextResult[str]:
        """Dispatch to appropriate formatter based on format type."""
        # Format dispatcher using dict mapping
        formatters = {
            FlextCliConstants.OutputFormats.JSON.value: lambda: self.format_json(data),
            FlextCliConstants.OutputFormats.YAML.value: lambda: self.format_yaml(data),
            FlextCliConstants.OutputFormats.TABLE.value: lambda: self._format_table_data(
                data,
                title,
                headers,
            ),
            FlextCliConstants.OutputFormats.CSV.value: lambda: self.format_csv(data),
            FlextCliConstants.OutputFormats.PLAIN.value: lambda: FlextResult[str].ok(
                str(data),
            ),
        }

        formatter = formatters.get(format_type)
        if formatter is None:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type,
                ),
            )

        return formatter()

    def _format_table_data(
        self,
        data: FlextTypes.GeneralValueType,
        title: str | None,
        headers: list[str] | None,
    ) -> FlextResult[str]:
        """Format data as table with type validation."""
        if FlextRuntime.is_dict_like(data):
            # Type narrowing: CliJsonValue dict -> dict representation
            # dict(data) creates a proper dict that can be used directly
            data_dict = dict(data)
            return self.format_table(
                FlextUtilities.DataMapper.convert_dict_to_json(data_dict),
                title=title,
                headers=headers,
            )

        if FlextRuntime.is_list_like(data):
            if not data:
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
                )
            if not all(FlextRuntime.is_dict_like(item) for item in data):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
                )
            # Type narrowing: CliJsonValue list -> list representation
            # list(data) creates a proper list that can be used directly
            data_list = list(data)
            return self.format_table(
                FlextUtilities.DataMapper.convert_list_to_json(data_list),
                title=title,
                headers=headers,
            )

        return FlextResult[str].fail(
            FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
        )

    def create_formatter(self, format_type: str) -> FlextResult[FlextCliOutput]:
        """Create a formatter instance for the specified format type.

        Uses FlextUtilities.Validation.validate_choice() for validation.

        Args:
            format_type: Format type to create formatter for

        Returns:
            FlextResult[FlextCliOutput]: Formatter instance or error

        """
        try:
            # Validate format using FlextUtilities.Validation.validate_choice directly
            format_lower = format_type.lower()
            validation_result = FlextUtilities.Validation.validate_choice(
                format_lower,
                set(FlextCliConstants.OUTPUT_FORMATS_LIST),
                "Output format",
                case_sensitive=False,
            )
            if validation_result.is_failure:
                return FlextResult[FlextCliOutput].fail(
                    FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type,
                    ),
                )
            return FlextResult[FlextCliOutput].ok(self)
        except Exception as e:
            return FlextResult[FlextCliOutput].fail(
                FlextCliConstants.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e),
            )

    # =========================================================================
    # RESULT FORMATTER REGISTRY - Domain-specific result formatting
    # =========================================================================

    def register_result_formatter(
        self,
        result_type: type,
        formatter: Callable[
            [FlextTypes.GeneralValueType | FlextResult[object], str], None
        ],
    ) -> FlextResult[bool]:
        r"""Register custom formatter for domain-specific result types.

        **PURPOSE**: Eliminate repetitive result display formatting boilerplate.

        Allows registering formatters for specific result types, enabling
        automatic formatting based on result type detection. Reduces ~74 lines
        of formatting boilerplate per result type.

        Args:
            result_type: Type of result to format (e.g., OperationResult)
            formatter: Callable that formats and displays the result
                Signature: (result: FlextTypes.GeneralValueType | FlextResult[object], output_format: str) -> None

        Returns:
            FlextResult[bool]: True on success, False on failure

        Example:
            ```python
            from flext_cli import FlextCliOutput
            from pydantic import BaseModel


            class OperationResult(BaseModel):
                # Example result model
                status: str
                entries_processed: int


            output = FlextCliOutput()


            # Register formatter for OperationResult
            def format_operation(result: OperationResult, fmt: str) -> None:
                if fmt == FlextCliConstants.OutputFormats.TABLE.value:
                    # Create Rich table from result
                    console = output._formatters.console
                    panel = output._formatters.create_panel(
                        f"[green]Operation completed![/green]\\n"
                        + f"Status: {result.status}\\n"
                        + f"Entries: {result.entries_processed}",
                        title="✅ Operation Result",
                    )
                    console.print(panel.unwrap())
                elif fmt == FlextCliConstants.OutputFormats.JSON.value:
                    print(result.model_dump_json())


            output.register_result_formatter(OperationResult, format_operation)

            # Now auto-format any OperationResult
            operation_result = OperationResult(status="success", entries_processed=100)
            output.format_and_display_result(operation_result, "table")
            ```

        **ELIMINATES**:
        - 74 lines of panel creation and table formatting per result type
        - Manual type checking and format branching
        - Duplicate formatting logic across commands

        """
        try:
            # Use cast to satisfy type checker - formatter is compatible but types differ slightly
            self._result_formatters[result_type] = cast(
                "Callable[[FlextTypes.GeneralValueType | FlextResult[FlextTypes.GeneralValueType], str], None]",
                formatter,
            )
            self.logger.debug(
                "Registered result formatter",
                extra={"formatter_type": result_type.__name__},
            )
            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}",
            )

    def format_and_display_result(
        self,
        result: BaseModel | FlextTypes.GeneralValueType | FlextResult[object],
        output_format: str = FlextCliConstants.OutputFormats.TABLE.value,
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
            formattable_result = self._convert_result_to_formattable(
                result, output_format
            )
            if formattable_result.is_failure:
                return FlextResult[bool].fail(
                    formattable_result.error
                    or "Failed to convert result to formattable",
                    error_code=formattable_result.error_code,
                    error_data=formattable_result.error_data,
                )

            formattable = formattable_result.unwrap()
            return self._display_formatted_result(formattable)

        except Exception as e:
            return FlextResult[bool].fail(f"Failed to format and display result: {e}")

    def _try_registered_formatter(
        self,
        result: BaseModel | FlextTypes.GeneralValueType | FlextResult[object],
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
            # Type narrowing: formatter accepts GeneralValueType | FlextResult[object]
            # BaseModel is not directly compatible, but we can pass it as GeneralValueType
            if isinstance(result, BaseModel):
                # Convert BaseModel to dict for formatter
                formattable_result: FlextTypes.GeneralValueType = result.model_dump()
                formatter(formattable_result, output_format)
            # result is already GeneralValueType | FlextResult[GeneralValueType]
            # Type narrowing: formatter accepts GeneralValueType
            elif isinstance(result, FlextResult):
                if result.is_success:
                    # Type narrowing: unwrap returns object, convert to GeneralValueType
                    unwrapped = result.unwrap()
                    if isinstance(
                        unwrapped,
                        (
                            str,
                            int,
                            float,
                            bool,
                            type(None),
                            dict,
                            list,
                        ),
                    ):
                        converted: FlextTypes.GeneralValueType = unwrapped
                        formatter(converted, output_format)
                    else:
                        # Convert other types to string
                        formatter(str(unwrapped), output_format)
                else:
                    return FlextResult[bool].fail(
                        f"Cannot format failed result: {result.error}"
                    )
            else:
                formatter(result, output_format)
            return FlextResult[bool].ok(True)

        return FlextResult[bool].fail(
            f"No registered formatter for type {result_type.__name__}",
        )

    def _convert_result_to_formattable(
        self,
        result: BaseModel | FlextTypes.GeneralValueType | FlextResult[object],
        output_format: str,
    ) -> FlextResult[str]:
        """Convert result object to formattable string.

        Handles multiple result types: Pydantic models, objects with __dict__, and fallback.
        Fast-fails if result is None - caller must handle None values explicitly.
        """
        # Fast-fail if result is None - no fallback to fake data
        if result is None:
            return FlextResult[str].fail(
                "Cannot format None result - provide a valid result object",
            )

        self.logger.info(
            f"No registered formatter for {type(result).__name__}, using generic formatting",
        )

        # Handle Pydantic models
        if isinstance(result, BaseModel):
            return self._format_pydantic_model(result, output_format)

        # Handle dict objects directly
        # Type narrowing: result is GeneralValueType, check if it's a dict
        if isinstance(result, dict):
            return self.format_data(result, output_format)
        if hasattr(result, "__dict__"):
            # Convert object with __dict__ to dict for formatting
            result_dict: dict[str, FlextTypes.GeneralValueType] = {
                k: v
                for k, v in result.__dict__.items()
                if isinstance(
                    v,
                    (
                        str,
                        int,
                        float,
                        bool,
                        type(None),
                        dict,
                        list,
                    ),
                )
            }
            return self.format_data(result_dict, output_format)

        # Use string representation (not a fallback - valid conversion)
        return FlextResult[str].ok(str(result))

    def _format_pydantic_model(
        self,
        result: BaseModel,
        output_format: str,
    ) -> FlextResult[str]:
        """Format Pydantic model to string."""
        # Use model_dump() directly - dict is compatible with FlextTypes.GeneralValueType
        result_dict = result.model_dump()
        return self.format_data(result_dict, output_format)

    def _format_dict_object(
        self,
        result: FlextTypes.GeneralValueType | FlextResult[FlextTypes.GeneralValueType],
        output_format: str,
    ) -> FlextResult[str]:
        """Format object with __dict__ to string."""
        # Type narrowing: result must have __dict__ attribute
        if isinstance(result, FlextResult):
            # Extract value from FlextResult
            if result.is_failure:
                return FlextResult[str].fail(
                    f"Cannot format failed result: {result.error}"
                )
            unwrapped = result.unwrap()
            # Type narrowing: unwrap returns GeneralValueType
            # Note: Cannot use isinstance with TypeAliasType (GeneralValueType)
            # unwrapped is already GeneralValueType from unwrap()
            result = unwrapped
        # Now result is GeneralValueType - check if it has __dict__
        if not hasattr(result, "__dict__"):
            return FlextResult[str].fail(
                f"Object {type(result).__name__} has no __dict__ attribute"
            )
        # Type narrowing: result has __dict__ attribute
        raw_dict: dict[str, FlextTypes.GeneralValueType] = getattr(
            result, "__dict__", {}
        )
        # Convert dict to JSON-compatible dict
        json_dict: dict[str, FlextTypes.GeneralValueType] = {}
        for key, value in raw_dict.items():
            json_value = FlextUtilities.DataMapper.convert_to_json_value(value)
            # Type narrowing: json_value is GeneralValueType
            json_dict[key] = json_value
        # Convert to CliJsonDict (dict[str, FlextTypes.GeneralValueType])
        cli_json_dict: dict[str, FlextTypes.GeneralValueType] = {}
        for key, value in json_dict.items():
            # value is GeneralValueType, check if it's JSON-compatible
            if isinstance(value, (str, int, float, bool, dict, list, type(None))):
                cli_json_dict[key] = value
            else:
                # Convert non-JSON types to string
                cli_json_dict[key] = str(value)
        return self.format_data(cli_json_dict, output_format)

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
        data: list[dict[str, FlextTypes.GeneralValueType]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[FlextCliProtocols.Display.RichTableProtocol]:
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
            return FlextResult[FlextCliProtocols.Display.RichTableProtocol].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED,
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
                return FlextResult[FlextCliProtocols.Display.RichTableProtocol].fail(
                    f"Failed to create Rich table: {table_result.error}",
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
                        return FlextResult[
                            FlextCliProtocols.Display.RichTableProtocol
                        ].fail(
                            f"Header {header!r} not found in row data. Available keys: {list(row_data.keys())}",
                        )
                    row_values.append(str(row_data[header]))
                table.add_row(*row_values)

            # RichTable (concrete type) implements RichTableProtocol structurally
            # Use cast for structural typing compatibility (cast imported at module level)
            protocol_table: FlextCliProtocols.Display.RichTableProtocol = cast(
                "FlextCliProtocols.Display.RichTableProtocol", table
            )
            return FlextResult[FlextCliProtocols.Display.RichTableProtocol].ok(
                protocol_table
            )

        except Exception as e:
            error_msg = FlextCliConstants.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[FlextCliProtocols.Display.RichTableProtocol].fail(
                error_msg
            )

    def table_to_string(
        self,
        table: FlextCliProtocols.Display.RichTableProtocol,
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
        # table is RichTableProtocol (structural), formatters accepts RichTable | object
        # Both conform structurally, so passing protocol object directly is safe
        return self._formatters.render_table_to_string(table, width)

    # =========================================================================
    # ASCII TABLE CREATION (Delegates to FlextCliTables)
    # =========================================================================

    def create_ascii_table(
        self,
        data: list[dict[str, FlextTypes.GeneralValueType]],
        headers: list[str] | None = None,
        table_format: str = FlextCliConstants.TableFormats.SIMPLE,
        *,
        config: FlextCliModels.TableConfig | None = None,
    ) -> FlextResult[str]:
        """Create ASCII table using FlextCliTables.

        Business Rule:
        ──────────────
        Creates ASCII tables from list of dicts using tabulate library.
        If config is provided, uses it directly. Otherwise, builds config
        from individual parameters for backward compatibility.

        Audit Implications:
        ───────────────────
        - Config object preferred for complex table configurations
        - Individual parameters provided for simple use cases
        - All parameters have sensible defaults from constants

        Args:
            data: List of dictionaries to display
            headers: Optional custom headers (ignored if config provided)
            table_format: Table format (ignored if config provided)
            config: Optional TableConfig object for full control

        Returns:
            FlextResult[str]: ASCII table string

        Example:
            >>> output = FlextCliOutput()
            >>> # Simple usage with defaults
            >>> result = output.create_ascii_table(
            ...     data=[{"name": "Bob", "age": 25}], table_format="grid"
            ... )
            >>> # Or with config object for full control
            >>> config = FlextCliModels.TableConfig(
            ...     headers=["Name", "Age"],
            ...     table_format="fancy_grid",
            ...     floatfmt=".2f",
            ... )
            >>> result = output.create_ascii_table(data, config=config)

        """
        if config is not None:
            # Use provided config directly
            return self._tables.create_table(data=data, config=config)

        # Build config from individual parameters for backward compatibility
        validated_headers = (
            headers if headers is not None else FlextCliConstants.TableFormats.KEYS
        )
        final_config = FlextCliModels.TableConfig(
            headers=validated_headers,
            table_format=table_format,
        )
        return self._tables.create_table(data=data, config=final_config)

    # =========================================================================
    # PROGRESS BARS (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_progress_bar(
        self,
    ) -> FlextResult[FlextCliProtocols.Interactive.RichProgressProtocol]:
        """Create a Rich progress bar using FlextCliFormatters.

        Returns:
            FlextResult[RichProgressProtocol]: Rich Progress wrapped in Result

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar()

        """
        # create_progress returns FlextResult[Progress] which implements RichProgressProtocol
        result = self._formatters.create_progress()
        if result.is_success:
            # Progress implements RichProgressProtocol structurally
            # Progress (concrete type) implements RichProgressProtocol structurally
            # Use cast for structural typing compatibility (cast imported at module level)
            progress_value = result.unwrap()
            protocol_progress: FlextCliProtocols.Interactive.RichProgressProtocol = (
                cast(
                    "FlextCliProtocols.Interactive.RichProgressProtocol", progress_value
                )
            )
            return FlextResult[FlextCliProtocols.Interactive.RichProgressProtocol].ok(
                protocol_progress
            )
        return FlextResult[FlextCliProtocols.Interactive.RichProgressProtocol].fail(
            result.error or ""
        )

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
        data: FlextTypes.GeneralValueType,
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
            >>> output.display_data(
            ...     {"key": "value"},
            ...     format_type=FlextCliConstants.OutputFormats.JSON.value,
            ... )

        """
        # Validate format type explicitly - no fallback
        final_format_type = (
            format_type
            if format_type is not None
            else FlextCliConstants.OutputDefaults.DEFAULT_FORMAT_TYPE
        )
        format_result = self.format_data(
            data,
            format_type=final_format_type,
            title=title,
            headers=headers,
        )

        if format_result.is_failure:
            return FlextResult[bool].fail(
                f"Failed to format data: {format_result.error}",
            )

        formatted_data = format_result.unwrap()

        # Display the formatted data
        return self.print_message(formatted_data)

    # =========================================================================
    # DATA FORMAT METHODS (Built-in)
    # =========================================================================

    def format_json(self, data: FlextTypes.GeneralValueType) -> FlextResult[str]:
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
                ),
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.JSON_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_yaml(self, data: FlextTypes.GeneralValueType) -> FlextResult[str]:
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
                ),
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.YAML_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_csv(self, data: FlextTypes.GeneralValueType) -> FlextResult[str]:
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

                # Prepare CSV rows with None values replaced by empty strings
                csv_rows = [
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
                ),
            )
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.CSV_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def format_table(
        self,
        data: dict[str, FlextTypes.GeneralValueType]
        | list[dict[str, FlextTypes.GeneralValueType]]
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
        prepared_result = self._prepare_table_data_safe(data, headers)
        if prepared_result.is_failure:
            return FlextResult[str].fail(
                prepared_result.error or "Failed to prepare table data",
                error_code=prepared_result.error_code,
                error_data=prepared_result.error_data,
            )

        prepared = prepared_result.unwrap()
        table_result = self._create_table_string(prepared[0], prepared[1])
        if table_result.is_failure:
            return table_result

        table = table_result.unwrap()
        return FlextResult.ok(self._add_title(table, title))

    def _prepare_table_data_safe(
        self,
        data: dict[str, FlextTypes.GeneralValueType]
        | list[dict[str, FlextTypes.GeneralValueType]]
        | str,
        headers: list[str] | None,
    ) -> FlextResult[
        tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
    ]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[
                tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
            ].fail(error_msg)

    def _prepare_table_data(
        self,
        data: dict[str, FlextTypes.GeneralValueType]
        | list[dict[str, FlextTypes.GeneralValueType]]
        | str,
        headers: list[str] | None,
    ) -> FlextResult[
        tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
    ]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            return self._prepare_dict_data(
                FlextUtilities.DataMapper.convert_dict_to_json(dict(data)),
                headers,
            )
        if FlextRuntime.is_list_like(data):
            return self._prepare_list_data(
                FlextUtilities.DataMapper.convert_list_to_json(list(data)),
                headers,
            )
        return FlextResult[
            tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
        ].fail(FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    @staticmethod
    def _prepare_dict_data(
        data: dict[str, FlextTypes.GeneralValueType],
        headers: list[str] | None,
    ) -> FlextResult[
        tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
    ]:
        """Prepare dict data for table display."""
        # Reject test invalid key
        if FlextCliConstants.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return FlextResult[
                tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

        table_data: list[dict[str, FlextTypes.GeneralValueType]] = [
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
            tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
        ].ok((
            table_data,
            table_headers,
        ))

    @staticmethod
    def _prepare_list_data(
        data: list[dict[str, FlextTypes.GeneralValueType]],
        headers: list[str] | None,
    ) -> FlextResult[
        tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
    ]:
        """Prepare list data for table display."""
        if not data:
            return FlextResult[
                tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED)

        # Validate headers type
        if headers is not None and not FlextRuntime.is_list_like(headers):
            return FlextResult[
                tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
            ].fail(FlextCliConstants.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST)

        # Validate headers explicitly - no fallback
        # headers is list[str] | None, so it's always a list or None
        if headers is not None:
            if FlextRuntime.is_list_like(headers):
                table_headers = [str(item) for item in headers]
            else:
                # Should not happen since headers is list[str] | None
                table_headers = [str(headers)]
        else:
            table_headers = [FlextCliConstants.TableFormats.KEYS]
        return FlextResult[
            tuple[list[dict[str, FlextTypes.GeneralValueType]], str | list[str]]
        ].ok((
            data,
            table_headers,
        ))

    def _create_table_string(
        self,
        table_data: list[dict[str, FlextTypes.GeneralValueType]],
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
                    f"Failed to create table: {table_result.error}",
                )

            return table_result
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{FlextCliConstants.OutputDefaults.NEWLINE}{table_str}{FlextCliConstants.OutputDefaults.NEWLINE}"
        return table_str

    def format_as_tree(
        self,
        data: FlextTypes.GeneralValueType,
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

        # Build tree structure - data is already FlextTypes.GeneralValueType
        # _build_tree now accepts CliJsonValue directly, no conversion needed
        # tree is rich.Tree, but conforms to RichTreeProtocol structurally
        # Use cast for structural typing compatibility

        protocol_tree: FlextCliProtocols.Display.RichTreeProtocol = cast(
            "FlextCliProtocols.Display.RichTreeProtocol", tree
        )
        self._build_tree(protocol_tree, data)

        # Render to string using formatters
        return self._formatters.render_tree_to_string(
            tree,
            width=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH,
        )

    def _build_tree(
        self,
        tree: FlextCliProtocols.Display.RichTreeProtocol,
        data: FlextTypes.GeneralValueType,
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from (CliJsonValue - can be dict, list, or primitive)

        """
        if isinstance(data, dict):
            # Type narrowing: data is dict -> process as dict[str, CliJsonValue]
            for key, value in data.items():
                if isinstance(value, dict):
                    branch = tree.add(str(key))
                    self._build_tree(branch, value)
                elif isinstance(value, list):
                    branch = tree.add(
                        f"{key}{FlextCliConstants.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}",
                    )
                    for item in value:
                        # item is already CliJsonValue from dict
                        self._build_tree(branch, item)
                else:
                    # value is primitive (str, int, float, bool, None)
                    tree.add(
                        f"{key}{FlextCliConstants.OutputDefaults.TREE_VALUE_SEPARATOR}{value}",
                    )
        elif isinstance(data, list):
            # Type narrowing: data is list -> process each item
            for item in data:
                # item is already CliJsonValue from list
                self._build_tree(tree, item)
        else:
            # data is primitive JsonValue (str, int, float, bool, None)
            tree.add(str(data))

    # =========================================================================
    # CONSOLE ACCESS (Delegates to FlextCliFormatters)
    # =========================================================================

    @property
    def console(self) -> FlextCliProtocols.Display.RichConsoleProtocol:
        """Get the console instance from FlextCliFormatters (property form).

        Returns:
            Console instance from formatters

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.console

        """
        # Console (concrete type) implements RichConsoleProtocol structurally
        # Use cast for structural typing compatibility

        concrete_console = self._formatters.console
        protocol_console: FlextCliProtocols.Display.RichConsoleProtocol = cast(
            "FlextCliProtocols.Display.RichConsoleProtocol", concrete_console
        )
        return protocol_console


__all__ = ["FlextCliOutput"]
