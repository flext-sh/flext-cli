"""FLEXT CLI utility facade and CLI-specific helpers."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import override

from flext_core import FlextUtilities, r
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import c, m, t


class FlextCliUtilities(FlextUtilities):
    """Main utilities class for the Flext CLI."""

    class Cli(FlextUtilities):
        """Command line interface specific utilities."""

        @staticmethod
        @override
        def process[T, U](
            items: Sequence[T],
            processor: Callable[[T], U],
            *,
            predicate: Callable[[T], bool] | None = None,
            on_error: str = "fail",
            filter_keys: set[str] | None = None,
            exclude_keys: set[str] | None = None,
        ) -> r[Sequence[U]]:
            """Process a sequence of items with error handling."""
            _ = (filter_keys, exclude_keys)
            errors: MutableSequence[str] = []
            values: MutableSequence[U] = []
            for idx, item in enumerate(items):
                if predicate is not None and (not predicate(item)):
                    continue
                try:
                    values.append(processor(item))
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as exc:
                    if on_error == "fail":
                        return r[Sequence[U]].fail(f"Error at index {idx}: {exc}")
                    if on_error == "collect":
                        errors.append(f"[{idx}]: {exc}")
                    else:
                        logging.getLogger(__name__).debug(
                            "process skip index %s: %s",
                            idx,
                            exc,
                            exc_info=False,
                        )
            return (
                r[Sequence[U]].fail("; ".join(errors))
                if errors
                else r[Sequence[U]].ok(values)
            )

        @staticmethod
        def process_mapping[T, U](
            items: Mapping[str, T],
            processor: Callable[[str, T], U],
            on_error: str = "fail",
        ) -> r[Mapping[str, U]]:
            """Process a mapping of items with error handling."""
            errors: MutableSequence[str] = []
            values: MutableMapping[str, U] = {}
            for key, value in items.items():
                try:
                    values[key] = processor(key, value)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as exc:
                    if on_error == "fail":
                        return r[Mapping[str, U]].fail(f"Error processing {key}: {exc}")
                    if on_error == "collect":
                        errors.append(f"{key}: {exc}")
                    else:
                        logging.getLogger(__name__).debug(
                            "process_mapping skip key %s: %s",
                            key,
                            exc,
                            exc_info=False,
                        )
            return (
                r[Mapping[str, U]].fail("; ".join(errors))
                if errors
                else r[Mapping[str, U]].ok(values)
            )

        @staticmethod
        def validate_required_string(value: str, *, context: str = "Value") -> None:
            """Validate that a string is not empty."""
            checked = FlextCliUtilities.Cli.CliValidation.v_empty(value, name=context)
            if checked.is_failure:
                raise ValueError(checked.error or f"{context} cannot be empty")

        class CliValidation:
            """CLI-specific validation utilities."""

            @staticmethod
            def to_str(value: t.Cli.CliValue) -> str:
                """Convert a value to a string safely."""
                if value is None:
                    return ""
                if isinstance(value, str):
                    return value
                return str(value)

            @staticmethod
            def v(
                val: t.Cli.CliValue,
                *,
                name: str = "field",
                empty: bool = True,
                in_list: t.StrSequence | None = None,
                eq: str | None = None,
                msg: str = "",
            ) -> r[bool]:
                """Validate a value against various criteria."""
                if not empty:
                    check = FlextCliUtilities.Cli.CliValidation.v_empty(val, name=name)
                    if check.is_failure:
                        return r[bool].fail(msg or check.error or "")
                if in_list is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation.to_str(val)
                    if val_str not in set(in_list):
                        err = (
                            c.Cli.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                                current_status=val_str,
                                valid_states=in_list,
                            )
                            if name == "session_status"
                            else c.Cli.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                                field_name=name,
                                valid_values=in_list,
                            )
                        )
                        return r[bool].fail(msg or err)
                if eq is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation.to_str(val)
                    if val_str != eq:
                        err = (
                            c.Cli.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                                operation=name,
                                current_status=val_str,
                                required_status=eq,
                            )
                        )
                        return r[bool].fail(msg or err)
                return r[bool].ok(value=True)

            @staticmethod
            def v_config(
                config: Mapping[str, t.Cli.CliValue]
                | Mapping[str, t.Cli.JsonValue]
                | None,
                *,
                fields: t.StrSequence,
            ) -> r[bool]:
                """Validate configuration fields."""
                return FlextCliUtilities.Cli.CliValidation.v_req(config, fields=fields)

            @staticmethod
            def v_empty(val: t.Cli.CliValue, *, name: str = "field") -> r[bool]:
                """Validate that a value is not empty."""
                if val is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                if isinstance(val, str) and (
                    not FlextUtilities.is_string_non_empty(val)
                ):
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                return r[bool].ok(value=True)

            @staticmethod
            def v_format(format_type: str) -> r[str]:
                """Validate an output format."""
                fmt = str(format_type).lower()
                valid = FlextCliUtilities.Cli.CliValidation.v(
                    fmt,
                    name="format",
                    empty=False,
                    in_list=c.Cli.ValidationLists.OUTPUT_FORMATS,
                )
                if valid.is_success:
                    return r[str].ok(fmt)
                return r[str].fail(
                    c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type,
                    ),
                )

            @staticmethod
            def v_level(level: str) -> r[bool]:
                """Validate a debug level."""
                return FlextCliUtilities.Cli.CliValidation.v(
                    level,
                    name="level",
                    empty=False,
                    in_list=c.Cli.ValidationLists.DEBUG_LEVELS,
                )

            @staticmethod
            def v_req(
                data: Mapping[str, t.Cli.CliValue]
                | Mapping[str, t.Cli.JsonValue]
                | None,
                *,
                fields: t.StrSequence,
            ) -> r[bool]:
                """Validate that required fields are present in a dictionary."""
                if data is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                            missing_fields=fields,
                        ),
                    )
                missing = [name for name in fields if name not in data]
                if not missing:
                    return r[bool].ok(True)
                return r[bool].fail(
                    c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=missing,
                    ),
                )

            @staticmethod
            def v_state(
                current: str,
                *,
                required: str | None = None,
                valid: t.StrSequence | None = None,
                name: str = "state",
            ) -> r[bool]:
                """Validate a state value."""
                if required is not None:
                    return FlextCliUtilities.Cli.CliValidation.v(
                        current,
                        name=name,
                        eq=required,
                    )
                if valid is not None:
                    return FlextCliUtilities.Cli.CliValidation.v(
                        current,
                        name=name,
                        in_list=valid,
                        empty=False,
                    )
                return r[bool].fail(f"{name}: no validation criteria provided")

        class ConfigOps:
            """Configuration operations."""

            @staticmethod
            def get_config_info() -> m.Cli.ConfigSnapshot:
                """Get configuration information."""
                path = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                exists = path.exists()
                return m.Cli.ConfigSnapshot(
                    config_dir=str(path),
                    config_exists=exists,
                    config_readable=exists and os.access(path, os.R_OK),
                    config_writable=exists and os.access(path, os.W_OK),
                    timestamp=datetime.now(UTC).isoformat(),
                )

            @staticmethod
            def get_config_paths() -> t.StrSequence:
                """Get standard configuration paths."""
                base = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                return [
                    str(base),
                    str(base / c.Cli.DictKeys.CONFIG),
                    str(base / c.Cli.Subdirectories.CACHE),
                    str(base / c.Cli.Subdirectories.LOGS),
                    str(base / c.Cli.DictKeys.TOKEN),
                    str(base / c.Cli.Subdirectories.REFRESH_TOKEN),
                ]

            @staticmethod
            def validate_config_structure() -> t.StrSequence:
                """Validate configuration directory structure."""
                base = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                ok = c.Cli.Symbols.SUCCESS_MARK
                fail = c.Cli.Symbols.FAILURE_MARK
                lines = [
                    f"{ok} Configuration directory exists"
                    if base.exists()
                    else f"{fail} Configuration directory missing",
                ]
                for subdir in c.Cli.Subdirectories.STANDARD_SUBDIRS:
                    path = base / subdir
                    lines.append(
                        c.Cli.CmdMessages.SUBDIR_EXISTS.format(symbol=ok, subdir=subdir)
                        if path.exists()
                        else c.Cli.CmdMessages.SUBDIR_MISSING.format(
                            symbol=fail,
                            subdir=subdir,
                        ),
                    )
                return lines

        FILE_NOT_FOUND_PATTERNS: tuple[str, ...] = (
            "not found",
            "no such file",
            "does not exist",
            "errno 2",
            "cannot open",
        )

        @staticmethod
        def is_file_not_found_error(error_msg: str) -> bool:
            """Check if error message indicates file not found."""
            return FlextCliUtilities.Cli.matches(
                error_msg,
                *FlextCliUtilities.Cli.FILE_NOT_FOUND_PATTERNS,
            )

        @staticmethod
        def matches(msg: str, *patterns: str) -> bool:
            """Check if message matches any pattern."""
            text = msg.lower()
            return any(pattern.lower() in text for pattern in patterns)


__all__ = ["FlextCliUtilities", "u"]

u = FlextCliUtilities
