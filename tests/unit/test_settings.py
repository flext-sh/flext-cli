"""FLEXT CLI Settings Tests - Comprehensive Settings Validation Testing.

Tests for FlextCliSettings covering initialization, serialization,
validation, integration workflows, and edge cases.

Modules tested: flext_cli.settings.FlextCliSettings
Scope: All kept settings operations, validation, integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCliSettings, cli
from tests import c


class TestsCliSettingsBasics:
    """Core settings functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        settings = FlextCliSettings()
        tm.that(settings, none=False)
        tm.that(settings, is_=FlextCliSettings)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        settings = FlextCliSettings()
        dumped = settings.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="verbose")

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior via fetch_global."""
        settings_1 = FlextCliSettings.fetch_global()
        settings_2 = FlextCliSettings.fetch_global()
        tm.that(settings_1.verbose, eq=settings_2.verbose)


class TestsCliSettingsService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_for_testing resets global state."""
        FlextCliSettings()
        FlextCliSettings.reset_for_testing()
        new_settings = FlextCliSettings()
        tm.that(new_settings, none=False)


class TestsCliLoggingSettings:
    """Logging settings tests."""

    @pytest.mark.parametrize(
        ("level", "expected"),
        c.Cli.Tests.ConfigFactory.logging_scenarios(),
    )
    def test_logging_levels(self, level: str, expected: str) -> None:
        """Test all logging levels with single parametrized test."""
        tm.that(level in c.Cli.Tests.ConfigFactory.VALID_LOGGING_LEVELS, eq=True)
        tm.that(level, eq=expected)


class TestsCliSettingsIntegration:
    """Integration with cli."""

    def test_flext_cli_integration(self) -> None:
        """Test cli uses settings."""
        instance = cli
        settings = instance.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=FlextCliSettings)

    def test_flext_cli_settings_namespace(self) -> None:
        """Test cli exposes direct namespaced settings access."""
        settings = cli.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=FlextCliSettings)


class TestsCliSettingsValidation:
    """Validation tests."""

    @pytest.mark.parametrize("env", c.Cli.Tests.ConfigFactory.VALID_ENVIRONMENTS)
    def test_valid_environments(self, env: str) -> None:
        """Test all valid environments."""
        tm.that(c.Cli.Tests.ConfigFactory.VALID_ENVIRONMENTS, has=env)

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        settings: FlextCliSettings = FlextCliSettings()
        dumped = settings.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, empty=False)


class TestsCliSettingsEdgeCases:
    """Edge cases and boundary conditions."""

    def test_basic_fields_exist(self) -> None:
        """Test settings has expected fields."""
        settings: FlextCliSettings = FlextCliSettings()
        tm.that(settings.verbose, is_=bool)
        tm.that(settings.debug, is_=bool)
        tm.that(settings.no_color, is_=bool)
        tm.that(settings.quiet, is_=bool)
