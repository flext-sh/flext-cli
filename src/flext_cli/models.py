"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import (
    Annotated,
    ClassVar,
)

from flext_core import FlextModels, r
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from flext_cli import FlextCliModelsSystemContext, c, t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels.

    NAMESPACE HIERARCHY PADRAO:
    ───────────────────────────
    1. Heranca real de FlextModels, SEM BaseModel direto
    2. Namespace hierarquico: FlextCliModels.Cli.Entity, FlextCliModels.Cli.Value, etc.
    3. SEM duplicacao de declaracoes ou aliases de raiz
    4. ConfigDict frozen=True, extra="forbid"
    5. StrEnum de constants, nao criar novos
    6. field_validator para validacao complexa
    7. Self para metodos de transformacao
    """

    class Cli(FlextCliModelsSystemContext):
        """CLI project namespace - PADRAO HIERARQUICO.

        Este namespace contem todos os modelos CLI especificos do flext-cli.
        PADRAO: Namespace hierarquico completo, sem duplicacao.
        """

        class DisplayData(BaseModel):
            """Key-value data for table/display — Pydantic v2 contract. Use m.Cli.DisplayData."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            data: Annotated[
                t.Cli.JsonValue,
                Field(
                    description="Field-value pairs for display",
                ),
            ] = Field(default_factory=dict)

        class CommandEntryModel(BaseModel):
            """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True,
                extra="forbid",
            )
            name: Annotated[t.NonEmptyStr, Field(..., description="Command name")]
            handler: Annotated[
                Callable[..., r[t.Cli.JsonValue]],
                Field(..., description="Command handler callable"),
            ]

        # CRÍTICO: NÃO redeclarar classes base de flext-core (Entity, Value, AggregateRoot, etc.)
        # Elas vêm automaticamente via herança: FlextCliModels(FlextModels)
        # APENAS declarar modelos CLI-ESPECÍFICOS que estendem as bases

        class TableConfig(FlextModels.Value):
            """Table display configuration for tabulate extending Value via inheritance.

            Fields map directly to tabulate() parameters.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            # Headers configuration
            headers: Annotated[
                str | t.StrSequence,
                Field(
                    description=(
                        "Table headers (string like 'keys', 'firstrow' "
                        "or sequence of header names)"
                    ),
                ),
            ] = "keys"
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
            showindex: Annotated[
                bool | str | Sequence[str | int],
                Field(description="Whether to show row indices"),
            ] = False

            # Column alignment
            colalign: Annotated[
                t.StrSequence | None,
                Field(
                    description="Per-column alignment (left, center, right, decimal)",
                ),
            ] = None

            # Number parsing
            disable_numparse: Annotated[
                bool | Sequence[int],
                Field(
                    description="Disable number parsing (bool or list of column indices)",
                ),
            ] = False

        class ConfigSnapshot(FlextModels.Value):
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

        class CliParamsConfig(FlextModels.Value):
            """CLI parameters configuration for command-line parsing.

            Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
            All fields are optional (None) to allow partial updates.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
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
            def params(self) -> Mapping[str, t.Cli.JsonValue]:
                """Parameters mapping - required by CliParamsConfig."""
                return {
                    "verbose": bool(self.verbose)
                    if self.verbose is not None
                    else False,
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

        class OptionConfig(FlextModels.Value):
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

        class ConfirmConfig(FlextModels.Value):
            """Configuration for confirm prompts.

            Used with confirm() method to reduce argument counts.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
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

        class PromptConfig(FlextModels.Value):
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
                Callable[[t.Cli.JsonValue], t.Cli.JsonValue] | None,
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


__all__ = [
    "FlextCliModels",
    "m",
]

m = FlextCliModels
