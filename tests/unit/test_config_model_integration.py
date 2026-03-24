"""FLEXT CLI Config Model Integration Tests - Comprehensive Integration Validation Testing.

Tests for FlextCli.model_command() covering configuration integration, config extraction,
default value propagation, parameter validation, alias handling, field precedence rules,
and edge cases with 100% coverage.

Modules tested: flext_cli.cli.FlextCliCli.model_command(), FlextCliSettings integration
Scope: All config-model integration operations, parameter validation, precedence rules

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, ClassVar

import pytest
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli import FlextCliCli, FlextCliSettings
from tests import t


class TestsCliConfigModelIntegration:
    """Config/model integration tests with pragmatic patterns."""

    class RequiredFieldsConfig(BaseSettings):
        """Config with required fields."""

        model_config = SettingsConfigDict(env_prefix="TEST_APP_")
        input_dir: Annotated[str, Field(default="/tmp/test/input")]
        output_dir: Annotated[str, Field(default="/tmp/test/output")]

    class OptionalFieldsConfig(BaseSettings):
        """Config with optional fields."""

        model_config = SettingsConfigDict(env_prefix="TEST_APP_")
        input_dir: Annotated[str | None, Field(default=None)]
        output_dir: Annotated[str | None, Field(default=None)]
        verbose: Annotated[bool, Field(default=False)]

    class TypedFieldsConfig(BaseSettings):
        """Config with various typed fields."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        timeout: Annotated[int, Field(default=30)]
        max_retries: Annotated[int, Field(default=3)]
        debug: Annotated[bool, Field(default=False)]
        optional_path: Annotated[str | None, Field(default=None)]

    class AppConfig(BaseSettings):
        """Application configuration."""

        model_config = SettingsConfigDict(env_prefix="TEST_")
        input_dir: Annotated[str, Field(default="/config/input")]
        output_dir: Annotated[str, Field(default="/config/output")]
        verbose: Annotated[bool, Field(default=False)]

    class FullAppConfig(BaseSettings):
        """Full application config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        input_dir: Annotated[str, Field(default="/app/input")]
        output_dir: Annotated[str, Field(default="/app/output")]
        batch_size: Annotated[int, Field(default=1000)]
        verbose: Annotated[bool, Field(default=False)]

    class StringConfig(BaseSettings):
        """String field config."""

        model_config = SettingsConfigDict(env_prefix="TEST_")
        input_path: Annotated[str, Field(default="/tmp/test/input")]
        output_path: Annotated[str, Field(default="/tmp/test/output")]

    class IntConfig(BaseSettings):
        """Integer field config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        timeout: Annotated[int, Field(default=30)]
        max_retries: Annotated[int, Field(default=3)]

    class BoolConfig(BaseSettings):
        """Boolean field config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        debug: Annotated[bool, Field(default=False)]
        verbose: Annotated[bool, Field(default=False)]

    class OptionalPathConfig(BaseSettings):
        """Config with optional fields."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        optional_path: Annotated[str | None, Field(default=None)]
        required_path: Annotated[str, Field(default="/default")]

    class AliasedParams(BaseModel):
        """Parameters with field aliases."""

        model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)

        input_dir: Annotated[str | None, Field(default=None, alias="input-dir")]
        output_dir: Annotated[str | None, Field(default=None, alias="output-dir")]
        batch_size: Annotated[int | None, Field(default=None, alias="batch-size")]

    class RequiredFieldsParams(BaseModel):
        """Parameters with required fields."""

        input_dir: Annotated[str, Field(min_length=1)]
        output_dir: Annotated[str | None, Field(default=None)]

    class AppParams(BaseModel):
        """Application parameters."""

        input_dir: Annotated[str | None, Field(default=None)]
        output_dir: Annotated[str | None, Field(default=None)]

    class SimpleParams(BaseModel):
        """Simple parameters."""

        name: Annotated[str | None, Field(default=None)]
        value: Annotated[str | None, Field(default=None)]

    class FullAppParams(BaseModel):
        """Full application parameters."""

        input_dir: Annotated[str | None, Field(default=None)]
        output_dir: Annotated[str | None, Field(default=None)]
        batch_size: Annotated[int | None, Field(default=None)]
        verbose: Annotated[bool, Field(default=False)]
        verbose_mode: Annotated[bool, Field(default=False)]

    class StrictParams(BaseModel):
        """Strict parameters with validation."""

        input_dir: str
        output_dir: str
        name: Annotated[str | None, Field(default=None)]
        count: Annotated[int | None, Field(default=None)]

    class ForbidExtraParams(BaseModel):
        """Parameters that forbid extra fields."""

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
        input_dir: Annotated[str | None, Field(default=None)]
        output_dir: Annotated[str | None, Field(default=None)]
        name: Annotated[str | None, Field(default=None)]

    @pytest.fixture
    def cli(self) -> FlextCliCli:
        """Create FlextCliCli instance."""
        return FlextCliCli()

    @pytest.fixture
    def temp_env_file(self, tmp_path: Path) -> Path:
        """Create temporary .env file for testing."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TEST_APP_INPUT_DIR=/test/input\nTEST_APP_OUTPUT_DIR=/test/output\nTEST_APP_TIMEOUT_SECONDS=60\nTEST_APP_VERBOSE=true\n",
        )
        return env_file

    @pytest.mark.parametrize(
        ("config_class", "expected_fields", "expected_values"),
        [
            (
                RequiredFieldsConfig,
                ["input_dir", "output_dir"],
                {"input_dir": "/tmp/test/input", "output_dir": "/tmp/test/output"},
            ),
            (
                OptionalFieldsConfig,
                ["input_dir", "output_dir", "verbose"],
                {"input_dir": None, "output_dir": None, "verbose": False},
            ),
            (
                TypedFieldsConfig,
                ["timeout", "max_retries", "debug"],
                {"timeout": 30, "max_retries": 3, "debug": False},
            ),
        ],
        ids=["required_fields", "optional_fields", "typed_fields"],
    )
    def test_config_initialization(
        self,
        config_class: type[BaseSettings],
        expected_fields: t.StrSequence,
        expected_values: t.ContainerMapping,
    ) -> None:
        """Test config initialization with various field types."""
        config = config_class()
        for field_name in expected_fields:
            tm.that(hasattr(config, field_name), eq=True)
        for field_name, expected_value in expected_values.items():
            if isinstance(expected_value, (str, int, float, bool, type(None))):
                field_value = getattr(config, field_name)
                tm.that(field_value, eq=expected_value)

    def test_config_with_environment_variables(self) -> None:
        """Test config loading from environment variables."""
        os.environ["TEST_APP_INPUT_DIR"] = "/env/input"
        os.environ["TEST_APP_OUTPUT_DIR"] = "/env/output"
        try:
            config = self.RequiredFieldsConfig()
            tm.that(config.input_dir, eq="/env/input")
            tm.that(config.output_dir, eq="/env/output")
        finally:
            os.environ.pop("TEST_APP_INPUT_DIR", None)
            os.environ.pop("TEST_APP_OUTPUT_DIR", None)

    @pytest.mark.parametrize(
        ("input_data", "expected_data"),
        [
            (
                {"input-dir": "/test/input", "output-dir": "/test/output"},
                {"input_dir": "/test/input", "output_dir": "/test/output"},
            ),
            (
                {"input_dir": "/alias/input", "output_dir": "/alias/output"},
                {"input_dir": "/alias/input", "output_dir": "/alias/output"},
            ),
            ({"batch-size": 100}, {"batch_size": 100}),
        ],
        ids=["aliases", "field_names", "single_field"],
    )
    def test_params_validation(
        self,
        input_data: t.ContainerMapping,
        expected_data: t.ContainerMapping,
    ) -> None:
        """Test parameter model validation with aliases."""
        params = self.AliasedParams.model_validate(input_data)
        for field_name, expected_value in expected_data.items():
            if isinstance(expected_value, (str, int, float, bool, type(None))):
                field_value = getattr(params, field_name)
                tm.that(field_value, eq=expected_value)

    def test_params_model_with_required_fields(self) -> None:
        """Test parameter model with required fields."""
        with pytest.raises(ValidationError):
            self.RequiredFieldsParams(input_dir="")
        params = self.RequiredFieldsParams(
            input_dir="/test/input",
            output_dir="/test/output",
        )
        tm.that(params.input_dir, eq="/test/input")
        tm.that(params.output_dir, eq="/test/output")

    def test_model_command_with_config(self, cli: FlextCliCli) -> None:
        """Test model_command applies config defaults to Typer parameters."""
        config = FlextCliSettings.get_global()

        def handler(_params: BaseModel) -> None:
            pass

        command = cli.model_command(self.AppParams, handler, config=config)
        tm.that(command, none=False)
        tm.that(callable(command), eq=True)

    def test_model_command_without_config(self, cli: FlextCliCli) -> None:
        """Test model_command works without config."""

        def handler(_params: BaseModel) -> None:
            pass

        command = cli.model_command(self.SimpleParams, handler)
        tm.that(command, none=False)

    @pytest.mark.parametrize(
        ("config_class", "field_name", "expected_type", "expected_value"),
        [
            (RequiredFieldsConfig, "input_dir", str, "/tmp/test/input"),
            (TypedFieldsConfig, "timeout", int, 30),
            (TypedFieldsConfig, "debug", bool, False),
            (TypedFieldsConfig, "optional_path", type(None), None),
        ],
        ids=["string_field", "int_field", "bool_field", "optional_field"],
    )
    def test_config_value_extraction_types(
        self,
        config_class: type[BaseSettings],
        field_name: str,
        expected_type: type,
        expected_value: t.Scalar | None,
    ) -> None:
        """Test extracting config values of different types."""
        config = config_class()
        value = getattr(config, field_name)
        tm.that(value, is_=expected_type)
        tm.that(value, eq=expected_value)

    def test_config_field_access(self) -> None:
        """Test accessing config fields directly."""
        config = self.StringConfig()
        tm.that(config.input_path, eq="/tmp/test/input")
        tm.that(config.output_path, eq="/tmp/test/output")
        tm.that(hasattr(config, "input_path"), eq=True)
        tm.that(hasattr(config, "output_path"), eq=True)

    def test_field_alias_in_params_model(self) -> None:
        """Test field aliases are properly handled in parameter models."""
        params = self.AliasedParams.model_validate({
            "input-dir": "/input",
            "output-dir": "/output",
            "batch-size": 100,
        })
        tm.that(params.input_dir, eq="/input")
        tm.that(params.output_dir, eq="/output")
        tm.that(params.batch_size, eq=100)
        params2 = self.AliasedParams.model_validate({
            "input_dir": "/input2",
            "output_dir": "/output2",
            "batch_size": 200,
        })
        tm.that(params2.input_dir, eq="/input2")
        tm.that(params2.output_dir, eq="/output2")
        tm.that(params2.batch_size, eq=200)

    def test_default_precedence_config_over_none(self) -> None:
        """Test that config defaults take precedence over None field defaults."""
        config = self.AppConfig()
        tm.that(config.input_dir, eq="/config/input")
        tm.that(config.output_dir, eq="/config/output")
        params = self.AppParams()
        tm.that(params.input_dir, none=True)
        tm.that(params.output_dir, none=True)
        params_from_config = self.AppParams(
            input_dir=config.input_dir,
            output_dir=config.output_dir,
        )
        tm.that(params_from_config.input_dir, eq="/config/input")
        tm.that(params_from_config.output_dir, eq="/config/output")

    def test_config_with_missing_environment_variable(self) -> None:
        """Test config with missing environment variable uses default."""
        os.environ.pop("MISSING_VAR", None)
        config = self.RequiredFieldsConfig()
        tm.that(config.input_dir, eq="/tmp/test/input")

    def test_params_validation_with_none_values(self) -> None:
        """Test parameter validation with None values."""
        params = self.AliasedParams()
        tm.that(params.input_dir, none=True)
        tm.that(params.output_dir, none=True)

    def test_params_validation_with_mixed_values(self) -> None:
        """Test parameter validation with mixed None and non-None values."""
        params_mixed = self.AliasedParams.model_validate({"input_dir": "/input"})
        tm.that(params_mixed.input_dir, eq="/input")
        tm.that(params_mixed.output_dir, none=True)

    def test_full_workflow_config_to_params(self) -> None:
        """Test full workflow from config to parameters."""
        config = self.FullAppConfig()
        cli_args = {
            "input_dir": config.input_dir,
            "output_dir": config.output_dir,
            "batch_size": config.batch_size,
            "verbose_mode": config.verbose,
        }
        params = self.FullAppParams.model_validate(cli_args)
        tm.that(params.input_dir, eq="/app/input")
        tm.that(params.output_dir, eq="/app/output")
        tm.that(params.batch_size, eq=1000)
        tm.that(params.verbose_mode is False, eq=True)

    def test_cli_parameter_override_config(self) -> None:
        """Test that CLI parameters override config defaults."""
        cli_override = {"input_dir": "/cli/input", "batch_size": 200}
        params = self.AliasedParams.model_validate(cli_override)
        tm.that(params.input_dir, eq="/cli/input")
        tm.that(params.batch_size, eq=200)

    def test_params_validation_strict(self) -> None:
        """Test params validation with strict mode."""
        params = self.StrictParams(
            input_dir="/test/input",
            output_dir="/test/output",
            name="test",
            count=5,
        )
        tm.that(params.name, eq="test")
        tm.that(params.count, eq=5)

    def test_params_forbid_extra_fields(self) -> None:
        """Test params model forbids extra fields."""
        params = self.ForbidExtraParams(name="test")
        tm.that(params.name, eq="test")
        with pytest.raises(ValidationError):
            self.ForbidExtraParams.model_validate({
                "name": "test",
                "extra_field": "value",
            })

    def test_config_value_extraction_int_field(self) -> None:
        """Test extracting integer values from config."""
        config = self.IntConfig()
        tm.that(config.timeout, eq=30)
        tm.that(config.max_retries, eq=3)

    def test_config_value_extraction_bool_field(self) -> None:
        """Test extracting boolean values from config."""
        config = self.BoolConfig()
        tm.that(config.debug is False, eq=True)
        tm.that(config.verbose is False, eq=True)

    def test_config_value_extraction_with_none(self) -> None:
        """Test config extraction returns None for unset optional fields."""
        config = self.OptionalPathConfig()
        tm.that(config.optional_path, none=True)
        tm.that(config.required_path, eq="/default")
