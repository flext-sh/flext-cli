"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.NormalizedValue as data contracts.
Reuse FlextTestsModels types where possible; add test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Annotated, ClassVar, Literal, Self

from flext_tests import FlextTestsModels
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from flext_cli import FlextCliModels, t


class FlextCliTestModels(FlextTestsModels, FlextCliModels):
    """Test namespace facade for flext-cli models. Use m alias; preserves all test model types."""

    class Cli(FlextCliModels.Cli):
        """CLI models with test-specific extensions."""

        class Test:
            """Test-specific model definitions."""

            class PositionalModel(BaseModel):
                """Model accepting positional data for test scenarios."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

                def __init__(
                    self,
                    data: Mapping[str, t.ContainerValue] | None = None,
                    /,
                    **kwargs: t.ContainerValue,
                ) -> None:
                    payload: dict[str, t.ContainerValue] = {}
                    if data is not None:
                        payload.update(data)
                    payload.update(kwargs)
                    super().__init__(**payload)

            class CliCommandInput(PositionalModel):
                """Test input for building CliCommand via model_construct. All optional with defaults."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                unique_id: Annotated[str, Field(default="test-cmd-0")]
                name: Annotated[str, Field(default="test_command")]
                description: Annotated[str, Field(default="Test command description")]
                status: Annotated[str, Field(default="pending")]
                created_at: Annotated[datetime | None, Field(default=None)]
                command_line: Annotated[str, Field(default="test_command")]
                args: t.StrSequence = Field(default_factory=list)
                result: Annotated[t.NormalizedValue, Field(default=None)]
                kwargs: Annotated[
                    Mapping[str, t.ContainerValue],
                    Field(default_factory=dict),
                ]

            class CliSessionInput(PositionalModel):
                """Test input for building CliSession via model_construct. All optional with defaults."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                session_id: Annotated[str, Field(default="test-session-0")]
                status: Annotated[str, Field(default="active")]
                created_at: Annotated[datetime | None, Field(default=None)]

            type _ScalarOnly = t.Primitives | None

            class ScalarConfigRestore(RootModel[Mapping[str, t.Primitives | None]]):
                """Holds scalar-only config for container restore in fixtures. Filters nested values out."""

                @classmethod
                def from_config_items(cls, items: t.ContainerMapping) -> Self:
                    """Build scalar-only dict from config items (drops nested dict/list/model)."""
                    out: Mapping[str, t.Primitives | None] = {
                        k: v
                        for k, v in items.items()
                        if v is None or isinstance(v, (str, int, float, bool))
                    }
                    return cls(out)

            class TextTestCaseDict(PositionalModel):
                """Parametrized test case for prompt_text — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                message: Annotated[str, Field(default="", description="Prompt message")]
                default: Annotated[str, Field(default="", description="Default value")]
                validation_pattern: Annotated[
                    str | None,
                    Field(
                        default=None,
                        description="Regex pattern",
                    ),
                ]
                expected_success: Annotated[
                    bool,
                    Field(
                        default=True,
                        description="Expect success",
                    ),
                ]

            class ConfirmTestCaseDict(PositionalModel):
                """Parametrized test case for prompt_confirmation — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                message: Annotated[str, Field(default="", description="Prompt message")]
                default: Annotated[
                    bool,
                    Field(default=False, description="Default value"),
                ]
                expected_value: Annotated[
                    bool,
                    Field(
                        default=False,
                        description="Expected result",
                    ),
                ]

            class ChoiceTestCaseDict(PositionalModel):
                """Parametrized test case for prompt_choice — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                message: Annotated[str, Field(default="", description="Prompt message")]
                choices: Annotated[
                    t.StrSequence,
                    Field(
                        description="Choice list",
                    ),
                ] = Field(default_factory=list)
                default: Annotated[
                    str | None,
                    Field(default=None, description="Default choice"),
                ]
                expected_success: Annotated[
                    bool,
                    Field(
                        default=True,
                        description="Expect success",
                    ),
                ]

            class PrintStatusCase(PositionalModel):
                """Parametrized test case for print_status — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                message: Annotated[str, Field(default="", description="Message")]
                status: Annotated[
                    str | None,
                    Field(default=None, description="Status type"),
                ]

            class UserData(PositionalModel):
                """User data for type scenario tests — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                id: Annotated[int, Field(description="User id")]
                name: Annotated[str, Field(description="User name")]
                email: Annotated[str, Field(description="Email")]
                active: Annotated[bool, Field(description="Active flag")]

            class ApiResponse(PositionalModel):
                """API response for type scenario tests — Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                status: Annotated[str, Field(description="Status")]
                data: Annotated[
                    t.NormalizedValue,
                    Field(default=None, description="Payload"),
                ]
                message: Annotated[str, Field(description="Message")]
                error: Annotated[str | None, Field(default=None, description="Error")]

            # ----- Model-command comprehensive tests (test_model_command_comprehensive.py) -----

            class ConnectionConfig(PositionalModel):
                """Connection config for model_command tests; port validated by t.PortNumber (1-65535)."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                host: Annotated[str | None, Field(default=None, description="Host")]
                port: Annotated[t.PortNumber, Field(default=5432, description="Port")]
                username: Annotated[str, Field(default="", description="Username")]

            class EnvironmentConfig(PositionalModel):
                """Environment config with Literal types for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                environment: Annotated[
                    Literal["dev", "prod", "staging"],
                    Field(
                        default="dev",
                        description="Environment",
                    ),
                ]

            class OptionalLiteralConfig(PositionalModel):
                """Config with Optional Literal for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                log_level: Annotated[
                    Literal["debug", "info", "warning", "error"] | None,
                    Field(
                        default=None,
                        description="Log level",
                    ),
                ]

            class AliasedConfig(PositionalModel):
                """Config with field aliases and populate_by_name for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(
                    extra="forbid",
                    populate_by_name=True,
                )
                input_dir: Annotated[
                    str,
                    Field(
                        default="",
                        alias="input-dir",
                        description="Input dir",
                    ),
                ]
                output_dir: Annotated[
                    str,
                    Field(
                        default="",
                        alias="output-dir",
                        description="Output dir",
                    ),
                ]

            class BooleanFlagsConfig(PositionalModel):
                """Config with boolean flags (default True/False/None) for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                enable_cache: Annotated[
                    bool,
                    Field(default=True, description="Enable cache"),
                ]
                verbose: Annotated[bool, Field(default=False, description="Verbose")]
                force: Annotated[bool | None, Field(default=None, description="Force")]

            class NestedModelConfig(PositionalModel):
                """Config with nested model for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

                class Inner(BaseModel):
                    """Inner key-value config for NestedModelConfig."""

                    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                    key: Annotated[str, Field(default="", description="Key")]
                    value: Annotated[int, Field(default=0, description="Value")]

                inner: Annotated[
                    Inner,
                    Field(description="Nested config"),
                ] = Field(
                    default_factory=lambda: (
                        FlextCliTestModels.Cli.Test.NestedModelConfig.Inner(
                            key="", value=0
                        )
                    )
                )

            class ValidatedConfig(PositionalModel):
                """Config with custom host validator for model_command tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                host: Annotated[
                    str,
                    Field(default="", description="Host (e.g. example.com)"),
                ]
                port: Annotated[t.PortNumber, Field(default=5432, description="Port")]

                @field_validator("host")
                @classmethod
                def host_not_invalid(cls, v: str) -> str:
                    msg = "host must not be 'invalid'"
                    if v == "invalid":
                        raise ValueError(msg)
                    return v

            # ----- Config model integration tests (test_config_model_integration.py) -----

            class AliasedParams(PositionalModel):
                """Params with field aliases for config model integration tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(
                    extra="forbid",
                    populate_by_name=True,
                )
                input_dir: Annotated[str | None, Field(default=None, alias="input-dir")]
                output_dir: Annotated[
                    str | None,
                    Field(default=None, alias="output-dir"),
                ]
                batch_size: Annotated[int, Field(default=0, alias="batch-size")]

            class RequiredFieldsParams(PositionalModel):
                """Params with required input_dir for config model integration tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                input_dir: Annotated[str, Field(..., description="Input directory")]
                output_dir: Annotated[
                    str | None,
                    Field(
                        default=None,
                        description="Output directory",
                    ),
                ]

            class AppParams(PositionalModel):
                """App params (input_dir, output_dir optional) for config model integration tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                input_dir: Annotated[str | None, Field(default=None)]
                output_dir: Annotated[str | None, Field(default=None)]

            class SimpleParams(PositionalModel):
                """Minimal params for model_command without config."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                name: Annotated[str, Field(default="", description="Name")]

            class FullAppParams(PositionalModel):
                """Full app params for config-to-params workflow tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                input_dir: Annotated[str, Field(default="")]
                output_dir: Annotated[str, Field(default="")]
                batch_size: Annotated[int, Field(default=0)]
                verbose_mode: Annotated[bool, Field(default=False)]

            class StrictParams(PositionalModel):
                """Params for strict validation tests."""

                model_config: ClassVar[ConfigDict] = ConfigDict(
                    extra="forbid",
                    strict=True,
                )
                name: Annotated[str, Field(default="")]
                count: Annotated[int, Field(default=0)]

            class ForbidExtraParams(PositionalModel):
                """Params that forbid extra fields."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                name: Annotated[str, Field(default="", description="Name")]


m = FlextCliTestModels

__all__ = [
    "FlextCliTestModels",
    "m",
]
