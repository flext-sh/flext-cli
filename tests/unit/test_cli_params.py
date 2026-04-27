"""FLEXT CLI Common Parameters Tests - Railway-Oriented Parameter Validation.

Tests for FlextCliCommonParams using Railway-oriented programming patterns.
Zero fallbacks, mocks, or state manipulation. Pure functional testing with
r[T] patterns and Python 3.13 advanced features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import FlextCliCommonParams
from tests import c, u


class TestsFlextCliCommonParams:
    """Railway-oriented tests for FlextCliCommonParams - zero fallbacks or state manipulation."""

    def test_create_option_returns_option_info_for_known_fields(self) -> None:
        """Test create_option returns OptionInfo for each registered CLI param."""
        for field_name in ("verbose", "quiet", "debug"):
            option = FlextCliCommonParams.create_option(field_name)
            assert isinstance(option, OptionInfo)

    def test_create_option_success(self) -> None:
        """Test create_option returns valid option using Railway pattern."""
        option = FlextCliCommonParams.create_option("verbose")
        assert option is not None

    def test_apply_to_config_with_valid_params(self) -> None:
        """Test apply_to_config with Railway pattern - no state manipulation."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(
            settings,
            verbose=True,
            debug=True,
            log_level=c.LogLevel.DEBUG,
        )

        tm.ok(result)
        updated_config = result.value
        tm.that(updated_config.verbose is True, eq=True)
        tm.that(updated_config.debug is True, eq=True)
        tm.that(updated_config.cli_log_level, eq=c.LogLevel.DEBUG)

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test trace requires debug - Railway pattern validation."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(settings, trace=True)

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that(error_msg, has="trace mode requires debug mode")

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test trace works with debug enabled - Railway pattern."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(settings, debug=True, trace=True)

        tm.ok(result)
        updated_config = result.value
        tm.that(updated_config.debug is True, eq=True)
        tm.that(updated_config.trace is True, eq=True)

    def test_apply_to_config_invalid_log_level(self) -> None:
        """Test invalid log level validation - Railway pattern."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(settings, log_level="INVALID")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "log level" in error_msg, eq=True)

    def test_decorator_adds_parameters(self) -> None:
        """Test decorator adds CLI parameters - Railway pattern."""
        app_result = u.Tests.create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = u.Tests.create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="--verbose")
        tm.that(result.stdout, has="--debug")
        tm.that(result.stdout, has="--log-level")
        tm.that(result.stdout, has="--output-format")

    def test_decorator_flags_work(self) -> None:
        """Test decorator flags work - Railway pattern."""
        app_result = u.Tests.create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = u.Tests.create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--debug"])

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="Verbose: enabled")
        tm.that(result.stdout, has="Debug: enabled")

    def test_decorator_parameters_work(self) -> None:
        """Test decorator parameters work - Railway pattern."""
        app_result = u.Tests.create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = u.Tests.create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "--log-level",
                c.LogLevel.WARNING,
                "--output-format",
                c.Cli.OutputFormats.JSON,
            ],
        )

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="Log level: WARNING")
        tm.that(result.stdout, has="Output format: json")

    def test_create_option_invalid_field(self) -> None:
        """Test create_option with invalid field - Railway pattern."""
        try:
            FlextCliCommonParams.create_option("nonexistent_field")
            pytest.fail("Expected ValueError to be raised")
        except ValueError as e:
            error_msg = str(e).lower()
            tm.that(error_msg, has="not found")

    def test_apply_to_config_invalid_log_format(self) -> None:
        """Test invalid log format - Railway pattern."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(settings, log_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "log format" in error_msg, eq=True)

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test invalid output format - Railway pattern."""
        config_result = u.Tests.create_test_settings()
        tm.ok(config_result)

        settings = config_result.value
        result = FlextCliCommonParams.apply_to_config(settings, output_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "output format" in error_msg, eq=True)
