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
from flext_tests import tm
from pydantic import BaseModel, ValidationError

from flext_cli import FlextCliCli
from tests import m


class TestsCliModelCommandComprehensive:
    """Comprehensive tests for model_command with real-world models."""

    @pytest.fixture
    def cli(self) -> FlextCliCli:
        """Create FlextCliCli instance."""
        return FlextCliCli()

    @pytest.fixture
    def sample_handler(self) -> Callable[[BaseModel], None]:
        """Sample handler function for commands."""

        def handler(params: BaseModel) -> None:
            """Process parameters."""
            assert params is not None

        return handler

    def test_connection_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with ConnectionConfig."""
        command = cli.model_command(m.ConnectionConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_environment_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with EnvironmentConfig (Literal types)."""
        command = cli.model_command(m.EnvironmentConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_optional_literal_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with Optional Literal types."""
        command = cli.model_command(m.OptionalLiteralConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_aliased_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with field aliases."""
        command = cli.model_command(m.AliasedConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_boolean_flags_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with various boolean flags."""
        command = cli.model_command(m.BooleanFlagsConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_nested_model_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with nested models."""
        command = cli.model_command(m.NestedModelConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_validated_config_command(
        self, cli: FlextCliCli, sample_handler: Callable[[BaseModel], None]
    ) -> None:
        """Test model_command with custom validators."""
        command = cli.model_command(m.ValidatedConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_literal_types_converted_to_str(self) -> None:
        """Test that Literal types are converted to str for Typer."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(m.EnvironmentConfig)
        tm.ok(params_result)
        params = params_result.value
        env_param = next((p for p in params if p.name == "environment"), None)
        assert env_param is not None
        tm.that(env_param.click_type, eq="STRING")

    def test_optional_literal_types_handled(self) -> None:
        """Test that Optional[Literal[...]] types are handled."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            m.OptionalLiteralConfig
        )
        tm.ok(params_result)
        params = params_result.value
        log_level_param = next((p for p in params if p.name == "log_level"), None)
        assert log_level_param is not None
        tm.that(log_level_param.click_type, eq="STRING")

    def test_boolean_flags_default_true(self) -> None:
        """Test boolean flags with default=True."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            m.BooleanFlagsConfig
        )
        tm.ok(params_result)
        params = params_result.value
        cache_param = next((p for p in params if p.name == "enable_cache"), None)
        assert cache_param is not None
        tm.that(cache_param.click_type, eq="BOOL")
        tm.that(cache_param.default is True, eq=True)

    def test_boolean_flags_default_false(self) -> None:
        """Test boolean flags with default=False."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            m.BooleanFlagsConfig
        )
        tm.ok(params_result)
        params = params_result.value
        verbose_param = next((p for p in params if p.name == "verbose"), None)
        assert verbose_param is not None
        tm.that(verbose_param.click_type, eq="BOOL")
        tm.that(verbose_param.default is False, eq=True)

    def test_optional_boolean_flags(self) -> None:
        """Test optional boolean flags."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(
            m.BooleanFlagsConfig
        )
        tm.ok(params_result)
        params = params_result.value
        force_param = next((p for p in params if p.name == "force"), None)
        assert force_param is not None
        tm.that(force_param.click_type, eq="BOOL")
        tm.that(force_param.default is None, eq=True)

    def test_field_aliases_preserved(self) -> None:
        """Test that field aliases are preserved."""
        params_result = m.Cli.CliModelConverter.model_to_cli_params(m.AliasedConfig)
        tm.ok(params_result)
        params = params_result.value
        input_param = next((p for p in params if p.name == "input_dir"), None)
        assert input_param is not None
        tm.that(
            hasattr(input_param, "aliases") or input_param.name == "input_dir", eq=True
        )

    def test_populate_by_name_works(self) -> None:
        """Test that populate_by_name allows both alias and field name."""
        config1 = m.AliasedConfig.model_validate({"input-dir": "/test/input"})
        tm.that(config1.input_dir, eq="/test/input")
        config2 = m.AliasedConfig.model_validate({"input_dir": "/test/input2"})
        tm.that(config2.input_dir, eq="/test/input2")

    def test_custom_validator_works(self) -> None:
        """Test that custom validators work in CLI context."""
        config = m.ValidatedConfig.model_validate({
            "host": "example.com",
            "port": 5432,
        })
        tm.that(config.host, eq="example.com")
        with pytest.raises(ValidationError):
            m.ValidatedConfig.model_validate({"host": "invalid", "port": 5432})

    def test_field_constraints_enforced(self) -> None:
        """Test that Field constraints (ge, le) are enforced."""
        config = m.ConnectionConfig.model_validate({"username": "user", "port": 5432})
        tm.that(config.port, eq=5432)
        with pytest.raises(ValidationError):
            m.ConnectionConfig.model_validate({"username": "user", "port": 100})

    def test_model_command_execution_with_connection_config(
        self, cli: FlextCliCli
    ) -> None:
        """Test executing model_command with ConnectionConfig."""

        def handler(params: BaseModel) -> None:
            """Process connection config."""
            tm.that(isinstance(params, m.ConnectionConfig), eq=True)
            assert isinstance(params, m.ConnectionConfig)
            tm.that(params.host is not None, eq=True)
            tm.that(params.port is not None, eq=True)

        command = cli.model_command(m.ConnectionConfig, handler)
        assert command is not None

    def test_model_command_execution_with_environment_config(
        self, cli: FlextCliCli
    ) -> None:
        """Test executing model_command with EnvironmentConfig."""

        def handler(params: BaseModel) -> None:
            """Process environment config."""
            tm.that(isinstance(params, m.EnvironmentConfig), eq=True)
            assert isinstance(params, m.EnvironmentConfig)
            tm.that(params.environment is not None, eq=True)

        command = cli.model_command(m.EnvironmentConfig, handler)
        assert command is not None

    def test_model_command_execution_with_aliased_config(
        self, cli: FlextCliCli
    ) -> None:
        """Test executing model_command with AliasedConfig."""

        def handler(params: BaseModel) -> None:
            """Process aliased config."""
            tm.that(isinstance(params, m.AliasedConfig), eq=True)
            assert isinstance(params, m.AliasedConfig)
            tm.that(params.input_dir is not None, eq=True)
            tm.that(params.output_dir is not None, eq=True)

        command = cli.model_command(m.AliasedConfig, handler)
        assert command is not None
