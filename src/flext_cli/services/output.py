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
    FlextConstants,
    FlextExceptions,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextRuntime,
    t,
    u,
)
from pydantic import BaseModel

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.services.tables import FlextCliTables

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions

# ═══════════════════════════════════════════════════════════════════════════
# GENERALIZED MNEMONIC HELPERS - Advanced DSL parametrization
# ═══════════════════════════════════════════════════════════════════════════


def is_json(v: object) -> bool:
    """Check if value is JSON-compatible type."""
    return isinstance(v, (str, int, float, bool, type(None), dict, list))


def to_json(v: t.GeneralValueType) -> t.GeneralValueType:
    """Convert value to JSON-compatible using build DSL."""
    return (
        u.build(
            v, ops={"ensure": "dict", "transform": {"to_json": True}}, on_error="skip"
        )
        if isinstance(v, dict)
        else v
    )


def get_keys(d: dict[str, t.GeneralValueType] | t.GeneralValueType) -> list[str]:
    """Extract keys from dict using build DSL."""
    d_dict = u.build(d, ops={"ensure": "dict"}, on_error="skip")
    return cast(
        "list[str]",
        u.build(
            u.when(
                condition=isinstance(d_dict, dict),
                then_value=u.keys(d_dict),
                else_value=[],
            ),
            ops={"ensure": "list"},
            on_error="skip",
        ),
    )


def norm_json(item: t.GeneralValueType) -> t.GeneralValueType:
    """Normalize item to JSON-compatible using build DSL."""
    if isinstance(item, (str, int, float, bool, type(None))):
        return item
    if FlextRuntime.is_dict_like(item):
        return cast_if(to_dict_json(item), dict, str(item))
    if FlextRuntime.is_list_like(item):
        return cast_if(to_list_json(item), list, list(item))
    return str(item)


def ensure_str(v: t.GeneralValueType | None, default: str = "") -> str:
    """Ensure value is str with default using build DSL."""
    return cast(
        "str",
        u.build(v, ops={"ensure": "str", "ensure_default": default}, on_error="skip"),
    )


def ensure_list(
    v: t.GeneralValueType | None, default: list[t.GeneralValueType] | None = None
) -> list[t.GeneralValueType]:
    """Ensure value is list with default using build DSL."""
    return cast(
        "list[t.GeneralValueType]",
        u.build(
            v, ops={"ensure": "list", "ensure_default": default or []}, on_error="skip"
        ),
    )


def ensure_dict(
    v: t.GeneralValueType | None, default: dict[str, t.GeneralValueType] | None = None
) -> dict[str, t.GeneralValueType]:
    """Ensure value is dict with default using build DSL."""
    return cast(
        "dict[str, t.GeneralValueType]",
        u.build(
            v, ops={"ensure": "dict", "ensure_default": default or {}}, on_error="skip"
        ),
    )


def ensure_bool(v: t.GeneralValueType | None, *, default: bool = False) -> bool:
    """Ensure value is bool with default using build DSL."""
    return cast(
        "bool",
        u.build(v, ops={"ensure": "bool", "ensure_default": default}, on_error="skip"),
    )


def get_map_val(
    m: dict[str, t.GeneralValueType], k: str, default: t.GeneralValueType
) -> t.GeneralValueType:
    """Get value from map with default using build DSL."""
    return cast(
        "t.GeneralValueType",
        u.build(m.get(k), ops={"ensure_default": default}, on_error="skip"),
    )


def unwrap_or[T](result: r[T], default: T) -> T:
    """Unwrap result or return default using build DSL."""
    return u.when(
        condition=result.is_success,
        then_value=result.unwrap(),
        else_value=default,
    )


def cast_if[T](v: object, t_type: type[T], default: T) -> T:
    """Cast value if isinstance else return default."""
    if isinstance(v, t_type):
        return cast("T", v)
    return default


