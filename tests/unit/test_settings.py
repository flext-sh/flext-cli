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

from flext_cli import cli
from tests import c, p


class TestsFlextCliSettingsUnit:
    """Core settings functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        settings = cli.new_settings()
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        settings = cli.new_settings()
        dumped = settings.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="Cli")
        tm.that(dumped["Cli"], has="verbose")

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior via fetch_global."""
        settings_1 = cli.settings.fetch_global()
        settings_2 = cli.settings.fetch_global()
        tm.that(settings_1.Cli.verbose, eq=settings_2.Cli.verbose)

    def test_reset_instance(self) -> None:
        """Test reset_for_testing resets global state."""
        cli.new_settings()
        cli.settings.reset_for_testing()
        new_settings = cli.new_settings()
        tm.that(new_settings, none=False)

    @pytest.mark.parametrize("level", list(c.LogLevel))
    def test_logging_levels(self, level: c.LogLevel) -> None:
        """Every declared log level round-trips through the enum."""
        tm.that(level, is_=c.LogLevel)
        tm.that(c.LogLevel(level.value), eq=level)

    def test_flext_cli_integration(self) -> None:
        """Test cli uses settings."""
        instance = cli
        settings = instance.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    def test_flext_cli_settings_namespace(self) -> None:
        """Test cli exposes direct namespaced settings access."""
        settings = cli.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    @pytest.mark.parametrize("env", list(c.Tests.Environment))
    def test_valid_environments(self, env: c.Tests.Environment) -> None:
        """Each declared deployment environment round-trips through the enum."""
        tm.that(c.Tests.Environment(env.value), eq=env)

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        settings: p.Cli.Settings = cli.new_settings()
        dumped = settings.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, empty=False)

    def test_basic_fields_exist(self) -> None:
        """Test settings has expected fields."""
        settings: p.Cli.Settings = cli.new_settings()
        tm.that(settings.Cli.verbose, is_=bool)
        tm.that(settings.debug, is_=bool)
        tm.that(settings.Cli.no_color, is_=bool)
        tm.that(settings.Cli.quiet, is_=bool)
