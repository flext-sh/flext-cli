"""FLEXT CLI Config Tests - Comprehensive Configuration Validation Testing.

Tests for FlextCliSettings covering initialization, serialization,
validation, integration workflows, and edge cases.

Modules tested: flext_cli.config.FlextCliSettings
Scope: All kept configuration operations, validation, integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm
from pydantic_settings import BaseSettings

from flext_cli import FlextCliSettings, cli
from tests import c


class TestsCliConfigBasics:
    """Core config functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        config = FlextCliSettings()
        tm.that(config, none=False)
        tm.that(config, is_=FlextCliSettings)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        config = FlextCliSettings()
        dumped = config.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="verbose")

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior via get_global."""
        config1 = FlextCliSettings.get_global()
        config2 = FlextCliSettings.get_global()
        tm.that(config1.verbose, eq=config2.verbose)


class TestsCliConfigService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_for_testing resets global state."""
        FlextCliSettings()
        FlextCliSettings.reset_for_testing()
        new_config = FlextCliSettings()
        tm.that(new_config, none=False)


class TestsCliLoggingConfig:
    """Logging configuration tests."""

    @pytest.mark.parametrize(
        ("level", "expected"),
        c.Cli.Tests.ConfigFactory.logging_scenarios(),
    )
    def test_logging_levels(self, level: str, expected: str) -> None:
        """Test all logging levels with single parametrized test."""
        tm.that(level in c.Cli.Tests.ConfigFactory.VALID_LOGGING_LEVELS, eq=True)
        tm.that(level, eq=expected)


class TestsCliConfigIntegration:
    """Integration with cli."""

    def test_flext_cli_integration(self) -> None:
        """Test cli uses config."""
        instance = cli
        config = instance.settings
        tm.that(config, none=False)
        tm.that(config, is_=FlextCliSettings)

    def test_flext_cli_settings_namespace(self) -> None:
        """Test cli exposes direct namespaced settings access."""
        settings = cli.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=FlextCliSettings)

    def test_config_inheritance(self) -> None:
        """Test inheritance from BaseSettings (Pydantic v2)."""
        config = FlextCliSettings()
        tm.that(config, is_=BaseSettings)


class TestsCliConfigValidation:
    """Validation tests."""

    @pytest.mark.parametrize("env", c.Cli.Tests.ConfigFactory.VALID_ENVIRONMENTS)
    def test_valid_environments(self, env: str) -> None:
        """Test all valid environments."""
        tm.that(c.Cli.Tests.ConfigFactory.VALID_ENVIRONMENTS, has=env)

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        config: FlextCliSettings = FlextCliSettings()
        dumped = config.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, empty=False)


class TestsCliConfigEdgeCases:
    """Edge cases and boundary conditions."""

    def test_basic_fields_exist(self) -> None:
        """Test config has expected fields."""
        config: FlextCliSettings = FlextCliSettings()
        tm.that(config.verbose, is_=bool)
        tm.that(config.debug, is_=bool)
        tm.that(config.no_color, is_=bool)
        tm.that(config.quiet, is_=bool)
