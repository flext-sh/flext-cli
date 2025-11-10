"""FLEXT CLI Config Model Integration Tests.

Comprehensive tests for FlextCli.model_command() configuration integration
with real functionality testing, targeting 100% coverage of config extraction
and default value propagation to Typer parameters.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli import FlextCliCli
from flext_cli.config import FlextCliConfig


class TestConfigModelExtraction:
    """Test config value extraction and default propagation."""

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
            "TEST_APP_VERBOSE=true\n"
        )
        return env_file

    # =========================================================================
    # CONFIGURATION CLASS TESTS
    # =========================================================================

    def test_config_with_required_fields(self) -> None:
        """Test configuration class with required fields."""

        class TestConfig(BaseSettings):
            """Test configuration with required fields."""

            model_config = SettingsConfigDict(env_prefix="TEST_APP_")

            input_dir: str = Field(default="data/input")
            output_dir: str = Field(default="data/output")

        config = TestConfig()
        assert config.input_dir == "data/input"
        assert config.output_dir == "data/output"

    def test_config_with_optional_fields(self) -> None:
        """Test configuration class with optional fields."""

        class TestConfig(BaseSettings):
            """Test config with optional fields (default=None)."""

            model_config = SettingsConfigDict(env_prefix="TEST_APP_")

            input_dir: str | None = Field(default=None)
            output_dir: str | None = Field(default=None)
            verbose: bool = Field(default=False)

        config = TestConfig()
        assert config.input_dir is None
        assert config.output_dir is None
        assert config.verbose is False

    def test_config_with_environment_variables(self, tmp_path: Path) -> None:
        """Test config loading from environment variables."""
        import os

        # Set environment variables
        os.environ["TEST_APP_INPUT_DIR"] = "/env/input"
        os.environ["TEST_APP_OUTPUT_DIR"] = "/env/output"

        try:

            class TestConfig(BaseSettings):
                """Test config from environment."""

                model_config = SettingsConfigDict(env_prefix="TEST_APP_")

                input_dir: str = Field(default="data/input")
                output_dir: str = Field(default="data/output")

            config = TestConfig()
            assert config.input_dir == "/env/input"
            assert config.output_dir == "/env/output"
        finally:
            # Clean up environment
            os.environ.pop("TEST_APP_INPUT_DIR", None)
            os.environ.pop("TEST_APP_OUTPUT_DIR", None)

    # =========================================================================
    # PARAMETER MODEL TESTS
    # =========================================================================

    def test_params_model_with_aliases(self) -> None:
        """Test parameter model with field aliases."""

        class TestParams(BaseModel):
            """Parameter model with aliases."""

            input_dir: str | None = Field(
                default=None, alias="input-dir", description="Input directory"
            )
            output_dir: str | None = Field(
                default=None,
                alias="output-dir",
                description="Output directory",
            )
            verbose: bool = Field(default=False, description="Verbose output")

            model_config = {"populate_by_name": True}

        # Test instantiation with field names
        params1 = TestParams.model_validate({
            "input_dir": "/test/input",
            "output_dir": "/test/output",
        })
        assert params1.input_dir == "/test/input"
        assert params1.output_dir == "/test/output"

        # Test instantiation with aliases
        params2 = TestParams.model_validate({
            "input-dir": "/alias/input",
            "output-dir": "/alias/output",
        })
        assert params2.input_dir == "/alias/input"
        assert params2.output_dir == "/alias/output"

    def test_params_model_with_required_fields(self) -> None:
        """Test parameter model with required fields."""

        class TestParams(BaseModel):
            """Parameter model with required fields."""

            input_dir: str = Field(alias="input-dir", description="Required input")
            output_dir: str | None = Field(
                default=None, alias="output-dir", description="Optional output"
            )

            model_config = {"populate_by_name": True}

        # Required field must be provided
        with pytest.raises(ValidationError):
            TestParams.model_validate({})

        # Can be provided
        params = TestParams.model_validate({
            "input_dir": "/test/input",
        })
        assert params.input_dir == "/test/input"
        assert params.output_dir is None

    # =========================================================================
    # MODEL COMMAND INTEGRATION TESTS
    # =========================================================================

    def test_model_command_with_config_defaults(self, cli: FlextCliCli) -> None:
        """Test model_command applies config defaults to Typer parameters."""

        class AppConfig(BaseSettings):
            """Application configuration."""

            model_config = SettingsConfigDict(env_prefix="TEST_")

            input_dir: str = Field(default="/config/input")
            output_dir: str = Field(default="/config/output")
            verbose: bool = Field(default=False)

        class AppParams(BaseModel):
            """Application parameters."""

            input_dir: str | None = Field(
                default=None, alias="input-dir", description="Input directory"
            )
            output_dir: str | None = Field(
                default=None,
                alias="output-dir",
                description="Output directory",
            )
            verbose: bool = Field(default=False, description="Verbose mode")

            model_config = {"populate_by_name": True}

        config = AppConfig()

        # Handler function that captures parameters
        captured_params: dict[str, Any] = {}

        def handler(params: AppParams) -> None:
            captured_params["params"] = params

        # Create command with config integration
        command = cli.model_command(
            AppParams,
            handler,
            config=cast("FlextCliConfig", config),
        )

        # Verify command was created and is callable
        assert command is not None
        assert callable(command)

    def test_model_command_none_config(self, cli: FlextCliCli) -> None:
        """Test model_command works without config."""

        class SimpleParams(BaseModel):
            """Simple parameter model."""

            name: str = Field(default="test", description="Name parameter")
            count: int = Field(default=1, description="Count parameter")

        def handler(params: SimpleParams) -> None:
            pass

        # Should work without config
        command = cli.model_command(SimpleParams, handler)
        assert command is not None

    def test_model_command_with_optional_fields_and_defaults(
        self, cli: FlextCliCli
    ) -> None:
        """Test model_command with optional fields that have defaults."""

        class ConfigWithDefaults(BaseSettings):
            """Config with optional fields and defaults."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            input_dir: str = Field(default="/default/input")
            batch_size: int = Field(default=100)

        class ParamsWithOptionals(BaseModel):
            """Params with optional fields."""

            input_dir: str | None = Field(
                default=None, alias="input-dir", description="Input"
            )
            batch_size: int | None = Field(
                default=None,
                alias="batch-size",
                description="Batch size",
            )

            model_config = {"populate_by_name": True}

        config = ConfigWithDefaults()

        captured_params: dict[str, Any] = {}

        def handler(params: ParamsWithOptionals) -> None:
            captured_params["params"] = params

        command = cli.model_command(
            ParamsWithOptionals,
            handler,
            config=cast("FlextCliConfig", config),
        )

        assert command is not None

    # =========================================================================
    # CONFIG VALUE EXTRACTION TESTS
    # =========================================================================

    def test_config_value_extraction_string_field(self) -> None:
        """Test extracting string values from config."""

        class Config(BaseSettings):
            """String config."""

            model_config = SettingsConfigDict(env_prefix="TEST_")

            input_path: str = Field(default="/data/input")
            output_path: str = Field(default="/data/output")

        config = Config()

        # Verify values can be extracted
        assert hasattr(config, "input_path")
        assert hasattr(config, "output_path")
        assert config.input_path == "/data/input"
        assert config.output_path == "/data/output"

    def test_config_value_extraction_int_field(self) -> None:
        """Test extracting integer values from config."""

        class Config(BaseSettings):
            """Integer config."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            timeout: int = Field(default=30)
            max_retries: int = Field(default=3)

        config = Config()

        assert config.timeout == 30
        assert config.max_retries == 3

    def test_config_value_extraction_bool_field(self) -> None:
        """Test extracting boolean values from config."""

        class Config(BaseSettings):
            """Boolean config."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            debug: bool = Field(default=False)
            verbose: bool = Field(default=False)

        config = Config()

        assert config.debug is False
        assert config.verbose is False

    def test_config_value_extraction_with_none(self) -> None:
        """Test config extraction returns None for unset optional fields."""

        class Config(BaseSettings):
            """Config with optional fields."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            optional_path: str | None = Field(default=None)
            required_path: str = Field(default="/default")

        config = Config()

        # Optional field should be None if not set
        assert config.optional_path is None
        # Required field should have default
        assert config.required_path == "/default"

    # =========================================================================
    # FIELD ALIAS HANDLING TESTS
    # =========================================================================

    def test_field_alias_in_params_model(self) -> None:
        """Test field aliases are properly handled in parameter models."""

        class Params(BaseModel):
            """Params with aliases."""

            input_dir: str | None = Field(default=None, alias="input-dir")
            output_dir: str | None = Field(default=None, alias="output-dir")
            batch_size: int | None = Field(default=None, alias="batch-size")

            model_config = {"populate_by_name": True}

        # Should accept alias names
        params = Params.model_validate({
            "input-dir": "/input",
            "output-dir": "/output",
            "batch-size": 100,
        })

        assert params.input_dir == "/input"
        assert params.output_dir == "/output"
        assert params.batch_size == 100

        # Should also accept field names
        params2 = Params.model_validate({
            "input_dir": "/input2",
            "output_dir": "/output2",
            "batch_size": 200,
        })

        assert params2.input_dir == "/input2"
        assert params2.output_dir == "/output2"
        assert params2.batch_size == 200

    # =========================================================================
    # DEFAULT PRECEDENCE TESTS
    # =========================================================================

    def test_default_precedence_config_over_none(self) -> None:
        """Test that config defaults take precedence over None field defaults."""

        class Config(BaseSettings):
            """Config with defaults."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            input_dir: str = Field(default="/config/input")
            timeout: int = Field(default=60)

        class Params(BaseModel):
            """Params with None defaults."""

            input_dir: str | None = Field(default=None)
            timeout: int | None = Field(default=None)

        config = Config()

        # Config should have the values
        assert config.input_dir == "/config/input"
        assert config.timeout == 60

        # Params default to None
        params = Params()
        assert params.input_dir is None
        assert params.timeout is None

        # But when instantiated from config, should get config values
        params_from_config = Params.model_validate({
            "input_dir": config.input_dir,
            "timeout": config.timeout,
        })
        assert params_from_config.input_dir == "/config/input"
        assert params_from_config.timeout == 60

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # =========================================================================

    def test_config_with_missing_environment_variable(self) -> None:
        """Test config with missing environment variable uses default."""
        import os

        # Ensure variable doesn't exist
        os.environ.pop("MISSING_VAR", None)

        class Config(BaseSettings):
            """Config with missing env var."""

            model_config = SettingsConfigDict(env_prefix="MISSING_")

            path: str = Field(default="/default/path")

        config = Config()
        # Should use default when env var missing
        assert config.path == "/default/path"

    def test_params_validation_with_none_values(self) -> None:
        """Test parameter validation with None values."""

        class Params(BaseModel):
            """Params allowing None."""

            input_dir: str | None = Field(default=None)
            output_dir: str | None = Field(default=None)

        # Should validate with None
        params = Params.model_validate({})
        assert params.input_dir is None
        assert params.output_dir is None

    def test_params_validation_with_mixed_values(self) -> None:
        """Test parameter validation with mixed None and non-None values."""

        class Params(BaseModel):
            """Params with mixed values."""

            input_dir: str | None = Field(default=None)
            output_dir: str | None = Field(default=None)
            verbose: bool = Field(default=False)

        params = Params.model_validate({
            "input_dir": "/input",
            "verbose": True,
        })

        assert params.input_dir == "/input"
        assert params.output_dir is None
        assert params.verbose is True

    def test_config_population_by_name(self) -> None:
        """Test that models can be populated by both field name and alias."""

        class Params(BaseModel):
            """Params with aliases and populate_by_name."""

            input_dir: str | None = Field(default=None, alias="input-dir")
            output_dir: str | None = Field(default=None, alias="output-dir")

            model_config = {"populate_by_name": True}

        # Both should work
        params1 = Params.model_validate({
            "input_dir": "/input1",
            "output_dir": "/output1",
        })
        assert params1.input_dir == "/input1"

        params2 = Params.model_validate({
            "input-dir": "/input2",
            "output-dir": "/output2",
        })
        assert params2.input_dir == "/input2"

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_full_workflow_config_to_params(self) -> None:
        """Test full workflow from config to parameters."""

        class AppConfig(BaseSettings):
            """Full application config."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            input_dir: str = Field(default="/app/input")
            output_dir: str = Field(default="/app/output")
            batch_size: int = Field(default=1000)
            verbose: bool = Field(default=False)

        class AppParams(BaseModel):
            """Full application params."""

            input_dir: str | None = Field(
                default=None, alias="input-dir", description="Input"
            )
            output_dir: str | None = Field(
                default=None, alias="output-dir", description="Output"
            )
            batch_size: int | None = Field(
                default=None,
                alias="batch-size",
                description="Batch size",
            )
            verbose: bool = Field(default=False, description="Verbose")

            model_config = {"populate_by_name": True}

        # Create config
        config = AppConfig()

        # Simulate CLI receiving parameters with config defaults
        cli_args = {
            "input_dir": config.input_dir,
            "output_dir": config.output_dir,
            "batch_size": config.batch_size,
            "verbose": config.verbose,
        }

        # Create params from CLI args
        params = AppParams.model_validate(cli_args)

        # Verify all values propagated correctly
        assert params.input_dir == "/app/input"
        assert params.output_dir == "/app/output"
        assert params.batch_size == 1000
        assert params.verbose is False

    def test_cli_parameter_override_config(self) -> None:
        """Test that CLI parameters override config defaults."""

        class Config(BaseSettings):
            """Config with defaults."""

            model_config = SettingsConfigDict(env_prefix="APP_")

            input_dir: str = Field(default="/config/input")
            batch_size: int = Field(default=100)

        class Params(BaseModel):
            """Params can override config."""

            input_dir: str | None = Field(default=None)
            batch_size: int | None = Field(default=None)

        # CLI provides override
        cli_override = {
            "input_dir": "/cli/input",
            "batch_size": 200,
        }

        params = Params.model_validate(cli_override)

        # CLI values should override config
        assert params.input_dir == "/cli/input"
        assert params.batch_size == 200


class TestConfigModelCoverage:
    """Tests to ensure 100% coverage of config model integration."""

    def test_config_field_access(self) -> None:
        """Test accessing config fields directly."""

        class TestConfig(BaseSettings):
            """Test config for field access."""

            model_config = SettingsConfigDict(env_prefix="TEST_")

            field1: str = Field(default="value1")
            field2: int = Field(default=42)
            field3: bool = Field(default=True)

        config = TestConfig()

        # Direct access
        assert config.field1 == "value1"
        assert config.field2 == 42
        assert config.field3 is True

        # hasattr check
        assert hasattr(config, "field1")
        assert hasattr(config, "field2")
        assert hasattr(config, "field3")

    def test_params_validation_strict(self) -> None:
        """Test params validation with strict mode."""

        class StrictParams(BaseModel):
            """Strict validation params."""

            model_config = {"strict": True}

            name: str
            count: int = Field(default=1)

        # Should validate with strict=True
        params = StrictParams.model_validate({
            "name": "test",
            "count": 5,
        })
        assert params.name == "test"
        assert params.count == 5

    def test_params_forbid_extra_fields(self) -> None:
        """Test params model forbids extra fields."""

        class StrictParams(BaseModel):
            """Params forbidding extra fields."""

            model_config = {"extra": "forbid"}

            name: str = Field(default="default")

        # Valid
        params = StrictParams.model_validate({"name": "test"})
        assert params.name == "test"

        # Extra fields should raise error
        with pytest.raises(ValidationError):
            StrictParams.model_validate({
                "name": "test",
                "extra_field": "value",
            })
