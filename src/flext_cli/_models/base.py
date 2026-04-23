"""CLI Pydantic domain models."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from types import MappingProxyType
from typing import Annotated

from flext_core import m, u

from flext_cli import c, p, t


class FlextCliModelsBase:
    """CLI project namespace."""

    class CommandOutput(m.Value):
        """Standardized external command execution payload. Use m.Cli.CommandOutput."""

        stdout: Annotated[
            str,
            m.Field("", description="Captured standard output"),
        ] = ""
        stderr: Annotated[
            str,
            m.Field("", description="Captured standard error"),
        ] = ""
        exit_code: Annotated[
            int,
            m.Field(description="Command exit code"),
        ] = 0
        duration: Annotated[
            t.NonNegativeFloat,
            m.Field(0.0, description="Duration in seconds"),
        ] = 0.0

    class DisplayData(m.BaseModel):
        """Key-value data for table/display — Pydantic v2 contract. Use m.Cli.DisplayData."""

        model_config = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        data: Annotated[
            t.JsonMapping,
            m.Field(
                description="Field-value pairs for display",
            ),
        ] = m.Field(
            default_factory=lambda: MappingProxyType({}),
            description="Field-value pairs for display",
        )

    class LoadedConfig(m.BaseModel):
        """Loaded configuration content wrapper — Pydantic v2 contract. Use m.Cli.LoadedConfig."""

        model_config = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        content: Annotated[
            t.JsonMapping,
            m.Field(
                description="Loaded configuration content (dict or other JSON value)",
            ),
        ] = m.Field(
            default_factory=lambda: MappingProxyType({}),
            description="Loaded configuration content (dict or other JSON value)",
        )

    class CliNormalizedJson(m.BaseModel):
        """Normalize raw JSON value with flat JSON serialization semantics."""

        model_config = m.ConfigDict(
            extra="forbid",
            frozen=True,
        )
        root: Annotated[
            t.JsonValue,
            m.Field(description="Normalized JSON-compatible value"),
        ]

        def __init__(self, root: t.JsonValue) -> None:
            """Preserve the positional root-value constructor used by callers."""
            super().__init__(root=root)

        @u.model_serializer(mode="plain")
        def serialize_model(self) -> t.JsonValue:
            """Serialize as the wrapped JSON value rather than an object envelope."""
            return self.root

    class NormalizedJsonList(m.BaseModel):
        """Resolve normalized JSON to a dict with defaults. Use m.Cli.NormalizedJsonList."""

        model_config = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        value: Annotated[
            t.JsonValue,
            m.Field(description="The normalized JSON value"),
        ] = m.Field(
            default_factory=dict,
            description="The normalized JSON value",
        )
        default: Annotated[
            t.JsonMapping,
            m.Field(description="Default mapping if value is not a dict"),
        ] = m.Field(
            default_factory=lambda: MappingProxyType({}),
            description="Default mapping if value is not a dict",
        )

        @property
        def resolved(self) -> t.JsonMapping:
            """Resolve value to dict or return default."""
            if isinstance(self.value, Mapping):
                return self.value
            return self.default

    class SuccessSummaryDetails(m.RootModel[dict[str, str]]):
        """Key-value success summary details. Use m.Cli.SuccessSummaryDetails."""

    class PromptRuntimeState(m.FlexibleInternalModel):
        """Centralized runtime state for CLI prompt behavior."""

        model_config = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )

        interactive: Annotated[
            bool,
            m.Field(True, description="Whether prompt interaction is enabled"),
        ] = True
        quiet: Annotated[
            bool,
            m.Field(False, description="Whether prompt output is suppressed"),
        ] = False
        default_timeout: Annotated[
            int,
            m.Field(
                description="Default prompt timeout in seconds",
            ),
        ] = c.Cli.PROMPT_DEFAULT_TIMEOUT

    class CommandEntryModel(m.BaseModel):
        """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

        model_config = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        handler: Annotated[
            t.Cli.JsonCommandFn,
            m.Field(..., description="Command handler callable"),
        ]

    class ResultCommandRoute(m.BaseModel):
        """Type-erased route contract for heterogeneous batch registration."""

        model_config = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        help_text: Annotated[str, m.Field(..., description="User-facing help text")]
        model_cls: Annotated[
            type[m.BaseModel],
            m.Field(..., description="Pydantic input model class"),
        ]
        handler: Annotated[
            t.Cli.ResultRouteHandler,
            m.Field(..., description="Command handler returning r[...]"),
        ]
        success_message: Annotated[
            str | None,
            m.Field(None, description="Static success message"),
        ] = None
        success_formatter: Annotated[
            p.Cli.SuccessMessageFormatter[t.Cli.ResultValue] | None,
            m.Field(None, description="Dynamic success formatter"),
        ] = None
        success_type: Annotated[
            c.Cli.MessageTypes,
            m.Field(
                description="CLI output style on success",
            ),
        ] = c.Cli.MessageTypes.SUCCESS

    class TableConfig(m.Value):
        """Table display configuration for tabulate extending Value via inheritance.

        Fields map directly to tabulate() parameters.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        # Headers configuration
        headers: Annotated[
            t.Cli.TableHeaders,
            m.Field(
                description=(
                    "Table headers (string like 'keys', 'firstrow' "
                    "or sequence of header names)"
                ),
            ),
        ] = "keys"
        title: Annotated[
            str | None,
            m.Field(description="Optional title printed before the rendered table"),
        ] = None
        show_header: Annotated[
            bool,
            m.Field(description="Whether to show table header"),
        ] = True

        # Format configuration
        table_format: Annotated[
            c.Cli.TabularFormat,
            m.Field(
                description="Table format enum-derived literal authority",
            ),
        ] = c.Cli.TabularFormat.SIMPLE

        @u.computed_field()
        @property
        def table_backend_format(self) -> c.Cli.TabularFormat:
            """Canonical backend format used by tabulate rendering."""
            return (
                c.Cli.TabularFormat.SIMPLE
                if self.table_format == c.Cli.TabularFormat.TABLE
                else self.table_format
            )

        # Number formatting
        floatfmt: Annotated[
            str,
            m.Field(description="Float format string"),
        ] = ".4g"
        numalign: Annotated[
            str,
            m.Field(description="Number alignment (right, center, left, decimal)"),
        ] = "decimal"

        # String formatting
        stralign: Annotated[
            str,
            m.Field(description="String alignment (left, center, right)"),
        ] = "left"

        align: Annotated[
            str,
            m.Field(description="General alignment (left, center, right, decimal)"),
        ] = "left"

        # Missing values
        missingval: Annotated[
            str,
            m.Field(description="String to use for missing values"),
        ] = ""

        # Index display
        showindex: Annotated[
            t.Cli.TableShowIndex,
            m.Field(
                default=False,
                validate_default=True,
                description="Whether to show row indices",
            ),
        ] = False

        # Column alignment
        colalign: Annotated[
            t.Cli.TableColAlign,
            m.Field(
                description="Per-column alignment (left, center, right, decimal)",
            ),
        ] = None

        # Number parsing
        disable_numparse: t.Cli.TableDisableNumparse = m.Field(
            False,
            validate_default=True,
            description="Disable number parsing (bool or list of column indices)",
        )

    class SettingsSnapshot(m.Value):
        """Snapshot of current CLI settings information."""

        model_config = m.ConfigDict(
            frozen=True,
            extra="forbid",
        )

        settings_dir: Annotated[
            str,
            m.Field(
                description="Settings directory path",
            ),
        ] = ""

        settings_exists: Annotated[
            bool,
            m.Field(
                description="Whether settings directory exists",
            ),
        ] = False

        settings_readable: Annotated[
            bool,
            m.Field(
                description="Whether settings directory is readable",
            ),
        ] = False

        settings_writable: Annotated[
            bool,
            m.Field(
                description="Whether settings directory is writable",
            ),
        ] = False

        timestamp: Annotated[
            str,
            m.Field(
                description="Timestamp of snapshot",
            ),
        ] = ""

    class CliParamsConfig(m.Value):
        """CLI parameters configuration for command-line parsing.

        Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
        All fields are optional (None) to allow partial updates.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        verbose: Annotated[
            bool | None,
            m.Field(
                description="Enable verbose output",
            ),
        ] = None
        quiet: Annotated[
            bool | None,
            m.Field(
                description="Suppress non-essential output",
            ),
        ] = None
        debug: Annotated[
            bool | None,
            m.Field(None, description="Enable debug mode"),
        ]
        trace: Annotated[
            bool | None,
            m.Field(
                description="Enable trace logging (requires debug)",
            ),
        ] = None
        log_level: Annotated[
            str | None,
            m.Field(
                description="Log level (DEBUG, INFO, WARNING, ERROR)",
            ),
        ] = None
        log_format: Annotated[
            str | None,
            m.Field(
                description="Log format (compact, detailed, full)",
            ),
        ] = None
        output_format: Annotated[
            str | None,
            m.Field(
                description="Output format (table, json, yaml, csv)",
            ),
        ] = None
        no_color: Annotated[
            bool | None,
            m.Field(
                description="Disable colored output",
            ),
        ] = None

        @property
        def params(self) -> t.JsonMapping:
            """Parameters mapping - required by CliParamsConfig."""
            return {
                "verbose": bool(self.verbose) if self.verbose is not None else False,
                "quiet": bool(self.quiet) if self.quiet is not None else False,
                "debug": bool(self.debug) if self.debug is not None else False,
                "trace": bool(self.trace) if self.trace is not None else False,
                "log_level": self.log_level or "",
                "log_format": self.log_format or "",
                "output_format": self.output_format or "",
                "no_color": (
                    bool(self.no_color) if self.no_color is not None else False
                ),
            }

    class OptionConfig(m.Value):
        """Configuration for CLI option decorators.

        Used with create_option_decorator to reduce argument counts.
        """

        model_config = m.ConfigDict(
            frozen=True,
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        default: Annotated[
            t.JsonValue | None,
            m.Field(
                None,
                description="Default value",
            ),
        ]
        type_hint: Annotated[
            t.JsonValue | None,
            m.Field(
                None,
                description="Parameter type (Click type or Python type)",
            ),
        ]
        required: Annotated[
            bool,
            m.Field(
                False,
                description="Whether option is required",
            ),
        ]
        help_text: Annotated[
            str | None,
            m.Field(
                None,
                description="Help text for option",
            ),
        ]
        flag: Annotated[
            bool,
            m.Field(
                False,
                description="Boolean flag option",
            ),
        ]
        flag_value: Annotated[
            t.JsonValue | None,
            m.Field(
                None,
                description="Value when flag is set",
            ),
        ]
        multiple: Annotated[
            bool,
            m.Field(False, description="Allow multiple values"),
        ]
        count: Annotated[
            bool,
            m.Field(False, description="Count occurrences"),
        ]
        show_default: Annotated[
            bool,
            m.Field(
                False,
                description="Show default in help",
            ),
        ]

    class ConfirmConfig(m.Value):
        """Configuration for confirm prompts.

        Used with confirm() method to reduce argument counts.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        default: Annotated[bool, m.Field(False, description="Default value")]
        abort: Annotated[
            bool,
            m.Field(False, description="Abort if not confirmed"),
        ]
        prompt_suffix: Annotated[
            str,
            m.Field(
                description="Suffix after prompt",
            ),
        ] = c.Cli.UI_DEFAULT_PROMPT_SUFFIX
        show_default: Annotated[
            bool,
            m.Field(
                description="Show default in prompt",
            ),
        ] = True
        err: Annotated[bool, m.Field(False, description="Write to stderr")]

    class PromptConfig(m.Value):
        """Configuration for input prompts.

        Used with prompt() method to reduce argument counts.
        """

        model_config = m.ConfigDict(
            frozen=True,
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        default: Annotated[
            t.JsonValue | None,
            m.Field(
                None,
                description="Default value",
            ),
        ]
        type_hint: Annotated[
            t.JsonValue | None,
            m.Field(
                None,
                description="Value type",
            ),
        ]
        value_proc: Annotated[
            p.Cli.JsonValueProcessor | None,
            m.Field(
                None,
                description="Value processor function",
            ),
        ]
        prompt_suffix: Annotated[
            str,
            m.Field(
                description="Suffix after prompt",
            ),
        ] = c.Cli.UI_DEFAULT_PROMPT_SUFFIX
        hide_input: Annotated[
            bool,
            m.Field(False, description="Hide user input"),
        ]
        confirmation_prompt: Annotated[
            bool,
            m.Field(
                False,
                description="Ask for confirmation",
            ),
        ]
        show_default: Annotated[
            bool,
            m.Field(
                description="Show default in prompt",
            ),
        ] = True
        err: Annotated[bool, m.Field(False, description="Write to stderr")]
        show_choices: Annotated[
            bool,
            m.Field(
                description="Show available choices",
            ),
        ] = True

    class PromptTimeoutResolved(m.BaseModel):
        """Single contract: raw (int | str | None) + default -> int."""

        model_config = m.ConfigDict(extra="forbid")
        raw: Annotated[
            t.Cli.IntTextValue,
            m.Field(None, description="Raw timeout input (int, str, or None)"),
        ]
        default: Annotated[
            int,
            m.Field(30, description="Default timeout in seconds"),
        ]

        @u.computed_field()
        @property
        def resolved(self) -> int:
            """Resolved timeout value."""
            return self.resolve()

        def resolve(self) -> int:
            """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
            if self.raw is None:
                return self.default
            if isinstance(self.raw, str):
                return int(self.raw) if self.raw.isdigit() else self.default
            return self.raw

    class LogLevelResolved(m.BaseModel):
        """Single contract for log level string."""

        model_config = m.ConfigDict(extra="forbid")
        raw: Annotated[
            str | None,
            m.Field(None, description="Raw log level input string"),
        ]
        default: Annotated[
            str,
            m.Field(
                c.LogLevel.INFO,
                description="Default log level when raw is absent",
            ),
        ]

        @u.computed_field()
        @property
        def resolved(self) -> str:
            """Resolved log level value."""
            return self.resolve()

        def resolve(self) -> str:
            """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
            s = (self.raw or self.default).strip().upper()
            return s or self.default

    class TypedExtract(m.BaseModel):
        """Single contract for typed value extraction (str | bool | dict)."""

        model_config = m.ConfigDict(extra="forbid")
        type_kind: Annotated[
            t.Cli.TypeKind,
            m.Field(description="Requested type"),
        ]
        value: Annotated[
            t.JsonValue | None,
            m.Field(None, description="Value to extract and coerce"),
        ]
        default: Annotated[
            t.JsonValue | None,
            m.Field(None, description="Fallback value when extraction fails"),
        ]

        @u.computed_field()
        @property
        def resolved(self) -> t.Cli.TypedExtractValue:
            """Value coerced to type_kind, or default."""
            return self.resolve()

        def resolve(self) -> t.Cli.TypedExtractValue:
            """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
            if self.value is None:
                return self._default_for_kind()
            if self.type_kind == c.Cli.TypeKind.STR:
                s = str(self.value).strip() if self.value else ""
                return s or (self.default if isinstance(self.default, str) else "")
            if self.type_kind == c.Cli.TypeKind.BOOL:
                return bool(self.value)
            if self.type_kind == c.Cli.TypeKind.DICT:
                if isinstance(self.value, Mapping):
                    return {
                        str(k): t.Cli.JSON_VALUE_ADAPTER.validate_python(vv)
                        for k, vv in self.value.items()
                    }
                if isinstance(self.default, Mapping):
                    return {
                        str(k): t.Cli.JSON_VALUE_ADAPTER.validate_python(vv)
                        for k, vv in self.default.items()
                    }
                return {}
            return self._default_for_kind()

        def _default_for_kind(self) -> t.Cli.TypedExtractValue:
            """Return default typed value for the requested kind."""
            if self.type_kind == c.Cli.TypeKind.STR:
                return self.default if isinstance(self.default, str) else ""
            if self.type_kind == c.Cli.TypeKind.BOOL:
                return self.default if isinstance(self.default, bool) else False
            if isinstance(self.default, Mapping):
                return {
                    str(k): t.Cli.JSON_VALUE_ADAPTER.validate_python(vv)
                    for k, vv in self.default.items()
                }
            return {}


__all__: list[str] = [
    "FlextCliModelsBase",
]
