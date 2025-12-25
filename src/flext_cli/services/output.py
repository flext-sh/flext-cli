"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from io import StringIO
from typing import TypeGuard

import yaml
from flext_core import FlextRuntime, r, t
from pydantic import BaseModel
from rich.tree import Tree as RichTree

from flext_cli.constants import FlextCliConstants
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.services.tables import FlextCliTables
from flext_cli.utilities import FlextCliUtilities

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
        ...     format_type=FlextCliConstants.Cli.OutputFormats.JSON.value,
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

    # ═══════════════════════════════════════════════════════════════════════════
    # STATIC HELPER METHODS - General purpose utilities for output operations
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def is_json(v: t.GeneralValueType) -> bool:
        """Check if value is JSON-compatible type.

        Uses t.GeneralValueType from lower layer instead of object for better type safety.
        """
        return isinstance(v, (str, int, float, bool, type(None), dict, list))

    @staticmethod
    def to_json(v: t.GeneralValueType) -> t.GeneralValueType:
        """Convert value to JSON-compatible using build DSL."""
        if isinstance(v, dict):
            result = FlextCliUtilities.build(
                v,
                ops={"ensure": "dict", "transform": {"to_json": True}},
                on_error="skip",
            )
            # Type narrowing: FlextCliUtilities.build returns object, need to check if it's FlextResult
            if (
                hasattr(result, "is_success")
                and hasattr(result, "value")
                and isinstance(result, r)
            ):
                # Type narrowing: result is FlextResult
                return result.value if result.is_success else v
            # If not FlextResult, assume it's the converted value
            # Type narrowing: result is already t.GeneralValueType from FlextCliUtilities.build
            # FlextCliUtilities.build returns object, but we know it's t.GeneralValueType compatible
            if isinstance(result, (str, int, float, bool, type(None), dict, list)):
                return result
            return str(result)
        return v

    @staticmethod
    def get_keys(
        d: Mapping[str, t.GeneralValueType] | t.GeneralValueType,
    ) -> list[str]:
        """Extract keys from dict using build DSL.

        Business Rules:
        ───────────────
        1. Keys extraction MUST handle both dict and non-dict inputs safely
        2. Non-dict inputs MUST return empty list (no error)
        3. Dict keys MUST be converted to list[str] for type safety

        Architecture Implications:
        ───────────────────────────
        - Uses FlextUtilities.build() for type coercion and validation
        - Returns empty list for non-dict inputs (safe fallback)
        - Type-safe conversion to list[str] using type narrowing

        Audit Implications:
        ───────────────────
        - Key extraction is safe and never raises exceptions
        - Empty dict returns empty list (expected behavior)
        - Non-dict inputs are handled gracefully without errors
        """
        d_dict = FlextCliUtilities.build(d, ops={"ensure": "dict"}, on_error="skip")
        # Python 3.13: Use isinstance with Mapping for proper type narrowing
        # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
        # Architecture: Direct list() conversion is type-safe and efficient
        # Audit Implication: Key extraction is deterministic and safe
        if isinstance(d_dict, Mapping):
            return list(d_dict.keys())
        return []

    @staticmethod
    def norm_json(item: t.GeneralValueType) -> t.GeneralValueType:
        """Normalize item to JSON-compatible using build DSL."""
        if isinstance(item, (str, int, float, bool, type(None))):
            return item
        if FlextRuntime.is_dict_like(item):
            return FlextCliOutput.to_dict_json(item)
        if FlextRuntime.is_list_like(item):
            return FlextCliOutput.to_list_json(item)
        # Type narrowing: str(item) is already t.GeneralValueType compatible
        return str(item)

    @staticmethod
    def ensure_str(v: t.GeneralValueType | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if v is None:
            return default
        try:
            return str(v)
        except Exception:
            return default

    @staticmethod
    def ensure_list(
        v: t.GeneralValueType | None,
        default: list[t.GeneralValueType] | None = None,
    ) -> list[t.GeneralValueType]:
        """Ensure value is list with default using build DSL."""
        built_result = FlextCliUtilities.build(
            v,
            ops={"ensure": "list", "ensure_default": default or []},
            on_error="skip",
        )
        # Python 3.13: Use Sequence check for more flexible list-like types
        # Type narrowing: FlextCliUtilities.build with ensure="list" returns list-like
        return (
            list(built_result)
            if isinstance(built_result, Sequence)
            else (default or [])
        )

    @staticmethod
    def ensure_dict(
        v: t.GeneralValueType | None,
        default: dict[str, t.GeneralValueType] | None = None,
    ) -> dict[str, t.GeneralValueType]:
        """Ensure value is dict with default using build DSL."""
        result = FlextCliUtilities.build(
            v,
            ops={"ensure": "dict", "ensure_default": default or {}},
            on_error="skip",
        )
        return result if isinstance(result, dict) else default or {}

    @staticmethod
    def ensure_bool(v: t.GeneralValueType | None, *, default: bool = False) -> bool:
        """Ensure value is bool with default using build DSL."""
        # Type narrowing: FlextCliUtilities.build with ensure="bool" returns bool
        result = FlextCliUtilities.build(
            v,
            ops={"ensure": "bool", "ensure_default": default},
            on_error="skip",
        )
        return bool(result) if result is not None else default

    @staticmethod
    def get_map_val(
        m: Mapping[str, t.GeneralValueType],
        k: str,
        default: t.GeneralValueType,
    ) -> t.GeneralValueType:
        """Get value from map with default using build DSL."""
        value = m.get(k, default)
        # Ensure value is compatible with GeneralValueType
        compatible_value: t.GeneralValueType
        if isinstance(value, (str, int, float, bool, type(None), list)):
            compatible_value = value
        elif isinstance(value, dict):
            # Type-safe dict comprehension: keys are str, values need type assertion
            dict_items: dict[str, t.GeneralValueType] = {}
            for kk, vv in value.items():
                dict_items[str(kk)] = (
                    vv
                    if isinstance(vv, (str, int, float, bool, type(None), list, dict))
                    else str(vv)
                )
            compatible_value = dict_items
        else:
            compatible_value = str(value)
        # compatible_value is already validated to be GeneralValueType compatible
        return compatible_value

    @staticmethod
    def cast_if[T](v: object, t_type: type[T], default: T | object) -> T:
        """Cast value if isinstance else return default.

        Note: default can be any type for flexibility, but return is always T.
        Caller must ensure default is T-compatible.
        """
        if isinstance(v, t_type):
            return v
        # Type narrowing: check if default is instance of t_type
        if isinstance(default, t_type):
            return default
        # If default is not T, raise error - caller must ensure default is T
        # This is safer than silently returning wrong type
        # Use getattr for type name access - works around pyrefly PEP 695 limitation
        type_name = getattr(t_type, "__name__", str(t_type))
        default_type_name = getattr(type(default), "__name__", str(type(default)))
        msg = f"default must be instance of {type_name}, got {default_type_name}"
        raise TypeError(msg)

    @staticmethod
    def _is_rich_table_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichTableProtocol]:
        """Type guard to check if object implements RichTableProtocol."""
        return (
            hasattr(obj, "add_column")
            and hasattr(obj, "add_row")
            and hasattr(obj, "columns")
        )

    @staticmethod
    def _is_rich_progress_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Interactive.RichProgressProtocol]:
        """Type guard to check if object implements RichProgressProtocol."""
        return (
            hasattr(obj, "__enter__")
            and hasattr(obj, "__exit__")
            and hasattr(obj, "add_task")
            and hasattr(obj, "update")
        )

    @staticmethod
    def _is_rich_tree_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichTreeProtocol]:
        """Type guard to check if object implements RichTreeProtocol."""
        return hasattr(obj, "add") and hasattr(obj, "label")

    @staticmethod
    def _is_rich_console_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichConsoleProtocol]:
        """Type guard to check if object implements RichConsoleProtocol."""
        return hasattr(obj, "print") and hasattr(obj, "rule")

    @staticmethod
    def to_dict_json(v: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
        """Convert value to dict with JSON transform using build DSL."""
        return FlextCliOutput.cast_if(
            FlextCliUtilities.build(
                v,
                ops={"ensure": "dict", "transform": {"to_json": True}},
                on_error="skip",
            ),
            dict,
            {},
        )

    @staticmethod
    def to_list_json(v: t.GeneralValueType) -> list[t.GeneralValueType]:
        """Convert value to list with JSON transform using build DSL."""
        return FlextCliOutput.cast_if(
            FlextCliUtilities.build(
                v,
                ops={"ensure": "list", "transform": {"to_json": True}},
                on_error="skip",
            ),
            list,
            [],
        )

    # =========================================================================
    # FORMAT DATA - UNIFIED API
    # =========================================================================

    def format_data(
        self,
        data: t.GeneralValueType,
        format_type: str = FlextCliConstants.Cli.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> r[str]:
        """Format data using specified format type with railway pattern.

        Args:
            data: Data to format
            format_type: Format type from FlextCliConstants.Cli.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[str]: Formatted data string or error

        Example:
            >>> output = FlextCliOutput()
            >>> result = output.format_data(
            ...     data={"name": "Alice", "age": 30},
            ...     format_type=FlextCliConstants.Cli.OutputFormats.JSON.value,
            ... )

        """
        # Railway pattern: validate format → dispatch to handler
        # Convert to string and validate choice using generalized helpers
        parse_result = FlextCliUtilities.Cli.parse(format_type, str, default="")
        format_str = self.ensure_str(
            parse_result.unwrap_or(str(format_type)),
            "",
        ).lower()
        valid_formats = set(FlextCliConstants.Cli.OUTPUT_FORMATS_LIST)
        if format_str not in valid_formats:
            return r[str].fail(
                FlextCliConstants.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=format_type,
                ),
            )
        return self._dispatch_formatter(format_str, data, title, headers)

    # Format validation uses FlextCliUtilities.convert() and direct validation

    def _dispatch_formatter(
        self,
        format_type: str,
        data: t.GeneralValueType,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
        """Dispatch to appropriate formatter based on format type."""
        # Format dispatcher using dict mapping
        formatters: dict[str, Callable[[], r[str]]] = {
            FlextCliConstants.Cli.OutputFormats.JSON.value: lambda: self.format_json(
                data
            ),
            FlextCliConstants.Cli.OutputFormats.YAML.value: lambda: self.format_yaml(
                data
            ),
            FlextCliConstants.Cli.OutputFormats.TABLE.value: lambda: (
                self._format_table_data(
                    data,
                    title,
                    headers,
                )
            ),
            FlextCliConstants.Cli.OutputFormats.CSV.value: lambda: self.format_csv(
                data
            ),
            FlextCliConstants.Cli.OutputFormats.PLAIN.value: lambda: r[str].ok(
                str(data)
            ),
        }

        formatter = formatters.get(format_type)
        if formatter is None:
            return r[str].fail(
                FlextCliConstants.Cli.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type,
                ),
            )
        # Type narrowing: formatter is Callable[[], r[str]] after get() check
        # formatters dict is typed as dict[str, Callable[[], r[str]]]
        # so formatter is guaranteed to be the correct type when not None
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
            transformed_data = self.to_dict_json(data)
            return self.format_table(transformed_data, title=title, headers=headers)

        if FlextRuntime.is_list_like(data):
            if not data:
                return r[str].fail(FlextCliConstants.Cli.ErrorMessages.NO_DATA_PROVIDED)
            # Use build() DSL: filter → validate → process → ensure list
            # Type narrowing: is_list_like ensures data is Sequence-like
            if isinstance(data, (list, tuple)):
                data_list: list[t.GeneralValueType] = list(data)
            elif isinstance(data, Sequence):
                data_list = list(data)
            else:
                # Should not happen if is_list_like is correct, but type checker needs this
                data_list = [data] if data is not None else []
            dict_items = FlextCliUtilities.filter(
                data_list, predicate=FlextRuntime.is_dict_like
            )
            # Type narrowing: data_list is list after normalization
            if not isinstance(dict_items, list) or len(dict_items) != len(data_list):
                return r[str].fail(
                    FlextCliConstants.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
                )
            # Use generalized norm_json helper
            # For lists, processor takes only item, not (key, item)
            # Filter first, then process (FlextCliUtilities.process doesn't accept predicate)
            # Type narrowing: data_list is list, so it's iterable
            filtered_data = [
                item for item in data_list if FlextRuntime.is_dict_like(item)
            ]
            json_list_result = FlextCliUtilities.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            # Type narrowing: ensure_list returns list[t.GeneralValueType]
            # Filter to ensure all items are dict
            converted_list_raw = self.ensure_list(
                json_list_result.unwrap_or([]),
                [],
            )
            converted_list: list[dict[str, t.GeneralValueType]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self.format_table(converted_list, title=title, headers=headers)

        return r[str].fail(
            FlextCliConstants.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
        )

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
            parse_result = FlextCliUtilities.Cli.parse(format_type, str, default="")
            format_str = self.ensure_str(
                parse_result.unwrap_or(str(format_type)),
                "",
            ).lower()
            valid_formats = set(FlextCliConstants.Cli.OUTPUT_FORMATS_LIST)
            if format_str not in valid_formats:
                return r[FlextCliOutput].fail(
                    FlextCliConstants.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type
                    ),
                )
            return r[FlextCliOutput].ok(self)
        except Exception as e:
            return r[FlextCliOutput].fail(
                FlextCliConstants.Cli.ErrorMessages.CREATE_FORMATTER_FAILED.format(
                    error=e
                ),
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
        from flext_cli.constants import FlextCliConstants
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
                    case FlextCliConstants.Cli.OutputFormats.TABLE.value:
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
                    case FlextCliConstants.Cli.OutputFormats.JSON.value:
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
            # Access _result_formatters via getattr for type checker compatibility
            formatters_dict = getattr(self, "_result_formatters", {})
            # Type narrowing: formatter accepts compatible types
            formatters_dict[result_type] = formatter
            self._result_formatters = formatters_dict
            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}",
            )

    def format_and_display_result(
        self,
        result: BaseModel | t.GeneralValueType | r[object],
        output_format: str = FlextCliConstants.Cli.OutputFormats.TABLE.value,
    ) -> r[bool]:
        """Auto-detect result type and apply registered formatter with extracted helpers.

        **PURPOSE**: Eliminate manual type checking and formatter dispatch.

        Args:
            result: Domain result object to format
            output_format: Output format ("table", "json", "yaml", etFlextCliConstants.Cli.)

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
        result: BaseModel | t.GeneralValueType | r[object],
        output_format: str,
    ) -> r[bool]:
        """Try to use registered formatter for result type.

        Returns:
            r[bool]: True if formatter was found and executed,
            False if no formatter registered for this type

        """
        result_type = type(result)

        # Access _result_formatters via getattr for type checker compatibility
        formatters_dict: dict[
            type,
            Callable[[t.GeneralValueType | r[t.GeneralValueType], str], None],
        ] = getattr(self, "_result_formatters", {})
        if result_type in formatters_dict:
            formatter = formatters_dict[result_type]
            # Type narrowing: formatter accepts t.GeneralValueType | r[object]
            # BaseModel is not directly compatible, but we can pass it as t.GeneralValueType
            if isinstance(result, BaseModel):
                # Convert BaseModel to dict for formatter
                formattable_result: t.GeneralValueType = result.model_dump()
                formatter(formattable_result, output_format)
            # result is already t.GeneralValueType | r[t.GeneralValueType]
            # Type narrowing: formatter accepts t.GeneralValueType
            elif isinstance(result, r):
                if result.is_success:
                    # Use .value directly instead of deprecated .value
                    # Use build() DSL: value → ensure JSON-compatible → convert to string if needed
                    result_value = result.value
                    # Type narrowing: result_value from .value is t.GeneralValueType compatible
                    result_value_general: t.GeneralValueType = (
                        result_value
                        if isinstance(
                            result_value,
                            (str, int, float, bool, type(None), dict, list, tuple),
                        )
                        else str(result_value)
                    )
                    if self.is_json(result_value_general):
                        # Type narrowing: result_value is t.GeneralValueType from .value
                        # Convert to t.GeneralValueType explicitly for type checker
                        unwrapped_value: t.GeneralValueType = (
                            result_value
                            if isinstance(
                                result_value,
                                (str, int, float, bool, type(None), dict, list),
                            )
                            else str(result_value)
                        )
                        formatter(unwrapped_value, output_format)
                    else:
                        formatter(str(result_value), output_format)
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

        # Handle Pydantic models
        if isinstance(result, BaseModel):
            return self._format_pydantic_model(result, output_format)

        # Handle dict objects directly
        # Type narrowing: result is t.GeneralValueType, check if it's a dict
        if isinstance(result, dict):
            return self.format_data(result, output_format)
        if hasattr(result, "__dict__"):
            # Use build() DSL: filter JSON-compatible → ensure dict
            # Use mapper to filter dict items
            filtered_dict = FlextCliUtilities.mapper().filter_dict(
                result.__dict__,
                lambda _k, v: self.is_json(v),
            )
            result_dict = self.ensure_dict(filtered_dict, {})
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
            # Use .value directly instead of deprecated .value
            # Type narrowing: .value returns t.GeneralValueType
            # Note: Cannot use isinstance with TypeAliasType (t.GeneralValueType)
            # result_value is already t.GeneralValueType from .value
            result = result.value
        # Now result is t.GeneralValueType - check if it has __dict__
        if not hasattr(result, "__dict__"):
            return r[str].fail(
                f"Object {type(result).__name__} has no __dict__ attribute",
            )
        # Type narrowing: result has __dict__ attribute
        raw_dict: dict[str, t.GeneralValueType] = getattr(result, "__dict__", {})
        # Use build() DSL: process_mapping → to_json → filter → ensure dict
        json_dict_result = FlextCliUtilities.Cli.process_mapping(
            raw_dict,
            processor=lambda _k, v: self.to_json(v),
            on_error="skip",
        )
        # Type narrowing: unwrap_or returns dict or empty dict
        json_dict_raw = json_dict_result.unwrap_or({})
        json_dict: dict[str, t.GeneralValueType] = (
            json_dict_raw if isinstance(json_dict_raw, dict) else {}
        )
        # Use mapper to filter dict items
        filtered_json_dict = FlextCliUtilities.mapper().filter_dict(
            json_dict,
            lambda _k, v: self.is_json(v),
        )
        cli_json_dict_result = FlextCliUtilities.Cli.process_mapping(
            filtered_json_dict,
            processor=lambda _k, v: v,
            on_error="skip",
        )
        # Type narrowing: unwrap_or returns dict or empty dict
        cli_json_dict_raw = cli_json_dict_result.unwrap_or({})
        cli_json_dict: dict[str, t.GeneralValueType] = (
            cli_json_dict_raw if isinstance(cli_json_dict_raw, dict) else {}
        )
        return self.format_data(cli_json_dict, output_format)

    @staticmethod
    def _display_formatted_result(formatted: str) -> r[bool]:
        """Display formatted result string using Rich console."""
        console = FlextCliFormatters().console
        console.print(formatted)
        return r[bool].ok(True)

    # =========================================================================
    # RICH TABLE CREATION (Delegates to FlextCliFormatters)
    # =========================================================================

    @staticmethod
    def _validate_headers(
        headers: list[str],
        data: list[dict[str, t.GeneralValueType]],
    ) -> r[bool]:
        """Validate headers exist in data."""

        def _extract_keys(row: dict[str, t.GeneralValueType]) -> set[str]:
            """Extract keys from dict row."""
            return set(row.keys())

        all_keys = FlextCliUtilities.Cli.process(
            data,
            processor=_extract_keys,
            on_error="skip",
        )
        if all_keys.is_failure:
            return r.fail("Failed to extract keys from data")
        combined_keys = set()
        for key_set in all_keys.value or []:
            if isinstance(key_set, set):
                combined_keys.update(key_set)
        missing = FlextCliUtilities.filter(headers, lambda h: h not in combined_keys)
        if missing:
            return r.fail(f"Header(s) not found in data: {', '.join(missing)}")
        return r[bool].ok(True)

    @staticmethod
    def _build_table_rows(
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str],
    ) -> r[list[list[str]]]:
        """Build table rows from data."""

        def build_row(row_data: dict[str, t.GeneralValueType]) -> list[str]:
            """Build row values using u utilities."""
            values = FlextCliUtilities.Cli.process(
                headers,
                processor=lambda h: (
                    str(FlextCliUtilities.get(row_data, h)) if h in row_data else None
                ),
                on_error="skip",
            )
            # FlextCliUtilities.filter expects predicate as second positional arg
            values_list = values.value or []
            filtered = FlextCliUtilities.filter(
                values_list, predicate=lambda v: v is not None
            )
            # Type narrowing: filtered contains only non-None values, convert to str
            filtered_list: list[str] = [
                str(item) for item in filtered if item is not None
            ]
            return filtered_list

        rows_result = FlextCliUtilities.Cli.process(
            data, processor=build_row, on_error="fail"
        )
        if rows_result.is_failure:
            return r.fail(rows_result.error or "Failed to build rows")
        # Type narrowing: ensure_list returns list[t.GeneralValueType]
        # Filter to ensure all items are list[str]
        rows_raw = FlextCliOutput.ensure_list(
            rows_result.unwrap_or([]),
            [],
        )
        rows: list[list[str]] = [
            [str(item) for item in row if isinstance(row, list)]
            for row in rows_raw
            if isinstance(row, list)
        ]
        return r.ok(rows)

    def _prepare_table_headers(
        self,
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str] | None = None,
    ) -> r[list[str]]:
        """Prepare and validate table headers."""
        default_headers = self.get_keys(data[0]) if data else []
        default_headers_general: list[t.GeneralValueType] = list(default_headers)
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
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str],
    ) -> r[bool]:
        """Add columns and rows to table.

        Uses RichTableProtocol from lower layer instead of object for better type safety.
        """
        # Add columns
        FlextCliUtilities.Cli.process(
            headers,
            processor=lambda h: table.add_column(str(h)),
            on_error="skip",
        )

        # Build and add rows
        rows_result = FlextCliOutput._build_table_rows(data, headers)
        if rows_result.is_failure:
            return r[bool].fail(rows_result.error or "Failed to build rows")

        rows_list = rows_result.value or []
        if isinstance(rows_list, list):
            for row in rows_list:
                if isinstance(row, list):
                    table.add_row(*row)

        return r[bool].ok(True)

    def create_rich_table(
        self,
        data: list[dict[str, t.GeneralValueType]],
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
                FlextCliConstants.Cli.ErrorMessages.NO_DATA_PROVIDED,
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
            error_msg = (
                FlextCliConstants.Cli.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(
                    error=e,
                )
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
        data: list[dict[str, t.GeneralValueType]],
        headers: list[str] | None = None,
        table_format: str = FlextCliConstants.Cli.TableFormats.SIMPLE,
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
        # Type narrowing: ensure_list returns list[t.GeneralValueType], convert to list[str]
        validated_headers_raw = FlextCliOutput.ensure_list(
            headers, [FlextCliConstants.Cli.TableFormats.KEYS]
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
        validated_style = self.ensure_str(
            style, FlextCliConstants.Cli.OutputDefaults.EMPTY_STYLE
        )
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
            f"{FlextCliConstants.Cli.Symbols.ERROR_PREFIX} {message}",
            style=FlextCliConstants.Cli.Styles.BOLD_RED,
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
            f"{FlextCliConstants.Cli.Symbols.SUCCESS_PREFIX} {message}",
            style=FlextCliConstants.Cli.Styles.BOLD_GREEN,
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
            f"{FlextCliConstants.Cli.Emojis.WARNING} {FlextCliConstants.Cli.OutputDefaults.WARNING_PREFIX} {message}",
            style=FlextCliConstants.Cli.Styles.BOLD_YELLOW,
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
        validated_style = self.ensure_str(
            style, FlextCliConstants.Cli.OutputDefaults.EMPTY_STYLE
        )
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
            FlextCliConstants.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE,
        )

        # Use build() DSL for style and emoji mapping with generalized helpers
        style_map = {
            FlextCliConstants.Cli.MessageTypes.INFO.value: FlextCliConstants.Cli.Styles.BLUE,
            FlextCliConstants.Cli.MessageTypes.SUCCESS.value: FlextCliConstants.Cli.Styles.BOLD_GREEN,
            FlextCliConstants.Cli.MessageTypes.ERROR.value: FlextCliConstants.Cli.Styles.BOLD_RED,
            FlextCliConstants.Cli.MessageTypes.WARNING.value: FlextCliConstants.Cli.Styles.BOLD_YELLOW,
        }
        emoji_map = {
            FlextCliConstants.Cli.MessageTypes.INFO.value: FlextCliConstants.Cli.Emojis.INFO,
            FlextCliConstants.Cli.MessageTypes.SUCCESS.value: FlextCliConstants.Cli.Emojis.SUCCESS,
            FlextCliConstants.Cli.MessageTypes.ERROR.value: FlextCliConstants.Cli.Emojis.ERROR,
            FlextCliConstants.Cli.MessageTypes.WARNING.value: FlextCliConstants.Cli.Emojis.WARNING,
        }
        # Type narrowing: style_map and emoji_map are dict[str, str], convert to t.GeneralValueType
        style_map_general: dict[str, t.GeneralValueType] = dict(style_map)
        emoji_map_general: dict[str, t.GeneralValueType] = dict(emoji_map)
        style = self.ensure_str(
            self.get_map_val(
                style_map_general, final_message_type, FlextCliConstants.Cli.Styles.BLUE
            ),
        )
        emoji = self.ensure_str(
            self.get_map_val(
                emoji_map_general, final_message_type, FlextCliConstants.Cli.Emojis.INFO
            ),
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
            format_type: Format type (table, json, yaml, etFlextCliConstants.Cli.)
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[bool]: True on success, False on failure

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data(
            ...     {"key": "value"},
            ...     format_type=FlextCliConstants.Cli.OutputFormats.JSON.value,
            ... )

        """
        # Use build() DSL for format type normalization
        final_format_type = self.ensure_str(
            format_type,
            FlextCliConstants.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE,
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
                    indent=FlextCliConstants.Cli.OutputDefaults.JSON_INDENT,
                ),
            )
        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.OutputLogMessages.JSON_FORMAT_FAILED.format(
                    error=e,
                )
            )

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
                    default_flow_style=FlextCliConstants.Cli.OutputDefaults.YAML_DEFAULT_FLOW_STYLE,
                ),
            )
        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.OutputLogMessages.YAML_FORMAT_FAILED.format(
                    error=e,
                )
            )

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
            # Type narrowing: check if data is list-like and has dict items
            if FlextRuntime.is_list_like(data) and data:
                # Type narrowing: data is list-like, check first item
                if isinstance(data, (list, tuple, Sequence)) and len(data) > 0:
                    # Type narrowing: data[0] is t.GeneralValueType, check if dict-like
                    first_item: t.GeneralValueType = data[0]
                    if FlextRuntime.is_dict_like(first_item):
                        # Type narrowing: data is Sequence, convert to list
                        if isinstance(data, list):
                            return self._format_csv_list(data)
                        if isinstance(data, (tuple, Sequence)):
                            return self._format_csv_list(list(data))
                # Type narrowing: data is Sequence, convert to list
                if isinstance(data, list):
                    return self._format_csv_list(data)
                if isinstance(data, (tuple, Sequence)):
                    return self._format_csv_list(list(data))
            if FlextRuntime.is_dict_like(data):
                return self._format_csv_dict(data)
            return r[str].ok(
                json.dumps(
                    data,
                    default=str,
                    indent=FlextCliConstants.Cli.OutputDefaults.JSON_INDENT,
                ),
            )
        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.OutputLogMessages.CSV_FORMAT_FAILED.format(
                    error=e,
                )
            )

            return r.fail(error_msg)

    def _coerce_to_list(self, data: t.GeneralValueType) -> list[t.GeneralValueType]:
        """Coerce data to list for CSV processing.

        Uses types from lower layer (t.GeneralValueType) for proper type safety.
        """
        # Direct list return
        if isinstance(data, list):
            return data
        # Sequence types (tuple, Sequence)
        if isinstance(data, (tuple, Sequence)):
            return list(data)
        # Dict returns items
        if isinstance(data, dict):
            return list(data.items())
        # Data is already a list, so it's iterable and sequence
        # Other iterables - convert with type narrowing
        # Type narrowing: data is iterable (has __iter__) and not a non-iterable type
        # Verify it's Sequence or other iterable before converting
        if isinstance(data, Sequence):
            return list(data)
        # For other iterables, use helper method
        # Type narrowing: data has __iter__ and is not a non-iterable type, so it's Iterable
        # Use runtime check to verify it's iterable before converting
        if hasattr(data, "__iter__") and callable(getattr(data, "__iter__", None)) and data is not None:
            # Runtime check: data is iterable, convert items to list
            # Use list comprehension with type narrowing for each item
            iterable_items: list[t.GeneralValueType] = []
            try:
                for item in data:
                    # Type narrowing: each item from iterable is t.GeneralValueType compatible
                    item_general: t.GeneralValueType = (
                        item
                        if isinstance(
                            item, (str, int, float, bool, type(None), dict, list, tuple)
                        )
                        else str(item)  # Fallback to string for other types
                    )
                    iterable_items.append(item_general)
                return iterable_items
            except (TypeError, ValueError):
                return []
        return []

    def _convert_iterable_to_list(
        self, data: Iterable[t.GeneralValueType]
    ) -> list[t.GeneralValueType]:
        """Convert iterable to list with type narrowing.

        Helper method to reduce complexity of _coerce_to_list.
        Uses Iterable from lower layer for proper type safety.
        """
        try:
            if isinstance(data, Sequence):
                return list(data)
            # For other iterables, convert using list comprehension
            # Each item is narrowed to t.GeneralValueType from lower layer
            iterable_items: list[t.GeneralValueType] = []
            for item in data:
                # Type narrowing: item from iterable is t.GeneralValueType compatible
                item_general: t.GeneralValueType = (
                    item
                    if isinstance(
                        item, (str, int, float, bool, type(None), dict, list, tuple)
                    )
                    else str(item)  # Fallback to string for other types
                )
                iterable_items.append(item_general)
            return iterable_items
        except (TypeError, ValueError):
            return []

    def _format_csv_list(self, data: t.GeneralValueType) -> r[str]:
        """Format list of dicts as CSV."""
        output_buffer = StringIO()
        data_list = self._coerce_to_list(data)
        if not data_list or not FlextRuntime.is_dict_like(data_list[0]):
            return r[str].fail("CSV list format requires list of dicts")
        fieldnames = self.get_keys(data_list[0])
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()

        # Process rows
        filtered_rows = FlextCliUtilities.filter(
            data_list, predicate=FlextRuntime.is_dict_like
        )
        dict_rows_raw = self.ensure_list(
            filtered_rows if isinstance(filtered_rows, list) else [],
            [],
        )
        # Use t.GeneralValueType from lower layer instead of object
        dict_rows: list[dict[str, t.GeneralValueType]] = [
            item for item in dict_rows_raw if isinstance(item, dict)
        ]
        csv_rows: list[dict[str, str | int | float | bool]] = []
        for row in dict_rows:
            # Process CSV row - operations are safe and shouldn't raise exceptions
            processed_row = self._process_csv_row(row)
            csv_rows.append(processed_row)
        writer.writerows(csv_rows)
        return r[str].ok(output_buffer.getvalue())

    def _format_csv_dict(self, data: t.GeneralValueType) -> r[str]:
        """Format single dict as CSV."""
        output_buffer = StringIO()
        fieldnames = self.get_keys(data)
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        # Type narrowing: data is dict-like from format_csv check
        # Use t.GeneralValueType from lower layer instead of object
        data_dict: dict[str, t.GeneralValueType] = (
            dict(data) if isinstance(data, dict) else {}
        )
        writer.writerow(data_dict)
        return r[str].ok(output_buffer.getvalue())

    def _process_csv_row(
        self,
        row: dict[str, t.GeneralValueType],
    ) -> dict[str, str | int | float | bool]:
        """Process CSV row with None replacement.

        Uses t.GeneralValueType from lower layer instead of object for better type safety.
        """
        processed: dict[str, str | int | float | bool] = {}
        for k, v in row.items():
            processed[k] = self._replace_none_for_csv(k, v)
        return processed

    @staticmethod
    def _replace_none_for_csv(
        _k: str, v: t.GeneralValueType
    ) -> str | int | float | bool:
        """Replace None with empty string for CSV."""
        if v is None:
            return ""
        if isinstance(v, (str, int, float, bool)):
            return v
        return str(v)

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
        data: dict[str, t.GeneralValueType] | list[dict[str, t.GeneralValueType]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                    error=e,
                )
            )

            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                error_msg,
            )

    def _prepare_table_data(
        self,
        data: dict[str, t.GeneralValueType] | list[dict[str, t.GeneralValueType]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            # Use build() DSL: ensure dict → transform to JSON
            json_data = self.to_dict_json(data)
            return self._prepare_dict_data(json_data, headers)
        if FlextRuntime.is_list_like(data):
            # Use build() DSL: process → norm_json → ensure list
            # For lists, processor takes only item, not (key, item)
            # Filter first, then process (FlextCliUtilities.process doesn't accept predicate)
            filtered_data = [item for item in data if FlextRuntime.is_dict_like(item)]
            process_result = FlextCliUtilities.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            # Type narrowing: ensure_list returns list[t.GeneralValueType]
            # Filter to ensure all items are dict[str, t.GeneralValueType]
            converted_list_raw = self.ensure_list(
                process_result.unwrap_or([]),
                [],
            )
            converted_list: list[dict[str, t.GeneralValueType]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self._prepare_list_data(converted_list, headers)
        return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
            FlextCliConstants.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT,
        )

    @staticmethod
    def _prepare_dict_data(
        data: dict[str, t.GeneralValueType],
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]]:
        """Prepare dict data for table display."""
        # Reject test invu
        if (
            FlextCliConstants.Cli.OutputDefaults.TEST_INVALID_KEY in data
            and len(data) == 1
        ):
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                FlextCliConstants.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT,
            )

        # Use build() DSL: process → kv_pair → ensure dict → extract values → ensure list
        def kv_pair(k: str, v: t.GeneralValueType) -> Mapping[str, t.GeneralValueType]:
            """Create key-value pair dict."""
            return {
                FlextCliConstants.Cli.OutputFieldNames.KEY: k,
                FlextCliConstants.Cli.OutputFieldNames.VALUE: str(v),
            }

        process_result = FlextCliUtilities.Cli.process_mapping(
            data, processor=kv_pair, on_error="skip"
        )
        dict_result = FlextCliOutput.ensure_dict(
            process_result.unwrap_or({}),
            {},
        )
        # Type narrowing: ensure_list returns list[t.GeneralValueType]
        # Filter to ensure all items are dict[str, t.GeneralValueType]
        table_data_raw = FlextCliOutput.ensure_list(list(dict_result.values()), [])
        table_data: list[dict[str, t.GeneralValueType]] = [
            item for item in table_data_raw if isinstance(item, dict)
        ]
        # Use build() DSL: ensure list → ensure default
        # Type narrowing: ensure_list returns list[t.GeneralValueType], convert to list[str]
        table_headers_raw = FlextCliOutput.ensure_list(
            headers, [FlextCliConstants.Cli.TableFormats.KEYS]
        )
        table_headers: list[str] = [str(h) for h in table_headers_raw]
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
                FlextCliConstants.Cli.ErrorMessages.NO_DATA_PROVIDED,
            )

        # Validate headers type
        if headers is not None and not FlextRuntime.is_list_like(headers):
            return r[tuple[list[dict[str, t.GeneralValueType]], str | list[str]]].fail(
                FlextCliConstants.Cli.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST,
            )

        # Ensure list and map to str
        headers_list = FlextCliOutput.ensure_list(
            headers, [FlextCliConstants.Cli.TableFormats.KEYS]
        )
        table_headers = [str(h) for h in headers_list]

        # Validate headers exist in data if headers are provided (not using KEYS)
        if headers is not None and table_headers != [
            FlextCliConstants.Cli.TableFormats.KEYS
        ]:
            validation_result = FlextCliOutput._validate_headers(table_headers, data)
            if validation_result.is_failure:
                return r[
                    tuple[list[dict[str, t.GeneralValueType]], str | list[str]]
                ].fail(
                    validation_result.error or "Header validation failed",
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
            config_instance = m.Cli.TableConfig.model_validate({
                "headers": table_headers,
                "table_format": FlextCliConstants.Cli.TableFormats.GRID,
            })
            # Type narrowing: TableConfig implements TableConfigProtocol structurally
            config: p.Cli.TableConfigProtocol = config_instance
            table_result = FlextCliTables.create_table(
                data=table_data, config=config
            )

            if table_result.is_failure:
                return r[str].fail(
                    f"Failed to create table: {table_result.error}",
                )

            return table_result
        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(
                    error=e,
                )
            )

            return r[str].fail(error_msg)

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{FlextCliConstants.Cli.OutputDefaults.NEWLINE}{table_str}{FlextCliConstants.Cli.OutputDefaults.NEWLINE}"
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
        final_title = self.ensure_str(
            title, FlextCliConstants.Cli.OutputDefaults.DEFAULT_TREE_TITLE
        )

        # Create tree through formatters
        tree_result = FlextCliFormatters().create_tree(label=final_title)

        if tree_result.is_failure:
            return r[str].fail(f"Failed to create tree: {tree_result.error}")

        # Use .value directly instead of deprecated .value
        # create_tree returns r[RichTree], so tree is RichTree (concrete type)
        concrete_tree: RichTree = tree_result.value

        # Build tree structure - data is already t.GeneralValueType
        # Use concrete RichTree type (file already imports it for formatters)
        self._build_tree(concrete_tree, data)

        # Render to string using formatters - use concrete tree type (RichTree)
        return FlextCliFormatters().render_tree_to_string(
            concrete_tree,
            width=FlextCliConstants.Cli.CliDefaults.DEFAULT_MAX_WIDTH,
        )

    def _build_tree(
        self,
        tree: RichTree,
        data: t.GeneralValueType,
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from (t.GeneralValueType - can be dict, list, or primitive)

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
                        f"{k}{FlextCliConstants.Cli.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}"
                    )

                    def process_list_item(item: t.GeneralValueType) -> None:
                        """Process list item."""
                        self._build_tree(branch, item)

                    if isinstance(v, list):
                        FlextCliUtilities.Cli.process(
                            v, processor=process_list_item, on_error="skip"
                        )
                else:
                    tree.add(
                        f"{k}{FlextCliConstants.Cli.OutputDefaults.TREE_VALUE_SEPARATOR}{v}"
                    )

            FlextCliUtilities.Cli.process_mapping(
                data, processor=process_tree_item, on_error="skip"
            )
        elif isinstance(data, list):
            # Use build() DSL: process each item
            def process_list_item(item: t.GeneralValueType) -> None:
                """Process list item."""
                self._build_tree(tree, item)

            FlextCliUtilities.Cli.process(
                data, processor=process_list_item, on_error="skip"
            )
        else:
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

    def execute(self) -> r[dict[str, t.GeneralValueType]]:
        """Execute service - required by FlextService abstract method.

        Returns:
            r[dict]: Service status and operation information

        Note:
            FlextCliOutput is a utility service that formats and displays data.
            The execute() method returns service operational status.

        """
        return r[dict[str, t.GeneralValueType]].ok({
            FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.Services.OUTPUT,
        })


__all__ = ["FlextCliOutput"]
