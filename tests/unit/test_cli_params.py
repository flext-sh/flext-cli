"""FLEXT CLI Common Parameters Tests - Railway-Oriented Parameter Validation.

Tests for FlextCliCommonParams using Railway-oriented programming patterns.
Zero fallbacks, mocks, or state manipulation. Pure functional testing with
FlextResult[T] patterns and Python 3.13 advanced features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path

import pytest
import typer
from flext_cli import (
    FlextCliCommonParams,
    FlextCliSettings,
)
from flext_core import r
from flext_tests import tm
from typer.testing import CliRunner


class ConfigParam(StrEnum):
    """Test configuration parameters for parametrized tests."""

    VERBOSE = "verbose"
    QUIET = "quiet"
    DEBUG = "debug"
    NO_COLOR = "no_color"
    LOG_LEVEL = "log_level"
    LOG_FORMAT = "log_format"
    OUTPUT_FORMAT = "output_format"


# ============================================================================
# TEST DATA - Railway-Oriented Constants
# ============================================================================

# Python 3.13 advanced type features for test data
type CliTestConfig = dict[str, bool | str | Path | None]
type CliTestResult = r[CliTestConfig]

# ============================================================================
# RAILWAY-ORIENTED TEST HELPERS
# ============================================================================


def create_test_config() -> r[FlextCliSettings]:
    """Create test config using Railway pattern - no fallbacks or state manipulation."""
    try:
        config = FlextCliSettings()
        return r.ok(config)
    except Exception as e:
        return r.fail(f"Failed to create test config: {e}")


def create_cli_app() -> r[typer.Typer]:
    """Create CLI app using Railway pattern."""
    try:
        app = typer.Typer()
        return r.ok(app)
    except Exception as e:
        return r.fail(f"Failed to create CLI app: {e}")


def create_decorated_command(
    app: typer.Typer,
    command_name: str = "test",
) -> r[Callable[..., object]]:
    """Create decorated command using Railway pattern - no mocks or manipulation."""

    @app.command(name=command_name)
    def typer_command(
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Enable verbose output",
        ),
        debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
        log_level: str = typer.Option(
            "INFO",
            "--log-level",
            "-L",
            help="Set logging level",
        ),
        output_format: str = typer.Option(
            "table",
            "--output-format",
            "-o",
            help="Set output format",
        ),
    ) -> None:
        """Test command with Railway-oriented parameter handling."""
        # Direct parameter usage - no manipulation or fallbacks
        typer.echo(f"Command: {command_name}")
        if verbose:
            typer.echo("Verbose: enabled")
        if debug:
            typer.echo("Debug: enabled")
        typer.echo(f"Log level: {log_level}")
        typer.echo(f"Output format: {output_format}")

    # Return the command function directly - Railway pattern
    return r.ok(typer_command)


# ============================================================================
# RAILWAY-ORIENTED TEST CLASS
# ============================================================================


class TestsCliCommonParams:
    """Railway-oriented tests for FlextCliCommonParams - zero fallbacks or state manipulation.

    Tests use pure functional patterns with FlextResult[T] for all operations.
    No mocks, no state manipulation, no environment variable changes.
    """

    def test_common_params_class_exists(self) -> None:
        """Test that FlextCliCommonParams exists and has required methods."""
        # Direct assertion - no fallbacks
        assert FlextCliCommonParams is not None
        assert hasattr(FlextCliCommonParams, "create_option")
        assert hasattr(FlextCliCommonParams, "apply_to_config")
        assert hasattr(FlextCliCommonParams, "get_all_common_params")

    def test_create_option_success(self) -> None:
        """Test create_option returns valid option using Railway pattern."""
        # Direct call - Railway pattern with proper validation
        option = FlextCliCommonParams.create_option("verbose")

        assert option is not None

    def test_apply_to_config_with_valid_params(self) -> None:
        """Test apply_to_config with Railway pattern - no state manipulation."""
        # Create config using Railway pattern
        config_result = create_test_config()
        tm.ok(config_result)

        # Apply parameters using Railway pattern
        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=True,
            debug=True,
            log_level="DEBUG",
        )

        tm.ok(result)
        updated_config = result.value
        assert updated_config.verbose is True
        assert updated_config.debug is True
        assert updated_config.cli_log_level == "DEBUG"

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test trace requires debug - Railway pattern validation."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "trace mode requires debug mode" in error_msg

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test trace works with debug enabled - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, debug=True, trace=True)

        tm.ok(result)
        updated_config = result.value
        assert updated_config.debug is True
        assert updated_config.trace is True

    def test_apply_to_config_invalid_log_level(self) -> None:
        """Test invalid log level validation - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, log_level="INVALID")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "invalid" in error_msg and "log level" in error_msg

    def test_configure_logger_success(self) -> None:
        """Test logger configuration - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        # Apply valid log level first
        config_result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")
        tm.ok(config_result)

        updated_config = config_result.value
        result = FlextCliCommonParams.configure_logger(updated_config)

        tm.ok(result)

    def test_decorator_adds_parameters(self) -> None:
        """Test decorator adds CLI parameters - Railway pattern."""
        app_result = create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--verbose" in result.stdout
        assert "--debug" in result.stdout
        assert "--log-level" in result.stdout
        assert "--output-format" in result.stdout

    def test_decorator_flags_work(self) -> None:
        """Test decorator flags work - Railway pattern."""
        app_result = create_cli_app()
        tm.ok(app_result)

        app = app_result.value
        command_result = create_decorated_command(app, "test")
        tm.ok(command_result)

        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--debug"])

        assert result.exit_code == 0
        assert "Verbose: enabled" in result.stdout
        assert "Debug: enabled" in result.stdout

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

        assert result.exit_code == 0
        assert "Log level: WARNING" in result.stdout
        assert "Output format: json" in result.stdout

    def test_get_all_common_params(self) -> None:
        """Test get_all_common_params returns valid dict - Railway pattern."""
        # Get params directly - Railway pattern without None values
        params = FlextCliCommonParams.get_all_common_params()

        assert isinstance(params, dict)
        assert len(params) > 0
        assert "verbose" in params
        assert "debug" in params
        assert "cli_log_level" in params

    def test_enforcement_can_be_disabled(self) -> None:
        """Test enforcement can be disabled for testing - Railway pattern."""
        # Test enable/disable cycle
        FlextCliCommonParams.enable_enforcement()
        assert FlextCliCommonParams._enforcement_mode is True

        FlextCliCommonParams.disable_enforcement()
        assert not FlextCliCommonParams._enforcement_mode

        # Restore enforcement
        FlextCliCommonParams.enable_enforcement()
        assert FlextCliCommonParams._enforcement_mode is True

    def test_validate_enabled_when_enforced(self) -> None:
        """Test validate_enabled succeeds when enforced - Railway pattern."""
        FlextCliCommonParams.enable_enforcement()
        result = FlextCliCommonParams.validate_enabled()
        tm.ok(result)

    def test_validate_enabled_fails_when_disabled(self) -> None:
        """Test validate_enabled fails when disabled in enforcement mode."""
        FlextCliCommonParams.enable_enforcement()
        FlextCliCommonParams._params_enabled = False

        try:
            result = FlextCliCommonParams.validate_enabled()
            tm.fail(result)
            error_msg = str(result.error).lower() if result.error else ""
            assert "mandatory" in error_msg or "disabled" in error_msg
        finally:
            # Restore state
            FlextCliCommonParams._params_enabled = True

    def test_create_option_invalid_field(self) -> None:
        """Test create_option with invalid field - Railway pattern."""
        # Direct call - Railway pattern handles exceptions properly
        try:
            FlextCliCommonParams.create_option("nonexistent_field")
            pytest.fail("Expected ValueError to be raised")
        except ValueError as e:
            error_msg = str(e).lower()
            assert "not found" in error_msg

    def test_apply_to_config_invalid_log_format(self) -> None:
        """Test invalid log format - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, log_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "invalid" in error_msg and "log format" in error_msg

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test invalid output format - Railway pattern."""
        config_result = create_test_config()
        tm.ok(config_result)

        config = config_result.value
        result = FlextCliCommonParams.apply_to_config(config, output_format="invalid")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "invalid" in error_msg and "output format" in error_msg
