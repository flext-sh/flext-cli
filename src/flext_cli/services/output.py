"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Sequence,
)
from io import StringIO

import yaml
from flext_core import FlextRuntime, r
from pydantic import TypeAdapter

from flext_cli import FlextCliFormatters, FlextCliTables, FlextCliTypes, c, m, t, u

_JSON_VALUE_ADAPTER: TypeAdapter[FlextCliTypes.Cli.JsonValue] = TypeAdapter(
    FlextCliTypes.Cli.JsonValue,
)


class FlextCliOutput:
    """CLI output tools for the flext ecosystem.

    Provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - FlextCliTables: Tabulate-based ASCII tables (performance, plain text)
    - Built-in: JSON, YAML, CSV formatting

    """

    # ── Static helpers ──────────────────────────────────────────────

    @staticmethod
    def _add_title(table_str: str, title: str | None) -> str:
        """Add title to table string if provided."""
        if title:
            return f"{title}{c.Cli.OutputDefaults.NEWLINE}{table_str}{c.Cli.OutputDefaults.NEWLINE}"
        return table_str

    @staticmethod
    def _is_custom_iterable_value(_data: FlextCliTypes.Cli.JsonValue) -> bool:
        """Check if value should use custom iterable strategy."""
        return False

    @staticmethod
    def _is_mapping_value(data: FlextCliTypes.Cli.JsonValue) -> bool:
        """Check if value should use mapping iteration strategy."""
        return isinstance(data, dict)

    @staticmethod
    def _is_sequence_value(data: FlextCliTypes.Cli.JsonValue) -> bool:
        """Check if value should use sequence iteration strategy."""
        return isinstance(data, (list, tuple))

    @staticmethod
    def _normalize_iterable_item(
        item: FlextCliTypes.Cli.JsonValue,
    ) -> FlextCliTypes.Cli.JsonValue:
        """Normalize iterable items to general value type."""
        return (
            item
            if (
                item is None
                or u.is_primitive(item)
                or isinstance(item, (dict, list, tuple))
            )
            else str(item)
        )

    @staticmethod
    def _prepare_dict_data(
        data: Mapping[str, FlextCliTypes.Cli.JsonValue],
        headers: t.StrSequence | None,
    ) -> r[
        tuple[Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]], str | t.StrSequence]
    ]:
        """Prepare dict data for table display."""
        if c.Cli.OutputDefaults.TEST_INVALID_KEY in data and len(data) == 1:
            return r[
                tuple[
                    Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                    str | t.StrSequence,
                ]
            ].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

        def kv_pair(
            k: str,
            v: FlextCliTypes.Cli.JsonValue,
        ) -> Mapping[str, FlextCliTypes.Cli.JsonValue]:
            """Create key-value pair dict."""
            return {c.Cli.OutputFieldNames.KEY: k, c.Cli.OutputFieldNames.VALUE: str(v)}

        process_result = u.Cli.process_mapping(data, processor=kv_pair, on_error="skip")
        process_value = process_result.unwrap_or({})
        dict_result: Mapping[str, Mapping[str, FlextCliTypes.Cli.JsonValue]] = dict(
            process_value,
        )
        table_data_raw = FlextCliOutput.ensure_list(list(dict_result.values()), [])
        table_data: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
            item for item in table_data_raw if isinstance(item, dict)
        ]
        table_headers_raw = (
            list(headers) if headers is not None else [c.Cli.TableFormats.KEYS]
        )
        table_headers: t.StrSequence = [str(h) for h in table_headers_raw]
        return r[
            tuple[
                Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                str | t.StrSequence,
            ]
        ].ok((
            table_data,
            table_headers,
        ))

    @staticmethod
    def _prepare_list_data(
        data: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
        headers: t.StrSequence | None,
    ) -> r[
        tuple[Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]], str | t.StrSequence]
    ]:
        """Prepare list data for table display."""
        if not data:
            return r[
                tuple[
                    Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                    str | t.StrSequence,
                ]
            ].fail(c.Cli.ErrorMessages.NO_DATA_PROVIDED)
        headers_list = (
            list(headers) if headers is not None else [c.Cli.TableFormats.KEYS]
        )
        table_headers = [str(h) for h in headers_list]
        if headers is not None and table_headers != [c.Cli.TableFormats.KEYS]:
            validation_result = FlextCliOutput._validate_headers(table_headers, data)
            if validation_result.is_failure:
                return r[
                    tuple[
                        Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                        str | t.StrSequence,
                    ]
                ].fail(validation_result.error or "Header validation failed")
        return r[
            tuple[
                Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                str | t.StrSequence,
            ]
        ].ok((
            data,
            table_headers,
        ))

    @staticmethod
    def _replace_none_for_csv(_k: str, v: FlextCliTypes.Cli.JsonValue) -> t.Scalar:
        """Replace None with empty string for CSV."""
        if v is None:
            return ""
        if u.is_primitive(v):
            return v
        return str(v)

    @staticmethod
    def _validate_headers(
        headers: t.StrSequence,
        data: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
    ) -> r[bool]:
        """Validate headers exist in data."""

        def _extract_keys(row: Mapping[str, FlextCliTypes.Cli.JsonValue]) -> set[str]:
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
        v: FlextCliTypes.Cli.JsonValue,
        t: type,
        default: FlextCliTypes.Cli.JsonValue,
    ) -> FlextCliTypes.Cli.JsonValue:
        """Cast value if isinstance else return default."""
        matched = isinstance(v, t)
        if matched:
            return v
        default_matched = isinstance(default, t)
        if default_matched:
            return default
        type_name = t.__name__ if hasattr(t, "__name__") else str(t)
        default_type_name = (
            type(default).__name__
            if hasattr(type(default), "__name__")
            else str(type(default))
        )
        msg = f"default must be instance of {type_name}, got {default_type_name}"
        raise TypeError(msg)

    @staticmethod
    def ensure_list(
        v: FlextCliTypes.Cli.JsonValue | None,
        default: Sequence[FlextCliTypes.Cli.JsonValue] | None = None,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Ensure value is list with default using build DSL."""
        v_typed = FlextRuntime.normalize_to_container(v) if v is not None else None
        built_result = u.build(
            v_typed,
            ops={"ensure": "list", "ensure_default": default or []},
            on_error="skip",
        )
        return (
            list(built_result) if isinstance(built_result, Sequence) else default or []
        )

    @staticmethod
    def ensure_str(v: FlextCliTypes.Cli.JsonValue | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if v is None:
            return default
        try:
            return str(v)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def get_keys(
        d: Mapping[str, FlextCliTypes.Cli.JsonValue] | FlextCliTypes.Cli.JsonValue,
    ) -> t.StrSequence:
        """Extract keys from dict using build DSL."""
        d_dict = u.build(d, ops={"ensure": "dict"}, on_error="skip")
        if isinstance(d_dict, dict):
            return list(d_dict.keys())
        return []

    @staticmethod
    def get_map_val(
        m: Mapping[str, FlextCliTypes.Cli.JsonValue],
        k: str,
        default: FlextCliTypes.Cli.JsonValue,
    ) -> FlextCliTypes.Cli.JsonValue:
        """Get value from map with default using build DSL."""
        value = m.get(k, default)
        compatible_value: FlextCliTypes.Cli.JsonValue
        if value is None or u.is_primitive(value) or isinstance(value, list):
            compatible_value = value
        elif isinstance(value, dict):
            dict_items: MutableMapping[str, FlextCliTypes.Cli.JsonValue] = {}
            for kk, vv in value.items():
                dict_items[str(kk)] = (
                    vv
                    if vv is None or u.is_primitive(vv) or isinstance(vv, (list, dict))
                    else str(vv)
                )
            compatible_value = dict_items
        else:
            compatible_value = str(value)
        return compatible_value

    @staticmethod
    def is_json(v: FlextCliTypes.Cli.JsonValue) -> bool:
        """Check if value is JSON-compatible type."""
        return v is None or u.is_primitive(v) or isinstance(v, (dict, list))

    @staticmethod
    def norm_json(item: FlextCliTypes.Cli.JsonValue) -> FlextCliTypes.Cli.JsonValue:
        """Normalize item to JSON-compatible using build DSL."""
        if item is None or u.is_primitive(item):
            return item
        if FlextRuntime.is_dict_like(item):
            return FlextCliOutput.to_dict_json(item)
        if FlextRuntime.is_list_like(item):
            return FlextCliOutput.to_list_json(item)
        return str(item)

    @staticmethod
    def to_dict_json(
        v: FlextCliTypes.Cli.JsonValue,
    ) -> Mapping[str, FlextCliTypes.Cli.JsonValue]:
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
    def to_json(v: FlextCliTypes.Cli.JsonValue) -> FlextCliTypes.Cli.JsonValue:
        """Convert value to JSON-compatible using build DSL."""
        if isinstance(v, dict):
            return u.build(
                v,
                ops={"ensure": "dict", "transform": {"to_json": True}},
                on_error="skip",
            )
        return v

    @staticmethod
    def to_list_json(
        v: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Convert value to list with JSON transform using build DSL."""
        v_typed = FlextRuntime.normalize_to_container(v)
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

    # ── Instance methods (public API) ───────────────────────────────

    def display_message(self, message: str, message_type: str | None = None) -> None:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        """
        final_message_type = self.ensure_str(
            message_type,
            c.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE,
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
        style_map_general: Mapping[str, FlextCliTypes.Cli.JsonValue] = dict(style_map)
        emoji_map_general: Mapping[str, FlextCliTypes.Cli.JsonValue] = dict(emoji_map)
        style = self.ensure_str(
            self.get_map_val(style_map_general, final_message_type, c.Cli.Styles.BLUE),
        )
        emoji = self.ensure_str(
            self.get_map_val(emoji_map_general, final_message_type, c.Cli.Emojis.INFO),
        )
        formatted_message = f"{emoji} {message}"
        self.print_message(formatted_message, style=style)

    def display_text(self, text: str, *, style: str | None = None) -> None:
        """Display text using FlextCliFormatters.

        Args:
            text: Text to display
            style: Optional Rich style

        """
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        FlextCliFormatters().print(text, style=validated_style)

    def format_data(
        self,
        data: FlextCliTypes.Cli.JsonValue,
        format_type: str = c.Cli.OutputFormats.TABLE.value,
        title: str | None = None,
        headers: t.StrSequence | None = None,
    ) -> r[str]:
        """Format data using specified format type with railway pattern.

        Args:
            data: Data to format
            format_type: Format type from c.Cli.OutputFormats
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            r[str]: Formatted data string or error

        """
        parse_result = u.Cli.parse(format_type, str, default="")
        format_str = self.ensure_str(
            parse_result.unwrap_or(str(format_type)),
            "",
        ).lower()
        valid_formats = set(c.Cli.ValidationLists.OUTPUT_FORMATS)
        if format_str not in valid_formats:
            return r[str].fail(
                c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=format_type),
            )
        return self._dispatch_formatter(format_str, data, title, headers)

    def print_message(self, message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print
            style: Optional Rich style

        """
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        FlextCliFormatters().print(message, style=validated_style)

    # ── Instance methods (format implementations) ───────────────────

    def format_csv(self, data: FlextCliTypes.Cli.JsonValue) -> r[str]:
        """Format data as CSV."""
        try:
            if FlextRuntime.is_list_like(data) and data:
                coerced_list = self._coerce_to_list(data)
                if coerced_list and FlextRuntime.is_dict_like(coerced_list[0]):
                    return self._format_csv_list(coerced_list)
            if FlextRuntime.is_dict_like(data):
                return self._format_csv_dict(data)
            return r[str].ok(
                _JSON_VALUE_ADAPTER.dump_json(
                    data,
                    indent=c.Cli.OutputDefaults.JSON_INDENT,
                ).decode("utf-8"),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.CSV_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def format_json(self, data: FlextCliTypes.Cli.JsonValue) -> r[str]:
        """Format data as JSON."""
        try:
            return r[str].ok(
                _JSON_VALUE_ADAPTER.dump_json(
                    data,
                    indent=c.Cli.OutputDefaults.JSON_INDENT,
                ).decode("utf-8"),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.JSON_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    def format_table(
        self,
        data: Mapping[str, FlextCliTypes.Cli.JsonValue]
        | Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]]
        | str,
        title: str | None = None,
        headers: t.StrSequence | None = None,
    ) -> r[str]:
        """Format data as a tabulated table string using FlextCliTables."""
        prepared_result = self._prepare_table_data_safe(data, headers)
        if prepared_result.is_failure:
            return r[str].fail(
                prepared_result.error or "Failed to prepare table data",
                error_code=prepared_result.error_code,
                error_data=prepared_result.error_data,
            )
        prepared = prepared_result.value
        table_data_list: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
            dict(row) for row in prepared[0]
        ]
        table_result = self._create_table_string(table_data_list, prepared[1])
        if table_result.is_failure:
            return table_result
        table = table_result.value
        return r[str].ok(self._add_title(table, title))

    def format_yaml(self, data: FlextCliTypes.Cli.JsonValue) -> r[str]:
        """Format data as YAML."""
        try:
            return r[str].ok(
                yaml.dump(
                    data,
                    default_flow_style=c.Cli.OutputDefaults.YAML_DEFAULT_FLOW_STYLE,
                ),
            )
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.YAML_FORMAT_FAILED.format(error=e)
            return r[str].fail(error_msg)

    # ── Private instance methods ────────────────────────────────────

    def _coerce_to_list(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Coerce data to list for CSV processing."""
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

    def _create_table_string(
        self,
        table_data: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
        table_headers: str | t.StrSequence,
    ) -> r[str]:
        """Create table string using FlextCliTables."""
        try:
            config_instance = m.Cli.TableConfig.model_validate({
                "headers": table_headers,
                "table_format": c.Cli.TableFormats.SIMPLE,
            })
            data_json: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
                {str(k): m.Cli.normalize_json_value(v) for k, v in row.items()}
                for row in table_data
            ]
            table_result = FlextCliTables.create_table(
                data=data_json,
                config=config_instance,
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
        data: FlextCliTypes.Cli.JsonValue,
        title: str | None,
        headers: t.StrSequence | None,
    ) -> r[str]:
        """Dispatch to appropriate formatter based on format type."""
        formatters: Mapping[str, Callable[[], r[str]]] = {
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
        return formatter()

    def _format_csv_dict(self, data: FlextCliTypes.Cli.JsonValue) -> r[str]:
        """Format single dict as CSV."""
        output_buffer = StringIO()
        fieldnames = self.get_keys(data)
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        data_dict: Mapping[str, FlextCliTypes.Cli.JsonValue] = (
            dict(data) if isinstance(data, dict) else {}
        )
        writer.writerow(data_dict)
        return r[str].ok(output_buffer.getvalue())

    def _format_csv_list(self, data: FlextCliTypes.Cli.JsonValue) -> r[str]:
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
        dict_rows: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
            item for item in dict_rows_raw if isinstance(item, dict)
        ]
        csv_rows: Sequence[t.ConfigurationMapping] = [
            self._process_csv_row(row) for row in dict_rows
        ]
        writer.writerows(csv_rows)
        return r[str].ok(output_buffer.getvalue())

    def _format_table_data(
        self,
        data: FlextCliTypes.Cli.JsonValue,
        title: str | None,
        headers: t.StrSequence | None,
    ) -> r[str]:
        """Format data as table with type validation."""
        if FlextRuntime.is_dict_like(data):
            transformed_data = self.to_dict_json(data)
            return self.format_table(transformed_data, title=title, headers=headers)
        if FlextRuntime.is_list_like(data):
            if not data:
                return r[str].fail(c.Cli.ErrorMessages.NO_DATA_PROVIDED)
            data_list: Sequence[FlextCliTypes.Cli.JsonValue] = [
                m.Cli.normalize_json_value(item) for item in data
            ]
            dict_items = u.filter(data_list, predicate=FlextRuntime.is_dict_like)
            if len(dict_items) != len(data_list):
                return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)
            filtered_data = [
                item for item in data_list if FlextRuntime.is_dict_like(item)
            ]
            json_list_result = u.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            converted_list_raw = self.ensure_list(json_list_result.unwrap_or([]), [])
            converted_list: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self.format_table(converted_list, title=title, headers=headers)
        return r[str].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def _iterate_mapping(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Iterate dictionary values as tuple items."""
        if not isinstance(data, dict):
            return []
        return [(key, value) for key, value in data.items()]

    def _iterate_model(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Iterate custom iterable values with normalization."""
        if not isinstance(data, Iterable):
            return []
        return [self._normalize_iterable_item(item) for item in data]

    def _iterate_sequence(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Iterate list/tuple values with normalization."""
        if not isinstance(data, (list, tuple)):
            return []
        return [self._normalize_iterable_item(item) for item in data]

    def _prepare_table_data(
        self,
        data: Mapping[str, FlextCliTypes.Cli.JsonValue]
        | Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]]
        | str,
        headers: t.StrSequence | None,
    ) -> r[
        tuple[Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]], str | t.StrSequence]
    ]:
        """Prepare and validate table data and headers."""
        if FlextRuntime.is_dict_like(data):
            json_data = self.to_dict_json(data)
            return self._prepare_dict_data(json_data, headers)
        if FlextRuntime.is_list_like(data):
            filtered_data = [item for item in data if FlextRuntime.is_dict_like(item)]
            process_result = u.Cli.process(
                filtered_data,
                processor=self.norm_json,
                on_error="skip",
            )
            converted_list_raw = self.ensure_list(process_result.unwrap_or([]), [])
            converted_list: Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]] = [
                item for item in converted_list_raw if isinstance(item, dict)
            ]
            return self._prepare_list_data(converted_list, headers)
        return r[
            tuple[
                Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                str | t.StrSequence,
            ]
        ].fail(c.Cli.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT)

    def _prepare_table_data_safe(
        self,
        data: Mapping[str, FlextCliTypes.Cli.JsonValue]
        | Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]]
        | str,
        headers: t.StrSequence | None,
    ) -> r[
        tuple[Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]], str | t.StrSequence]
    ]:
        """Safely prepare table data with exception handling."""
        try:
            return self._prepare_table_data(data, headers)
        except Exception as e:
            error_msg = c.Cli.OutputLogMessages.TABLE_FORMAT_FAILED.format(error=e)
            return r[
                tuple[
                    Sequence[Mapping[str, FlextCliTypes.Cli.JsonValue]],
                    str | t.StrSequence,
                ]
            ].fail(error_msg)

    def _process_csv_row(
        self,
        row: Mapping[str, FlextCliTypes.Cli.JsonValue],
    ) -> t.ConfigurationMapping:
        """Process CSV row with None replacement."""
        processed: t.MutableConfigurationMapping = {}
        for k, v in row.items():
            processed[k] = self._replace_none_for_csv(k, v)
        return processed

    def _resolve_iteration_strategy(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Callable[..., Sequence[FlextCliTypes.Cli.JsonValue]] | None:
        """Resolve iterable strategy for general values."""
        strategies: tuple[
            tuple[
                Callable[..., bool],
                Callable[..., Sequence[FlextCliTypes.Cli.JsonValue]],
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

    def _try_iterate_items(
        self,
        data: FlextCliTypes.Cli.JsonValue,
    ) -> Sequence[FlextCliTypes.Cli.JsonValue]:
        """Try to iterate over data and return list of items."""
        try:
            strategy = self._resolve_iteration_strategy(data)
            if strategy is None:
                return []
            return strategy(data)
        except (TypeError, AttributeError):
            return []


__all__ = ["FlextCliOutput"]