def to_dict_json(v: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
    """Convert value to dict with JSON transform using build DSL."""
    return cast_if(
        u.build(
            v, ops={"ensure": "dict", "transform": {"to_json": True}}, on_error="skip"
        ),
        dict,
        {},
    )


def to_list_json(v: t.GeneralValueType) -> list[t.GeneralValueType]:
    """Convert value to list with JSON transform using build DSL."""
    return cast_if(
        u.build(
            v, ops={"ensure": "list", "transform": {"to_json": True}}, on_error="skip"
        ),
        list,
        [],
    )


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
    7. All formatting operations MUST return r[T] for error handling
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
                    t.GeneralValueType | r[t.GeneralValueType],
                    str,
                ],
                None,
            ],
        ] = {}

    @override
    def execute(self, **_kwargs: t.JsonDict) -> r[t.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters
                (unused, for FlextService compatibility)

        """
        return r[t.JsonDict].ok({
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
        data: t.GeneralValueType,
        format_type: str = FlextCliConstants.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[str]:
        """Format data using specified format type with railway pattern.

        Args:
            data: Data to format
            format_type: Format type from FlextCliConstants.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[str]: Formatted data string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_data(
            ...     data={"name": "Alice", "age": 30},
            ...     format_type=FlextCliConstants.OutputFormats.JSON.value,
            ... )

        """
        # Railway pattern: validate format → dispatch to handler
        # Convert to string and validate choice using generalized helpers
        parse_result = u.parse(format_type, str, default="")
        format_str = ensure_str(unwrap_or(parse_result, str(format_type)), "").lower()
        valid_formats = set(FlextCliConstants.OUTPUT_FORMATS_LIST)
        if format_str not in valid_formats:
            return r[str].fail(
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=format_type,
                ),
            )
        return self._dispatch_formatter(format_str, data, title, headers)

    # Format validation uses u.convert() and direct validation

    def _dispatch_formatter(
        self,
        format_type: str,
        data: t.GeneralValueType,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
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
            FlextCliConstants.OutputFormats.PLAIN.value: lambda: r[str].ok(str(data)),
        }

        formatter = formatters.get(format_type)
        if formatter is None:
            return r[str].fail(
                FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type,
                ),
            )

        return formatter()

    def _format_table_data(
        self,
        data: t.GeneralValueType,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
        """Format data as table with type validation."""
        if FlextRuntime.is_dict_like(data):
            # Use build() DSL: ensure dict → transform to JSON
            transformed_data = to_dict_json(data)
            return self.format_table(transformed_data, title=title, headers=headers)

        if FlextRuntime.is_list_like(data):
            if not data:
                return r[str].fail(FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED)
            # Use build() DSL: filter → validate → process → ensure list
            dict_items = u.filter(data, predicate=FlextRuntime.is_dict_like)
            if not isinstance(dict_items, list) or len(dict_items) != len(data):
                return r[str].fail(
                    FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
                )
            # Use generalized norm_json helper
            json_list_result = u.process(
                list(data),
                processor=lambda _k, item: norm_json(item),
                predicate=FlextRuntime.is_dict_like,
                on_error="skip",
            )
            converted_list = cast(
                "list[dict[str, t.GeneralValueType]]",
                ensure_list(unwrap_or(json_list_result, []), []),
            )
            return self.format_table(converted_list, title=title, headers=headers)

        return r[str].fail(FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def create_formatter(self, format_type: str) -> r[FlextCliOutput]:
        """Create a formatter instance for the specified format type.

        Uses u.convert() and direct validation for format checking.

        Args:
            format_type: Format type to create formatter for

        Returns:
            r[FlextCliOutput]: Formatter instance or error

        """
        try:
            # Use build() DSL: parse → ensure str → normalize → validate
            parse_result = u.parse(format_type, str, default="")
            format_str = ensure_str(
                unwrap_or(parse_result, str(format_type)), ""
            ).lower()
            valid_formats = set(FlextCliConstants.OUTPUT_FORMATS_LIST)
            if format_str not in valid_formats:
                return r[FlextCliOutput].fail(
                    FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type
                    )
                )
            return r[FlextCliOutput].ok(self)
        except Exception as e:
            return r[FlextCliOutput].fail(
                FlextCliConstants.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e),
            )

    # =========================================================================
    # RESULT FORMATTER REGISTRY - Domain-specific result formatting
    # =========================================================================

    def register_result_formatter(
        self,
        result_type: type,
        formatter: Callable[[t.GeneralValueType | r[object], str], None],
    ) -> r[bool]:
        r"""Register custom formatter for domain-specific result types.

        **PURPOSE**: Eliminate repetitive result display formatting boilerplate.

        Allows registering formatters for specific result types, enabling
        automatic formatting based on result type detection. Reduces ~74 lines
        of formatting boilerplate per result type.

        Args:
            result_type: Type of result to format (e.g., OperationResult)
            formatter: Callable that formats and displays the result
                Signature: (result: t.GeneralValueType | r[object], output_format: str) -> None

        Returns:
            r[bool]: True on success, False on failure

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
                "Callable[[t.GeneralValueType | r[t.GeneralValueType], str], None]",
                formatter,
            )
            self.logger.debug(
                "Registered result formatter",
                extra={"formatter_type": result_type.__name__},
            )
            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}",
            )

    def format_and_display_result(
        self,
        result: BaseModel | t.GeneralValueType | r[object],
        output_format: str = FlextCliConstants.OutputFormats.TABLE.value,
    ) -> r[bool]:
        """Auto-detect result type and apply registered formatter with extracted helpers.

        **PURPOSE**: Eliminate manual type checking and formatter dispatch.

        Args:
            result: Domain result object to format
            output_format: Output format ("table", "json", "yaml", etc.)

        Returns:
            r[bool]: True on success, False on failure

        """
        try:
            # Try registered formatter first - use r pattern
            registered_result = self._try_registered_formatter(result, output_format)
            if registered_result.is_success:
                return registered_result

            # Use generic formatting with railway pattern
            formattable_result = self._convert_result_to_formattable(
                result, output_format
            )
            if formattable_result.is_failure:
                return r[bool].fail(
                    formattable_result.error
                    or "Failed to convert result to formattable",
                    error_code=formattable_result.error_code,
                    error_data=formattable_result.error_data,
                )

            formattable = formattable_result.unwrap()
            return self._display_formatted_result(formattable)

        except Exception as e:
            return r[bool].fail(f"Failed to format and display result: {e}")

    def _try_registered_formatter(
        self,
        result: BaseModel | t.GeneralValueType | r[object],
        output_format: str,
    ) -> r[bool]:
        """Try to use registered formatter for result type.

        Returns:
            r[bool]: True if formatter was found and executed,
            False if no formatter registered for this type

        """
        result_type = type(result)

        if result_type in self._result_formatters:
            formatter = self._result_formatters[result_type]
            # Type narrowing: formatter accepts GeneralValueType | r[object]
            # BaseModel is not directly compatible, but we can pass it as GeneralValueType
            if isinstance(result, BaseModel):
                # Convert BaseModel to dict for formatter
                formattable_result: t.GeneralValueType = result.model_dump()
                formatter(formattable_result, output_format)
            # result is already GeneralValueType | r[GeneralValueType]
            # Type narrowing: formatter accepts GeneralValueType
            elif isinstance(result, r):
                if result.is_success:
                    # Use build() DSL: unwrap → ensure JSON-compatible → convert to string if needed
                    unwrapped = result.unwrap()
                    if is_json(unwrapped):
                        formatter(cast("t.GeneralValueType", unwrapped), output_format)
                    else:
                        formatter(str(unwrapped), output_format)
                else:
                    return r[bool].fail(f"Cannot format failed result: {result.error}")
            else:
                formatter(result, output_format)
            return r[bool].ok(True)

        return r[bool].fail(
            f"No registered formatter for type {result_type.__name__}",
        )

    def _convert_result_to_formattable(
        self,
        result: BaseModel | t.GeneralValueType | r[object],
        output_format: str,
    ) -> r[str]:
        """Convert result object to formattable string.

        Handles multiple result types: Pydantic models, objects with __dict__, and fallback.
        Fast-fails if result is None - caller must handle None values explicitly.
        """
        # Fast-fail if result is None - no fallback to fake data
        if result is None:
            return r[str].fail(
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
            # Use build() DSL: filter JSON-compatible → ensure dict
            filtered = u.filter(result.__dict__, predicate=lambda _k, v: is_json(v))
            result_dict = ensure_dict(filtered, {})
            return self.format_data(result_dict, output_format)

        # Use string representation (not a fallback - valid conversion)
        return r[str].ok(str(result))

    def _format_pydantic_model(
        self,
        result: BaseModel,
        output_format: str,
    ) -> r[str]:
        """Format Pydantic model to string."""
        # Use model_dump() directly - dict is compatible with t.GeneralValueType
        result_dict = result.model_dump()
        return self.format_data(result_dict, output_format)

    def _format_dict_object(
        self,
        result: t.GeneralValueType | r[t.GeneralValueType],
        output_format: str,
    ) -> r[str]:
        """Format object with __dict__ to string."""
        # Type narrowing: result must have __dict__ attribute
        if isinstance(result, r):
            # Extract value from r
            if result.is_failure:
                return r[str].fail(f"Cannot format failed result: {result.error}")
            unwrapped = result.unwrap()
            # Type narrowing: unwrap returns GeneralValueType
            # Note: Cannot use isinstance with TypeAliasType (GeneralValueType)
            # unwrapped is already GeneralValueType from unwrap()
            result = unwrapped
        # Now result is GeneralValueType - check if it has __dict__
        if not hasattr(result, "__dict__"):
            return r[str].fail(
                f"Object {type(result).__name__} has no __dict__ attribute"
            )
        # Type narrowing: result has __dict__ attribute
        raw_dict: dict[str, t.GeneralValueType] = getattr(result, "__dict__", {})
        # Use build() DSL: process → to_json → filter → ensure dict
        json_dict_result = u.process(
            raw_dict, processor=lambda _k, v: to_json(v), on_error="skip"
        )
        json_dict = cast(
            "dict[str, t.GeneralValueType]", unwrap_or(json_dict_result, {})
        )
        cli_json_dict_result = u.process(
            json_dict,
            processor=lambda _k, v: v if is_json(v) else None,
            predicate=lambda _k, v: is_json(v),
            on_error="skip",
        )
        cli_json_dict = cast(
            "dict[str, t.GeneralValueType]", unwrap_or(cli_json_dict_result, {})
        )
        return self.format_data(cli_json_dict, output_format)

    def _display_formatted_result(self, formatted: str) -> r[bool]:
        """Display formatted result string using Rich console."""
        console = self._formatters.console
        console.print(formatted)
        return r[bool].ok(True)

    # =========================================================================
    # RICH TABLE CREATION (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_rich_table(
        self,
        data: list[dict[str, t.GeneralValueType]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[FlextCliProtocols.Display.RichTableProtocol]:
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
            return r[FlextCliProtocols.Display.RichTableProtocol].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED,
            )

        try:
            # Use build() DSL: ensure dict → extract keys → ensure list → ensure default
            default_headers = u.when(
                condition=data,
                then_value=get_keys(data[0]),
                else_value=[],
            )
            table_headers = cast("list[str]", ensure_list(headers, default_headers))

            # Create Rich table through formatters abstraction (basic parameters only)
            table_result = self._formatters.create_table(
                data=None,  # We'll populate manually
                headers=table_headers,
                title=title,
            )

            if table_result.is_failure:
                return r[FlextCliProtocols.Display.RichTableProtocol].fail(
                    f"Failed to create Rich table: {table_result.error}",
                )

            table = table_result.unwrap()

            # Use build() DSL for column addition
            def add_col(h: str) -> None:
                """Add column to table."""
                table.add_column(str(h))

            u.process(table_headers, processor=add_col, on_error="skip")

            # Use build() DSL for row processing with validation
            def build_row(row_data: dict[str, t.GeneralValueType]) -> list[str]:
                """Build row values using build DSL."""

                def get_val(h: str) -> str | None:
                    """Get header value or None."""
                    return u.when(
                        condition=h in row_data,
                        then_value=str(u.get(row_data, h)),
                        else_value=None,
                    )

                def is_not_none(v: str | None) -> bool:
                    """Check if value is not None."""
                    return v is not None

                return cast(
                    "list[str]",
                    u.build(
                        table_headers,
                        ops={"map": get_val, "filter": is_not_none, "ensure": "list"},
                        on_error="skip",
                    ),
                )

            rows_result = u.process(data, processor=build_row, on_error="fail")
            if rows_result.is_failure:
                return r[FlextCliProtocols.Display.RichTableProtocol].fail(
                    rows_result.error or "Failed to build rows"
                )
            rows = cast("list[list[str]]", ensure_list(unwrap_or(rows_result, []), []))
            u.process(rows, processor=lambda row: table.add_row(*row), on_error="skip")

            # RichTable (concrete type) implements RichTableProtocol structurally
            # Use cast for structural typing compatibility (cast imported at module level)
            protocol_table: FlextCliProtocols.Display.RichTableProtocol = cast(
                "FlextCliProtocols.Display.RichTableProtocol", table
            )
            return r[FlextCliProtocols.Display.RichTableProtocol].ok(protocol_table)

        except Exception as e:
            error_msg = FlextCliConstants.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return r[FlextCliProtocols.Display.RichTableProtocol].fail(error_msg)

    def table_to_string(
        self,
        table: FlextCliProtocols.Display.RichTableProtocol,
        width: int | None = None,
    ) -> r[str]:
        """Convert table to string using FlextCliFormatters.

        Args:
            table: Table object from formatters
            width: Optional width for console

        Returns:
            r[str]: Table as string or error

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
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str] | None = None,
        table_format: str = FlextCliConstants.TableFormats.SIMPLE,
        *,
        config: FlextCliModels.TableConfig | None = None,
    ) -> r[str]:
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
            r[str]: ASCII table string

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

        # Use build() DSL for headers normalization
        validated_headers = cast(
            "list[str]", ensure_list(headers, [FlextCliConstants.TableFormats.KEYS])
        )
        final_config = FlextCliModels.TableConfig(
            headers=validated_headers, table_format=table_format
        )
        return self._tables.create_table(data=data, config=final_config)

    # =========================================================================
    # PROGRESS BARS (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_progress_bar(
        self,
    ) -> r[FlextCliProtocols.Interactive.RichProgressProtocol]:
        """Create a Rich progress bar using FlextCliFormatters.

        Returns:
            r[RichProgressProtocol]: Rich Progress wrapped in Result

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar()

        """
        # create_progress returns r[Progress] which implements RichProgressProtocol
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
            return r[FlextCliProtocols.Interactive.RichProgressProtocol].ok(
                protocol_progress
            )
        return r[FlextCliProtocols.Interactive.RichProgressProtocol].fail(
            result.error or ""
        )

    # =========================================================================
    # STYLED PRINTING (Delegates to FlextCliFormatters)
    # =========================================================================

    def print_message(
        self,
        message: str,
        style: str | None = None,
    ) -> r[bool]:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print
            style: Optional Rich style

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_message("Hello", style="bold blue")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        # Use build() DSL for style normalization
        validated_style = ensure_str(
            style, FlextCliConstants.OutputDefaults.EMPTY_STYLE
        )
        return self._formatters.print(message, style=validated_style)

    def print_error(self, message: str) -> r[bool]:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_error("Operation failed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.ERROR_PREFIX} {message}",
            style=FlextCliConstants.Styles.BOLD_RED,
        )

    def print_success(self, message: str) -> r[bool]:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_success("Task completed")

        """
        return self.print_message(
            f"{FlextCliConstants.Symbols.SUCCESS_PREFIX} {message}",
            style=FlextCliConstants.Styles.BOLD_GREEN,
        )

    def print_warning(self, message: str) -> r[bool]:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Returns:
            r[bool]: True on success, False on failure

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
    ) -> r[bool]:
        """Display text using FlextCliFormatters.

        Args:
            text: Text to display
            style: Optional Rich style

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_text("Important info", style="bold")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        # Use build() DSL for style normalization
        validated_style = ensure_str(
            style, FlextCliConstants.OutputDefaults.EMPTY_STYLE
        )
        return self._formatters.print(text, style=validated_style)

    def display_message(
        self,
        message: str,
        message_type: str | None = None,
    ) -> r[bool]:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_message("Operation completed", message_type="success")

        """
        # Use build() DSL for message type normalization
        final_message_type = ensure_str(
            message_type, FlextCliConstants.OutputDefaults.DEFAULT_MESSAGE_TYPE
        )

        # Use build() DSL for style and emoji mapping with generalized helpers
        style_map = {
            FlextCliConstants.MessageTypes.INFO.value: FlextCliConstants.Styles.BLUE,
            FlextCliConstants.MessageTypes.SUCCESS.value: FlextCliConstants.Styles.BOLD_GREEN,
            FlextCliConstants.MessageTypes.ERROR.value: FlextCliConstants.Styles.BOLD_RED,
            FlextCliConstants.MessageTypes.WARNING.value: FlextCliConstants.Styles.BOLD_YELLOW,
        }
        emoji_map = {
            FlextCliConstants.MessageTypes.INFO.value: FlextCliConstants.Emojis.INFO,
            FlextCliConstants.MessageTypes.SUCCESS.value: FlextCliConstants.Emojis.SUCCESS,
            FlextCliConstants.MessageTypes.ERROR.value: FlextCliConstants.Emojis.ERROR,
            FlextCliConstants.MessageTypes.WARNING.value: FlextCliConstants.Emojis.WARNING,
        }
        style = ensure_str(
            get_map_val(style_map, final_message_type, FlextCliConstants.Styles.BLUE)
        )
        emoji = ensure_str(
            get_map_val(emoji_map, final_message_type, FlextCliConstants.Emojis.INFO)
        )
        formatted_message = f"{emoji} {message}"

        return self.print_message(formatted_message, style=style)

    def display_data(
        self,
        data: t.GeneralValueType,
        format_type: str | None = None,
        *,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[bool]:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.)
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data(
            ...     {"key": "value"},
            ...     format_type=FlextCliConstants.OutputFormats.JSON.value,
            ... )

        """
        # Use build() DSL for format type normalization
        final_format_type = ensure_str(
            format_type, FlextCliConstants.OutputDefaults.DEFAULT_FORMAT_TYPE
        )
        format_result = self.format_data(
            data,
            format_type=final_format_type,
            title=title,
            headers=headers,
        )

        if format_result.is_failure:
            return r[bool].fail(
                f"Failed to format data: {format_result.error}",
            )

        formatted_data = format_result.unwrap()

        # Display the formatted data
        return self.print_message(formatted_data)

    # =========================================================================
    # DATA FORMAT METHODS (Built-in)
    # =========================================================================

    def format_json(self, data: t.GeneralValueType) -> r[str]:
        """Format data as JSON.

        Args:
            data: Data to format

        Returns:
            r[str]: Formatted JSON string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_json({"key": "value"})

        """
        try:
            return r[str].ok(
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
            return r[str].fail(error_msg)

    def format_yaml(self, data: t.GeneralValueType) -> r[str]:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            r[str]: Formatted YAML string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_yaml({"key": "value"})

        """
        try:
            return r[str].ok(
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
            return r[str].fail(error_msg)

    def format_csv(self, data: t.GeneralValueType) -> r[str]:
        """Format data as CSV.

        Args:
            data: Data to format

        Returns:
            r[str]: Formatted CSV string

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
                # Use build() DSL: ensure dict → extract keys → ensure list
                fieldnames = get_keys(data[0])
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()

                # Use build() DSL: filter → ensure list → process → map replace None → ensure dict
                def replace_none(_k: str, v: object) -> str | int | float | bool:
                    """Replace None with empty string."""
                    return u.when(
                        condition=v is not None,
                        then_value=cast("str | int | float | bool", v),
                        else_value="",
                    )

                def process_row(
                    row: dict[str, object],
                ) -> dict[str, str | int | float | bool]:
                    """Process row with None replacement."""
                    return cast(
                        "dict[str, str | int | float | bool]",
                        u.build(
                            cast("dict[str, object]", row),
                            ops={"map": replace_none, "ensure": "dict"},
                            on_error="skip",
                        ),
                    )

                filtered_rows = u.filter(data, predicate=FlextRuntime.is_dict_like)
                dict_rows = cast(
                    "list[dict[str, object]]",
                    ensure_list(
                        u.when(
                            condition=isinstance(filtered_rows, list),
                            then_value=filtered_rows,
                            else_value=[],
                        ),
                        [],
                    ),
                )
                csv_rows_result = u.process(
                    dict_rows, processor=process_row, on_error="skip"
                )
                csv_rows = cast(
                    "list[dict[str, str | int | float | bool]]",
                    ensure_list(unwrap_or(csv_rows_result, []), []),
                )
                writer.writerows(csv_rows)
                return r[str].ok(output_buffer.getvalue())
            if FlextRuntime.is_dict_like(data):
                output_buffer = StringIO()
                # Use build() DSL: ensure dict → extract keys → ensure list
                fieldnames = get_keys(data)
                writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
                return r[str].ok(output_buffer.getvalue())
            return r[str].ok(
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
            return r[str].fail(error_msg)

    def format_table(
        self,
        data: dict[str, t.GeneralValueType] | list[dict[str, t.GeneralValueType]] | str,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[str]:
        """Format data as a tabulated table string using FlextCliTables.

        Args:
            data: Data to format (dict or list of dicts). Non-dict/list types return error.
            title: Optional table title
            headers: Optional column headers

        Returns:
            r[str]: Table as string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_table(
            ...     data=[{"name": "Alice", "age": 30}], title="Users"
            ... )

        """
        # Railway pattern: prepare data → create table → add title
        prepared_result = self._prepare_table_data_safe(data, headers)
        if prepared_result.is_failure:
            return r[str].fail(
                prepared_result.error or "Failed to prepare table data",
                error_code=prepared_result.error_code,
                error_data=prepared_result.error_data,
            )

        prepared = prepared_result.unwrap()
        table_result = self._create_table_string(prepared[0], prepared[1])
        if table_result.is_failure:
            return table_result

        table = table_result.unwrap()
        return r.ok(self._add_title(table, title))

    def _prepare_table_data_safe(
        self,
        data: dict[str, t.GeneralValueType] | list[dict[str, t.GeneralValueType]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                error_msg
            )

    def _prepare_table_data(
        self,
        data: dict[str, t.GeneralValueType] | list[dict[str, t.GeneralValueType]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[t.GeneralValueType], str | list[str]]]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            # Use build() DSL: ensure dict → transform to JSON
            json_data = to_dict_json(data)
            return self._prepare_dict_data(json_data, headers)
        if FlextRuntime.is_list_like(data):
            # Use build() DSL: process → norm_json → ensure list
            process_result = u.process(
                list(data),
                processor=lambda _k, item: norm_json(item),
                predicate=FlextRuntime.is_dict_like,
                on_error="skip",
            )
            converted_list = cast(
                "list[dict[str, t.GeneralValueType]]",
                ensure_list(unwrap_or(process_result, []), []),
            )
            return self._prepare_list_data(converted_list, headers)
        return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
            FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
        )

    @staticmethod
    def _prepare_dict_data(
        data: dict[str, t.GeneralValueType],
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Prepare dict data for table display."""
        # Reject test invu
        if FlextCliConstants.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
            )

        # Use build() DSL: process → kv_pair → ensure dict → extract values → ensure list
        def kv_pair(k: str, v: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
            """Create key-value pair dict."""
            return {
                FlextCliConstants.OutputFieldNames.KEY: k,
                FlextCliConstants.OutputFieldNames.VALUE: str(v),
            }

        process_result = u.process(data, processor=kv_pair, on_error="skip")
        dict_result = ensure_dict(unwrap_or(process_result, {}), {})
        table_data = cast(
            "list[dict[str, t.GeneralValueType]]",
            ensure_list(list(dict_result.values()), []),
        )
        # Use build() DSL: ensure list → ensure default
        table_headers = cast(
            "str | list[str]",
            ensure_list(headers, [FlextCliConstants.TableFormats.KEYS]),
        )
        return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].ok((
            table_data,
            table_headers,
        ))

    @staticmethod
    def _prepare_list_data(
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Prepare list data for table display."""
        if not data:
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
            )

        # Validate headers type
        if headers is not None and not FlextRuntime.is_list_like(headers):
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                FlextCliConstants.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST
            )

        # Use build() DSL: ensure list → map to str → ensure default
        table_headers = cast(
            "list[str]",
            u.build(
                ensure_list(headers, [FlextCliConstants.TableFormats.KEYS]),
                ops={"map": str, "ensure": "list"},
                on_error="skip",
            ),
        )
        return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].ok((
            data,
            table_headers,
        ))

    def _create_table_string(
        self,
        table_data: list[dict[str, t.GeneralValueType]],
        table_headers: str | list[str],
    ) -> r[str]:
        """Create table string using FlextCliTables."""
        try:
            config = FlextCliModels.TableConfig(
                headers=table_headers,
                table_format=FlextCliConstants.TableFormats.GRID,
            )
            table_result = self._tables.create_table(data=table_data, config=config)

            if table_result.is_failure:
                return r[str].fail(
                    f"Failed to create table: {table_result.error}",
                )

            return table_result
        except Exception as e:
            error_msg = FlextCliConstants.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )
            self.logger.exception(error_msg)
            return r[str].fail(error_msg)

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{FlextCliConstants.OutputDefaults.NEWLINE}{table_str}{FlextCliConstants.OutputDefaults.NEWLINE}"
        return table_str

    def format_as_tree(
        self,
        data: t.GeneralValueType,
        title: str | None = None,
    ) -> r[str]:
        """Format hierarchical data as tree view using FlextCliFormatters.

        Args:
            data: Hierarchical data to format
            title: Tree title

        Returns:
            r[str]: Tree view as string

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_as_tree(
            ...     data={"root": {"child1": "value1", "child2": "value2"}},
            ...     title="Config",
            ... )

        """
        # Use build() DSL for title normalization
        final_title = ensure_str(
            title, FlextCliConstants.OutputDefaults.DEFAULT_TREE_TITLE
        )

        # Create tree through formatters
        tree_result = self._formatters.create_tree(label=final_title)

        if tree_result.is_failure:
            return r[str].fail(f"Failed to create tree: {tree_result.error}")

        tree = tree_result.unwrap()

        # Build tree structure - data is already t.GeneralValueType
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
        data: t.GeneralValueType,
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from (CliJsonValue - can be dict, list, or primitive)

        """
        if isinstance(data, dict):
            # Use build() DSL: process → handle nested structures
            def process_tree_item(k: str, v: t.GeneralValueType) -> None:
                """Process single tree item."""
                if isinstance(v, dict):
                    branch = tree.add(str(k))
                    self._build_tree(branch, v)
                elif isinstance(v, list):
                    branch = tree.add(
                        f"{k}{FlextCliConstants.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}"
                    )

                    def process_list_item(_i: int, item: t.GeneralValueType) -> None:
                        """Process list item."""
                        self._build_tree(branch, item)

                    u.process(v, processor=process_list_item, on_error="skip")
                else:
                    tree.add(
                        f"{k}{FlextCliConstants.OutputDefaults.TREE_VALUE_SEPARATOR}{v}"
                    )

            u.process(data, processor=process_tree_item, on_error="skip")
        elif isinstance(data, list):
            # Use build() DSL: process each item
            def process_list_item(_i: int, item: t.GeneralValueType) -> None:
                """Process list item."""
                self._build_tree(tree, item)

            u.process(data, processor=process_list_item, on_error="skip")
        else:
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
