"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/object as data contracts.
Reuse m.Cli types where possible; add test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Literal

from flext_tests import FlextTestsModels
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from flext_cli import t


class CliCommandInput(BaseModel):
    """Test input for building CliCommand via model_construct. All optional with defaults."""

    model_config = ConfigDict(extra="forbid")
    unique_id: str = Field(default="test-cmd-0")
    name: str = Field(default="test_command")
    description: str = Field(default="Test command description")
    status: str = Field(default="pending")
    created_at: datetime | None = Field(default=None)
    command_line: str = Field(default="test_command")
    args: Sequence[str] = Field(default_factory=list)
    result: t.JsonValue | None = Field(default=None)
    kwargs: dict[str, t.JsonValue] = Field(default_factory=dict)


class CliSessionInput(BaseModel):
    """Test input for building CliSession via model_construct. All optional with defaults."""

    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(default="test-session-0")
    status: str = Field(default="active")
    created_at: datetime | None = Field(default=None)


_ScalarOnly = str | int | float | bool | None


class ScalarConfigRestore(RootModel[dict[str, _ScalarOnly]]):
    """Holds scalar-only config for container restore in fixtures. Filters nested values out."""

    @classmethod
    def from_config_items(
        cls, items: Mapping[str, t.ContainerValue]
    ) -> ScalarConfigRestore:
        """Build scalar-only dict from config items (drops nested dict/list/model)."""
        out: dict[str, _ScalarOnly] = {
            k: v
            for k, v in items.items()
            if v is None or isinstance(v, (str, int, float, bool))
        }
        return cls.model_validate(out)


class TextTestCaseDict(BaseModel):
    """Parametrized test case for prompt_text — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(default="", description="Prompt message")
    default: str = Field(default="", description="Default value")
    validation_pattern: str | None = Field(default=None, description="Regex pattern")
    expected_success: bool = Field(default=True, description="Expect success")


class ConfirmTestCaseDict(BaseModel):
    """Parametrized test case for prompt_confirmation — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(default="", description="Prompt message")
    default: bool = Field(default=False, description="Default value")
    expected_value: bool = Field(default=False, description="Expected result")


class ChoiceTestCaseDict(BaseModel):
    """Parametrized test case for prompt_choice — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(default="", description="Prompt message")
    choices: list[str] = Field(default_factory=list, description="Choice list")
    default: str | None = Field(default=None, description="Default choice")
    expected_success: bool = Field(default=True, description="Expect success")


class PrintStatusCase(BaseModel):
    """Parametrized test case for print_status — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(default="", description="Message")
    status: str | None = Field(default=None, description="Status type")


class UserData(BaseModel):
    """User data for type scenario tests — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    id: int = Field(description="User id")
    name: str = Field(description="User name")
    email: str = Field(description="Email")
    active: bool = Field(description="Active flag")


class ApiResponse(BaseModel):
    """API response for type scenario tests — Pydantic v2."""

    model_config = ConfigDict(extra="forbid")
    status: str = Field(description="Status")
    data: t.JsonValue = Field(description="Payload")
    message: str = Field(description="Message")
    error: str | None = Field(default=None, description="Error")


# ----- Model-command comprehensive tests (test_model_command_comprehensive.py) -----


class ConnectionConfig(BaseModel):
    """Connection config for model_command tests; port ge=1024."""

    model_config = ConfigDict(extra="forbid")
    host: str | None = Field(default=None, description="Host")
    port: int = Field(default=5432, ge=1024, description="Port")
    username: str = Field(default="", description="Username")


class EnvironmentConfig(BaseModel):
    """Environment config with Literal types for model_command tests."""

    model_config = ConfigDict(extra="forbid")
    environment: Literal["dev", "prod", "staging"] = Field(
        default="dev", description="Environment"
    )


class OptionalLiteralConfig(BaseModel):
    """Config with Optional Literal for model_command tests."""

    model_config = ConfigDict(extra="forbid")
    log_level: Literal["debug", "info", "warning", "error"] | None = Field(
        default=None, description="Log level"
    )


class AliasedConfig(BaseModel):
    """Config with field aliases and populate_by_name for model_command tests."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    input_dir: str = Field(default="", alias="input-dir", description="Input dir")
    output_dir: str = Field(default="", alias="output-dir", description="Output dir")


class BooleanFlagsConfig(BaseModel):
    """Config with boolean flags (default True/False/None) for model_command tests."""

    model_config = ConfigDict(extra="forbid")
    enable_cache: bool = Field(default=True, description="Enable cache")
    verbose: bool = Field(default=False, description="Verbose")
    force: bool | None = Field(default=None, description="Force")


class NestedModelConfig(BaseModel):
    """Config with nested model for model_command tests."""

    model_config = ConfigDict(extra="forbid")

    class Inner(BaseModel):
        """Inner key-value config for NestedModelConfig."""

        model_config = ConfigDict(extra="forbid")
        key: str = Field(default="", description="Key")
        value: int = Field(default=0, description="Value")

    inner: Inner = Field(default_factory=Inner, description="Nested config")


