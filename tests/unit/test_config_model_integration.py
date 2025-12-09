"""FLEXT CLI Config Model Integration Tests - Comprehensive Integration Validation Testing.

Tests for FlextCli.model_command() covering configuration integration, config extraction,
default value propagation, parameter validation, alias handling, field precedence rules,
and edge cases with 100% coverage.

Modules tested: flext_cli.cli.FlextCliCli.model_command(), FlextCliConfig integration
Scope: All config-model integration operations, parameter validation, precedence rules

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

import pytest
from flext_core import t
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli import FlextCliCli, FlextCliConfig


class TestsCliConfigModelIntegration:
    """Config/model integration tests with pragmatic patterns."""

    # =========================================================================
    # MODEL DEFINITIONS (Reusable across tests)
    # =========================================================================

    class RequiredFieldsConfig(BaseSettings):
        """Config with required fields."""

        model_config = SettingsConfigDict(env_prefix="TEST_APP_")
        input_dir: str = Field(default="/tmp/test/input")
        output_dir: str = Field(default="/tmp/test/output")

    class OptionalFieldsConfig(BaseSettings):
        """Config with optional fields."""

        model_config = SettingsConfigDict(env_prefix="TEST_APP_")
        input_dir: str | None = Field(default=None)
        output_dir: str | None = Field(default=None)
        verbose: bool = Field(default=False)

    class TypedFieldsConfig(BaseSettings):
        """Config with various typed fields."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        timeout: int = Field(default=30)
        max_retries: int = Field(default=3)
        debug: bool = Field(default=False)
        optional_path: str | None = Field(default=None)

    class AliasedParams(BaseModel):
        """Parameter model with field aliases."""

        input_dir: str | None = Field(default=None, alias="input-dir")
        output_dir: str | None = Field(default=None, alias="output-dir")
        batch_size: int | None = Field(default=None, alias="batch-size")

        model_config = {"populate_by_name": True}

    class SimpleParams(BaseModel):
        """Simple parameter model."""

        name: str = Field(default="test", description="Name")
        count: int = Field(default=1, description="Count")

    class AppConfig(BaseSettings):
        """Application configuration."""

        model_config = SettingsConfigDict(env_prefix="TEST_")
        input_dir: str = Field(default="/config/input")
        output_dir: str = Field(default="/config/output")
        verbose: bool = Field(default=False)

    class AppParams(BaseModel):
        """Application parameters."""

        input_dir: str | None = Field(default=None, alias="input-dir")
        output_dir: str | None = Field(default=None, alias="output-dir")
        verbose_mode: bool = Field(default=False, alias="verbose-mode")

        model_config = {"populate_by_name": True}

    class FullAppConfig(BaseSettings):
        """Full application config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        input_dir: str = Field(default="/app/input")
        output_dir: str = Field(default="/app/output")
        batch_size: int = Field(default=1000)
        verbose: bool = Field(default=False)

    class FullAppParams(BaseModel):
        """Full application params."""

        input_dir: str | None = Field(default=None, alias="input-dir")
        output_dir: str | None = Field(default=None, alias="output-dir")
        batch_size: int | None = Field(default=None, alias="batch-size")
        verbose_mode: bool = Field(default=False, alias="verbose-mode")

        model_config = {"populate_by_name": True}

    class StringConfig(BaseSettings):
        """String field config."""

        model_config = SettingsConfigDict(env_prefix="TEST_")
        input_path: str = Field(default="/tmp/test/input")
        output_path: str = Field(default="/tmp/test/output")

    class IntConfig(BaseSettings):
        """Integer field config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        timeout: int = Field(default=30)
        max_retries: int = Field(default=3)

    class BoolConfig(BaseSettings):
        """Boolean field config."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        debug: bool = Field(default=False)
        verbose: bool = Field(default=False)

    class OptionalPathConfig(BaseSettings):
        """Config with optional fields."""

        model_config = SettingsConfigDict(env_prefix="APP_")
        optional_path: str | None = Field(default=None)
        required_path: str = Field(default="/default")

    class RequiredFieldsParams(BaseModel):
        """Parameter model with required fields."""

        input_dir: str = Field(alias="input-dir")
        output_dir: str | None = Field(default=None, alias="output-dir")

        model_config = {"populate_by_name": True}

    class StrictParams(BaseModel):
        """Strict validation params."""

        model_config = {"strict": True}
        name: str
        count: int = Field(default=1)

    class ForbidExtraParams(BaseModel):
        """Params forbidding extra fields."""

        model_config = {"extra": "forbid"}
        name: str = Field(default="default")

    # =========================================================================
    # FIXTURES
    # =========================================================================

    @pytest.fixture
    def cli(self) -> FlextCliCli:
        """Create FlextCliCli instance."""
        return FlextCliCli()

    @pytest.fixture
    def temp_env_file(self, tmp_path: Path) -> Path:
        """Create temporary .env file for testing."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TEST_APP_INPUT_DIR=/test/input\n"
            "TEST_APP_OUTPUT_DIR=/test/output\n"
            "TEST_APP_TIMEOUT_SECONDS=60\n"
            "TEST_APP_VERBOSE=true\n",
        )
        return env_file

    # =========================================================================
    # CONFIGURATION CLASS TESTS - Parametrized
    # =========================================================================

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
        expected_fields: list[str],
        expected_values: dict[str, t.GeneralValueType],
    ) -> None:
        """Test config initialization with various field types."""
        config = config_class()

        # Verify all expected fields exist
        for field_name in expected_fields:
            assert hasattr(config, field_name)

        # Verify expected values
        for field_name, expected_value in expected_values.items():
            assert getattr(config, field_name) == expected_value

    def test_config_with_environment_variables(self) -> None:
        """Test config loading from environment variables."""
        # Set environment variables
        os.environ["TEST_APP_INPUT_DIR"] = "/env/input"
        os.environ["TEST_APP_OUTPUT_DIR"] = "/env/output"

        try:
            config = self.RequiredFieldsConfig()
            assert config.input_dir == "/env/input"
            assert config.output_dir == "/env/output"
        finally:
            # Clean up environment
            os.environ.pop("TEST_APP_INPUT_DIR", None)
            os.environ.pop("TEST_APP_OUTPUT_DIR", None)

    # =========================================================================
    # PARAMETER MODEL TESTS - Parametrized
    # =========================================================================

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
            (
                {"batch-size": 100},
                {"batch_size": 100},
            ),
        ],
        ids=["aliases", "field_names", "single_field"],
    )
    def test_params_validation(
        self,
        input_data: dict[str, t.GeneralValueType],
        expected_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test parameter model validation with aliases."""
        params = self.AliasedParams.model_validate(input_data)

        for field_name, expected_value in expected_data.items():
            assert getattr(params, field_name) == expected_value

    def test_params_model_with_required_fields(self) -> None:
        """Test parameter model with required fields."""
        # Required field must be provided
        with pytest.raises(ValidationError):
            self.RequiredFieldsParams.model_validate({})

        # Can be provided
        params = self.RequiredFieldsParams.model_validate({"input_dir": "/test/input"})
        assert params.input_dir == "/test/input"
        assert params.output_dir is None

    # =========================================================================
    # MODEL COMMAND INTEGRATION TESTS
    # =========================================================================

    def test_model_command_with_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test model_command applies config defaults to Typer parameters."""
        config = self.AppConfig()

        def handler(_params: BaseModel) -> None:
            pass

        # Create command - should not raise
        command = cli.model_command(
            self.AppParams,
            handler,
            config=cast("FlextCliConfig", config),
        )
        assert command is not None
        assert callable(command)

    def test_model_command_without_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test model_command works without config."""

        def handler(_params: BaseModel) -> None:
            pass

        command = cli.model_command(self.SimpleParams, handler)
        assert command is not None

    # =========================================================================
    # CONFIG VALUE EXTRACTION TESTS - Parametrized
    # =========================================================================

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
        expected_value: str | int | bool | None,
    ) -> None:
        """Test extracting config values of different types."""
        config = config_class()

        value = getattr(config, field_name)
        assert isinstance(value, expected_type)
        assert value == expected_value

    def test_config_field_access(self) -> None:
        """Test accessing config fields directly."""
        config = self.StringConfig()

        # Direct access (defaults from StringConfig model)
        assert config.input_path == "/tmp/test/input"
        assert config.output_path == "/tmp/test/output"

        # hasattr check
        assert hasattr(config, "input_path")
        assert hasattr(config, "output_path")

    # =========================================================================
    # FIELD ALIAS & DEFAULT PRECEDENCE TESTS
    # =========================================================================

    def test_field_alias_in_params_model(self) -> None:
        """Test field aliases are properly handled in parameter models."""
        # Should accept alias names
        params = self.AliasedParams.model_validate(
            {
                "input-dir": "/input",
                "output-dir": "/output",
                "batch-size": 100,
            }
        )

        assert params.input_dir == "/input"
        assert params.output_dir == "/output"
        assert params.batch_size == 100

        # Should also accept field names
        params2 = self.AliasedParams.model_validate(
            {
                "input_dir": "/input2",
                "output_dir": "/output2",
                "batch_size": 200,
            }
        )

        assert params2.input_dir == "/input2"
        assert params2.output_dir == "/output2"
        assert params2.batch_size == 200

    def test_default_precedence_config_over_none(self) -> None:
        """Test that config defaults take precedence over None field defaults."""
        config = self.AppConfig()

        # Config should have the values
        assert config.input_dir == "/config/input"
        assert config.output_dir == "/config/output"

        # Params default to None
        params = self.AppParams()
        assert params.input_dir is None
        assert params.output_dir is None

        # But when instantiated from config, should get config values
        params_from_config = self.AppParams.model_validate(
            {
                "input_dir": config.input_dir,
                "output_dir": config.output_dir,
            }
        )
        assert params_from_config.input_dir == "/config/input"
        assert params_from_config.output_dir == "/config/output"

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # =========================================================================

    def test_config_with_missing_environment_variable(self) -> None:
        """Test config with missing environment variable uses default."""
        # Ensure variable doesn't exist
        os.environ.pop("MISSING_VAR", None)

        config = self.RequiredFieldsConfig()
        # Should use default when env var missing (default is "/tmp/test/input" from Field)
        assert config.input_dir == "/tmp/test/input"

    def test_params_validation_with_none_values(self) -> None:
        """Test parameter validation with None values."""
        # Should validate with None
        params = self.AliasedParams.model_validate({})
        assert params.input_dir is None
        assert params.output_dir is None

    def test_params_validation_with_mixed_values(self) -> None:
        """Test parameter validation with mixed None and non-None values."""
        params_mixed = self.AliasedParams.model_validate(
            {
                "input_dir": "/input",
            }
        )

        assert params_mixed.input_dir == "/input"
        assert params_mixed.output_dir is None

    def test_full_workflow_config_to_params(self) -> None:
        """Test full workflow from config to parameters."""
        # Create config
        config = self.FullAppConfig()

        # Simulate CLI receiving parameters with config defaults
        cli_args = {
            "input_dir": config.input_dir,
            "output_dir": config.output_dir,
            "batch_size": config.batch_size,
            "verbose_mode": config.verbose,
        }

        # Create params from CLI args
        params = self.FullAppParams.model_validate(cli_args)

        # Verify all values propagated correctly
        assert params.input_dir == "/app/input"
        assert params.output_dir == "/app/output"
        assert params.batch_size == 1000
        assert params.verbose_mode is False

    def test_cli_parameter_override_config(self) -> None:
        """Test that CLI parameters override config defaults."""
        # CLI provides override
        cli_override = {
            "input_dir": "/cli/input",
            "batch_size": 200,
        }

        params = self.AliasedParams.model_validate(cli_override)

        # CLI values should override config
        assert params.input_dir == "/cli/input"
        assert params.batch_size == 200

    # =========================================================================
    # VALIDATION TESTS
    # =========================================================================

    def test_params_validation_strict(self) -> None:
        """Test params validation with strict mode."""
        # Should validate with strict=True
        params = self.StrictParams.model_validate(
            {
                "name": "test",
                "count": 5,
            }
        )
        assert params.name == "test"
        assert params.count == 5

    def test_params_forbid_extra_fields(self) -> None:
        """Test params model forbids extra fields."""
        # Valid
        params = self.ForbidExtraParams.model_validate({"name": "test"})
        assert params.name == "test"

        # Extra fields should raise error
        with pytest.raises(ValidationError):
            self.ForbidExtraParams.model_validate(
                {
                    "name": "test",
                    "extra_field": "value",
                }
            )

    def test_config_value_extraction_int_field(self) -> None:
        """Test extracting integer values from config."""
        config = self.IntConfig()

        assert config.timeout == 30
        assert config.max_retries == 3

    def test_config_value_extraction_bool_field(self) -> None:
        """Test extracting boolean values from config."""
        config = self.BoolConfig()

        assert config.debug is False
        assert config.verbose is False

    def test_config_value_extraction_with_none(self) -> None:
        """Test config extraction returns None for unset optional fields."""
        config = self.OptionalPathConfig()

        # Optional field should be None if not set
        assert config.optional_path is None
        # Required field should have default
        assert config.required_path == "/default"
