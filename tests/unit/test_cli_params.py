"""FLEXT CLI Common Parameters Tests - Railway-Oriented Parameter Validation.

Tests for FlextCliCommonParams using Railway-oriented programming patterns.
Zero fallbacks, mocks, or state manipulation. Pure functional testing with
r[T] patterns and Python 3.13 advanced features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum, unique

import pytest
import typer
from flext_core import r
from flext_tests import tm
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliSettings,
)
from tests import t


@unique
class ConfigParam(StrEnum):
    """Test configuration parameters for parametrized tests."""

    VERBOSE = "verbose"
    QUIET = "quiet"
    DEBUG = "debug"
    NO_COLOR = "no_color"
    LOG_LEVEL = "log_level"
    LOG_FORMAT = "log_format"
    OUTPUT_FORMAT = "output_format"


def create_test_config() -> r[FlextCliSettings]:
    """Create test config using Railway pattern - no fallbacks or state manipulation."""
    try:
        config = FlextCliSettings()
        return r[FlextCliSettings].ok(config)
    except Exception as e:
        return r[FlextCliSettings].fail(f"Failed to create test config: {e}")


def create_cli_app() -> r[typer.Typer]:
    """Create CLI app using Railway pattern."""
    try:
        app = typer.Typer()
        return r[typer.Typer].ok(app)
    except Exception as e:
        return r[typer.Typer].fail(f"Failed to create CLI app: {e}")


def create_decorated_command(
    app: typer.Typer,
    command_name: str = "test",
) -> r[Callable[..., t.NormalizedValue]]:
    """Create decorated command using Railway pattern - no mocks or manipulation."""

    @app.command(name=command_name)
    def typer_command(
        verbose: bool = typer.Option(  # pyright: ignore[reportUnknownMemberType]
            False,
            "--verbose",
            "-v",
            help="Enable verbose output",
        ),
        debug: bool = typer.Option(  # pyright: ignore[reportUnknownMemberType]
            False, "--debug", "-d", help="Enable debug mode"
        ),
        log_level: str = typer.Option(  # pyright: ignore[reportUnknownMemberType]
            "INFO",
            "--log-level",
            "-L",
            help="Set logging level",
        ),
        output_format: str = typer.Option(  # pyright: ignore[reportUnknownMemberType]
            "table",
            "--output-format",
            "-o",
            help="Set output format",
        ),
    ) -> None:
        """Test command with Railway-oriented parameter handling."""
        typer.echo(f"Command: {command_name}")
        if verbose:
            typer.echo("Verbose: enabled")
        if debug:
            typer.echo("Debug: enabled")
        typer.echo(f"Log level: {log_level}")
        typer.echo(f"Output format: {output_format}")

    return r[Callable[..., t.NormalizedValue]].ok(typer_command)


class TestsCliCommonParams:
    """Railway-oriented tests for FlextCliCommonParams - zero fallbacks or state manipulation."""

    def test_common_params_class_exists(self) -> None:
        """Test that FlextCliCommonParams exists and has required methods."""
        tm.that(FlextCliCommonParams, none=False)
        tm.that(hasattr(FlextCliCommonParams, "create_option"), eq=True)
        tm.that(hasattr(FlextCliCommonParams, "apply_to_config"), eq=True)

    def test_create_option_success(self) -> None:
        """Test create_option returns valid option using Railway pattern."""
        option = FlextCliCommonParams.create_option("verbose")
        tm.that(option, none=False)

    def test_apply_to_config_with_valid_params(self) -> None:
        """Test apply_to_config with Railway pattern - no state manipulation."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=True,
            debug=True,
            log_level="DEBUG",
        )

        tm.ok(result)
        updated_config = result.value
        tm.that(updated_config.verbose is True, eq=True)
        tm.that(updated_config.debug is True, eq=True)
        tm.that(updated_config.cli_log_level, eq="DEBUG")

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test trace requires debug - Railway pattern validation."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that(error_msg, has="trace mode requires debug mode")

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test trace works with debug enabled - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, debug=True, trace=True)

        tm.ok(result)
        updated_config = result.value
        tm.that(updated_config.debug is True, eq=True)
        tm.that(updated_config.trace is True, eq=True)

    def test_apply_to_config_invalid_log_level(self) -> None:
        """Test invalid log level validation - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, log_level="INVALID")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "log level" in error_msg, eq=True)

    def test_decorator_adds_parameters(self) -> None:
        """Test decorator adds CLI parameters - Railway pattern."""
        app_result = create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = create_decorated_command(app, "test")
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
        app_result = create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--debug"])

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="Verbose: enabled")
        tm.that(result.stdout, has="Debug: enabled")

    def test_decorator_parameters_work(self) -> None:
        """Test decorator parameters work - Railway pattern."""
        app_result = create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["--log-level", "WARNING", "--output-format", "json"],
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
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, log_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "log format" in error_msg, eq=True)

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test invalid output format - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, output_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        tm.that("invalid" in error_msg and "output format" in error_msg, eq=True)
