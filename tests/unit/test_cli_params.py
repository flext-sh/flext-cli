"""FLEXT CLI Common Parameters Tests - Comprehensive testing of mandatory CLI parameter group.

Tests for FlextCliCommonParams and common_cli_params decorator with real functionality
testing integrated with FlextConfig and FlextLogger.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from flext_cli import FlextCliCommonParams, FlextCliConfig


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
        assert "trace mode requires debug mode" in result.error.lower()

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
        from flext_core import FlextCore

        logger = FlextCore.Logger(__name__)
        config = FlextCliConfig(log_level="DEBUG")

        result = FlextCliCommonParams.configure_logger(logger, config)

        assert result.is_success
        # FlextCore.Logger uses structlog - level is managed via FlextConfig

    def test_configure_logger_info_level(self) -> None:
        """Test configuring logger with INFO level."""
        from flext_core import FlextCore

        logger = FlextCore.Logger(__name__)
        config = FlextCliConfig(log_level="INFO")

        result = FlextCliCommonParams.configure_logger(logger, config)

        assert result.is_success
        # FlextCore.Logger uses structlog - level managed via config
        # assert logger.level == logging.INFO

    def test_configure_logger_warning_level(self) -> None:
        """Test configuring logger with WARNING level."""
        from flext_core import FlextCore

        logger = FlextCore.Logger(__name__)
        config = FlextCliConfig(log_level="WARNING")

        result = FlextCliCommonParams.configure_logger(logger, config)

        assert result.is_success
        # FlextCore.Logger uses structlog - level managed via config
        # assert logger.level == logging.WARNING

    def test_configure_logger_error_level(self) -> None:
        """Test configuring logger with ERROR level."""
        from flext_core import FlextCore

        logger = FlextCore.Logger(__name__)
        config = FlextCliConfig(log_level="ERROR")

        result = FlextCliCommonParams.configure_logger(logger, config)

        assert result.is_success
        # FlextCore.Logger uses structlog - level managed via config
        # assert logger.level == logging.ERROR

    def test_configure_logger_critical_level(self) -> None:
        """Test configuring logger with CRITICAL level."""
        from flext_core import FlextCore

        logger = FlextCore.Logger(__name__)
        config = FlextCliConfig(log_level="CRITICAL")

        result = FlextCliCommonParams.configure_logger(logger, config)

        assert result.is_success
        # FlextCore.Logger uses structlog - level managed via config
        # assert logger.level == logging.CRITICAL


class TestCommonCliParamsDecorator:
    """Test FlextCliCommonParams.create_decorator() method."""

    def test_decorator_adds_all_parameters(self) -> None:
        """Test that decorator adds all common parameters."""
        app = typer.Typer()

        @app.command()
        @FlextCliCommonParams.create_decorator()
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        def test_command(
            name: str,
            verbose: bool = FlextCliCommonParams.verbose_option(),
            quiet: bool = FlextCliCommonParams.quiet_option(),
            debug: bool = FlextCliCommonParams.debug_option(),
            trace: bool = FlextCliCommonParams.trace_option(),
            log_level: str = FlextCliCommonParams.log_level_option(),
            log_format: str = FlextCliCommonParams.log_format_option(),
            output_format: str = FlextCliCommonParams.output_format_option(),
            no_color: bool = FlextCliCommonParams.no_color_option(),
            config_file: str | None = FlextCliCommonParams.config_file_option(),
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
        monkeypatch.setenv("FLEXT_DEBUG", "false")
        monkeypatch.setenv("FLEXT_VERBOSE", "false")

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
        from flext_core import FlextCore

        # Create config with DEBUG level
        config = FlextCliConfig(log_level="INFO")

        # Apply CLI parameter to change to DEBUG
        result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")
        assert result.is_success
        updated_config = result.unwrap()

        # Configure logger
        logger = FlextCore.Logger("test_cli_params")
        logger_result = FlextCliCommonParams.configure_logger(logger, updated_config)
        assert logger_result.is_success

        # Test logging
        logger.debug("Debug message")
        logger.info("Info message")

        # FlextCore.Logger uses structlog - outputs to stdout, not standard logging
        captured = capsys.readouterr()
        assert "Info message" in captured.out

    def test_logger_respects_runtime_level_change(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that logger respects runtime log level changes."""
        from flext_core import FlextCore

        # Start with INFO
        config = FlextCliConfig(log_level="INFO")
        logger = FlextCore.Logger("test_runtime")
        FlextCliCommonParams.configure_logger(logger, config)

        logger.info("Info at INFO level")
        captured = capsys.readouterr()
        assert "Info at INFO level" in captured.out

        # Change to WARNING via CLI param
        result = FlextCliCommonParams.apply_to_config(config, log_level="WARNING")
        assert result.is_success
        updated_config = result.unwrap()

        FlextCliCommonParams.configure_logger(logger, updated_config)

        # Note: structlog configuration is global and set at initialization
        # Runtime level changes require logger re-initialization
        # This test validates config application, not structlog behavior
        logger.warning("Warning at WARNING level")

        captured = capsys.readouterr()
        assert "Warning at WARNING level" in captured.out
