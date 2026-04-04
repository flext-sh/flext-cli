"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)

from flext_cli import FlextCliFormatters, FlextCliServiceBase, c, t, u


class FlextCliOutput(FlextCliServiceBase):
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
    def ensure_str(value: t.RecursiveContainer, default: str = "") -> str:
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
        if u.is_primitive(value) or (
            isinstance(value, Sequence) and not isinstance(value, str)
        ):
            compatible_value = value
        elif isinstance(value, Mapping):
            compatible_value = {
                str(kk): u.Cli.normalize_json_value(vv) for kk, vv in value.items()
            }
        else:
            compatible_value = str(value)
        return compatible_value

    @staticmethod
    def to_dict_json(
        v: t.Cli.JsonValue,
    ) -> Mapping[str, t.Cli.JsonValue]:
        """Convert value to dict natively instead of using build DSL."""
        built: Mapping[str, t.Cli.JsonValue] = v if isinstance(v, Mapping) else {}
        result: dict[str, t.Cli.JsonValue] = {}
        for k, val in built.items():
            compatible_value: t.Cli.JsonValue
            if isinstance(val, (bool, float, int, str)):
                compatible_value = val
            elif isinstance(val, Mapping):
                compatible_value = {
                    str(kk): u.Cli.normalize_json_value(vv) for kk, vv in val.items()
                }
            else:
                compatible_value = u.Cli.normalize_json_value(val)
            result[str(k)] = compatible_value
        return result

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
            c.Cli.MessageTypes.DEBUG.value: "dim",
        }
        emoji_map = {
            c.Cli.MessageTypes.INFO.value: c.Cli.Emojis.INFO,
            c.Cli.MessageTypes.SUCCESS.value: c.Cli.Emojis.SUCCESS,
            c.Cli.MessageTypes.ERROR.value: c.Cli.Emojis.ERROR,
            c.Cli.MessageTypes.WARNING.value: c.Cli.Emojis.WARNING,
            c.Cli.MessageTypes.DEBUG.value: "D",
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
        FlextCliFormatters.print(message, style=validated_style)

    @staticmethod
    def display_header(text: str) -> None:
        """Display a section header via Rich rule."""
        FlextCliFormatters.render_rule(text)

    @staticmethod
    def display_progress(
        current: int,
        total: int,
        label: str,
        *,
        detail: str = "",
    ) -> None:
        """Display progress indicator [current/total] label detail."""
        w = len(str(total))
        suffix = f" {detail}" if detail else ""
        FlextCliFormatters.print(f"[{current:0{w}d}/{total}] {label}{suffix}")

    @staticmethod
    def display_status(
        success: bool,
        label: str,
        detail: str,
        *,
        elapsed: float | None = None,
    ) -> None:
        """Display a pass/fail status line."""
        sym = c.Cli.Symbols.SUCCESS_MARK if success else c.Cli.Symbols.FAILURE_MARK
        style = c.Cli.Styles.BOLD_GREEN if success else c.Cli.Styles.BOLD_RED
        timing = f"  ({elapsed:.2f}s)" if elapsed is not None else ""
        FlextCliFormatters.print(
            f"  {sym} {label:<8} {detail:<24}{timing}", style=style
        )

    @staticmethod
    def display_summary(
        title: str,
        *,
        total: int,
        success: int,
        failed: int,
        skipped: int = 0,
    ) -> None:
        """Display a summary panel."""
        content = (
            f"Total: {total}  Success: {success}  Failed: {failed}  Skipped: {skipped}"
        )
        FlextCliFormatters.render_panel(content, title=title)

    @staticmethod
    def display_gate(name: str, passed: bool, *, message: str = "") -> None:
        """Display a quality gate result."""
        sym = c.Cli.Symbols.SUCCESS_MARK if passed else c.Cli.Symbols.FAILURE_MARK
        style = c.Cli.Styles.BOLD_GREEN if passed else c.Cli.Styles.BOLD_RED
        suffix = f"  {message}" if message else ""
        FlextCliFormatters.print(f"    {sym} {name:<10}{suffix}", style=style)

    @staticmethod
    def display_metrics(
        metrics: t.ConfigValueMapping,
    ) -> None:
        """Display key=value metric pairs."""
        for key, value in metrics.items():
            FlextCliFormatters.print(f"{key}={value}")

    @staticmethod
    def display_debug(message: str, *, verbose: bool = False) -> None:
        """Display debug message (no-op unless verbose)."""
        if not verbose:
            return
        FlextCliFormatters.print(f"[DEBUG] {message}", style="dim")


__all__ = ["FlextCliOutput"]
