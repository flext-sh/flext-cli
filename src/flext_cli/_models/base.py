"""CLI Pydantic domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Annotated,
    ClassVar,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue as PydanticJsonValue,
    RootModel,
    computed_field,
)

from flext_cli import c, p, t
from flext_core import m


class FlextCliModelsBase:
    """CLI project namespace."""

    class DisplayData(BaseModel):
        """Key-value data for table/display — Pydantic v2 contract. Use m.Cli.DisplayData."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        data: Annotated[
            t.ContainerMapping,
            Field(
                description="Field-value pairs for display",
            ),
        ] = Field(default_factory=dict)

    class LoadedConfig(BaseModel):
        """Loaded configuration content wrapper — Pydantic v2 contract. Use m.Cli.LoadedConfig."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        content: Annotated[
            t.ContainerMapping,
            Field(
                description="Loaded configuration content (dict or other JSON value)",
            ),
        ] = Field(default_factory=dict)

    class CliNormalizedJson(RootModel[PydanticJsonValue]):
        """Normalize raw JSON value. Use m.Cli.CliNormalizedJson(value).root."""

    class NormalizedJsonDict(BaseModel):
        """Resolve normalized JSON to a dict with defaults. Use m.Cli.NormalizedJsonDict."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        value: Annotated[
            t.Cli.JsonValue,
            Field(description="The normalized JSON value"),
        ] = Field(default_factory=dict)
        default: Annotated[
            t.Cli.JsonMapping,
            Field(description="Default mapping if value is not a dict"),
        ] = Field(default_factory=dict)

        @property
        def resolved(self) -> t.Cli.JsonMapping:
            """Resolve value to dict or return default."""
            if isinstance(self.value, dict):
                return self.value
            return self.default

    class SuccessSummaryDetails(RootModel[Mapping[str, str]]):
        """Key-value success summary details. Use m.Cli.SuccessSummaryDetails."""

    class CommandEntryModel(BaseModel):
        """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
        )
        name: Annotated[t.NonEmptyStr, Field(..., description="Command name")]
        handler: Annotated[
            t.Cli.JsonCommandFn,
            Field(..., description="Command handler callable"),
        ]

    class ResultCommandRoute(BaseModel):
        """Type-erased route contract for heterogeneous batch registration."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,
        )
        name: Annotated[t.NonEmptyStr, Field(..., description="Command name")]
        help_text: Annotated[str, Field(..., description="User-facing help text")]
        model_cls: Annotated[
            type[BaseModel],
            Field(..., description="Pydantic input model class"),
        ]
        handler: Annotated[
            t.Cli.CliCommand,
            Field(..., description="Command handler returning r[...]"),
        ]
        failure_message: Annotated[
            str,
            Field(..., description="Fallback error message on handler failure"),
        ]
        success_message: Annotated[
            str | None,
            Field(default=None, description="Static success message"),
        ] = None
        success_formatter: Annotated[
            p.Cli.SuccessMessageFormatter[t.Cli.ValueOrModel] | None,
            Field(default=None, description="Dynamic success formatter"),
        ] = None
        success_type: Annotated[
            str,
            Field(default="success", description="CLI output style on success"),
        ] = "success"

    class TableConfig(m.Value):
        """Table display configuration for tabulate extending Value via inheritance.

        Fields map directly to tabulate() parameters.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        # Headers configuration
        headers: Annotated[
            t.Cli.TableHeaders,
            Field(
                description=(
                    "Table headers (string like 'keys', 'firstrow' "
                    "or sequence of header names)"
                ),
            ),
        ] = "keys"
        title: Annotated[
            str | None,
            Field(description="Optional title printed before the rendered table"),
        ] = None
        show_header: Annotated[
            bool,
            Field(description="Whether to show table header"),
        ] = True

        # Format configuration
        table_format: Annotated[
            str,
            Field(
                description="Table format (simple, grid, fancy_grid, pipe, orgtbl, etc.)",
            ),
        ] = "simple"

        # Number formatting
        floatfmt: Annotated[
            str,
            Field(description="Float format string"),
        ] = ".4g"
        numalign: Annotated[
            str,
            Field(description="Number alignment (right, center, left, decimal)"),
        ] = "decimal"

        # String formatting
        stralign: Annotated[
            str,
            Field(description="String alignment (left, center, right)"),
        ] = "left"

        align: Annotated[
            str,
            Field(description="General alignment (left, center, right, decimal)"),
        ] = "left"

        # Missing values
        missingval: Annotated[
            str,
            Field(description="String to use for missing values"),
        ] = ""

        # Index display
        showindex: t.Cli.TableShowIndex = Field(
            default=False, description="Whether to show row indices"
        )

        # Column alignment
        colalign: Annotated[
            t.StrSequence | None,
            Field(
                description="Per-column alignment (left, center, right, decimal)",
            ),
        ] = None

        # Number parsing
        disable_numparse: t.Cli.TableDisableNumparse = Field(
            default=False,
            description="Disable number parsing (bool or list of column indices)",
        )

    class ConfigSnapshot(m.Value):
        """Snapshot of current CLI configuration information."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            frozen=True,
            extra="forbid",
        )

        config_dir: Annotated[
            str,
            Field(
                default="",
                description="Configuration directory path",
            ),
        ]

        config_exists: Annotated[
            bool,
            Field(
                default=False,
                description="Whether config directory exists",
            ),
        ]

        config_readable: Annotated[
            bool,
            Field(
                default=False,
                description="Whether config directory is readable",
            ),
        ]

        config_writable: Annotated[
            bool,
            Field(
                default=False,
                description="Whether config directory is writable",
            ),
        ]

        timestamp: Annotated[
            str,
            Field(
                default="",
                description="Timestamp of snapshot",
            ),
        ]

    class CliParamsConfig(m.Value):
        """CLI parameters configuration for command-line parsing.

        Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
        All fields are optional (None) to allow partial updates.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        verbose: Annotated[
            bool | None,
            Field(
                default=None,
                description="Enable verbose output",
            ),
        ]
        quiet: Annotated[
            bool | None,
            Field(
                default=None,
                description="Suppress non-essential output",
            ),
        ]
        debug: Annotated[
            bool | None,
            Field(default=None, description="Enable debug mode"),
        ]
        trace: Annotated[
            bool | None,
            Field(
                default=None,
                description="Enable trace logging (requires debug)",
            ),
        ]
        log_level: Annotated[
            str | None,
            Field(
                default=None,
                description="Log level (DEBUG, INFO, WARNING, ERROR)",
            ),
        ]
        log_format: Annotated[
            str | None,
            Field(
                default=None,
                description="Log format (compact, detailed, full)",
            ),
        ]
        output_format: Annotated[
            str | None,
            Field(
                default=None,
                description="Output format (table, json, yaml, csv)",
            ),
        ]
        no_color: Annotated[
            bool | None,
            Field(
                default=None,
                description="Disable colored output",
            ),
        ]

        @property
        def params(self) -> t.Cli.JsonMapping:
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

        model_config: ClassVar[ConfigDict] = ConfigDict(
            frozen=True,
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        default: Annotated[
            t.Cli.JsonValue | None,
            Field(
                default=None,
                description="Default value",
            ),
        ]
        type_hint: Annotated[
            t.Cli.JsonValue | None,
            Field(
                default=None,
                description="Parameter type (Click type or Python type)",
            ),
        ]
        required: Annotated[
            bool,
            Field(
                default=False,
                description="Whether option is required",
            ),
        ]
        help_text: Annotated[
            str | None,
            Field(
                default=None,
                description="Help text for option",
            ),
        ]
        is_flag: Annotated[
            bool,
            Field(
                default=False,
                description="Whether this is a boolean flag",
            ),
        ]
        flag_value: Annotated[
            t.Cli.JsonValue | None,
            Field(
                default=None,
                description="Value when flag is set",
            ),
        ]
        multiple: Annotated[
            bool,
            Field(default=False, description="Allow multiple values"),
        ]
        count: Annotated[
            bool,
            Field(default=False, description="Count occurrences"),
        ]
        show_default: Annotated[
            bool,
            Field(
                default=False,
                description="Show default in help",
            ),
        ]

    class ConfirmConfig(m.Value):
        """Configuration for confirm prompts.

        Used with confirm() method to reduce argument counts.
        Inherits frozen=True and extra="forbid" from m.Value.
        """

        default: Annotated[bool, Field(default=False, description="Default value")]
        abort: Annotated[
            bool,
            Field(default=False, description="Abort if not confirmed"),
        ]
        prompt_suffix: Annotated[
            str,
            Field(
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                description="Suffix after prompt",
            ),
        ]
        show_default: Annotated[
            bool,
            Field(
                default=True,
                description="Show default in prompt",
            ),
        ]
        err: Annotated[bool, Field(default=False, description="Write to stderr")]

    class PromptConfig(m.Value):
        """Configuration for input prompts.

        Used with prompt() method to reduce argument counts.
        """

        model_config: ClassVar[ConfigDict] = ConfigDict(
            frozen=True,
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        default: Annotated[
            t.Cli.JsonValue | None,
            Field(
                default=None,
                description="Default value",
            ),
        ]
        type_hint: Annotated[
            t.Cli.JsonValue | None,
            Field(
                default=None,
                description="Value type",
            ),
        ]
        value_proc: Annotated[
            p.Cli.JsonValueProcessor | None,
            Field(
                default=None,
                description="Value processor function",
            ),
        ]
        prompt_suffix: Annotated[
            str,
            Field(
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                description="Suffix after prompt",
            ),
        ]
        hide_input: Annotated[
            bool,
            Field(default=False, description="Hide user input"),
        ]
        confirmation_prompt: Annotated[
            bool,
            Field(
                default=False,
                description="Ask for confirmation",
            ),
        ]
        show_default: Annotated[
            bool,
            Field(
                default=True,
                description="Show default in prompt",
            ),
        ]
        err: Annotated[bool, Field(default=False, description="Write to stderr")]
        show_choices: Annotated[
            bool,
            Field(
                default=True,
                description="Show available choices",
            ),
        ]

    class PromptTimeoutResolved(BaseModel):
        """Single contract: raw (int | str | None) + default -> int."""

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
        raw: Annotated[t.Cli.IntTextValue, Field(default=None)]
        default: Annotated[
            int,
            Field(default=30, description="Default timeout in seconds"),
        ]

        @computed_field
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

    class LogLevelResolved(BaseModel):
        """Single contract for log level string."""

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
        raw: Annotated[str | None, Field(default=None)]
        default: Annotated[str, Field(default="INFO")]

        @computed_field
        @property
        def resolved(self) -> str:
            """Resolved log level value."""
            return self.resolve()

        def resolve(self) -> str:
            """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
            s = (self.raw or self.default).strip().upper()
            return s or self.default

    class TypedExtract(BaseModel):
        """Single contract for typed value extraction (str | bool | dict)."""

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
        type_kind: Annotated[
            t.Cli.TypeKind,
            Field(description="Requested type"),
        ]
        value: Annotated[t.Cli.JsonValue | None, Field(default=None)]
        default: Annotated[t.Cli.JsonValue | None, Field(default=None)]

        @computed_field
        @property
        def resolved(self) -> t.Cli.TypedExtractValue:
            """Value coerced to type_kind, or default."""
            return self.resolve()

        def resolve(self) -> t.Cli.TypedExtractValue:
            """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
            if self.value is None:
                return self._default_for_kind()
            if self.type_kind == "str":
                s = str(self.value).strip() if self.value else ""
                return s or (self.default if isinstance(self.default, str) else None)
            if self.type_kind == "bool":
                return bool(self.value)
            if self.type_kind == "dict":
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
            if self.type_kind == "str":
                return self.default if isinstance(self.default, str) else None
            if self.type_kind == "bool":
                return self.default if isinstance(self.default, bool) else False
            if isinstance(self.default, Mapping):
                return {
                    str(k): t.Cli.JSON_VALUE_ADAPTER.validate_python(vv)
                    for k, vv in self.default.items()
                }
            return {}


__all__ = [
    "FlextCliModelsBase",
]
