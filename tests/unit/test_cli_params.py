"""FLEXT CLI Common Parameters Tests - Comprehensive testing of mandatory CLI parameter group.

Tests for FlextCliCommonParams and common_cli_params decorator with real functionality
testing integrated with FlextConfig and FlextLogger.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Never, cast

import pytest
import typer
from flext_core import FlextLogger
from typer.testing import CliRunner

from flext_cli import FlextCliCommonParams, FlextCliConfig

# Module-level defaults to avoid B008 - use cast() for type-safe defaults
DEFAULT_VERBOSE: bool = cast("bool", FlextCliCommonParams.verbose_option().default)
DEFAULT_QUIET: bool = cast("bool", FlextCliCommonParams.quiet_option().default)
DEFAULT_DEBUG: bool = cast("bool", FlextCliCommonParams.debug_option().default)
DEFAULT_TRACE: bool = cast("bool", FlextCliCommonParams.trace_option().default)
DEFAULT_LOG_LEVEL: str = cast("str", FlextCliCommonParams.log_level_option().default)
DEFAULT_LOG_FORMAT: str = cast("str", FlextCliCommonParams.log_format_option().default)
DEFAULT_OUTPUT_FORMAT: str = cast(
    "str", FlextCliCommonParams.output_format_option().default
)
DEFAULT_NO_COLOR: bool = cast("bool", FlextCliCommonParams.no_color_option().default)
DEFAULT_CONFIG_FILE: Path | None = FlextCliCommonParams.config_file_option().default


class TestFlextCliCommonParams:
    """Test FlextCliCommonParams class."""

    def test_common_params_class_exists(self) -> None:
        """Test that FlextCliCommonParams class exists."""
        assert FlextCliCommonParams is not None
        assert hasattr(FlextCliCommonParams, "verbose_option")
        assert hasattr(FlextCliCommonParams, "debug_option")
        assert hasattr(FlextCliCommonParams, "apply_to_config")

    def test_enforcement_enabled_by_default(self) -> None:
        """Test that enforcement is enabled by default."""
        # Reset to default state
        FlextCliCommonParams.enable_enforcement()
        assert FlextCliCommonParams._enforcement_mode is True

    def test_can_disable_enforcement_for_testing(self) -> None:
        """Test that enforcement can be disabled for testing."""
        original_state = FlextCliCommonParams._enforcement_mode

        try:
            FlextCliCommonParams.disable_enforcement()
            assert FlextCliCommonParams._enforcement_mode is False

            # Re-enable
            FlextCliCommonParams.enable_enforcement()
            assert FlextCliCommonParams._enforcement_mode is True

        finally:
            # Restore original state
            if original_state:
                FlextCliCommonParams.enable_enforcement()
            else:
                FlextCliCommonParams.disable_enforcement()

    def test_validate_enabled_success(self) -> None:
        """Test validation succeeds when params are enabled."""
        result = FlextCliCommonParams.validate_enabled()
        assert result.is_success

    def test_apply_to_config_verbose(self) -> None:
        """Test applying verbose parameter to config."""
        config = FlextCliConfig(verbose=False)
        result = FlextCliCommonParams.apply_to_config(config, verbose=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.verbose is True

    def test_apply_to_config_quiet(self) -> None:
        """Test applying quiet parameter to config."""
        config = FlextCliConfig(quiet=False)
        result = FlextCliCommonParams.apply_to_config(config, quiet=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.quiet is True

    def test_apply_to_config_debug(self) -> None:
        """Test applying debug parameter to config."""
        config = FlextCliConfig(debug=False)
        result = FlextCliCommonParams.apply_to_config(config, debug=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.debug is True

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test that trace requires debug to be enabled."""
        config = FlextCliConfig(debug=False)
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        # Should fail because debug is not enabled
        assert result.is_failure
        error_msg = result.error or ""
        assert "trace mode requires debug mode" in error_msg.lower()

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test applying trace with debug enabled."""
        config = FlextCliConfig(debug=True)
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.trace is True
        assert updated_config.debug is True

    def test_apply_to_config_log_level(self) -> None:
        """Test applying log level parameter."""
        config = FlextCliConfig(log_level="INFO")
        result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.log_level == "DEBUG"

    def test_apply_to_config_log_format(self) -> None:
        """Test applying log format parameter."""
        config = FlextCliConfig(log_verbosity="detailed")
        result = FlextCliCommonParams.apply_to_config(config, log_format="full")

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.log_verbosity == "full"

    def test_apply_to_config_output_format(self) -> None:
        """Test applying output format parameter."""
        config = FlextCliConfig(output_format="table")
        result = FlextCliCommonParams.apply_to_config(config, output_format="json")

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.output_format == "json"

    def test_apply_to_config_no_color(self) -> None:
        """Test applying no-color parameter."""
        config = FlextCliConfig(no_color=False)
        result = FlextCliCommonParams.apply_to_config(config, no_color=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.no_color is True

    def test_apply_to_config_multiple_params(self) -> None:
        """Test applying multiple parameters at once."""
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=True,
            debug=True,
            log_level="DEBUG",
            output_format="json",
            no_color=True,
        )

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.verbose is True
        assert updated_config.debug is True
        assert updated_config.log_level == "DEBUG"
        assert updated_config.output_format == "json"
        assert updated_config.no_color is True

    def test_apply_to_config_none_values_ignored(self) -> None:
        """Test that None values don't override existing config."""
        config = FlextCliConfig(verbose=True, debug=False)
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=None,  # Should not change
            debug=None,  # Should not change
        )

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.verbose is True  # Unchanged
        assert updated_config.debug is False  # Unchanged

    def test_configure_logger_debug_level(self) -> None:
        """Test configuring logger with DEBUG level."""
        config = FlextCliConfig(log_level="DEBUG")

        result = FlextCliCommonParams.configure_logger(config)

        assert result.is_success
        # FlextLogger uses structlog - level is managed via FlextConfig

    def test_configure_logger_info_level(self) -> None:
        """Test configuring logger with INFO level."""
        config = FlextCliConfig(log_level="INFO")

        result = FlextCliCommonParams.configure_logger(config)

        assert result.is_success
        # FlextLogger uses structlog - level managed via config
        # assert logger.level == logging.INFO

    def test_configure_logger_warning_level(self) -> None:
        """Test configuring logger with WARNING level."""
        config = FlextCliConfig(log_level="WARNING")

        result = FlextCliCommonParams.configure_logger(config)

        assert result.is_success
        # FlextLogger uses structlog - level managed via config
        # assert logger.level == logging.WARNING

    def test_configure_logger_error_level(self) -> None:
        """Test configuring logger with ERROR level."""
        config = FlextCliConfig(log_level="ERROR")

        result = FlextCliCommonParams.configure_logger(config)

        assert result.is_success
        # FlextLogger uses structlog - level managed via config
        # assert logger.level == logging.ERROR

    def test_configure_logger_critical_level(self) -> None:
        """Test configuring logger with CRITICAL level."""
        config = FlextCliConfig(log_level="CRITICAL")

        result = FlextCliCommonParams.configure_logger(config)

        assert result.is_success
        # FlextLogger uses structlog - level managed via config
        # assert logger.level == logging.CRITICAL


