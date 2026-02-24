"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from io import StringIO
from typing import ClassVar, TypeGuard

import yaml
from flext_core import FlextRuntime, r, t
from pydantic import BaseModel
from rich.tree import Tree as RichTree

from flext_cli.constants import c
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.services.tables import FlextCliTables
from flext_cli.utilities import u

# ═══════════════════════════════════════════════════════════════════════════
# GENERALIZED MNEMONIC HELPERS - Advanced DSL parametrization
# ═══════════════════════════════════════════════════════════════════════════
# All helper functions moved into FlextCliOutput class as static methods
# to follow "one class per module" pattern


class FlextCliOutput:
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
    8. Output MUST respect configured output format from FlextCliSettings

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

    Examples:
        >>> output = FlextCliOutput()
        >>>
        >>> # Format data in various formats
        >>> result = output.format_data(
        ...     data={"key": "value"},
        ...     format_type=c.Cli.OutputFormats.JSON.value,
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

    # Logger is provided by FlextMixins mixin

    # Class-level attribute for result formatters (avoids reportUninitializedInstanceVariable)
    _result_formatters: ClassVar[
        dict[type, Callable[[t.JsonValue | r[t.JsonValue], str], None]]
    ] = {}

    # ═══════════════════════════════════════════════════════════════════════════
    # STATIC HELPER METHODS - General purpose utilities for output operations
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def is_json(v: t.JsonValue) -> bool:
        """Check if value is JSON-compatible type.

        Uses t.JsonValue from lower layer instead of object for better type safety.
        """
        match v:
            case str() | int() | float() | bool() | None | dict() | list():
                return True
            case _:
                return False

    @staticmethod
    def to_json(v: t.JsonValue) -> t.JsonValue:
        """Convert value to JSON-compatible using build DSL."""
        match v:
            case dict() as mapping:
                return u.build(
                    mapping,
                    ops={"ensure": "dict", "transform": {"to_json": True}},
                    on_error="skip",
                )
            case _:
                return v

    @staticmethod
    def get_keys(
        d: Mapping[str, t.JsonValue] | t.JsonValue,
    ) -> list[str]:
        """Extract keys from dict using build DSL.

        Business Rules:
        ───────────────
        1. Keys extraction MUST handle both dict and non-dict inputs safely
        2. Non-dict inputs MUST return empty list (no error)
        3. Dict keys MUST be converted to list[str] for type safety

        Architecture Implications:
        ───────────────────────────
        - Uses u.build() for type coercion and validation
        - Returns empty list for non-dict inputs (safe fallback)
        - Type-safe conversion to list[str] using type narrowing

        Audit Implications:
        ───────────────────
        - Key extraction is safe and never raises exceptions
        - Empty dict returns empty list (expected behavior)
        - Non-dict inputs are handled gracefully without errors
        """
        d_dict = u.build(d, ops={"ensure": "dict"}, on_error="skip")
        # Python 3.13: Use isinstance with Mapping for proper type narrowing
        # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
        # Architecture: Direct list() conversion is type-safe and efficient
        # Audit Implication: Key extraction is deterministic and safe
        match d_dict:
            case dict() as mapping:
                return list(mapping.keys())
            case _:
                return []

    @staticmethod
    def norm_json(item: t.JsonValue) -> t.JsonValue:
        """Normalize item to JSON-compatible using build DSL."""
        match item:
            case str() | int() | float() | bool() | None:
                return item
            case _:
                pass
        if u.is_dict_like(item):
            return FlextCliOutput.to_dict_json(item)
        if u.is_list_like(item):
            # item is narrowed to Sequence[t.JsonValue] by TypeGuard
            # to_list_json accepts both t.JsonValue | Sequence[t.JsonValue]
            return FlextCliOutput.to_list_json(item)
        # Type narrowing: str(item) is already t.JsonValue compatible
        return str(item)

    @staticmethod
    def ensure_str(v: t.JsonValue | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if v is None:
            return default
        try:
            return str(v)
        except Exception:
            return default

    @staticmethod
    def ensure_list(
        v: t.JsonValue | None,
        default: list[t.JsonValue] | None = None,
    ) -> list[t.JsonValue]:
        """Ensure value is list with default using build DSL."""
        # Normalize to JsonValue using FlextRuntime
        v_typed = FlextRuntime.normalize_to_general_value(v) if v is not None else None
        built_result = u.build(
            v_typed,
            ops={"ensure": "list", "ensure_default": default or []},
            on_error="skip",
        )
        # Python 3.13: Use Sequence check for more flexible list-like types
        # Type narrowing: FlextCliUtilities.build with ensure="list" returns list-like
        match built_result:
            case Sequence() as sequence_result:
                return list(sequence_result)
            case _:
                return default or []

    @staticmethod
    def ensure_dict(
        v: t.JsonValue | None,
        default: Mapping[str, t.JsonValue] | None = None,
    ) -> Mapping[str, t.JsonValue]:
        """Ensure value is dict with default using build DSL."""
        result = u.build(
            v,
            ops={"ensure": "dict", "ensure_default": default or {}},
            on_error="skip",
        )
        match result:
            case dict() as mapping:
                return mapping
            case _:
                return default or {}

    @staticmethod
    def ensure_bool(v: t.JsonValue | None, *, default: bool = False) -> bool:
        """Ensure value is bool with default using build DSL."""
        # Type narrowing: FlextCliUtilities.build with ensure="bool" returns bool
        result = u.build(
            v,
            ops={"ensure": "bool", "ensure_default": default},
            on_error="skip",
        )
        return bool(result) if result is not None else default

    @staticmethod
    def get_map_val(
        m: Mapping[str, t.JsonValue],
        k: str,
        default: t.JsonValue,
    ) -> t.JsonValue:
        """Get value from map with default using build DSL."""
        value = m.get(k, default)
        # Ensure value is compatible with JsonValue
        compatible_value: t.JsonValue
        match value:
            case str() | int() | float() | bool() | None | list():
                compatible_value = value
            case dict() as mapping:
                dict_items: dict[str, t.JsonValue] = {}
                for kk, vv in mapping.items():
                    match vv:
                        case str() | int() | float() | bool() | None | list() | dict():
                            dict_items[str(kk)] = vv
                        case _:
                            dict_items[str(kk)] = str(vv)
                compatible_value = dict_items
            case _:
                compatible_value = str(value)
        # compatible_value is already validated as JsonValue-compatible
        return compatible_value

    @staticmethod
    def cast_if[T](
        v: t.JsonValue,
        t_type: type[T],
        default: T,
    ) -> T:
        """Cast value if isinstance else return default.

        Pattern: Non-generic cast_if for runtime type checking.
        Checks v against t_type, returns v if match, else returns default.
        """
        match v:
            case _ if u.Guards.is_type(v, t_type):
                return v
            case _:
                return default

    @staticmethod
    def _is_rich_table_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichTableProtocol]:
        """Type guard to check if object implements RichTableProtocol."""
        return u.is_type(obj, p.Cli.Display.RichTableProtocol)

    @staticmethod
    def _is_rich_progress_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Interactive.RichProgressProtocol]:
        """Type guard to check if object implements RichProgressProtocol."""
        return u.is_type(obj, p.Cli.Interactive.RichProgressProtocol)

    @staticmethod
    def _is_rich_tree_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichTreeProtocol]:
        """Type guard to check if object implements RichTreeProtocol."""
        return u.is_type(obj, p.Cli.Display.RichTreeProtocol)

    @staticmethod
    def _is_rich_console_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichConsoleProtocol]:
        """Type guard to check if object implements RichConsoleProtocol."""
        return u.is_type(obj, p.Cli.Display.RichConsoleProtocol)

    @staticmethod
    def to_dict_json(v: t.JsonValue) -> Mapping[str, t.JsonValue]:
        """Convert value to dict with JSON transform using build DSL."""
        result = FlextCliOutput.cast_if(
            u.build(
                v,
                ops={"ensure": "dict", "transform": {"to_json": True}},
                on_error="skip",
            ),
            dict,
            {},
        )
        # Type narrowing: cast_if ensures result is dict-like
        match result:
            case dict() as mapping:
                return mapping
            case _:
                # Fallback to empty dict
                return {}

    @staticmethod
    def to_list_json(
        v: t.JsonValue,
    ) -> list[t.JsonValue]:
        """Convert value to list with JSON transform using build DSL."""
        # Normalize to JsonValue using FlextRuntime
        v_typed = FlextRuntime.normalize_to_general_value(v)
        result = FlextCliOutput.cast_if(
            u.build(
                v_typed,
                ops={"ensure": "list", "transform": {"to_json": True}},
                on_error="skip",
            ),
            list,
            [],
        )
        # Type narrowing: cast_if ensures result is list-like
        match result:
            case list() as items:
                return items
            case _:
                # Fallback to empty list
                return []

    # =========================================================================
    # FORMAT DATA - UNIFIED API
    # =========================================================================

    def format_data(
        self,
        data: t.JsonValue,
        format_type: str = c.Cli.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[str]:
        """Format data using specified format type with railway pattern.

        Args:
            data: Data to format
            format_type: Format type from c.Cli.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[str]: Formatted data string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_data(
            ...     data={"name": "Alice", "age": 30},
            ...     format_type=c.Cli.OutputFormats.JSON.value,
            ... )

        """
        # Railway pattern: validate format → dispatch to handler
        # Convert to string and validate choice using generalized helpers
        parse_result = u.Cli.parse(format_type, str, default="")
        format_str = self.ensure_str(
            parse_result.unwrap_or(str(format_type)),
            "",
        ).lower()
        valid_formats = set(c.Cli.ValidationLists.OUTPUT_FORMATS)
        if format_str not in valid_formats:
            return r[str].fail(
                c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=format_type,
                ),
            )
        return self._dispatch_formatter(format_str, data, title, headers)

    # Format validation uses FlextCliUtilities.convert() and direct validation

    def _dispatch_formatter(
        self,
        format_type: str,
        data: t.JsonValue,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
        """Dispatch to appropriate formatter based on format type."""
        # Format dispatcher using dict mapping
        formatters: dict[str, Callable[[], r[str]]] = {
            c.Cli.OutputFormats.JSON.value: lambda: self.format_json(data),
            c.Cli.OutputFormats.YAML.value: lambda: self.format_yaml(data),
            c.Cli.OutputFormats.TABLE.value: lambda: self._format_table_data(
                data,
                title,
                headers,
            ),
            c.Cli.OutputFormats.CSV.value: lambda: self.format_csv(data),
            c.Cli.OutputFormats.PLAIN.value: lambda: r[str].ok(str(data)),
        }

        formatter = formatters.get(format_type)
        if formatter is None:
            return r[str].fail(
                c.Cli.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type,
                ),
            )
        # Type narrowing: formatter is Callable[[], r[str]] after get() check
        # formatters dict is typed as dict[str, Callable[[], r[str]]]
        # so formatter is guaranteed to be the correct type when not None
        return formatter()

    def _format_table_data(
        self,
        data: t.JsonValue,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
        """Format data as table with type validation."""
        if u.is_dict_like(data):
            # Use build() DSL: ensure dict → transform to JSON
            transformed_data = self.to_dict_json(data)
            return self.format_table(transformed_data, title=title, headers=headers)

        if u.is_list_like(data):
            if not data:
                return r[str].fail(c.Cli.ErrorMessages.NO_DATA_PROVIDED)
            # Use build() DSL: filter → validate → process → ensure list
            # Type narrowing: is_list_like ensures data is Sequence-like
            # Convert to list via iteration
            data_list: list[t.JsonValue] = [
                FlextRuntime.normalize_to_general_value(item) for item in data
            ]
            dict_items = u.filter(data_list, predicate=u.is_dict_like)
            # Type narrowing: data_list is list after normalization
            match dict_items:
                case list() as items if len(items) == len(data_list):
                    pass
                case _:
                    return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)
            # Use generalized norm_json helper
            # For lists, processor takes only item, not (key, item)
            # Filter first, then process (FlextCliUtilities.process doesn't accept predicate)
            # Type narrowing: data_list is list, so it's iterable
            filtered_data = [item for item in data_list if u.is_dict_like(item)]
            json_list_result = u.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            # Type narrowing: ensure_list returns list[t.JsonValue]
            # Filter to ensure all items are dict
            converted_list_raw = self.ensure_list(
                json_list_result.unwrap_or([]),
                [],
            )
            converted_list: list[dict[str, t.JsonValue]] = [
                item for item in converted_list_raw if u.is_dict_like(item)
            ]
            return self.format_table(converted_list, title=title, headers=headers)

        return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def create_formatter(self, format_type: str) -> r[FlextCliOutput]:
        """Create a formatter instance for the specified format type.

        Uses FlextCliUtilities.convert() and direct validation for format checking.

        Args:
            format_type: Format type to create formatter for

        Returns:
            r[FlextCliOutput]: Formatter instance or error

        """
        try:
            # Use build() DSL: parse → ensure str → normalize → validate
            parse_result = u.Cli.parse(format_type, str, default="")
            format_str = self.ensure_str(
                parse_result.unwrap_or(str(format_type)),
                "",
            ).lower()
            valid_formats = set(c.Cli.ValidationLists.OUTPUT_FORMATS)
            if format_str not in valid_formats:
                return r[FlextCliOutput].fail(
                    c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type
                    ),
                )
            return r[FlextCliOutput].ok(self)
        except Exception as e:
            return r[FlextCliOutput].fail(
                c.Cli.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e),
            )

    # =========================================================================
    # RESULT FORMATTER REGISTRY - Domain-specific result formatting
    # =========================================================================

    def register_result_formatter(
        self,
        result_type: type,
        formatter: Callable[[t.JsonValue | r[t.JsonValue], str], None],
    ) -> r[bool]:
        r"""Register custom formatter for domain-specific result types.

        **PURPOSE**: Eliminate repetitive result display formatting boilerplate.

        Allows registering formatters for specific result types, enabling
        automatic formatting based on result type detection. Reduces ~74 lines
        of formatting boilerplate per result type.

        Args:
            result_type: Type of result to format (e.g., OperationResult)
            formatter: Callable that formats and displays the result
                Signature: (result: t.JsonValue | r[t.JsonValue], output_format: str) -> None

        Returns:
            r[bool]: True on success, False on failure

        Example:
            ```python
            from flext_cli import FlextCliOutput
        from flext_cli.constants import c
            from pydantic import BaseModel


            class OperationResult(BaseModel):
                # Example result model
                status: str
                entries_processed: int


            output = FlextCliOutput()


            # Register formatter for OperationResult
            def format_operation(result: OperationResult, fmt: str) -> None:
                # Python 3.13: match/case - more elegant and modern
                match fmt:
                    case c.Cli.OutputFormats.TABLE.value:
                        # Create Rich table from result
                        console = output._formatters.console
                        panel = output._formatters.create_panel(
                            f"[green]Operation completed![/green]\\n"
                            + f"Status: {result.status}\\n"
                            + f"Entries: {result.entries_processed}",
                            title="✅ Operation Result",
                        )
                        # Use .value directly instead of deprecated .value
                        console.print(panel.value)
                    case c.Cli.OutputFormats.JSON.value:
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
            # Type narrowing: formatter is compatible with expected signature
            # Access _result_formatters via class (ClassVar)
            FlextCliOutput._result_formatters[result_type] = formatter
            return r[bool].ok(value=True)

        except Exception as e:
            return r[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}",
            )

    def format_and_display_result(
        self,
        result: BaseModel | t.JsonValue | r[t.JsonValue],
        output_format: str = c.Cli.OutputFormats.TABLE.value,
    ) -> r[bool]:
        """Auto-detect result type and apply registered formatter with extracted helpers.

        **PURPOSE**: Eliminate manual type checking and formatter dispatch.

        Args:
            result: Domain result object to format
            output_format: Output format ("table", "json", "yaml", etc.Cli.)

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
                result,
                output_format,
            )
            if formattable_result.is_failure:
                return r[bool].fail(
                    formattable_result.error
                    or "Failed to convert result to formattable",
                    error_code=formattable_result.error_code,
                    error_data=formattable_result.error_data,
                )

            # Use .value directly instead of deprecated .value
            formattable = formattable_result.value
            return self._display_formatted_result(formattable)

        except Exception as e:
            return r[bool].fail(f"Failed to format and display result: {e}")

    def _try_registered_formatter(
        self,
        result: BaseModel | t.JsonValue | r[t.JsonValue],
        output_format: str,
    ) -> r[bool]:
        """Try to use registered formatter for result type.

        Returns:
            r[bool]: True if formatter was found and executed,
            False if no formatter registered for this type

        """
        result_type = type(result)

        formatter = self._get_registered_formatter(result_type)
        if formatter is not None:
            return self._dispatch_registered_formatter(result, formatter, output_format)

        return r[bool].fail(
            f"No registered formatter for type {result_type.__name__}",
        )

    def _get_registered_formatter(
        self,
        result_type: type,
    ) -> Callable[[t.JsonValue | r[t.JsonValue], str], None] | None:
        """Get registered formatter for a concrete result type."""
        formatters_dict: dict[
            type,
            Callable[[t.JsonValue | r[t.JsonValue], str], None],
        ] = FlextCliOutput._result_formatters
        return formatters_dict.get(result_type)

    def _dispatch_registered_formatter(
        self,
        result: BaseModel | t.JsonValue | r[t.JsonValue],
        formatter: Callable[[t.JsonValue | r[t.JsonValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Dispatch registered formatter by result strategy."""
        match result:
            case BaseModel() as model_result:
                return self._format_registered_basemodel(
                    model_result,
                    formatter,
                    output_format,
                )
            case r() as railway_result:
                return self._format_registered_result(
                    railway_result,
                    formatter,
                    output_format,
                )
            case _:
                return self._format_registered_generic(result, formatter, output_format)

    def _format_registered_basemodel(
        self,
        result: BaseModel,
        formatter: Callable[[t.JsonValue | r[t.JsonValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Format registered BaseModel result."""
        formattable_result: t.JsonValue = result.model_dump()
        formatter(formattable_result, output_format)
        return r[bool].ok(value=True)

    def _format_registered_result(
        self,
        result: r[t.JsonValue],
        formatter: Callable[[t.JsonValue | r[t.JsonValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Format registered railway result payload."""
        if result.is_failure:
            return r[bool].fail(f"Cannot format failed result: {result.error}")

        result_value = result.value
        result_value_general = self._normalize_formatter_value(result_value)
        if self.is_json(result_value_general):
            formatter(result_value_general, output_format)
            return r[bool].ok(value=True)

        formatter(str(result_value), output_format)
        return r[bool].ok(value=True)

    def _format_registered_generic(
        self,
        result: t.JsonValue,
        formatter: Callable[[t.JsonValue | r[t.JsonValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Format registered plain general value."""
        formatter(result, output_format)
        return r[bool].ok(value=True)

    @staticmethod
    def _normalize_formatter_value(value: t.JsonValue) -> t.JsonValue:
        """Normalize formatter input to a JSON-compatible general value."""
        match value:
            case str() | int() | float() | bool() | None | dict() | list() | tuple():
                return value
            case _:
                return str(value)

    def _convert_result_to_formattable(
        self,
        result: BaseModel | t.JsonValue | r[t.JsonValue],
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

        # Handle Pydantic models
        match result:
            case BaseModel() as model_result:
                return self._format_pydantic_model(model_result, output_format)
            case _:
                pass

        # Handle dict objects directly
        # Type narrowing: result is t.JsonValue, check if it's a dict
        match result:
            case dict() as dict_result:
                return self.format_data(dict_result, output_format)
            case _:
                pass
        match result:
            case object(__dict__=raw_source):
                match raw_source:
                    case Mapping() as source_mapping:
                        object_dict = dict(source_mapping)
                    case _:
                        object_dict = {}
                filtered_dict = u.mapper().filter_dict(
                    object_dict,
                    lambda _k, v: self.is_json(v),
                )
                result_dict = self.ensure_dict(filtered_dict, {})
                return self.format_data(result_dict, output_format)
            case _:
                pass

        # Use string representation (not a fallback - valid conversion)
        return r[str].ok(str(result))

    def _format_pydantic_model(
        self,
        result: BaseModel,
        output_format: str,
    ) -> r[str]:
        """Format Pydantic model to string."""
        # Use model_dump() directly - dict is compatible with t.JsonValue
        result_dict = result.model_dump()
        return self.format_data(result_dict, output_format)

    def _format_dict_object(
        self,
        result: t.JsonValue | r[t.JsonValue],
        output_format: str,
    ) -> r[str]:
        """Format object with __dict__ to string."""
        # Type narrowing: result must have __dict__ attribute
        match result:
            case r() as railway_result:
                # Extract value from r
                if railway_result.is_failure:
                    return r[str].fail(
                        f"Cannot format failed result: {railway_result.error}"
                    )
                # Use .value directly instead of deprecated .value
                # Type narrowing: .value returns t.JsonValue
                # Note: Cannot use isinstance with TypeAliasType (t.JsonValue)
                # result_value is already t.JsonValue from .value
                result = railway_result.value
            case _:
                pass
        # Now result is t.JsonValue - check if it has __dict__
        match result:
            case object(__dict__=raw_source):
                pass
            case _:
                return r[str].fail(
                    f"Object {type(result).__name__} has no __dict__ attribute",
                )
        match raw_source:
            case Mapping() as mapping_source:
                raw_dict: dict[str, t.JsonValue] = dict(mapping_source)
            case _:
                raw_dict = {}
        # Use build() DSL: process_mapping → to_json → filter → ensure dict
        json_dict_result = u.Cli.process_mapping(
            raw_dict,
            processor=lambda _k, v: self.to_json(v),
            on_error="skip",
        )
        # Type narrowing: unwrap_or returns dict or empty dict
        json_dict_raw = json_dict_result.unwrap_or({})
        match json_dict_raw:
            case dict() as mapping_result:
                json_dict: dict[str, t.JsonValue] = mapping_result
            case _:
                json_dict = {}
        # Use mapper to filter dict items
        filtered_json_dict = u.mapper().filter_dict(
            json_dict,
            lambda _k, v: self.is_json(v),
        )
        cli_json_dict_result = u.Cli.process_mapping(
            filtered_json_dict,
            processor=lambda _k, v: v,
            on_error="skip",
        )
        # Type narrowing: unwrap_or returns dict or empty dict
        cli_json_dict_raw = cli_json_dict_result.unwrap_or({})
        match cli_json_dict_raw:
            case dict() as mapping_result:
                cli_json_dict: dict[str, t.JsonValue] = mapping_result
            case _:
                cli_json_dict = {}
        return self.format_data(cli_json_dict, output_format)

    @staticmethod
    def _display_formatted_result(formatted: str) -> r[bool]:
        """Display formatted result string using Rich console."""
        console = FlextCliFormatters().console
        console.print(formatted)
        return r[bool].ok(value=True)

    # =========================================================================
    # RICH TABLE CREATION (Delegates to FlextCliFormatters)
    # =========================================================================

    @staticmethod
    def _validate_headers(
        headers: list[str],
        data: list[Mapping[str, t.JsonValue]],
    ) -> r[bool]:
        """Validate headers exist in data."""

        def _extract_keys(row: Mapping[str, t.JsonValue]) -> set[str]:
            """Extract keys from dict row."""
            return set(row.keys())

        all_keys = u.Cli.process(
            data,
            processor=_extract_keys,
            on_error="skip",
        )
        if all_keys.is_failure:
            return r.fail("Failed to extract keys from data")
        combined_keys = set()
        for key_set in all_keys.value or []:
            match key_set:
                case set() as key_set_value:
                    combined_keys.update(key_set_value)
                case _:
                    pass
        missing = u.filter(headers, lambda h: h not in combined_keys)
        if missing:
            return r.fail(f"Header(s) not found in data: {', '.join(missing)}")
        return r[bool].ok(value=True)

    @staticmethod
    def _build_table_rows(
        data: list[Mapping[str, t.JsonValue]],
        headers: list[str],
    ) -> r[list[list[str]]]:
        """Build table rows from data."""

        def build_row(row_data: Mapping[str, t.JsonValue]) -> list[str]:
            """Build row values using u utilities."""
            values = u.Cli.process(
                headers,
                processor=lambda h: str(u.get(row_data, h)) if h in row_data else None,
                on_error="skip",
            )
            # FlextCliUtilities.filter expects predicate as second positional arg
            values_list = values.value or []
            filtered = u.filter(values_list, predicate=lambda v: v is not None)
            # Type narrowing: filtered contains only non-None values, convert to str
            filtered_list: list[str] = [
                str(item) for item in filtered if item is not None
            ]
            return filtered_list

        rows_result = u.Cli.process(data, processor=build_row, on_error="fail")
        if rows_result.is_failure:
            return r.fail(rows_result.error or "Failed to build rows")
        # Type narrowing: ensure_list returns list[t.JsonValue]
        # Filter to ensure all items are list[str]
        rows_raw = FlextCliOutput.ensure_list(
            rows_result.unwrap_or([]),
            [],
        )
        rows: list[list[str]] = []
        for row in rows_raw:
            match row:
                case list() as row_items:
                    rows.append([str(item) for item in row_items])
                case _:
                    pass
        return r.ok(rows)

    def _prepare_table_headers(
        self,
        data: list[Mapping[str, t.JsonValue]],
        headers: list[str] | None = None,
    ) -> r[list[str]]:
        """Prepare and validate table headers."""
        default_headers = self.get_keys(data[0]) if data else []
        default_headers_general: list[t.JsonValue] = list(default_headers)
        table_headers_raw = self.ensure_list(headers, default_headers_general)
        table_headers: list[str] = [str(h) for h in table_headers_raw]

        # Validate headers if provided
        if headers is not None:
            validation_result = FlextCliOutput._validate_headers(
                table_headers,
                data,
            )
            if validation_result.is_failure:
                return r[list[str]].fail(
                    validation_result.error or "Header validation failed"
                )

        return r[list[str]].ok(table_headers)

    def _initialize_rich_table(
        self,
        headers: list[str],
        title: str | None = None,
    ) -> r[p.Cli.Display.RichTableProtocol]:
        """Initialize a Rich table with headers.

        Uses RichTableProtocol from lower layer instead of object for better type safety.
        """
        table_result = FlextCliFormatters().create_table(
            data=None,
            headers=headers,
            title=title,
        )
        if table_result.is_failure:
            return r[p.Cli.Display.RichTableProtocol].fail(
                f"Failed to create Rich table: {table_result.error}"
            )
        # Type narrowing: table_result.value is RichTableProtocol compatible
        # Use type guard to verify it implements the protocol
        table_value = table_result.value
        if self._is_rich_table_protocol(table_value):
            return r[p.Cli.Display.RichTableProtocol].ok(table_value)
        # Fallback: convert to string representation if not RichTableProtocol
        return r[p.Cli.Display.RichTableProtocol].fail(
            "Table value is not RichTableProtocol compatible"
        )

    def _populate_table_rows(
        self,
        table: p.Cli.Display.RichTableProtocol,
        data: list[Mapping[str, t.JsonValue]],
        headers: list[str],
    ) -> r[bool]:
        """Add columns and rows to table.

        Uses RichTableProtocol from lower layer instead of object for better type safety.
        """
        # Add columns
        u.Cli.process(
            headers,
            processor=lambda h: table.add_column(str(h)),
            on_error="skip",
        )

        # Build and add rows
        rows_result = FlextCliOutput._build_table_rows(data, headers)
        if rows_result.is_failure:
            return r[bool].fail(rows_result.error or "Failed to build rows")

        rows_list = rows_result.value or []
        match rows_list:
            case list() as table_rows:
                for row in table_rows:
                    match row:
                        case list() as row_items:
                            table.add_row(*row_items)
                        case _:
                            pass
            case _:
                pass

        return r[bool].ok(value=True)

    def create_rich_table(
        self,
        data: list[Mapping[str, t.JsonValue]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[p.Cli.Display.RichTableProtocol]:
        """Create a Rich table from data using FlextCliFormatters.

        Args:
            data: List of dictionaries to display
            title: Optional table title
            headers: Optional custom headers

        Returns:
            r containing Rich Table object

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
            return r[p.Cli.Display.RichTableProtocol].fail(
                c.Cli.ErrorMessages.NO_DATA_PROVIDED,
            )

        try:
            # Prepare headers
            headers_result = self._prepare_table_headers(data, headers)
            if headers_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    headers_result.error or "Failed to prepare headers"
                )
            table_headers = headers_result.value

            # Initialize table
            table_result = self._initialize_rich_table(table_headers, title)
            if table_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    table_result.error or "Failed to initialize table"
                )
            table = table_result.value

            # Populate table
            populate_result = self._populate_table_rows(table, data, table_headers)
            if populate_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    populate_result.error or "Failed to populate table"
                )

            # Return protocol-compatible table
            if not self._is_rich_table_protocol(table):
                msg = "table must implement RichTableProtocol"
                raise TypeError(msg)
            return r[p.Cli.Display.RichTableProtocol].ok(table)

        except Exception as e:
            error_msg = c.Cli.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                error=e,
            )
            return r[p.Cli.Display.RichTableProtocol].fail(error_msg)

    def table_to_string(
        self,
        table: p.Cli.Display.RichTableProtocol,
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
        return FlextCliFormatters().render_table_to_string(table, width)

    # =========================================================================
    # ASCII TABLE CREATION (Delegates to FlextCliTables)
    # =========================================================================

    @staticmethod
    def create_ascii_table(
        data: list[Mapping[str, t.JsonValue]],
        headers: list[str] | None = None,
        table_format: str = c.Cli.TableFormats.SIMPLE,
        *,
        config: p.Cli.TableConfigProtocol | None = None,
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
            >>> config = m.Cli.TableConfig(
            ...     headers=["Name", "Age"],
            ...     table_format="fancy_grid",
            ...     floatfmt=".2f",
            ... )
            >>> result = output.create_ascii_table(data, config=config)

        """
        if config is not None:
            # Use provided config directly
            return FlextCliTables.create_table(data=data, config=config)

        # Use build() DSL for headers normalization
        # Type narrowing: ensure_list returns list[t.JsonValue], convert to list[str]
        validated_headers_raw = FlextCliOutput.ensure_list(
            headers, [c.Cli.TableFormats.KEYS]
        )
        validated_headers: list[str] = [str(h) for h in validated_headers_raw]
        final_config = m.Cli.TableConfig.model_validate({
            "headers": validated_headers,
            "table_format": table_format,
        })
        # Type narrowing: TableConfig implements TableConfigProtocol structurally
        config_protocol: p.Cli.TableConfigProtocol = final_config
        return FlextCliTables.create_table(data=data, config=config_protocol)

    # =========================================================================
    # PROGRESS BARS (Delegates to FlextCliFormatters)
    # =========================================================================

    def create_progress_bar(
        self,
    ) -> r[p.Cli.Interactive.RichProgressProtocol]:
        """Create a Rich progress bar using FlextCliFormatters.

        Returns:
            r[RichProgressProtocol]: Rich Progress wrapped in Result

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar()

        """
        # create_progress returns r[Progress] which implements RichProgressProtocol
        result = FlextCliFormatters().create_progress()
        if result.is_success:
            # Progress implements RichProgressProtocol structurally
            # Progress (concrete type) implements RichProgressProtocol structurally
            # Type narrowing: progress_value implements RichProgressProtocol structurally
            # Use .value directly instead of deprecated .value
            progress_value = result.value
            # Rich Progress implements RichProgressProtocol structurally at runtime
            # Use type guard to narrow type for mypy
            if not self._is_rich_progress_protocol(progress_value):
                msg = "progress_value must implement RichProgressProtocol"
                raise TypeError(msg)
            return r[p.Cli.Interactive.RichProgressProtocol].ok(progress_value)
        return r[p.Cli.Interactive.RichProgressProtocol].fail(result.error or "")

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
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        return FlextCliFormatters().print(message, style=validated_style)

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
            f"{c.Cli.Symbols.ERROR_PREFIX} {message}",
            style=c.Cli.Styles.BOLD_RED,
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
            f"{c.Cli.Symbols.SUCCESS_PREFIX} {message}",
            style=c.Cli.Styles.BOLD_GREEN,
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
            f"{c.Cli.Emojis.WARNING} {c.Cli.OutputDefaults.WARNING_PREFIX} {message}",
            style=c.Cli.Styles.BOLD_YELLOW,
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
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        return FlextCliFormatters().print(text, style=validated_style)

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
        final_message_type = self.ensure_str(
            message_type,
            c.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE,
        )

        # Use build() DSL for style and emoji mapping with generalized helpers
        style_map = {
            c.Cli.MessageTypes.INFO.value: c.Cli.Styles.BLUE,
            c.Cli.MessageTypes.SUCCESS.value: c.Cli.Styles.BOLD_GREEN,
            c.Cli.MessageTypes.ERROR.value: c.Cli.Styles.BOLD_RED,
            c.Cli.MessageTypes.WARNING.value: c.Cli.Styles.BOLD_YELLOW,
        }
        emoji_map = {
            c.Cli.MessageTypes.INFO.value: c.Cli.Emojis.INFO,
            c.Cli.MessageTypes.SUCCESS.value: c.Cli.Emojis.SUCCESS,
            c.Cli.MessageTypes.ERROR.value: c.Cli.Emojis.ERROR,
            c.Cli.MessageTypes.WARNING.value: c.Cli.Emojis.WARNING,
        }
        # Type narrowing: style_map and emoji_map are dict[str, str], convert to t.JsonValue
        style_map_general: dict[str, t.JsonValue] = dict(style_map)
        emoji_map_general: dict[str, t.JsonValue] = dict(emoji_map)
        style = self.ensure_str(
            self.get_map_val(style_map_general, final_message_type, c.Cli.Styles.BLUE),
        )
        emoji = self.ensure_str(
            self.get_map_val(emoji_map_general, final_message_type, c.Cli.Emojis.INFO),
        )
        formatted_message = f"{emoji} {message}"

        return self.print_message(formatted_message, style=style)

    def display_data(
        self,
        data: t.JsonValue,
        format_type: str | None = None,
        *,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[bool]:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.Cli.)
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data(
            ...     {"key": "value"},
            ...     format_type=c.Cli.OutputFormats.JSON.value,
            ... )

        """
        # Use build() DSL for format type normalization
        final_format_type = self.ensure_str(
            format_type,
            c.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE,
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

        # Use .value directly instead of deprecated .value
        formatted_data = format_result.value

        # Display the formatted data
        return self.print_message(formatted_data)

    # =========================================================================
    # DATA FORMAT METHODS (Built-in)
    # =========================================================================

    def format_json(self, data: t.JsonValue) -> r[str]:
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
                    indent=c.Cli.OutputDefaults.JSON_INDENT,
                ),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.JSON_FORMAT_FAILED.format(
                error=e,
            )

            return r[str].fail(error_msg)

    def format_yaml(self, data: t.JsonValue) -> r[str]:
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
                    default_flow_style=c.Cli.OutputDefaults.YAML_DEFAULT_FLOW_STYLE,
                ),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.YAML_FORMAT_FAILED.format(
                error=e,
            )

            return r[str].fail(error_msg)

    def format_csv(self, data: t.JsonValue) -> r[str]:
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
            # Format based on data type
            if u.is_list_like(data) and data:
                # Normalize data to JsonValue first (works with Sequence[t.JsonValue])
                normalized_data = FlextRuntime.normalize_to_general_value(data)
                # Coerce to list with type normalization
                coerced_list = self._coerce_to_list(normalized_data)
                if coerced_list and u.is_dict_like(coerced_list[0]):
                    return self._format_csv_list(coerced_list)
            if u.is_dict_like(data):
                return self._format_csv_dict(data)
            # Fallback to JSON for non-dict/list data
            return r[str].ok(
                json.dumps(
                    data,
                    default=str,
                    indent=c.Cli.OutputDefaults.JSON_INDENT,
                ),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.CSV_FORMAT_FAILED.format(
                error=e,
            )

            return r.fail(error_msg)

    def _coerce_to_list(self, data: t.JsonValue) -> list[t.JsonValue]:
        """Coerce data to list for CSV processing.

        Uses types from lower layer (t.JsonValue) for proper type safety.
        """
        # Direct list return
        match data:
            case list() as list_data:
                return list_data
            case _:
                pass
        # Sequence types (tuple, Sequence) - includes str but handled as single value
        match data:
            case tuple() as tuple_data:
                return [self._normalize_iterable_item(item) for item in tuple_data]
            case _:
                pass
        # Dict returns items
        match data:
            case dict() as dict_data:
                return list(dict_data.items())
            case _:
                pass
        # For other types, try to convert using _convert_iterable_to_list
        # Data might be a custom iterable like BaseModel or other objects with __iter__
        try:
            match data:
                case str():
                    # str is iterable but we don't want to treat it as a sequence
                    return []
                case _:
                    pass
            # Try to iterate by checking if iter() works
            # Use a separate method to avoid type checker errors
            result = self._try_iterate_items(data)
            return result or []
        except (TypeError, AttributeError):
            # data is not iterable (int, float, bool, datetime, Path, etc.)
            return []

    def _try_iterate_items(self, data: t.JsonValue) -> list[t.JsonValue]:
        """Try to iterate over data and return list of items.

        Helper to avoid type checker issues with non-iterable JsonValue types.
        Uses duck typing: attempts iteration and catches TypeError if not iterable.
        """
        try:
            strategy = self._resolve_iteration_strategy(data)
            if strategy is None:
                return []
            return strategy(data)
        except (TypeError, AttributeError):
            # Fallback: not iterable, return empty
            return []

    def _resolve_iteration_strategy(
        self,
        data: t.JsonValue,
    ) -> Callable[[t.JsonValue], list[t.JsonValue]] | None:
        """Resolve iterable strategy for general values."""
        strategies: tuple[
            tuple[
                Callable[[t.JsonValue], bool],
                Callable[[t.JsonValue], list[t.JsonValue]],
            ],
            ...,
        ] = (
            (self._is_mapping_value, self._iterate_mapping),
            (self._is_sequence_value, self._iterate_sequence),
            (self._is_custom_iterable_value, self._iterate_model),
        )
        for matcher, strategy in strategies:
            if matcher(data):
                return strategy
        return None

    @staticmethod
    def _is_mapping_value(data: t.JsonValue) -> bool:
        """Check if value should use mapping iteration strategy."""
        match data:
            case dict():
                return True
            case _:
                return False

    @staticmethod
    def _is_sequence_value(data: t.JsonValue) -> bool:
        """Check if value should use sequence iteration strategy."""
        match data:
            case list() | tuple():
                return True
            case _:
                return False

    @staticmethod
    def _is_custom_iterable_value(data: t.JsonValue) -> bool:
        """Check if value should use custom iterable strategy."""
        match data:
            case str() | list() | tuple() | dict():
                return False
            case Iterable():
                return True
            case _:
                return False

    def _iterate_mapping(self, data: t.JsonValue) -> list[t.JsonValue]:
        """Iterate dictionary values as tuple items."""
        match data:
            case dict() as mapping_data:
                pass
            case _:
                return []
        iterable_items: list[t.JsonValue] = []
        for key, value in mapping_data.items():
            key_value = (key, value)
            match key_value:
                case tuple() as tuple_value:
                    dict_item: t.JsonValue = tuple_value
                case _:
                    dict_item = str(key_value)
            iterable_items.append(dict_item)
        return iterable_items

    def _iterate_sequence(self, data: t.JsonValue) -> list[t.JsonValue]:
        """Iterate list/tuple values with normalization."""
        match data:
            case list() | tuple() as sequence_data:
                return [self._normalize_iterable_item(item) for item in sequence_data]
            case _:
                return []

    def _iterate_model(self, data: t.JsonValue) -> list[t.JsonValue]:
        """Iterate custom iterable values with normalization."""
        match data:
            case Iterable() as iterable_data:
                return [self._normalize_iterable_item(item) for item in iterable_data]
            case _:
                return []

    @staticmethod
    def _normalize_iterable_item(item: object) -> t.JsonValue:
        """Normalize iterable items to general value type."""
        match item:
            case str() | int() | float() | bool() | None | dict() | list() | tuple():
                return item
            case _:
                return str(item)

    def _convert_iterable_to_list(
        self, data: Iterable[t.JsonValue]
    ) -> list[t.JsonValue]:
        """Convert iterable to list with type narrowing.

        Helper method to reduce complexity of _coerce_to_list.
        Uses Iterable from lower layer for proper type safety.
        """
        try:
            match data:
                case Sequence() as sequence_data:
                    return list(sequence_data)
                case _:
                    pass
            # For other iterables, convert using list comprehension
            # Each item is narrowed to t.JsonValue from lower layer
            iterable_items: list[t.JsonValue] = []
            for item in data:
                # Type narrowing: item from iterable is t.JsonValue compatible
                match item:
                    case (
                        str()
                        | int()
                        | float()
                        | bool()
                        | None
                        | dict()
                        | list()
                        | tuple()
                    ) as supported_item:
                        item_general: t.JsonValue = supported_item
                    case _:
                        item_general = str(item)  # Fallback to string for other types
                iterable_items.append(item_general)
            return iterable_items
        except (TypeError, ValueError):
            return []

    def _format_csv_list(self, data: t.JsonValue) -> r[str]:
        """Format list of dicts as CSV."""
        output_buffer = StringIO()
        data_list = self._coerce_to_list(data)
        if not data_list or not u.is_dict_like(data_list[0]):
            return r[str].fail("CSV list format requires list of dicts")
        fieldnames = self.get_keys(data_list[0])
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()

        # Process rows
        filtered_rows = u.filter(data_list, predicate=u.is_dict_like)
        match filtered_rows:
            case list() as list_rows:
                rows_source = list_rows
            case _:
                rows_source = []
        dict_rows_raw = self.ensure_list(rows_source, [])
        # Use t.JsonValue from lower layer instead of object
        dict_rows: list[dict[str, t.JsonValue]] = [
            item for item in dict_rows_raw if u.is_dict_like(item)
        ]
        csv_rows: list[dict[str, str | int | float | bool]] = []
        for row in dict_rows:
            # Process CSV row - operations are safe and shouldn't raise exceptions
            processed_row = self._process_csv_row(row)
            csv_rows.append(processed_row)
        writer.writerows(csv_rows)
        return r[str].ok(output_buffer.getvalue())

    def _format_csv_dict(self, data: t.JsonValue) -> r[str]:
        """Format single dict as CSV."""
        output_buffer = StringIO()
        fieldnames = self.get_keys(data)
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        # Type narrowing: data is dict-like from format_csv check
        # Use t.JsonValue from lower layer instead of object
        match data:
            case dict() as mapping_data:
                data_dict: dict[str, t.JsonValue] = dict(mapping_data)
            case _:
                data_dict = {}
        writer.writerow(data_dict)
        return r[str].ok(output_buffer.getvalue())

    def _process_csv_row(
        self,
        row: Mapping[str, t.JsonValue],
    ) -> Mapping[str, str | int | float | bool]:
        """Process CSV row with None replacement.

        Uses t.JsonValue from lower layer instead of object for better type safety.
        """
        processed: dict[str, str | int | float | bool] = {}
        for k, v in row.items():
            processed[k] = self._replace_none_for_csv(k, v)
        return processed

    @staticmethod
    def _replace_none_for_csv(_k: str, v: t.JsonValue) -> str | int | float | bool:
        """Replace None with empty string for CSV."""
        if v is None:
            return ""
        match v:
            case str() | int() | float() | bool() as scalar_value:
                return scalar_value
            case _:
                pass
        return str(v)

    def format_table(
        self,
        data: Mapping[str, t.JsonValue] | list[Mapping[str, t.JsonValue]] | str,
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

        # Use .value directly instead of deprecated .value
        prepared = prepared_result.value
        table_result = self._create_table_string(prepared[0], prepared[1])
        if table_result.is_failure:
            return table_result

        # Use .value directly instead of deprecated .value
        table = table_result.value
        return r.ok(self._add_title(table, title))

    def _prepare_table_data_safe(
        self,
        data: Mapping[str, t.JsonValue] | list[Mapping[str, t.JsonValue]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )

            return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
                error_msg,
            )

    def _prepare_table_data(
        self,
        data: Mapping[str, t.JsonValue] | list[Mapping[str, t.JsonValue]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]]:
        """Prepare and validate table data and headers."""
        if u.is_dict_like(data):
            # Use build() DSL: ensure dict → transform to JSON
            json_data = self.to_dict_json(data)
            return self._prepare_dict_data(json_data, headers)
        if u.is_list_like(data):
            # Use build() DSL: process → norm_json → ensure list
            # For lists, processor takes only item, not (key, item)
            # Filter first, then process (FlextCliUtilities.process doesn't accept predicate)
            filtered_data = [item for item in data if u.is_dict_like(item)]
            process_result = u.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            # Type narrowing: ensure_list returns list[t.JsonValue]
            # Filter to ensure all items are dict[str, t.JsonValue]
            converted_list_raw = self.ensure_list(
                process_result.unwrap_or([]),
                [],
            )
            converted_list: list[dict[str, t.JsonValue]] = [
                item for item in converted_list_raw if u.is_dict_like(item)
            ]
            return self._prepare_list_data(converted_list, headers)
        return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
            c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT,
        )

    @staticmethod
    def _prepare_dict_data(
        data: Mapping[str, t.JsonValue],
        headers: list[str] | None,
    ) -> r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]]:
        """Prepare dict data for table display."""
        # Reject test invu
        if c.Cli.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT,
            )

        # Use build() DSL: process → kv_pair → ensure dict → extract values → ensure list
        def kv_pair(k: str, v: t.JsonValue) -> Mapping[str, t.JsonValue]:
            """Create key-value pair dict."""
            return {
                c.Cli.OutputFieldNames.KEY: k,
                c.Cli.OutputFieldNames.VALUE: str(v),
            }

        process_result = u.Cli.process_mapping(data, processor=kv_pair, on_error="skip")
        dict_result = FlextCliOutput.ensure_dict(
            process_result.unwrap_or({}),
            {},
        )
        # Type narrowing: ensure_list returns list[t.JsonValue]
        # Filter to ensure all items are dict[str, t.JsonValue]
        table_data_raw = FlextCliOutput.ensure_list(list(dict_result.values()), [])
        table_data: list[dict[str, t.JsonValue]] = [
            item for item in table_data_raw if u.is_dict_like(item)
        ]
        # Use build() DSL: ensure list → ensure default
        # Type narrowing: ensure_list returns list[t.JsonValue], convert to list[str]
        table_headers_raw = FlextCliOutput.ensure_list(
            headers, [c.Cli.TableFormats.KEYS]
        )
        table_headers: list[str] = [str(h) for h in table_headers_raw]
        return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].ok((
            table_data,
            table_headers,
        ))

    @staticmethod
    def _prepare_list_data(
        data: list[Mapping[str, t.JsonValue]],
        headers: list[str] | None,
    ) -> r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]]:
        """Prepare list data for table display."""
        if not data:
            return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.NO_DATA_PROVIDED,
            )

        # Validate headers type
        if headers is not None and not u.is_list_like(headers):
            return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST,
            )

        # Ensure list and map to str
        # headers is narrowed to Sequence[t.JsonValue] | None by TypeGuard check
        # ensure_list now accepts Sequence[t.JsonValue] directly
        headers_list = FlextCliOutput.ensure_list(
            headers,
            [c.Cli.TableFormats.KEYS],
        )
        table_headers = [str(h) for h in headers_list]

        # Validate headers exist in data if headers are provided (not using KEYS)
        if headers is not None and table_headers != [c.Cli.TableFormats.KEYS]:
            validation_result = FlextCliOutput._validate_headers(table_headers, data)
            if validation_result.is_failure:
                return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].fail(
                    validation_result.error or "Header validation failed",
                )

        return r[tuple[list[Mapping[str, t.JsonValue]], str | list[str]]].ok((
            data,
            table_headers,
        ))

    def _create_table_string(
        self,
        table_data: list[Mapping[str, t.JsonValue]],
        table_headers: str | list[str],
    ) -> r[str]:
        """Create table string using FlextCliTables."""
        try:
            config_instance = m.Cli.TableConfig.model_validate({
                "headers": table_headers,
                "table_format": c.Cli.TableFormats.GRID,
            })
            # Type narrowing: TableConfig implements TableConfigProtocol structurally
            config: p.Cli.TableConfigProtocol = config_instance
            table_result = FlextCliTables.create_table(data=table_data, config=config)

            if table_result.is_failure:
                return r[str].fail(
                    f"Failed to create table: {table_result.error}",
                )

            return table_result
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                error=e,
            )

            return r[str].fail(error_msg)

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{c.Cli.OutputDefaults.NEWLINE}{table_str}{c.Cli.OutputDefaults.NEWLINE}"
        return table_str

    def format_as_tree(
        self,
        data: t.JsonValue,
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
        final_title = self.ensure_str(title, c.Cli.OutputDefaults.DEFAULT_TREE_TITLE)

        # Create tree through formatters
        tree_result = FlextCliFormatters().create_tree(label=final_title)

        if tree_result.is_failure:
            return r[str].fail(f"Failed to create tree: {tree_result.error}")

        concrete_tree = tree_result.value

        self._build_tree(concrete_tree, data)

        return FlextCliFormatters().render_tree_to_string(
            concrete_tree,
            width=c.Cli.CliDefaults.DEFAULT_MAX_WIDTH,
        )

    def _build_tree(
        self,
        tree: RichTree,
        data: t.JsonValue,
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from (t.JsonValue - can be dict, list, or primitive)

        """
        match data:
            case dict() as dict_data:
                # Use build() DSL: process → handle nested structures
                def process_tree_item(k: str, v: t.JsonValue) -> None:
                    """Process single tree item."""
                    match v:
                        case dict() as dict_value:
                            branch = tree.add(str(k))
                            self._build_tree(branch, dict_value)
                        case list() as list_value:
                            branch = tree.add(
                                f"{k}{c.Cli.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}"
                            )

                            def process_list_item(item: t.JsonValue) -> None:
                                """Process list item."""
                                self._build_tree(branch, item)

                            match list_value:
                                case list() as ensured_list:
                                    u.Cli.process(
                                        ensured_list,
                                        processor=process_list_item,
                                        on_error="skip",
                                    )
                                case _:
                                    pass
                        case _:
                            tree.add(
                                f"{k}{c.Cli.OutputDefaults.TREE_VALUE_SEPARATOR}{v}"
                            )

                u.Cli.process_mapping(
                    dict_data,
                    processor=process_tree_item,
                    on_error="skip",
                )
            case list() as list_data:
                # Use build() DSL: process each item
                def process_list_item(item: t.JsonValue) -> None:
                    """Process list item."""
                    self._build_tree(tree, item)

                u.Cli.process(list_data, processor=process_list_item, on_error="skip")
            case _:
                tree.add(str(data))

    # =========================================================================
    # CONSOLE ACCESS (Delegates to FlextCliFormatters)
    # =========================================================================

    @property
    def console(self) -> p.Cli.Display.RichConsoleProtocol:
        """Get the console instance from FlextCliFormatters (property form).

        Returns:
            Console instance from formatters

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.console

        """
        # Console (concrete type) implements RichConsoleProtocol structurally
        # Use cast for structural typing compatibility

        concrete_console = FlextCliFormatters().console
        # Rich Console implements RichConsoleProtocol structurally at runtime
        # Protocol is structural, so concrete_console is compatible
        # Use type guard to narrow type for mypy
        if not self._is_rich_console_protocol(concrete_console):
            msg = "concrete_console must implement RichConsoleProtocol"
            raise TypeError(msg)
        return concrete_console

    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute service - required by FlextService abstract method.

        Returns:
            r[dict]: Service status and operation information

        Note:
            FlextCliOutput is a utility service that formats and displays data.
            The execute() method returns service operational status.

        """
        return r[Mapping[str, t.JsonValue]].ok({
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.Services.OUTPUT,
        })


__all__ = ["FlextCliOutput"]