class ValidatedConfig(BaseModel):
    """Config with custom host validator for model_command tests."""

    model_config = ConfigDict(extra="forbid")
    host: str = Field(default="", description="Host (e.g. example.com)")
    port: int = Field(default=5432, description="Port")

    @field_validator("host")
    @classmethod
    def host_not_invalid(cls, v: str) -> str:
        msg = "host must not be 'invalid'"
        if v == "invalid":
            raise ValueError(msg)
        return v


# ----- Config model integration tests (test_config_model_integration.py) -----


class AliasedParams(BaseModel):
    """Params with field aliases for config model integration tests."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    input_dir: str | None = Field(default=None, alias="input-dir")
    output_dir: str | None = Field(default=None, alias="output-dir")
    batch_size: int = Field(default=0, alias="batch-size")


class RequiredFieldsParams(BaseModel):
    """Params with required input_dir for config model integration tests."""

    model_config = ConfigDict(extra="forbid")
    input_dir: str = Field(..., description="Input directory")
    output_dir: str | None = Field(default=None, description="Output directory")


class AppParams(BaseModel):
    """App params (input_dir, output_dir optional) for config model integration tests."""

    model_config = ConfigDict(extra="forbid")
    input_dir: str | None = Field(default=None)
    output_dir: str | None = Field(default=None)


class SimpleParams(BaseModel):
    """Minimal params for model_command without config."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="", description="Name")


class FullAppParams(BaseModel):
    """Full app params for config-to-params workflow tests."""

    model_config = ConfigDict(extra="forbid")
    input_dir: str = Field(default="")
    output_dir: str = Field(default="")
    batch_size: int = Field(default=0)
    verbose_mode: bool = Field(default=False)


class StrictParams(BaseModel):
    """Params for strict validation tests."""

    model_config = ConfigDict(extra="forbid", strict=True)
    name: str = Field(default="")
    count: int = Field(default=0)


class ForbidExtraParams(BaseModel):
    """Params that forbid extra fields."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="", description="Name")


_CliCommandInputModel = CliCommandInput
_CliSessionInputModel = CliSessionInput
_ScalarConfigRestoreModel = ScalarConfigRestore
_TextTestCaseDictModel = TextTestCaseDict
_ConfirmTestCaseDictModel = ConfirmTestCaseDict
_ChoiceTestCaseDictModel = ChoiceTestCaseDict
_PrintStatusCaseModel = PrintStatusCase
_UserDataModel = UserData
_ApiResponseModel = ApiResponse
_ConnectionConfigModel = ConnectionConfig
_EnvironmentConfigModel = EnvironmentConfig
_OptionalLiteralConfigModel = OptionalLiteralConfig
_AliasedConfigModel = AliasedConfig
_BooleanFlagsConfigModel = BooleanFlagsConfig
_NestedModelConfigModel = NestedModelConfig
_ValidatedConfigModel = ValidatedConfig
_AliasedParamsModel = AliasedParams
_RequiredFieldsParamsModel = RequiredFieldsParams
_AppParamsModel = AppParams
_SimpleParamsModel = SimpleParams
_FullAppParamsModel = FullAppParams
_StrictParamsModel = StrictParams
_ForbidExtraParamsModel = ForbidExtraParams


class TestsFlextCliModels(FlextTestsModels):
    """Test namespace facade for flext-cli models. Use tm alias; m is flext_cli.FlextCliModels."""

    CliCommandInput = _CliCommandInputModel
    CliSessionInput = _CliSessionInputModel
    ScalarConfigRestore = _ScalarConfigRestoreModel
    TextTestCaseDict = _TextTestCaseDictModel
    ConfirmTestCaseDict = _ConfirmTestCaseDictModel
    ChoiceTestCaseDict = _ChoiceTestCaseDictModel
    PrintStatusCase = _PrintStatusCaseModel
    UserData = _UserDataModel
    ApiResponse = _ApiResponseModel
    ConnectionConfig = _ConnectionConfigModel
    EnvironmentConfig = _EnvironmentConfigModel
    OptionalLiteralConfig = _OptionalLiteralConfigModel
    AliasedConfig = _AliasedConfigModel
    BooleanFlagsConfig = _BooleanFlagsConfigModel
    NestedModelConfig = _NestedModelConfigModel
    ValidatedConfig = _ValidatedConfigModel
    AliasedParams = _AliasedParamsModel
    RequiredFieldsParams = _RequiredFieldsParamsModel
    AppParams = _AppParamsModel
    SimpleParams = _SimpleParamsModel
    FullAppParams = _FullAppParamsModel
    StrictParams = _StrictParamsModel
    ForbidExtraParams = _ForbidExtraParamsModel


tm = TestsFlextCliModels

__all__ = [
    "AliasedConfig",
    "AliasedParams",
    "ApiResponse",
    "AppParams",
    "BooleanFlagsConfig",
    "ChoiceTestCaseDict",
    "CliCommandInput",
    "CliSessionInput",
    "ConfirmTestCaseDict",
    "ConnectionConfig",
    "EnvironmentConfig",
    "ForbidExtraParams",
    "FullAppParams",
    "NestedModelConfig",
    "OptionalLiteralConfig",
    "PrintStatusCase",
    "RequiredFieldsParams",
    "ScalarConfigRestore",
    "SimpleParams",
    "StrictParams",
    "TestsFlextCliModels",
    "TextTestCaseDict",
    "UserData",
    "ValidatedConfig",
    "tm",
]
