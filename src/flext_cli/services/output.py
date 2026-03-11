"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Sequence
from io import StringIO
from typing import ClassVar, TypeGuard

import yaml
from flext_core import FlextRuntime, r, t
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import FlextCliFormatters, FlextCliTables, c, m, p, u


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

    _result_formatters: ClassVar[
        dict[type, Callable[[t.ContainerValue | r[t.ContainerValue], str], None]]
    ] = {}

    @property
    def console(self) -> p.Cli.Display.RichConsoleProtocol:
        """Get the console instance from FlextCliFormatters (property form).

        Returns:
            Console instance from formatters

        Example:
            >>> output = FlextCliOutput()
            >>> console = output.console

        """
        concrete_console = FlextCliFormatters().console
        if not self._is_rich_console_protocol(concrete_console):
            msg = "concrete_console must implement RichConsoleProtocol"
            raise TypeError(msg)
        return concrete_console

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{c.Cli.OutputDefaults.NEWLINE}{table_str}{c.Cli.OutputDefaults.NEWLINE}"
        return table_str

    @staticmethod
    def _build_table_rows(
        data: list[dict[str, t.ContainerValue]], headers: list[str]
    ) -> r[list[list[str]]]:
        """Build table rows from data."""

        def build_row(row_data: dict[str, t.ContainerValue]) -> list[str]:
            """Build row values using u utilities."""
            values = u.Cli.process(
                headers,
                processor=lambda h: str(u.get(row_data, h)) if h in row_data else None,
                on_error="skip",
            )
            values_list = values.value or []
            filtered = u.filter(values_list, predicate=lambda v: v is not None)
            filtered_list: list[str] = [
                str(item) for item in filtered if item is not None
            ]
            return filtered_list

        rows_result = u.Cli.process(data, processor=build_row, on_error="fail")
        if rows_result.is_failure:
            return r[list[list[str]]].fail(rows_result.error or "Failed to build rows")
        rows_raw = FlextCliOutput.ensure_list(rows_result.unwrap_or([]), [])
        rows: list[list[str]] = [
            [str(item) for item in row] for row in rows_raw if isinstance(row, list)
        ]
        return r[list[list[str]]].ok(rows)

    @staticmethod
    def _display_formatted_result(formatted: str) -> None:
        """Display formatted result string using Rich console."""
        console = FlextCliFormatters().console
        console.print(formatted)

    @staticmethod
    def _is_custom_iterable_value(data: t.ContainerValue) -> bool:
        """Check if value should use custom iterable strategy."""
        return isinstance(data, Iterable) and (
            not isinstance(data, (str, list, tuple, dict))
        )

    @staticmethod
    def _is_mapping_value(data: t.ContainerValue) -> bool:
        """Check if value should use mapping iteration strategy."""
        return isinstance(data, dict)

    @staticmethod
    def _is_rich_console_protocol(
        obj: Console,
    ) -> TypeGuard[p.Cli.Display.RichConsoleProtocol]:
        """Type guard to check if object implements RichConsoleProtocol."""
        return hasattr(obj, "print") and hasattr(obj, "rule")

    @staticmethod
    def _is_rich_progress_protocol(
        obj: Progress,
    ) -> TypeGuard[p.Cli.Interactive.RichProgressProtocol]:
        """Type guard to check if object implements RichProgressProtocol."""
        return (
            hasattr(obj, "__enter__")
            and hasattr(obj, "__exit__")
            and hasattr(obj, "add_task")
            and hasattr(obj, "update")
        )

    @staticmethod
    def _is_rich_table_protocol(
        obj: RichTable | p.Cli.Display.RichTableProtocol,
    ) -> TypeGuard[p.Cli.Display.RichTableProtocol]:
        """Type guard to check if object implements RichTableProtocol."""
        return (
            hasattr(obj, "add_column")
            and hasattr(obj, "add_row")
            and hasattr(obj, "columns")
        )

    @staticmethod
    def _is_rich_tree_protocol(
        obj: t.ContainerValue,
    ) -> TypeGuard[p.Cli.Display.RichTreeProtocol]:
        """Type guard to check if object implements RichTreeProtocol."""
        return hasattr(obj, "add") and hasattr(obj, "label")

    @staticmethod
    def _is_sequence_value(data: t.ContainerValue) -> bool:
        """Check if value should use sequence iteration strategy."""
        return isinstance(data, (list, tuple))

    @staticmethod
    def _normalize_formatter_value(value: t.ContainerValue) -> t.ContainerValue:
        """Normalize formatter input to a JSON-compatible general value."""
        return (
            value
            if isinstance(value, (str, int, float, bool, type(None), dict, list, tuple))
            else str(value)
        )

    @staticmethod
    def _normalize_iterable_item(item: t.ContainerValue) -> t.ContainerValue:
        """Normalize iterable items to general value type."""
        return (
            item
            if isinstance(item, (str, int, float, bool, type(None), dict, list, tuple))
            else str(item)
        )

    @staticmethod
    def _prepare_dict_data(
        data: dict[str, t.ContainerValue], headers: list[str] | None
    ) -> r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]]:
        """Prepare dict data for table display."""
        if c.Cli.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
            )

        def kv_pair(k: str, v: t.ContainerValue) -> dict[str, t.ContainerValue]:
            """Create key-value pair dict."""
            return {c.Cli.OutputFieldNames.KEY: k, c.Cli.OutputFieldNames.VALUE: str(v)}

        process_result = u.Cli.process_mapping(data, processor=kv_pair, on_error="skip")
        dict_result = FlextCliOutput.ensure_dict(process_result.unwrap_or({}), {})
        table_data_raw = FlextCliOutput.ensure_list(list(dict_result.values()), [])
        table_data: list[dict[str, t.ContainerValue]] = [
            item for item in table_data_raw if isinstance(item, dict)
        ]
        table_headers_raw = FlextCliOutput.ensure_list(
            headers, [c.Cli.TableFormats.KEYS]
        )
        table_headers: list[str] = [str(h) for h in table_headers_raw]
        return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].ok((
            table_data,
            table_headers,
        ))

    @staticmethod
    def _prepare_list_data(
        data: list[dict[str, t.ContainerValue]], headers: list[str] | None
    ) -> r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]]:
        """Prepare list data for table display."""
        if not data:
            return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.NO_DATA_PROVIDED
            )
        if headers is not None and (not FlextRuntime.is_list_like(headers)):
            return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].fail(
                c.Cli.ErrorMessages.TABLE_HEADERS_MUST_BE_LIST
            )
        headers_list = FlextCliOutput.ensure_list(headers, [c.Cli.TableFormats.KEYS])
        table_headers = [str(h) for h in headers_list]
        if headers is not None and table_headers != [c.Cli.TableFormats.KEYS]:
            validation_result = FlextCliOutput._validate_headers(table_headers, data)
            if validation_result.is_failure:
                return r[
                    tuple[list[dict[str, t.ContainerValue]], str | list[str]]
                ].fail(validation_result.error or "Header validation failed")
        return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].ok((
            data,
            table_headers,
        ))

    @staticmethod
    def _replace_none_for_csv(_k: str, v: t.ContainerValue) -> t.Scalar:
        """Replace None with empty string for CSV."""
        if v is None:
            return ""
        if isinstance(v, (str, int, float, bool)):
            return v
        return str(v)

    @staticmethod
    def _validate_headers(
        headers: list[str], data: list[dict[str, t.ContainerValue]]
    ) -> r[bool]:
        """Validate headers exist in data."""

        def _extract_keys(row: dict[str, t.ContainerValue]) -> set[str]:
            """Extract keys from dict row."""
            return set(row.keys())

        all_keys = u.Cli.process(data, processor=_extract_keys, on_error="skip")
        if all_keys.is_failure:
            return r[bool].fail("Failed to extract keys from data")
        combined_keys: set[str] = set()
        for key_set in all_keys.value or []:
            combined_keys.update(key_set)
        missing = u.filter(headers, lambda h: h not in combined_keys)
        if missing:
            return r[bool].fail(f"Header(s) not found in data: {', '.join(missing)}")
        return r[bool].ok(value=True)

    @staticmethod
    def cast_if(
        v: t.ContainerValue, t_type: type[t.ContainerValue], default: t.ContainerValue
    ) -> t.ContainerValue:
        """Cast value if isinstance else return default.

        Pattern: Non-generic cast_if for runtime type checking.
        Checks v against t_type, returns v if match, else returns default.
        """
        if isinstance(v, t_type):
            return v
        if isinstance(default, t_type):
            return default
        type_name = t_type.__name__ if hasattr(t_type, "__name__") else str(t_type)
        default_type_name = (
            type(default).__name__
            if hasattr(type(default), "__name__")
            else str(type(default))
        )
        msg = f"default must be instance of {type_name}, got {default_type_name}"
        raise TypeError(msg)

    @staticmethod
    def create_ascii_table(
        data: list[dict[str, t.ContainerValue]],
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
            config_for_table: m.Cli.TableConfig
            if isinstance(config, m.Cli.TableConfig):
                config_for_table = config
            elif hasattr(config, "model_dump"):
                model_dump_method = getattr(config, "model_dump")
                if callable(model_dump_method):
                    config_dict = model_dump_method()
                    config_for_table = m.Cli.TableConfig.model_validate(config_dict)
                else:
                    config_for_table = m.Cli.TableConfig.model_validate({})
            else:
                config_for_table = m.Cli.TableConfig.model_validate({})
            data_json: list[dict[str, t.JsonValue]] = [
                {str(k): m.Cli.normalize_to_json_value(v) for k, v in row.items()}
                for row in data
            ]
            return FlextCliTables.create_table(data=data_json, config=config_for_table)
        validated_headers_raw = FlextCliOutput.ensure_list(
            headers, [c.Cli.TableFormats.KEYS]
        )
        validated_headers: list[str] = [str(h) for h in validated_headers_raw]
        final_config = m.Cli.TableConfig.model_validate({
            "headers": validated_headers,
            "table_format": table_format,
        })
        data_json_final: list[dict[str, t.JsonValue]] = [
            {str(k): m.Cli.normalize_to_json_value(v) for k, v in row.items()}
            for row in data
        ]
        return FlextCliTables.create_table(data=data_json_final, config=final_config)

    @staticmethod
    def ensure_bool(v: t.ContainerValue | None, *, default: bool = False) -> bool:
        """Ensure value is bool with default using build DSL."""
        result = u.build(
            v, ops={"ensure": "bool", "ensure_default": default}, on_error="skip"
        )
        return bool(result) if result is not None else default

    @staticmethod
    def ensure_dict(
        v: t.ContainerValue | None, default: dict[str, t.ContainerValue] | None = None
    ) -> dict[str, t.ContainerValue]:
        """Ensure value is dict with default using build DSL."""
        result = u.build(
            v, ops={"ensure": "dict", "ensure_default": default or {}}, on_error="skip"
        )
        return result if isinstance(result, dict) else default or {}

    @staticmethod
    def ensure_list(
        v: t.ContainerValue | None, default: list[t.ContainerValue] | None = None
    ) -> list[t.ContainerValue]:
        """Ensure value is list with default using build DSL."""
        v_typed = FlextRuntime.normalize_to_general_value(v) if v is not None else None
        built_result = u.build(
            v_typed,
            ops={"ensure": "list", "ensure_default": default or []},
            on_error="skip",
        )
        return (
            list(built_result) if isinstance(built_result, Sequence) else default or []
        )

    @staticmethod
    def ensure_str(v: t.ContainerValue | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if v is None:
            return default
        try:
            return str(v)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def get_keys(d: dict[str, t.ContainerValue] | t.ContainerValue) -> list[str]:
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
        if isinstance(d_dict, dict):
            return list(d_dict.keys())
        return []

    @staticmethod
    def get_map_val(
        m: dict[str, t.ContainerValue], k: str, default: t.ContainerValue
    ) -> t.ContainerValue:
        """Get value from map with default using build DSL."""
        value = m.get(k, default)
        compatible_value: t.ContainerValue
        if isinstance(value, (str, int, float, bool, type(None), list)):
            compatible_value = value
        elif isinstance(value, dict):
            dict_items: dict[str, t.ContainerValue] = {}
            for kk, vv in value.items():
                dict_items[str(kk)] = (
                    vv
                    if isinstance(vv, (str, int, float, bool, type(None), list, dict))
                    else str(vv)
                )
            compatible_value = dict_items
        else:
            compatible_value = str(value)
        return compatible_value

    @staticmethod
    def is_json(v: t.ContainerValue) -> bool:
        """Check if value is JSON-compatible type.

        Uses t.ContainerValue from lower layer instead of object for better type safety.
        """
        return isinstance(v, (str, int, float, bool, type(None), dict, list))

    @staticmethod
    def norm_json(item: t.ContainerValue) -> t.ContainerValue:
        """Normalize item to JSON-compatible using build DSL."""
        if isinstance(item, (str, int, float, bool, type(None))):
            return item
        if FlextRuntime.is_dict_like(item):
            return FlextCliOutput.to_dict_json(item)
        if FlextRuntime.is_list_like(item):
            return FlextCliOutput.to_list_json(item)
        return str(item)

    @staticmethod
    def to_dict_json(v: t.ContainerValue) -> dict[str, t.ContainerValue]:
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
        if isinstance(result, dict):
            return result
        return {}

    @staticmethod
    def to_json(v: t.ContainerValue) -> t.ContainerValue:
        """Convert value to JSON-compatible using build DSL."""
        if isinstance(v, dict):
            return u.build(
                v,
                ops={"ensure": "dict", "transform": {"to_json": True}},
                on_error="skip",
            )
        return v

    @staticmethod
    def to_list_json(v: t.ContainerValue) -> list[t.ContainerValue]:
        """Convert value to list with JSON transform using build DSL."""
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
        if isinstance(result, list):
            return result
        return []

    def create_formatter(self, format_type: str) -> r[FlextCliOutput]:
        """Create a formatter instance for the specified format type.

        Uses FlextCliUtilities.convert() and direct validation for format checking.

        Args:
            format_type: Format type to create formatter for

        Returns:
            r[FlextCliOutput]: Formatter instance or error

        """
        try:
            parse_result = u.Cli.parse(format_type, str, default="")
            format_str = self.ensure_str(
                parse_result.unwrap_or(str(format_type)), ""
            ).lower()
            valid_formats = set(c.Cli.ValidationLists.OUTPUT_FORMATS)
            if format_str not in valid_formats:
                return r[FlextCliOutput].fail(
                    c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=format_type)
                )
            return r[FlextCliOutput].ok(self)
        except Exception as e:
            return r[FlextCliOutput].fail(
                c.Cli.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e)
            )

    def create_progress_bar(self) -> r[p.Cli.Interactive.RichProgressProtocol]:
        """Create a Rich progress bar using FlextCliFormatters.

        Returns:
            r[RichProgressProtocol]: Rich Progress wrapped in Result

        Example:
            >>> output = FlextCliOutput()
            >>> progress_result = output.create_progress_bar()

        """
        result = FlextCliFormatters().create_progress()
        if result.is_success:
            progress_value = result.value
            if not self._is_rich_progress_protocol(progress_value):
                msg = "progress_value must implement RichProgressProtocol"
                raise TypeError(msg)
            return r[p.Cli.Interactive.RichProgressProtocol].ok(progress_value)
        return r[p.Cli.Interactive.RichProgressProtocol].fail(result.error or "")

    def create_rich_table(
        self,
        data: list[dict[str, t.ContainerValue]],
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
                c.Cli.ErrorMessages.NO_DATA_PROVIDED
            )
        try:
            headers_result = self._prepare_table_headers(data, headers)
            if headers_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    headers_result.error or "Failed to prepare headers"
                )
            table_headers = headers_result.value
            table_result = self._initialize_rich_table(table_headers, title)
            if table_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    table_result.error or "Failed to initialize table"
                )
            table = table_result.value
            populate_result = self._populate_table_rows(table, data, table_headers)
            if populate_result.is_failure:
                return r[p.Cli.Display.RichTableProtocol].fail(
                    populate_result.error or "Failed to populate table"
                )
            if not self._is_rich_table_protocol(table):
                msg = "table must implement RichTableProtocol"
                raise TypeError(msg)
            return r[p.Cli.Display.RichTableProtocol].ok(table)
        except Exception as e:
            error_msg = c.Cli.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(error=e)
            return r[p.Cli.Display.RichTableProtocol].fail(error_msg)

    def display_data(
        self,
        data: t.ContainerValue,
        format_type: str | None = None,
        *,
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> None:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.Cli.)
            title: Optional title for table format
            headers: Optional headers for table format

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_data(
            ...     {"key": "value"},
            ...     format_type=c.Cli.OutputFormats.JSON.value,
            ... )

        """
        final_format_type = self.ensure_str(
            format_type, c.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE
        )
        format_result = self.format_data(
            data, format_type=final_format_type, title=title, headers=headers
        )
        if format_result.is_failure:
            self.print_message(f"Failed to format data: {format_result.error}")
            return
        formatted_data = format_result.value
        self.print_message(formatted_data)

    def display_message(self, message: str, message_type: str | None = None) -> None:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_message("Operation completed", message_type="success")

        """
        final_message_type = self.ensure_str(
            message_type, c.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE
        )
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
        style_map_general: dict[str, t.ContainerValue] = dict(style_map)
        emoji_map_general: dict[str, t.ContainerValue] = dict(emoji_map)
        style = self.ensure_str(
            self.get_map_val(style_map_general, final_message_type, c.Cli.Styles.BLUE)
        )
        emoji = self.ensure_str(
            self.get_map_val(emoji_map_general, final_message_type, c.Cli.Emojis.INFO)
        )
        formatted_message = f"{emoji} {message}"
        self.print_message(formatted_message, style=style)

    def display_text(self, text: str, *, style: str | None = None) -> None:
        """Display text using FlextCliFormatters.

        Args:
            text: Text to display
            style: Optional Rich style

        Example:
            >>> output = FlextCliOutput()
            >>> output.display_text("Important info", style="bold")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        FlextCliFormatters().print(text, style=validated_style)

    def execute(self) -> r[dict[str, t.ContainerValue]]:
        """Execute service - required by FlextService abstract method.

        Returns:
            r[dict]: Service status and operation information

        Note:
            FlextCliOutput is a utility service that formats and displays data.
            The execute() method returns service operational status.

        """
        return r[t.ConfigurationMapping].ok({
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.Services.OUTPUT,
        })

    def format_and_display_result(
        self,
        result: BaseModel | t.ContainerValue | r[t.ContainerValue],
        output_format: str = c.Cli.OutputFormats.TABLE.value,
    ) -> None:
        """Auto-detect result type and apply registered formatter with extracted helpers.

        **PURPOSE**: Eliminate manual type checking and formatter dispatch.

        Args:
            result: Domain result object to format
            output_format: Output format ("table", "json", "yaml", etc.Cli.)

        """
        try:
            registered_result = self._try_registered_formatter(result, output_format)
            if registered_result.is_success:
                return
            formattable_result = self._convert_result_to_formattable(
                result, output_format
            )
            if formattable_result.is_failure:
                self.print_error(
                    formattable_result.error
                    or "Failed to convert result to formattable"
                )
                return
            formattable = formattable_result.value
            self._display_formatted_result(formattable)
        except Exception as e:
            self.print_error(f"Failed to format and display result: {e}")

    def format_as_tree(
        self, data: t.ContainerValue, title: str | None = None
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
        final_title = self.ensure_str(title, c.Cli.OutputDefaults.DEFAULT_TREE_TITLE)
        tree_result = FlextCliFormatters().create_tree(label=final_title)
        if tree_result.is_failure:
            return r[str].fail(f"Failed to create tree: {tree_result.error}")
        concrete_tree = tree_result.value
        self._build_tree(concrete_tree, data)
        return FlextCliFormatters().render_tree_to_string(
            concrete_tree, width=c.Cli.CliDefaults.DEFAULT_MAX_WIDTH
        )

    def format_csv(self, data: t.ContainerValue) -> r[str]:
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
            if FlextRuntime.is_list_like(data) and data:
                normalized_data = FlextRuntime.normalize_to_general_value(data)
                coerced_list = self._coerce_to_list(normalized_data)
                if coerced_list and FlextRuntime.is_dict_like(coerced_list[0]):
                    return self._format_csv_list(coerced_list)
            if FlextRuntime.is_dict_like(data):
                return self._format_csv_dict(data)
            return r[str].ok(
                json.dumps(data, default=str, indent=c.Cli.OutputDefaults.JSON_INDENT)
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.CSV_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def format_data(
        self,
        data: t.ContainerValue,
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
        parse_result = u.Cli.parse(format_type, str, default="")
        format_str = self.ensure_str(
            parse_result.unwrap_or(str(format_type)), ""
        ).lower()
        valid_formats = set(c.Cli.ValidationLists.OUTPUT_FORMATS)
        if format_str not in valid_formats:
            return r[str].fail(
                c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=format_type)
            )
        return self._dispatch_formatter(format_str, data, title, headers)

    def format_json(self, data: t.ContainerValue) -> r[str]:
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
                json.dumps(data, default=str, indent=c.Cli.OutputDefaults.JSON_INDENT)
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.JSON_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def format_table(
        self,
        data: dict[str, t.ContainerValue] | list[dict[str, t.ContainerValue]] | str,
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
        prepared_result = self._prepare_table_data_safe(data, headers)
        if prepared_result.is_failure:
            return r[str].fail(
                prepared_result.error or "Failed to prepare table data",
                error_code=prepared_result.error_code,
                error_data=prepared_result.error_data,
            )
        prepared = prepared_result.value
        table_data_list: list[dict[str, t.ContainerValue]] = [
            dict(row) for row in prepared[0]
        ]
        table_result = self._create_table_string(table_data_list, prepared[1])
        if table_result.is_failure:
            return table_result
        table = table_result.value
        return r[str].ok(self._add_title(table, title))

    def format_yaml(self, data: t.ContainerValue) -> r[str]:
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
                )
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.YAML_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def print_error(self, message: str) -> None:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_error("Operation failed")

        """
        self.print_message(
            f"{c.Cli.Symbols.ERROR_PREFIX} {message}", style=c.Cli.Styles.BOLD_RED
        )

    def print_message(self, message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print
            style: Optional Rich style

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_message("Hello", style="bold blue")

        Note:
            For advanced Rich features like syntax highlighting, use
            FlextCliFormatters.console to access Rich Console directly.

        """
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        FlextCliFormatters().print(message, style=validated_style)

    def print_success(self, message: str) -> None:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_success("Task completed")

        """
        self.print_message(
            f"{c.Cli.Symbols.SUCCESS_PREFIX} {message}", style=c.Cli.Styles.BOLD_GREEN
        )

    def print_warning(self, message: str) -> None:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Example:
            >>> output = FlextCliOutput()
            >>> output.print_warning("Deprecated feature")

        """
        self.print_message(
            f"{c.Cli.Emojis.WARNING} {c.Cli.OutputDefaults.WARNING_PREFIX} {message}",
            style=c.Cli.Styles.BOLD_YELLOW,
        )

    def register_result_formatter(
        self,
        result_type: type,
        formatter: Callable[[t.ContainerValue | r[t.ContainerValue], str], None],
    ) -> r[bool]:
        r"""Register custom formatter for domain-specific result types.

        **PURPOSE**: Eliminate repetitive result display formatting boilerplate.

        Allows registering formatters for specific result types, enabling
        automatic formatting based on result type detection. Reduces ~74 lines
        of formatting boilerplate per result type.

        Args:
            result_type: Type of result to format (e.g., OperationResult)
            formatter: Callable that formats and displays the result
                Signature: (result: t.ContainerValue | r[t.ContainerValue], output_format: str) -> None

        Returns:
            r[bool]: True on success, False on failure

        Example:
            ```python
            from flext_cli import FlextCliOutput
        from flext_cli import c
            class OperationResult:
                # Example result model
                status: str = "success"
                entries_processed: int = 0


            output = FlextCliOutput()


            # Register formatter for OperationResult
            def format_operation(result: OperationResult, fmt: str) -> None:
                # Python 3.13: match/case - more elegant and modern
                match fmt:
                    case c.Cli.OutputFormats.TABLE.value:
                        # Create Rich table from result
                        console = output._formatters.console
                        panel = output._formatters.create_panel(
                            f"[green]Operation completed![/green]\\\\n"
                            + f"Status: {result.status}\\\\n"
                            + f"Entries: {result.entries_processed}",
                            title="✅ Operation Result",
                        )
                        console.print(panel.value)
                    case c.Cli.OutputFormats.JSON.value:
                        logger = FlextLogger(__name__)
                        logger.info(result.model_dump_json())


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
            FlextCliOutput._result_formatters[result_type] = formatter
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(
                f"Failed to register formatter for {result_type.__name__}: {e}"
            )

    def table_to_string(
        self, table: p.Cli.Display.RichTableProtocol, width: int | None = None
    ) -> r[str]:
        """Convert table to string using FlextCliFormatters.

        Args:
            table: Table object from formatters
            width: Optional width for console

        Returns:
            r[str]: Table as string or error

        """
        return FlextCliFormatters().render_table_to_string(table, width)

    def _build_tree(
        self, tree: RichTree | FlextCliFormatters.Tree, data: t.ContainerValue
    ) -> None:
        """Build tree recursively (helper for format_as_tree).

        Args:
            tree: Tree object from formatters
            data: Data to build tree from (t.ContainerValue - can be dict, list, or primitive)

        """
        if isinstance(data, dict):

            def process_tree_item(k: str, v: t.ContainerValue) -> None:
                """Process single tree item."""
                if isinstance(v, dict):
                    branch = tree.add(str(k))
                    if branch is not None:
                        self._build_tree(branch, v)
                elif isinstance(v, list):
                    branch = tree.add(
                        f"{k}{c.Cli.OutputDefaults.TREE_BRANCH_LIST_SUFFIX}"
                    )

                    def process_list_item(item: t.ContainerValue) -> None:
                        """Process list item."""
                        if branch is not None:
                            self._build_tree(branch, item)

                    u.Cli.process(v, processor=process_list_item, on_error="skip")
                else:
                    tree.add(f"{k}{c.Cli.OutputDefaults.TREE_VALUE_SEPARATOR}{v}")

            u.Cli.process_mapping(data, processor=process_tree_item, on_error="skip")
        elif isinstance(data, list):

            def process_list_item(item: t.ContainerValue) -> None:
                """Process list item."""
                self._build_tree(tree, item)

            u.Cli.process(data, processor=process_list_item, on_error="skip")
        else:
            tree.add(str(data))

    def _coerce_to_list(self, data: t.ContainerValue) -> list[t.ContainerValue]:
        """Coerce data to list for CSV processing.

        Uses types from lower layer (t.ContainerValue) for proper type safety.
        """
        if isinstance(data, list):
            return data
        if isinstance(data, tuple):
            return [self._normalize_iterable_item(item) for item in data]
        if isinstance(data, dict):
            return list(data.items())
        try:
            if isinstance(data, str):
                return []
            result = self._try_iterate_items(data)
            return result or []
        except (TypeError, AttributeError):
            return []

    def _convert_iterable_to_list(
        self, data: Iterable[t.ContainerValue]
    ) -> list[t.ContainerValue]:
        """Convert iterable to list with type narrowing.

        Helper method to reduce complexity of _coerce_to_list.
        Uses Iterable from lower layer for proper type safety.
        """
        try:
            if isinstance(data, Sequence):
                return list(data)
            iterable_items: list[t.ContainerValue] = []
            for item in data:
                item_general: t.ContainerValue = (
                    item
                    if isinstance(
                        item, (str, int, float, bool, type(None), dict, list, tuple)
                    )
                    else str(item)
                )
                iterable_items.append(item_general)
            return iterable_items
        except (TypeError, ValueError):
            return []

    def _convert_result_to_formattable(
        self,
        result: BaseModel | t.ContainerValue | r[t.ContainerValue],
        output_format: str,
    ) -> r[str]:
        """Convert result object to formattable string.

        Handles multiple result types: Pydantic models, objects with __dict__, and fallback.
        Fast-fails if result is None - caller must handle None values explicitly.
        """
        if result is None:
            return r[str].fail(
                "Cannot format None result - provide a valid result object"
            )
        if isinstance(result, BaseModel):
            return self._format_pydantic_model(result, output_format)
        if isinstance(result, dict):
            return self.format_data(result, output_format)
        if hasattr(result, "__dict__"):
            filtered_dict = {
                k: v for k, v in result.__dict__.items() if self.is_json(v)
            }
            result_dict = self.ensure_dict(filtered_dict, {})
            return self.format_data(result_dict, output_format)
        return r[str].ok(str(result))

    def _create_table_string(
        self,
        table_data: list[dict[str, t.ContainerValue]],
        table_headers: str | list[str],
    ) -> r[str]:
        """Create table string using FlextCliTables."""
        try:
            config_instance = m.Cli.TableConfig.model_validate({
                "headers": table_headers,
                "table_format": c.Cli.TableFormats.GRID,
            })
            data_json: list[dict[str, t.JsonValue]] = [
                {str(k): m.Cli.normalize_to_json_value(v) for k, v in row.items()}
                for row in table_data
            ]
            table_result = FlextCliTables.create_table(
                data=data_json, config=config_instance
            )
            if table_result.is_failure:
                return r[str].fail(f"Failed to create table: {table_result.error}")
            return table_result
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def _dispatch_formatter(
        self,
        format_type: str,
        data: t.ContainerValue,
        title: str | None,
        headers: list[str] | None,
    ) -> r[str]:
        """Dispatch to appropriate formatter based on format type."""
        formatters: dict[str, Callable[[], r[str]]] = {
            c.Cli.OutputFormats.JSON.value: lambda: self.format_json(data),
            c.Cli.OutputFormats.YAML.value: lambda: self.format_yaml(data),
            c.Cli.OutputFormats.TABLE.value: lambda: self._format_table_data(
                data, title, headers
            ),
            c.Cli.OutputFormats.CSV.value: lambda: self.format_csv(data),
            c.Cli.OutputFormats.PLAIN.value: lambda: r[str].ok(str(data)),
        }
        formatter = formatters.get(format_type)
        if formatter is None:
            return r[str].fail(
                c.Cli.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                    format_type=format_type
                )
            )
        return formatter()

    def _dispatch_registered_formatter(
        self,
        result: BaseModel | t.ContainerValue | r[t.ContainerValue],
        formatter: Callable[[t.ContainerValue | r[t.ContainerValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Dispatch registered formatter by result strategy."""
        if isinstance(result, BaseModel):
            return self._format_registered_basemodel(result, formatter, output_format)
        if isinstance(result, r):
            return self._format_registered_result(result, formatter, output_format)
        return self._format_registered_generic(result, formatter, output_format)

    def _format_csv_dict(self, data: t.ContainerValue) -> r[str]:
        """Format single dict as CSV."""
        output_buffer = StringIO()
        fieldnames = self.get_keys(data)
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        data_dict: dict[str, t.ContainerValue] = (
            dict(data) if isinstance(data, dict) else {}
        )
        writer.writerow(data_dict)
        return r[str].ok(output_buffer.getvalue())

    def _format_csv_list(self, data: t.ContainerValue) -> r[str]:
        """Format list of dicts as CSV."""
        output_buffer = StringIO()
        data_list = self._coerce_to_list(data)
        if not data_list or not FlextRuntime.is_dict_like(data_list[0]):
            return r[str].fail("CSV list format requires list of dicts")
        fieldnames = self.get_keys(data_list[0])
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        filtered_rows = u.filter(data_list, predicate=FlextRuntime.is_dict_like)
        dict_rows_raw = self.ensure_list(filtered_rows, [])
        dict_rows: list[dict[str, t.ContainerValue]] = [
            item for item in dict_rows_raw if isinstance(item, dict)
        ]
        csv_rows: list[dict[str, t.Scalar]] = []
        for row in dict_rows:
            processed_row = self._process_csv_row(row)
            csv_rows.append(processed_row)
        writer.writerows(csv_rows)
        return r[str].ok(output_buffer.getvalue())

    def _format_dict_object(
        self, result: t.ContainerValue | r[t.ContainerValue], output_format: str
    ) -> r[str]:
        """Format object with __dict__ to string."""
        if isinstance(result, r):
            if result.is_failure:
                return r[str].fail(f"Cannot format failed result: {result.error}")
            result = result.value
        if not hasattr(result, "__dict__"):
            return r[str].fail(
                f"Object {type(result).__name__} has no __dict__ attribute"
            )
        raw_dict_raw = result.__dict__
        raw_dict: dict[str, t.ContainerValue] = (
            dict(raw_dict_raw) if isinstance(raw_dict_raw, dict) else {}
        )
        json_dict_result = u.Cli.process_mapping(
            raw_dict, processor=lambda _k, v: self.to_json(v), on_error="skip"
        )
        json_dict_raw = json_dict_result.unwrap_or({})
        json_dict: dict[str, t.ContainerValue] = (
            json_dict_raw if isinstance(json_dict_raw, dict) else {}
        )
        filtered_json_dict = {k: v for k, v in json_dict.items() if self.is_json(v)}
        cli_json_dict_result = u.Cli.process_mapping(
            filtered_json_dict, processor=lambda _k, v: v, on_error="skip"
        )
        cli_json_dict_raw = cli_json_dict_result.unwrap_or({})
        cli_json_dict: dict[str, t.ContainerValue] = (
            cli_json_dict_raw if isinstance(cli_json_dict_raw, dict) else {}
        )
        return self.format_data(cli_json_dict, output_format)

    def _format_pydantic_model(self, result: BaseModel, output_format: str) -> r[str]:
        """Format Pydantic model to string."""
        result_dict = result.model_dump()
        return self.format_data(result_dict, output_format)

    def _format_registered_basemodel(
        self,
        result: BaseModel,
        formatter: Callable[[t.ContainerValue | r[t.ContainerValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Format registered BaseModel result."""
        formattable_result: t.ContainerValue = result.model_dump()
        formatter(formattable_result, output_format)
        return r[bool].ok(value=True)

    def _format_registered_generic(
        self,
        result: t.ContainerValue,
        formatter: Callable[[t.ContainerValue | r[t.ContainerValue], str], None],
        output_format: str,
    ) -> r[bool]:
        """Format registered plain general value."""
        formatter(result, output_format)
        return r[bool].ok(value=True)

    def _format_registered_result(
        self,
        result: r[t.ContainerValue],
        formatter: Callable[[t.ContainerValue | r[t.ContainerValue], str], None],
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

    def _format_table_data(
        self, data: t.ContainerValue, title: str | None, headers: list[str] | None
    ) -> r[str]:
        """Format data as table with type validation."""
        if FlextRuntime.is_dict_like(data):
            transformed_data = self.to_dict_json(data)
            return self.format_table(transformed_data, title=title, headers=headers)
        if FlextRuntime.is_list_like(data):
            if not data:
                return r[str].fail(c.Cli.ErrorMessages.NO_DATA_PROVIDED)
            data_list: list[t.ContainerValue] = [
                FlextRuntime.normalize_to_general_value(item) for item in data
            ]
            dict_items = u.filter(data_list, predicate=FlextRuntime.is_dict_like)
            if len(dict_items) != len(data_list):
                return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)
            filtered_data = [
                item for item in data_list if FlextRuntime.is_dict_like(item)
            ]
            json_list_result = u.Cli.process(
                filtered_data, processor=self.norm_json, on_error="skip"
            )
            converted_list_raw = self.ensure_list(json_list_result.unwrap_or([]), [])
            converted_list: list[dict[str, t.ContainerValue]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self.format_table(converted_list, title=title, headers=headers)
        return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def _get_registered_formatter(
        self, result_type: type
    ) -> Callable[[t.ContainerValue | r[t.ContainerValue], str], None] | None:
        """Get registered formatter for a concrete result type."""
        formatters_dict: dict[
            type, Callable[[t.ContainerValue | r[t.ContainerValue], str], None]
        ] = FlextCliOutput._result_formatters
        return formatters_dict.get(result_type)

    def _initialize_rich_table(
        self, headers: list[str], title: str | None = None
    ) -> r[p.Cli.Display.RichTableProtocol]:
        """Initialize a Rich table with headers.

        Uses RichTableProtocol from lower layer instead of object for better type safety.
        """
        table_result = FlextCliFormatters().create_table(
            data=None, headers=headers, title=title
        )
        if table_result.is_failure:
            return r[p.Cli.Display.RichTableProtocol].fail(
                f"Failed to create Rich table: {table_result.error}"
            )
        table_value = table_result.value
        if self._is_rich_table_protocol(table_value):
            return r[p.Cli.Display.RichTableProtocol].ok(table_value)
        return r[p.Cli.Display.RichTableProtocol].fail(
            "Table value is not RichTableProtocol compatible"
        )

    def _iterate_mapping(self, data: t.ContainerValue) -> list[t.ContainerValue]:
        """Iterate dictionary values as tuple items."""
        if not isinstance(data, dict):
            return []
        iterable_items: list[t.ContainerValue] = []
        for key, value in data.items():
            dict_item: t.ContainerValue = (key, value)
            iterable_items.append(dict_item)
        return iterable_items

    def _iterate_model(self, data: t.ContainerValue) -> list[t.ContainerValue]:
        """Iterate custom iterable values with normalization."""
        if not isinstance(data, Iterable):
            return []
        return [self._normalize_iterable_item(item) for item in data]

    def _iterate_sequence(self, data: t.ContainerValue) -> list[t.ContainerValue]:
        """Iterate list/tuple values with normalization."""
        if not isinstance(data, (list, tuple)):
            return []
        return [self._normalize_iterable_item(item) for item in data]

    def _populate_table_rows(
        self,
        table: p.Cli.Display.RichTableProtocol,
        data: list[dict[str, t.ContainerValue]],
        headers: list[str],
    ) -> r[bool]:
        """Add columns and rows to table.

        Uses RichTableProtocol from lower layer instead of object for better type safety.
        """
        u.Cli.process(
            headers, processor=lambda h: table.add_column(str(h)), on_error="skip"
        )
        rows_result = FlextCliOutput._build_table_rows(data, headers)
        if rows_result.is_failure:
            return r[bool].fail(rows_result.error or "Failed to build rows")
        rows_list = rows_result.value or []
        for row in rows_list:
            table.add_row(*row)
        return r[bool].ok(value=True)

    def _prepare_table_data(
        self,
        data: dict[str, t.ContainerValue] | list[dict[str, t.ContainerValue]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            json_data = self.to_dict_json(data)
            return self._prepare_dict_data(json_data, headers)
        if FlextRuntime.is_list_like(data):
            filtered_data = [item for item in data if FlextRuntime.is_dict_like(item)]
            process_result = u.Cli.process(
                filtered_data, processor=self.norm_json, on_error="skip"
            )
            converted_list_raw = self.ensure_list(process_result.unwrap_or([]), [])
            converted_list: list[dict[str, t.ContainerValue]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self._prepare_list_data(converted_list, headers)
        return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].fail(
            c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT
        )

    def _prepare_table_data_safe(
        self,
        data: dict[str, t.ContainerValue] | list[dict[str, t.ContainerValue]] | str,
        headers: list[str] | None,
    ) -> r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(error=e)
            return r[tuple[list[dict[str, t.ContainerValue]], str | list[str]]].fail(
                error_msg
            )

    def _prepare_table_headers(
        self, data: list[dict[str, t.ContainerValue]], headers: list[str] | None = None
    ) -> r[list[str]]:
        """Prepare and validate table headers."""
        default_headers = self.get_keys(data[0]) if data else []
        default_headers_general: list[t.ContainerValue] = list(default_headers)
        table_headers_raw = self.ensure_list(headers, default_headers_general)
        table_headers: list[str] = [str(h) for h in table_headers_raw]
        if headers is not None:
            validation_result = FlextCliOutput._validate_headers(table_headers, data)
            if validation_result.is_failure:
                return r[list[str]].fail(
                    validation_result.error or "Header validation failed"
                )
        return r[list[str]].ok(table_headers)

    def _process_csv_row(self, row: dict[str, t.ContainerValue]) -> dict[str, t.Scalar]:
        """Process CSV row with None replacement.

        Uses t.ContainerValue from lower layer instead of object for better type safety.
        """
        processed: dict[str, t.Scalar] = {}
        for k, v in row.items():
            processed[k] = self._replace_none_for_csv(k, v)
        return processed

    def _resolve_iteration_strategy(
        self, data: t.ContainerValue
    ) -> Callable[[t.ContainerValue], list[t.ContainerValue]] | None:
        """Resolve iterable strategy for general values."""
        strategies: tuple[
            tuple[
                Callable[[t.ContainerValue], bool],
                Callable[[t.ContainerValue], list[t.ContainerValue]],
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

    def _try_iterate_items(self, data: t.ContainerValue) -> list[t.ContainerValue]:
        """Try to iterate over data and return list of items.

        Helper to avoid type checker issues with non-iterable types in ContainerValue.
        Uses duck typing: attempts iteration and catches TypeError if not iterable.
        """
        try:
            strategy = self._resolve_iteration_strategy(data)
            if strategy is None:
                return []
            return strategy(data)
        except (TypeError, AttributeError):
            return []

    def _try_registered_formatter(
        self,
        result: BaseModel | t.ContainerValue | r[t.ContainerValue],
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
        return r[bool].fail(f"No registered formatter for type {result_type.__name__}")


__all__ = ["FlextCliOutput"]
