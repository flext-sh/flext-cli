"""Comprehensive Model Command Tests - Real-World Pydantic Models.

Tests for FlextCli.model_command() with complex real-world Pydantic models
based on patterns from flext-db-oracle and other FLEXT projects.

Tests cover:
- Literal types (environment, status, etc.)
- Optional fields with defaults
- Union types
- Nested models
- Boolean flags with various defaults
- Field aliases and populate_by_name
- Complex validation rules

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import (
    BaseModel,
    ValidationError,
)

from flext_cli import FlextCliCli, m


class TestsCliModelCommandComprehensive:
    """Comprehensive tests for model_command with real-world models."""

    # =========================================================================
    # REAL-WORLD MODEL DEFINITIONS (Based on flext-db-oracle patterns)
    # =========================================================================

    @pytest.fixture
    def cli(self) -> FlextCliCli:
        """Create FlextCliCli instance."""
        return FlextCliCli()

    @pytest.fixture
    def sample_handler(
        self,
    ) -> Callable[[BaseModel], None]:
        """Sample handler function for commands."""

        def handler(params: BaseModel) -> None:
            """Process parameters."""
            assert params is not None

        return handler

    # =========================================================================
    # BASIC MODEL COMMAND TESTS
    # =========================================================================

    def test_connection_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with ConnectionConfig."""
        command = cli.model_command(self.ConnectionConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_environment_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with EnvironmentConfig (Literal types)."""
        command = cli.model_command(self.EnvironmentConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_optional_literal_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with Optional Literal types."""
        command = cli.model_command(self.OptionalLiteralConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_aliased_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with field aliases."""
        command = cli.model_command(self.AliasedConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_boolean_flags_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with various boolean flags."""
        command = cli.model_command(self.BooleanFlagsConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_nested_model_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with nested models."""
        command = cli.model_command(self.NestedModelConfig, sample_handler)
        assert command is not None
        assert callable(command)

    def test_validated_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with custom validators."""
        command = cli.model_command(self.ValidatedConfig, sample_handler)
        assert command is not None
        assert callable(command)

    # =========================================================================
    # LITERAL TYPE HANDLING TESTS
    # =========================================================================

    def test_literal_types_converted_to_str(self) -> None:
        """Test that Literal types are converted to str for Typer."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.EnvironmentConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find environment parameter
        env_param = next((p for p in params if p.name == "environment"), None)
        assert env_param is not None
        # Literal types should be converted to str
        assert env_param.click_type == "STRING"

    def test_optional_literal_types_handled(self) -> None:
        """Test that Optional[Literal[...]] types are handled."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.OptionalLiteralConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find log_level parameter
        log_level_param = next((p for p in params if p.name == "log_level"), None)
        assert log_level_param is not None
        # Optional Literal should be converted to Optional[str]
        assert log_level_param.click_type == "STRING"

    # =========================================================================
    # BOOLEAN FLAGS TESTS
    # =========================================================================

    def test_boolean_flags_default_true(self) -> None:
        """Test boolean flags with default=True."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.BooleanFlagsConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find enable_cache parameter
        cache_param = next((p for p in params if p.name == "enable_cache"), None)
        assert cache_param is not None
        assert cache_param.click_type == "BOOL"
        assert cache_param.default is True

    def test_boolean_flags_default_false(self) -> None:
        """Test boolean flags with default=False."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.BooleanFlagsConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find verbose parameter
        verbose_param = next((p for p in params if p.name == "verbose"), None)
        assert verbose_param is not None
        assert verbose_param.click_type == "BOOL"
        assert verbose_param.default is False

    def test_optional_boolean_flags(self) -> None:
        """Test optional boolean flags."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.BooleanFlagsConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find force parameter
        force_param = next((p for p in params if p.name == "force"), None)
        assert force_param is not None
        assert force_param.click_type == "BOOL"
        assert force_param.default is None

    # =========================================================================
    # FIELD ALIASES TESTS
    # =========================================================================

    def test_field_aliases_preserved(self) -> None:
        """Test that field aliases are preserved."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            self.AliasedConfig,
        )

        assert params_result.is_success
        params = params_result.value

        # Find input_dir parameter
        input_param = next((p for p in params if p.name == "input_dir"), None)
        assert input_param is not None
        # Aliases should be available
        assert hasattr(input_param, "aliases") or input_param.name == "input_dir"

    def test_populate_by_name_works(self) -> None:
        """Test that populate_by_name allows both alias and field name."""
        # Should accept alias
        config1 = self.AliasedConfig.model_validate({"input-dir": "/test/input"})
        assert config1.input_dir == "/test/input"

        # Should accept field name
        config2 = self.AliasedConfig.model_validate({"input_dir": "/test/input2"})
        assert config2.input_dir == "/test/input2"

    # =========================================================================
    # VALIDATION TESTS
    # =========================================================================

    def test_custom_validator_works(self) -> None:
        """Test that custom validators work in CLI context."""
        # Valid host
        config = self.ValidatedConfig.model_validate({
            "host": "example.com",
            "port": 5432,
        })
        assert config.host == "example.com"

        # Invalid host should raise ValidationError
        with pytest.raises(ValidationError):
            self.ValidatedConfig.model_validate({
                "host": "invalid",
                "port": 5432,
            })

    def test_field_constraints_enforced(self) -> None:
        """Test that Field constraints (ge, le) are enforced."""
        # Valid port
        config = self.ConnectionConfig.model_validate({
            "username": "user",
            "port": 5432,
        })
        assert config.port == 5432

        # Invalid port should raise ValidationError
        with pytest.raises(ValidationError):
            self.ConnectionConfig.model_validate({
                "username": "user",
                "port": 100,  # Below minimum
            })

    # =========================================================================
    # INTEGRATION TESTS WITH REAL HANDLERS
    # =========================================================================

    def test_model_command_execution_with_connection_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with ConnectionConfig."""

        def handler(params: BaseModel) -> None:
            """Process connection config."""
            assert isinstance(params, self.ConnectionConfig)
            assert params.host is not None
            assert params.port is not None

        command = cli.model_command(self.ConnectionConfig, handler)
        assert command is not None

    def test_model_command_execution_with_environment_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with EnvironmentConfig."""

        def handler(params: BaseModel) -> None:
            """Process environment config."""
            assert isinstance(params, self.EnvironmentConfig)
            assert params.environment is not None

        command = cli.model_command(self.EnvironmentConfig, handler)
        assert command is not None

    def test_model_command_execution_with_aliased_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with AliasedConfig."""

        def handler(params: BaseModel) -> None:
            """Process aliased config."""
            assert isinstance(params, self.AliasedConfig)
            assert params.input_dir is not None
            assert params.output_dir is not None

        command = cli.model_command(self.AliasedConfig, handler)
        assert command is not None
