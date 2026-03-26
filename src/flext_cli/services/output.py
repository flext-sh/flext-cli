"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
)

from flext_cli import FlextCliFormatters, FlextCliTypes, c, u


class FlextCliOutput:
    """CLI output tools for the flext ecosystem.

    Provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - Built-in: JSON, YAML, CSV formatting

    """

    # ── Static helpers ──────────────────────────────────────────────

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
    def ensure_str(value: FlextCliTypes.Cli.JsonValue | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if value is None:
            return default
        try:
            return str(value)
        except (TypeError, ValueError):
            return default

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
        """Display text with optional style. Delegates to print_message."""
        self.print_message(text, style=style)

    def print_message(self, message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters."""
        validated_style = self.ensure_str(style, c.Cli.OutputDefaults.EMPTY_STYLE)
        FlextCliFormatters().print(message, style=validated_style)


__all__ = ["FlextCliOutput"]
