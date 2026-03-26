"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
)

from flext_cli import FlextCliFormatters, c, t, u

_FORMATTER = FlextCliFormatters()


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
        v: t.Cli.JsonValue,
        target_type: type,
        default: t.Cli.JsonValue,
    ) -> t.Cli.JsonValue:
        """Cast value if isinstance else return default."""
        matched = isinstance(v, target_type)
        if matched:
            return v
        default_matched = isinstance(default, target_type)
        if default_matched:
            return default
        type_name = (
            target_type.__name__
            if hasattr(target_type, "__name__")
            else str(target_type)
        )
        default_type_name = (
            type(default).__name__
            if hasattr(type(default), "__name__")
            else str(type(default))
        )
        msg = f"default must be instance of {type_name}, got {default_type_name}"
        raise TypeError(msg)

    @staticmethod
    def ensure_str(value: t.Cli.JsonValue | None, default: str = "") -> str:
        """Ensure value is str with default."""
        if value is None:
            return default
        try:
            return str(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def get_map_val(
        mapping: Mapping[str, t.Cli.JsonValue],
        k: str,
        default: t.Cli.JsonValue,
    ) -> t.Cli.JsonValue:
        """Get value from map with default using build DSL."""
        value = mapping.get(k, default)
        compatible_value: t.Cli.JsonValue
        if value is None or u.is_primitive(value) or isinstance(value, list):
            compatible_value = value
        elif isinstance(value, dict):
            dict_items: MutableMapping[str, t.Cli.JsonValue] = {}
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
        v: t.Cli.JsonValue,
    ) -> Mapping[str, t.Cli.JsonValue]:
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

    # ── Static methods (public API) ─────────────────────────────────

    @staticmethod
    def display_message(message: str, message_type: str | None = None) -> None:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        """
        final_type = message_type or c.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE
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
        style = style_map.get(final_type, c.Cli.Styles.BLUE)
        emoji = emoji_map.get(final_type, c.Cli.Emojis.INFO)
        FlextCliOutput.print_message(f"{emoji} {message}", style=style)

    @staticmethod
    def display_text(text: str, *, style: str | None = None) -> None:
        """Display text with optional style. Delegates to print_message."""
        FlextCliOutput.print_message(text, style=style)

    @staticmethod
    def print_message(message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters."""
        validated_style = FlextCliOutput.ensure_str(
            style, c.Cli.OutputDefaults.EMPTY_STYLE
        )
        _FORMATTER.print(message, style=validated_style)


__all__ = ["FlextCliOutput"]
