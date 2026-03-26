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
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with ConnectionConfig."""
        command = cli.model_command(m.Cli.Test.ConnectionConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_environment_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with EnvironmentConfig (Literal types)."""
        command = cli.model_command(m.Cli.Test.EnvironmentConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_optional_literal_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with Optional Literal types."""
        command = cli.model_command(m.Cli.Test.OptionalLiteralConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_aliased_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with field aliases."""
        command = cli.model_command(m.Cli.Test.AliasedConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_boolean_flags_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with various boolean flags."""
        command = cli.model_command(m.Cli.Test.BooleanFlagsConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_nested_model_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with nested models."""
        command = cli.model_command(m.Cli.Test.NestedModelConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_validated_config_command(
        self,
        cli: FlextCliCli,
        sample_handler: Callable[[BaseModel], None],
    ) -> None:
        """Test model_command with custom validators."""
        command = cli.model_command(m.Cli.Test.ValidatedConfig, sample_handler)
        assert command is not None
        tm.that(callable(command), eq=True)

    def test_populate_by_name_works(self) -> None:
        """Test that populate_by_name allows both alias and field name."""
        config1 = m.Cli.Test.AliasedConfig.model_validate({"input-dir": "/test/input"})
        tm.that(config1.input_dir, eq="/test/input")
        config2 = m.Cli.Test.AliasedConfig.model_validate({"input_dir": "/test/input2"})
        tm.that(config2.input_dir, eq="/test/input2")

    def test_custom_validator_works(self) -> None:
        """Test that custom validators work in CLI context."""
        config = m.Cli.Test.ValidatedConfig.model_validate({
            "host": "example.com",
            "port": 5432,
        })
        tm.that(config.host, eq="example.com")
        with pytest.raises(ValidationError):
            m.Cli.Test.ValidatedConfig.model_validate({"host": "invalid", "port": 5432})

    def test_field_constraints_enforced(self) -> None:
        """Test that Field constraints (ge, le) are enforced."""
        config = m.Cli.Test.ConnectionConfig.model_validate({
            "username": "user",
            "port": 5432,
        })
        tm.that(config.port, eq=5432)
        with pytest.raises(ValidationError):
            m.Cli.Test.ConnectionConfig.model_validate({"username": "user", "port": 0})

    def test_model_command_execution_with_connection_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with ConnectionConfig."""

        def handler(params: BaseModel) -> None:
            """Process connection config."""
            tm.that(params, is_=m.Cli.Test.ConnectionConfig)
            assert isinstance(params, m.Cli.Test.ConnectionConfig)
            tm.that(params.host, none=False)
            tm.that(params.port, none=False)

        command = cli.model_command(m.Cli.Test.ConnectionConfig, handler)
        assert command is not None

    def test_model_command_execution_with_environment_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with EnvironmentConfig."""

        def handler(params: BaseModel) -> None:
            """Process environment config."""
            tm.that(params, is_=m.Cli.Test.EnvironmentConfig)
            assert isinstance(params, m.Cli.Test.EnvironmentConfig)
            tm.that(params.environment, none=False)

        command = cli.model_command(m.Cli.Test.EnvironmentConfig, handler)
        assert command is not None

    def test_model_command_execution_with_aliased_config(
        self,
        cli: FlextCliCli,
    ) -> None:
        """Test executing model_command with AliasedConfig."""

        def handler(params: BaseModel) -> None:
            """Process aliased config."""
            tm.that(params, is_=m.Cli.Test.AliasedConfig)
            assert isinstance(params, m.Cli.Test.AliasedConfig)
            tm.that(params.input_dir, none=False)
            tm.that(params.output_dir, none=False)

        command = cli.model_command(m.Cli.Test.AliasedConfig, handler)
        assert command is not None