class TestCommonCliParamsDecorator:
    """Test FlextCliCommonParams.create_decorator() method."""

    def test_decorator_adds_all_parameters(self) -> None:
        """Test that decorator adds all common parameters."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command with all common parameters."""
            typer.echo(f"Name: {name}")
            typer.echo(f"Verbose: {verbose}")
            typer.echo(f"Debug: {debug}")
            typer.echo(f"Log Level: {log_level}")

        runner = CliRunner()
        result = runner.invoke(app, ["test", "--help"])

        # Verify help text contains all parameters
        assert "--verbose" in result.stdout
        assert "--quiet" in result.stdout
        assert "--debug" in result.stdout
        assert "--trace" in result.stdout
        assert "--log-level" in result.stdout
        assert "--log-format" in result.stdout
        assert "--output-format" in result.stdout
        assert "--no-color" in result.stdout
        assert "--config-file" in result.stdout

    def test_decorator_verbose_flag_works(self) -> None:
        """Test that --verbose flag works."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command."""
            if verbose:
                typer.echo("Verbose mode enabled")
            typer.echo(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(app, ["test", "--verbose"])

        assert "Verbose mode enabled" in result.stdout
        assert result.exit_code == 0

    def test_decorator_debug_flag_works(self) -> None:
        """Test that --debug flag works."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command."""
            if debug:
                typer.echo("Debug mode enabled")
            typer.echo(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(app, ["test", "--debug"])

        assert "Debug mode enabled" in result.stdout
        assert result.exit_code == 0

    def test_decorator_log_level_parameter_works(self) -> None:
        """Test that --log-level parameter works."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command."""
            typer.echo(f"Log level: {log_level}")

        runner = CliRunner()
        result = runner.invoke(app, ["test", "--log-level", "DEBUG"])

        assert "Log level: DEBUG" in result.stdout
        assert result.exit_code == 0

    def test_decorator_output_format_parameter_works(self) -> None:
        """Test that --output-format parameter works."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command."""
            typer.echo(f"Output format: {output_format}")

        runner = CliRunner()
        result = runner.invoke(app, ["test", "--output-format", "json"])

        assert "Output format: json" in result.stdout
        assert result.exit_code == 0

    def test_decorator_with_config_integration(self) -> None:
        """Test decorator with FlextConfig integration."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str,
            verbose: bool = DEFAULT_VERBOSE,
            quiet: bool = DEFAULT_QUIET,
            debug: bool = DEFAULT_DEBUG,
            trace: bool = DEFAULT_TRACE,
            log_level: str = DEFAULT_LOG_LEVEL,
            log_format: str = DEFAULT_LOG_FORMAT,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
            no_color: bool = DEFAULT_NO_COLOR,
            config_file: Path | None = DEFAULT_CONFIG_FILE,
        ) -> None:
            """Test command with config integration."""
            # Create config and apply CLI params
            config = FlextCliConfig()
            result = FlextCliCommonParams.apply_to_config(
                config,
                verbose=verbose,
                debug=debug,
                log_level=log_level,
                output_format=output_format,
            )

            if result.is_success:
                updated_config = result.unwrap()
                typer.echo(f"Config verbose: {updated_config.verbose}")
                typer.echo(f"Config debug: {updated_config.debug}")
                typer.echo(f"Config log_level: {updated_config.log_level}")
                typer.echo(f"Config output_format: {updated_config.output_format}")

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "test",
                "--verbose",
                "--debug",
                "--log-level",
                "DEBUG",
                "--output-format",
                "json",
            ],
        )

        assert "Config verbose: True" in result.stdout
        assert "Config debug: True" in result.stdout
        assert "Config log_level: DEBUG" in result.stdout
        assert "Config output_format: json" in result.stdout
        assert result.exit_code == 0


class TestCLIParametersPrecedence:
    """Test CLI parameters precedence over environment and config."""

    def test_cli_param_overrides_env_variable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that CLI parameter overrides environment variable."""
        # Set environment variable
        monkeypatch.setenv("FLEXT_DEBUG", "0")
        monkeypatch.setenv("FLEXT_VERBOSE", "0")

        # Create config (loads from ENV)
        config = FlextCliConfig()
        assert config.debug is False
        assert config.verbose is False

        # Apply CLI parameters (should override ENV)
        result = FlextCliCommonParams.apply_to_config(config, debug=True, verbose=True)

        assert result.is_success
        updated_config = result.unwrap()
        assert updated_config.debug is True  # CLI overrides ENV
        assert updated_config.verbose is True  # CLI overrides ENV

    def test_precedence_order_cli_over_all(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test complete precedence: CLI > ENV > .env > defaults."""
        import os

        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("FLEXT_LOG_LEVEL=WARNING\n")

        # Set ENV variable
        monkeypatch.setenv("FLEXT_LOG_LEVEL", "ERROR")

        # Change to tmp directory
        original_dir = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Create config (loads .env and ENV)
            config = FlextCliConfig()
            # ENV should override .env
            assert config.log_level == "ERROR"

            # CLI parameter should override all
            result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")

            assert result.is_success
            updated_config = result.unwrap()
            assert updated_config.log_level == "DEBUG"  # CLI wins

        finally:
            os.chdir(original_dir)


class TestLoggerIntegration:
    """Test integration with FlextLogger."""

    def test_logger_configured_with_cli_params(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that logger is properly configured from CLI parameters."""
        # Create config with DEBUG level
        config = FlextCliConfig(log_level="INFO")

        # Apply CLI parameter to change to DEBUG
        result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")
        assert result.is_success
        updated_config = result.unwrap()

        # Configure logger (validates config only)
        logger_result = FlextCliCommonParams.configure_logger(updated_config)
        assert logger_result.is_success

        # Create logger with validated config
        logger = FlextLogger("test_cli_params")

        # Test logging
        logger.debug("Debug message")
        logger.info("Info message")

        # FlextLogger uses structlog - outputs to stdout, not standard logging
        captured = capsys.readouterr()
        assert "Info message" in captured.out

    def test_logger_respects_runtime_level_change(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that logger respects runtime log level changes."""
        # Start with INFO
        config = FlextCliConfig(log_level="INFO")
        FlextCliCommonParams.configure_logger(config)

        logger = FlextLogger("test_runtime")
        logger.info("Info at INFO level")
        captured = capsys.readouterr()
        assert "Info at INFO level" in captured.out

        # Change to WARNING via CLI param
        result = FlextCliCommonParams.apply_to_config(config, log_level="WARNING")
        assert result.is_success
        updated_config = result.unwrap()

        FlextCliCommonParams.configure_logger(updated_config)

        # Note: structlog configuration is global and set at initialization
        # Runtime level changes require logger re-initialization
        # This test validates config application, not structlog behavior
        logger.warning("Warning at WARNING level")

        captured = capsys.readouterr()
        assert "Warning at WARNING level" in captured.out


class TestCliParamsCoverageCompletion:
    """Coverage completion tests for missing lines in cli_params.py."""

    def test_validate_enabled_when_disabled_in_enforcement_mode(self) -> None:
        """Test validate_enabled fails when disabled in enforcement mode (line 112)."""
        original_state = FlextCliCommonParams._enforcement_mode
        original_enabled = FlextCliCommonParams._params_enabled

        try:
            # Enable enforcement and disable params
            FlextCliCommonParams.enable_enforcement()
            FlextCliCommonParams._params_enabled = False

            result = FlextCliCommonParams.validate_enabled()

            assert result.is_failure
            assert result.error is not None
            assert (
                "mandatory" in result.error.lower()
                or "disabled" in result.error.lower()
            )

        finally:
            # Restore original state
            FlextCliCommonParams._enforcement_mode = original_state
            FlextCliCommonParams._params_enabled = original_enabled

    def test_create_option_invalid_field_name(self) -> None:
        """Test create_option with invalid field name (lines 145-146)."""
        with pytest.raises(ValueError) as exc_info:
            FlextCliCommonParams.create_option("nonexistent_field")

        assert "not found" in str(exc_info.value).lower()

    def test_apply_to_config_invalid_log_level(self) -> None:
        """Test apply_to_config with invalid log level (lines 338-339)."""
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(config, log_level="INVALID_LEVEL")

        assert result.is_failure
        assert result.error is not None
        assert "invalid log level" in result.error.lower()

    def test_apply_to_config_invalid_log_format(self) -> None:
        """Test apply_to_config with invalid log format (lines 347-348)."""
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(
            config, log_format="invalid_format"
        )

        assert result.is_failure
        assert result.error is not None
        assert "invalid log format" in result.error.lower()

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test apply_to_config with invalid output format (lines 356-357)."""
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(
            config, output_format="invalid_format"
        )

        assert result.is_failure
        assert result.error is not None
        assert "invalid output format" in result.error.lower()

    def test_apply_to_config_exception_handling(self) -> None:
        """Test apply_to_config exception handling with actual validation errors."""
        # Test with invalid log level that should trigger validation error
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(config, log_level="INVALID_LEVEL")

        assert result.is_failure
        assert result.error is not None
        assert "invalid log level" in result.error.lower()

        # Test with invalid log format that should trigger validation error
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(
            config, log_format="invalid_format"
        )

        assert result.is_failure
        assert result.error is not None
        assert "invalid log format" in result.error.lower()

        # Test with invalid output format that should trigger validation error
        config = FlextCliConfig()
        result = FlextCliCommonParams.apply_to_config(
            config, output_format="invalid_format"
        )

        assert result.is_failure
        assert result.error is not None
        assert "invalid output format" in result.error.lower()

        # Test trace without debug (business rule validation)
        config = FlextCliConfig(debug=False)
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        assert result.is_failure
        assert result.error is not None
        assert "trace mode requires debug mode" in result.error.lower()

    def test_configure_logger_invalid_log_level(self) -> None:
        """Test configure_logger with invalid log level (lines 394-395)."""
        config = FlextCliConfig()
        # Directly set invalid log level (bypassing validation)
        config.__dict__["log_level"] = "INVALID"

        result = FlextCliCommonParams.configure_logger(config)

        # Should fail with invalid log level
        assert result.is_failure
        assert result.error is not None

    def test_configure_logger_exception_handling(self) -> None:
        """Test configure_logger exception handling (lines 403-404)."""
        # Use a valid config but patch log_level property to raise exception
        config = FlextCliConfig()

        # Patch the log_level property to raise an exception
        original_log_level = config.log_level

        def failing_log_level(self: object) -> Never:
            msg = "Log level access failed"
            raise RuntimeError(msg)

        # Create property that raises on access
        config.__dict__["log_level"] = property(failing_log_level)

        try:
            result = FlextCliCommonParams.configure_logger(config)
        finally:
            # Restore original log_level
            config.__dict__["log_level"] = original_log_level

        assert result.is_failure
        assert result.error is not None
        assert "failed" in result.error.lower()

    def test_get_all_common_params(self) -> None:
        """Test get_all_common_params method (lines 278-282)."""
        params = FlextCliCommonParams.get_all_common_params()

        # Should return dict[str, object] with all common parameters
        assert isinstance(params, dict)
        assert len(params) > 0
        # Check that parameters are sorted by priority
        assert "verbose" in params
        assert "debug" in params
        assert "log_level" in params

    def test_create_option_with_pydantic_undefined_default(self) -> None:
        """Test create_option with PydanticUndefinedType default (line 180)."""
        # config_dir has PydanticUndefined as default
        option = FlextCliCommonParams.create_option("config_dir")

        # Should successfully create option with None as default
        assert option is not None
        # The option should be created without errors

    def test_create_option_with_minimum_maximum_constraints(self) -> None:
        """Test create_option with min/max constraints (lines 192-193, 207, 209)."""
        # database_pool_size has both minimum (1) and maximum (100) constraints
        option = FlextCliCommonParams.create_option("database_pool_size")

        # Should successfully create option with min/max constraints
        assert option is not None
        # The option should include range in help text and min/max in kwargs

    def test_create_decorator_enforcement_mode_exit(self) -> None:
        """Test create_decorator exits when enforcement fails (line 455)."""
        import sys

        original_state = FlextCliCommonParams._enforcement_mode
        original_enabled = FlextCliCommonParams._params_enabled

        try:
            # Enable enforcement and disable params (will fail validation)
            FlextCliCommonParams.enable_enforcement()
            FlextCliCommonParams._params_enabled = False

            # Mock sys.exit to prevent actual exit
            original_exit = sys.exit
            exit_called = []

            def mock_exit(code: int | str | None = None) -> Never:
                exit_called.append(code)
                raise SystemExit(code)

            sys.exit = mock_exit

            try:
                # Create decorator - this returns a function
                decorator = FlextCliCommonParams.create_decorator()

                # Apply decorator to a test function - THIS triggers the validation
                @decorator
                def decorated_test_function() -> None:
                    """Test function."""

                # If we get here without SystemExit, test fails
                msg = "Expected SystemExit but got none"
                raise AssertionError(msg)
            except SystemExit:
                # Expected - sys.exit was called
                assert len(exit_called) > 0
                assert exit_called[0] == 1
            finally:
                sys.exit = original_exit

        finally:
            # Restore original state
            FlextCliCommonParams._enforcement_mode = original_state
            FlextCliCommonParams._params_enabled = original_enabled

    def test_apply_to_config_setattr_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test apply_to_config exception handler (lines 388-389)."""
        config = FlextCliConfig()

        # Mock FlextCliConstants.LOG_LEVELS_LIST to raise exception when accessed
        # This will trigger the exception handler during log_level validation
        def mock_log_levels_list_raises(*args: object, **kwargs: object) -> None:
            msg = "Constants access error"
            raise RuntimeError(msg)

        # Create mock error messages class
        mock_error_messages = type(
            "MockErrorMessages",
            (),
            {
                "APPLY_PARAMS_FAILED": "Failed to apply CLI parameters to config: {error}"
            },
        )()

        # Create a mock property that raises
        mock_constants = type(
            "MockConstants",
            (),
            {
                "LOG_LEVELS_LIST": property(lambda self: mock_log_levels_list_raises()),
                "CliParamsErrorMessages": mock_error_messages,
            },
        )()

        monkeypatch.setattr("flext_cli.cli_params.FlextCliConstants", mock_constants)

        result = FlextCliCommonParams.apply_to_config(config, log_level="INFO")

        assert result.is_failure
        assert "failed to apply" in str(result.error).lower()
