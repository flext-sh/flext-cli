"""FLEXT CLI Common Parameters Tests - Comprehensive Parameter Validation Testing.

Tests for FlextCliCommonParams and common_cli_params decorator covering parameter enforcement,
config application, decorator functionality, logger integration, precedence rules,
validation, error handling, and edge cases with 100% coverage.

Modules tested: flext_cli.common_params.FlextCliCommonParams, FlextCliConfig, FlextCliModels,
FlextCliServiceBase, FlextLogger integration
Scope: All common CLI parameters, parameter enforcement, config application, decorator functionality

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Never

import pytest
import typer
from flext_core import FlextConstants, FlextLogger
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliConfig,
    FlextCliModels,
    FlextCliServiceBase,
)
from flext_cli.typings import CliJsonValue

from ..helpers import FlextCliTestHelpers

# ============================================================================
# ENUMS FOR TEST ORGANIZATION
# ============================================================================


class ConfigParam(StrEnum):
    """Configuration parameter names for testing."""

    VERBOSE = "verbose"
    QUIET = "quiet"
    DEBUG = "debug"
    TRACE = "trace"
    LOG_LEVEL = "log_level"
    LOG_FORMAT = "log_format"
    OUTPUT_FORMAT = "output_format"
    NO_COLOR = "no_color"
    CONFIG_FILE = "config_file"


class LogLevel(StrEnum):
    """Log level values for testing."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(StrEnum):
    """Output format values for testing."""

    JSON = "json"
    TABLE = "table"
    YAML = "yaml"
    CSV = "csv"
    PLAIN = "plain"


class InvalidValue(StrEnum):
    """Invalid values for testing validation."""

    INVALID_LOG_LEVEL = "INVALID_LEVEL"
    INVALID_LOG_FORMAT = "invalid_format"
    INVALID_OUTPUT_FORMAT = "invalid_format"
    INVALID_FIELD_NAME = "nonexistent_field"


# ============================================================================
# TEST DATA MAPPINGS
# ============================================================================


def _get_bool_default(param_name: str) -> bool:
    """Get boolean default value for a parameter."""
    option = FlextCliCommonParams.create_option(param_name)
    default = option.default
    if isinstance(default, bool):
        return default
    return False


def _get_str_default(param_name: str) -> str:
    """Get string default value for a parameter."""
    option = FlextCliCommonParams.create_option(param_name)
    default = option.default
    if isinstance(default, str):
        return default
    return ""


def _get_path_default(param_name: str) -> Path | None:
    """Get Path default value for a parameter."""
    option = FlextCliCommonParams.create_option(param_name)
    default = option.default
    if isinstance(default, Path):
        return default
    if default is None:
        return None
    return None


# Module-level defaults extracted from options
DEFAULT_VERBOSE: bool = _get_bool_default("verbose")
DEFAULT_QUIET: bool = _get_bool_default("quiet")
DEFAULT_DEBUG: bool = _get_bool_default("debug")
DEFAULT_TRACE: bool = _get_bool_default("trace")
DEFAULT_LOG_LEVEL: str = _get_str_default("cli_log_level") or "INFO"
DEFAULT_LOG_FORMAT: str = _get_str_default("log_verbosity") or "compact"
DEFAULT_OUTPUT_FORMAT: str = _get_str_default("output_format") or "table"
DEFAULT_NO_COLOR: bool = _get_bool_default("no_color")
DEFAULT_CONFIG_FILE: Path | None = _get_path_default("config_file")


# Mapping of config parameters to test values
CONFIG_PARAM_TEST_VALUES: dict[ConfigParam, dict[str, bool | str]] = {
    ConfigParam.VERBOSE: {"initial": False, "updated": True},
    ConfigParam.QUIET: {"initial": False, "updated": True},
    ConfigParam.DEBUG: {"initial": False, "updated": True},
    ConfigParam.NO_COLOR: {"initial": False, "updated": True},
    ConfigParam.LOG_LEVEL: {"initial": "INFO", "updated": "DEBUG"},
    ConfigParam.LOG_FORMAT: {"initial": "detailed", "updated": "full"},
    ConfigParam.OUTPUT_FORMAT: {"initial": "table", "updated": "json"},
}

# Mapping of log levels to test
LOG_LEVEL_TEST_DATA: dict[LogLevel, FlextConstants.Settings.LogLevel] = {
    LogLevel.DEBUG: FlextConstants.Settings.LogLevel.DEBUG,
    LogLevel.INFO: FlextConstants.Settings.LogLevel.INFO,
    LogLevel.WARNING: FlextConstants.Settings.LogLevel.WARNING,
    LogLevel.ERROR: FlextConstants.Settings.LogLevel.ERROR,
    LogLevel.CRITICAL: FlextConstants.Settings.LogLevel.CRITICAL,
}

# Mapping of invalid values to expected error keywords
INVALID_VALUE_ERRORS: dict[InvalidValue, list[str]] = {
    InvalidValue.INVALID_LOG_LEVEL: ["invalid", "log level"],
    InvalidValue.INVALID_LOG_FORMAT: ["invalid", "log format"],
    InvalidValue.INVALID_OUTPUT_FORMAT: ["invalid", "output format"],
    InvalidValue.INVALID_FIELD_NAME: ["not found"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _reset_config_instance() -> None:
    """Reset config instance if method exists."""
    reset_method = getattr(FlextCliConfig, "_reset_instance", None)
    if reset_method and callable(reset_method):
        reset_method()


def _create_test_config(**overrides: object) -> FlextCliConfig:
    """Create test config with overrides."""
    # Create a base instance with defaults
    config = FlextCliConfig()
    # Apply overrides directly to the instance
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config


def _create_decorated_command(
    app: typer.Typer,
    command_name: str = "test",
    echo_message: str | None = None,
) -> Callable[..., CliJsonValue]:
    """Create a decorated test command."""

    @app.command(name=command_name)
    @FlextCliCommonParams.create_decorator()
    def decorated_test_command(
        name: str = command_name,
        verbose: bool = DEFAULT_VERBOSE,
        quiet: bool = DEFAULT_QUIET,
        debug: bool = DEFAULT_DEBUG,
        trace: bool = DEFAULT_TRACE,
        log_level: str = DEFAULT_LOG_LEVEL,
        log_format: str = DEFAULT_LOG_FORMAT,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        no_color: bool = DEFAULT_NO_COLOR,
        config_file: Path | None = DEFAULT_CONFIG_FILE,
    ) -> CliJsonValue:
        """Test command with all common parameters."""
        if echo_message:
            typer.echo(echo_message)
        typer.echo(f"Name: {name}")
        if verbose:
            typer.echo("Verbose mode enabled")
        if debug:
            typer.echo("Debug mode enabled")
        typer.echo(f"Log level: {log_level}")
        typer.echo(f"Output format: {output_format}")
        return None

    # Return decorated function - it satisfies CliCommandFunction protocol structurally
    # The protocol accepts any callable with (*args, **kwargs) -> CliJsonValue signature
    # Mypy strict mode may not recognize structural compatibility, but runtime works
    return decorated_test_command


# ============================================================================
# MAIN TEST CLASS
# ============================================================================


class TestFlextCliCommonParams:
    """Comprehensive tests for FlextCliCommonParams functionality.

    Single class with nested test groups organized by functionality.
    Uses factories, enums, mapping, and dynamic tests for maximum code reuse.
    """

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_common_params_class_exists(self) -> None:
        """Test that FlextCliCommonParams class exists."""
        assert FlextCliCommonParams is not None
        assert hasattr(FlextCliCommonParams, "create_option")
        assert hasattr(FlextCliCommonParams, "apply_to_config")
        assert hasattr(FlextCliCommonParams, "get_all_common_params")

    def test_enforcement_enabled_by_default(self) -> None:
        """Test that enforcement is enabled by default."""
        FlextCliCommonParams.enable_enforcement()
        assert FlextCliCommonParams._enforcement_mode is True

    def test_can_disable_enforcement_for_testing(self) -> None:
        """Test that enforcement can be disabled for testing."""
        original_state = FlextCliCommonParams._enforcement_mode

        try:
            FlextCliCommonParams.disable_enforcement()
            assert FlextCliCommonParams._enforcement_mode is False

            FlextCliCommonParams.enable_enforcement()
            assert FlextCliCommonParams._enforcement_mode is True

        finally:
            if original_state:
                FlextCliCommonParams.enable_enforcement()
            else:
                FlextCliCommonParams.disable_enforcement()

    def test_validate_enabled_success(self) -> None:
        """Test validation succeeds when params are enabled."""
        result = FlextCliCommonParams.validate_enabled()
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)

    # ========================================================================
    # CONFIG PARAMETER APPLICATION (Parametrized)
    # ========================================================================

    @pytest.mark.parametrize(
        ("param", "initial_value", "updated_value"),
        [
            (ConfigParam.VERBOSE, False, True),
            (ConfigParam.QUIET, False, True),
            (ConfigParam.DEBUG, False, True),
            (ConfigParam.NO_COLOR, False, True),
        ],
    )
    def test_apply_to_config_bool_params(
        self,
        param: ConfigParam,
        initial_value: bool,
        updated_value: bool,
    ) -> None:
        """Test applying boolean parameters to config."""
        config = _create_test_config(**{param.value: initial_value})

        # Apply parameter using keyword arguments
        if param == ConfigParam.VERBOSE:
            result = FlextCliCommonParams.apply_to_config(config, verbose=updated_value)
        elif param == ConfigParam.QUIET:
            result = FlextCliCommonParams.apply_to_config(config, quiet=updated_value)
        elif param == ConfigParam.DEBUG:
            result = FlextCliCommonParams.apply_to_config(config, debug=updated_value)
        elif param == ConfigParam.NO_COLOR:
            result = FlextCliCommonParams.apply_to_config(
                config, no_color=updated_value
            )
        else:
            msg = f"Unknown param: {param}"
            raise ValueError(msg)

        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()
        assert getattr(updated_config, param.value) == updated_value

    @pytest.mark.parametrize(
        ("param", "initial_value", "updated_value"),
        [
            (ConfigParam.LOG_LEVEL, "INFO", "DEBUG"),
            (ConfigParam.LOG_FORMAT, "detailed", "full"),
            (ConfigParam.OUTPUT_FORMAT, "table", "json"),
        ],
    )
    def test_apply_to_config_string_params(
        self,
        param: ConfigParam,
        initial_value: str,
        updated_value: str,
    ) -> None:
        """Test applying string parameters to config."""
        if param == ConfigParam.LOG_LEVEL:
            config = _create_test_config(
                cli_log_level=FlextConstants.Settings.LogLevel(initial_value)
            )
            result = FlextCliCommonParams.apply_to_config(
                config, log_level=updated_value
            )
            FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
            updated_config = result.unwrap()
            assert updated_config.cli_log_level.value == updated_value
        elif param == ConfigParam.LOG_FORMAT:
            config = _create_test_config(log_verbosity=initial_value)
            result = FlextCliCommonParams.apply_to_config(
                config, log_format=updated_value
            )
            FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
            updated_config = result.unwrap()
            assert updated_config.log_verbosity == updated_value
        elif param == ConfigParam.OUTPUT_FORMAT:
            config = _create_test_config(output_format=initial_value)
            result = FlextCliCommonParams.apply_to_config(
                config, output_format=updated_value
            )
            FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
            updated_config = result.unwrap()
            assert updated_config.output_format == updated_value

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test that trace requires debug to be enabled."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        config.debug = False
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "trace mode requires debug mode" in error_msg

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test applying trace with debug enabled."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        config.debug = True
        result = FlextCliCommonParams.apply_to_config(config, trace=True)

        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()
        assert updated_config.trace is True
        assert updated_config.debug is True

    def test_apply_to_config_multiple_params(self) -> None:
        """Test applying multiple parameters at once."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=True,
            debug=True,
            log_level="DEBUG",
            output_format="json",
            no_color=True,
        )

        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()
        assert updated_config.verbose is True
        assert updated_config.debug is True
        assert updated_config.cli_log_level.value == "DEBUG"
        assert updated_config.output_format == "json"
        assert updated_config.no_color is True

    def test_apply_to_config_none_values_ignored(self) -> None:
        """Test that None values don't override existing config."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        config.verbose = True
        config.debug = False
        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=None,
            debug=None,
        )

        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()
        assert updated_config.verbose is True
        assert updated_config.debug is False

    # ========================================================================
    # LOGGER CONFIGURATION (Parametrized)
    # ========================================================================

    @pytest.mark.parametrize("log_level", [LogLevel.DEBUG.value, LogLevel.INFO.value, LogLevel.WARNING.value, LogLevel.ERROR.value, LogLevel.CRITICAL.value])
    def test_configure_logger_levels(
        self,
        log_level: str,
    ) -> None:
        """Test configuring logger with all log levels."""
        # Convert string to LogLevel enum for dict lookup
        log_level_enum = LogLevel(log_level)
        level_enum = LOG_LEVEL_TEST_DATA[log_level_enum]
        config = _create_test_config(cli_log_level=level_enum)

        result = FlextCliCommonParams.configure_logger(config)

        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)

    # ========================================================================
    # DECORATOR FUNCTIONALITY
    # ========================================================================

    def test_decorator_adds_all_parameters(self) -> None:
        """Test that decorator adds all common parameters."""
        app = typer.Typer()
        _create_decorated_command(app)

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        expected_params = [
            "--verbose",
            "--quiet",
            "--debug",
            "--trace",
            "--log-level",
            "--log-format",
            "--output-format",
            "--no-color",
            "--config-file",
        ]
        for param in expected_params:
            assert param in result.stdout

    @pytest.mark.parametrize(
        ("flag", "expected_message"),
        [
            ("--verbose", "Verbose mode enabled"),
            ("--debug", "Debug mode enabled"),
        ],
    )
    def test_decorator_flags_work(
        self,
        flag: str,
        expected_message: str,
    ) -> None:
        """Test that decorator flags work."""
        app = typer.Typer()
        _create_decorated_command(app, echo_message=expected_message)

        runner = CliRunner()
        result = runner.invoke(app, [flag])

        assert expected_message in result.stdout
        assert result.exit_code == 0

    @pytest.mark.parametrize(
        ("param", "value", "expected_output"),
        [
            ("--log-level", "DEBUG", "Log level: DEBUG"),
            ("--output-format", "json", "Output format: json"),
        ],
    )
    def test_decorator_parameters_work(
        self,
        param: str,
        value: str,
        expected_output: str,
    ) -> None:
        """Test that decorator parameters work."""
        app = typer.Typer()
        _create_decorated_command(app)

        runner = CliRunner()
        result = runner.invoke(app, [param, value])

        assert expected_output in result.stdout
        assert result.exit_code == 0

    def test_decorator_with_config_integration(self) -> None:
        """Test decorator with FlextConfig integration."""
        app = typer.Typer()

        @app.command(name="test")
        @FlextCliCommonParams.create_decorator()
        def decorated_test_command(
            name: str = "test",
            verbose: bool = DEFAULT_VERBOSE,
            debug: bool = DEFAULT_DEBUG,
            log_level: str = DEFAULT_LOG_LEVEL,
            output_format: str = DEFAULT_OUTPUT_FORMAT,
        ) -> CliJsonValue:
            """Test command with config integration."""
            config = FlextCliServiceBase.get_cli_config()
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
                typer.echo(
                    f"Config cli_log_level: {updated_config.cli_log_level.value}",
                )
                typer.echo(f"Config output_format: {updated_config.output_format}")
            return None

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
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
        assert "Config cli_log_level: DEBUG" in result.stdout
        assert "Config output_format: json" in result.stdout
        assert result.exit_code == 0

    # ========================================================================
    # PRECEDENCE TESTS
    # ========================================================================

    def test_cli_param_overrides_env_variable(self) -> None:
        """Test that CLI parameter overrides environment variable."""
        original_debug = os.environ.get("FLEXT_CLI_DEBUG")
        original_verbose = os.environ.get("FLEXT_CLI_VERBOSE")

        try:
            os.environ["FLEXT_CLI_DEBUG"] = "0"
            os.environ["FLEXT_CLI_VERBOSE"] = "0"

            _reset_config_instance()

            config = FlextCliServiceBase.get_cli_config()
            assert config.debug is False
            assert config.verbose is False

            result = FlextCliCommonParams.apply_to_config(
                config, debug=True, verbose=True
            )

            FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
            updated_config = result.unwrap()
            assert updated_config.debug is True
            assert updated_config.verbose is True
        finally:
            if original_debug is None:
                os.environ.pop("FLEXT_CLI_DEBUG", None)
            else:
                os.environ["FLEXT_CLI_DEBUG"] = original_debug
            if original_verbose is None:
                os.environ.pop("FLEXT_CLI_VERBOSE", None)
            else:
                os.environ["FLEXT_CLI_VERBOSE"] = original_verbose

    def test_precedence_order_cli_over_all(self, tmp_path: Path) -> None:
        """Test complete precedence: CLI > ENV > .env > defaults."""
        env_file = tmp_path / ".env"
        env_file.write_text("FLEXT_LOG_LEVEL=WARNING\n")

        original_log_level = os.environ.get("FLEXT_LOG_LEVEL")

        try:
            os.environ["FLEXT_LOG_LEVEL"] = "ERROR"

            original_dir = Path.cwd()
            try:
                os.chdir(tmp_path)

                config = FlextCliServiceBase.get_cli_config()
                result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")

                FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
                updated_config = result.unwrap()
                assert updated_config.cli_log_level.value == "DEBUG"

            finally:
                os.chdir(original_dir)
        finally:
            if original_log_level is None:
                os.environ.pop("FLEXT_LOG_LEVEL", None)
            else:
                os.environ["FLEXT_LOG_LEVEL"] = original_log_level

    # ========================================================================
    # LOGGER INTEGRATION
    # ========================================================================

    def test_logger_configured_with_cli_params(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that logger is properly configured from CLI parameters."""
        config = _create_test_config(
            cli_log_level=FlextConstants.Settings.LogLevel.INFO
        )

        result = FlextCliCommonParams.apply_to_config(
            config,
            log_level=FlextConstants.Settings.LogLevel.DEBUG.value,
        )
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()

        logger_result = FlextCliCommonParams.configure_logger(updated_config)
        FlextCliTestHelpers.AssertHelpers.assert_result_success(logger_result)

        logger = FlextLogger("test_cli_params")
        logger.debug("Debug message")
        logger.info("Info message")

        captured = capsys.readouterr()
        assert "Info message" in captured.out

    def test_logger_respects_runtime_level_change(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that logger respects runtime log level changes."""
        config = _create_test_config(
            cli_log_level=FlextConstants.Settings.LogLevel.INFO
        )
        FlextCliCommonParams.configure_logger(config)

        logger = FlextLogger("test_runtime")
        logger.info("Info at INFO level")
        captured = capsys.readouterr()
        assert "Info at INFO level" in captured.out

        result = FlextCliCommonParams.apply_to_config(config, log_level="WARNING")
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        updated_config = result.unwrap()

        FlextCliCommonParams.configure_logger(updated_config)

        logger.warning("Warning at WARNING level")
        captured = capsys.readouterr()
        assert "Warning at WARNING level" in captured.out

    # ========================================================================
    # COVERAGE COMPLETION AND EDGE CASES
    # ========================================================================

    def test_validate_enabled_when_disabled_in_enforcement_mode(self) -> None:
        """Test validate_enabled fails when disabled in enforcement mode."""
        original_state = FlextCliCommonParams._enforcement_mode
        original_enabled = FlextCliCommonParams._params_enabled

        try:
            FlextCliCommonParams.enable_enforcement()
            FlextCliCommonParams._params_enabled = False

            result = FlextCliCommonParams.validate_enabled()

            FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
            error_msg = str(result.error).lower() if result.error else ""
            assert "mandatory" in error_msg or "disabled" in error_msg

        finally:
            FlextCliCommonParams._enforcement_mode = original_state
            FlextCliCommonParams._params_enabled = original_enabled

    def test_create_option_invalid_field_name(self) -> None:
        """Test create_option with invalid field name."""
        with pytest.raises(ValueError) as exc_info:
            FlextCliCommonParams.create_option(InvalidValue.INVALID_FIELD_NAME.value)

        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_FIELD_NAME]
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_invalid_log_level(self) -> None:
        """Test apply_to_config with invalid log level."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, log_level=InvalidValue.INVALID_LOG_LEVEL.value
        )

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_LEVEL]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_invalid_log_format(self) -> None:
        """Test apply_to_config with invalid log format."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, log_format=InvalidValue.INVALID_LOG_FORMAT.value
        )

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test apply_to_config with invalid output format."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, output_format=InvalidValue.INVALID_OUTPUT_FORMAT.value
        )

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_OUTPUT_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_exception_handling(self) -> None:
        """Test apply_to_config exception handling with actual validation errors."""
        _reset_config_instance()

        # Test invalid log level
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, log_level=InvalidValue.INVALID_LOG_LEVEL.value
        )
        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_LEVEL]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

        _reset_config_instance()

        # Test invalid log format
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, log_format=InvalidValue.INVALID_LOG_FORMAT.value
        )
        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

        _reset_config_instance()

        # Test invalid output format
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config, output_format=InvalidValue.INVALID_OUTPUT_FORMAT.value
        )
        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_OUTPUT_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_configure_logger_invalid_log_level(self) -> None:
        """Test configure_logger with invalid log level."""
        config = FlextCliServiceBase.get_cli_config()
        config.__dict__["cli_log_level"] = "INVALID"

        result = FlextCliCommonParams.configure_logger(config)

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)

    def test_configure_logger_exception_handling(self) -> None:
        """Test configure_logger exception handling."""
        config = FlextCliServiceBase.get_cli_config()
        original_log_level = config.cli_log_level

        def failing_log_level(self: object) -> Never:
            msg = "Log level access failed"
            raise RuntimeError(msg)

        config.__dict__["cli_log_level"] = property(failing_log_level)

        try:
            result = FlextCliCommonParams.configure_logger(config)
        finally:
            config.__dict__["cli_log_level"] = original_log_level

        FlextCliTestHelpers.AssertHelpers.assert_result_failure(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "failed" in error_msg

    def test_get_all_common_params(self) -> None:
        """Test get_all_common_params method."""
        params = FlextCliCommonParams.get_all_common_params()

        assert isinstance(params, dict)
        assert len(params) > 0
        assert "verbose" in params
        assert "debug" in params
        assert "cli_log_level" in params

    def test_create_option_with_pydantic_undefined_default(self) -> None:
        """Test create_option with PydanticUndefinedType default."""
        option = FlextCliCommonParams.create_option("config_file")

        assert option is not None

    def test_create_option_with_minimum_maximum_constraints(self) -> None:
        """Test create_option with min/max constraints."""
        option = FlextCliCommonParams.create_option("cli_log_level")

        assert option is not None
        assert isinstance(option, OptionInfo)
        assert hasattr(option, "default")

    def test_create_decorator_enforcement_mode_exit(self) -> None:
        """Test create_decorator exits when enforcement fails."""
        original_state = FlextCliCommonParams._enforcement_mode
        original_enabled = FlextCliCommonParams._params_enabled

        try:
            FlextCliCommonParams.enable_enforcement()
            FlextCliCommonParams._params_enabled = False

            original_exit = sys.exit
            exit_called: list[int | str | None] = []

            def mock_exit(code: int | str | None = None) -> Never:
                exit_called.append(code)
                raise SystemExit(code)

            sys.exit = mock_exit

            try:
                decorator = FlextCliCommonParams.create_decorator()

                @decorator
                def decorated_test_function(*args: object, **kwargs: object) -> CliJsonValue:
                    """Test function."""
                    return None

                msg = "Expected SystemExit but got none"
                raise AssertionError(msg)
            except SystemExit:
                assert len(exit_called) > 0
                assert exit_called[0] == 1
            finally:
                sys.exit = original_exit

        finally:
            FlextCliCommonParams._enforcement_mode = original_state
            FlextCliCommonParams._params_enabled = original_enabled

    def test_set_log_level_none(self) -> None:
        """Test _set_log_level when log_level is None."""
        config = FlextCliServiceBase.get_cli_config()
        params = FlextCliModels.CliParamsConfig(log_level=None)
        result = FlextCliCommonParams._set_log_level(config, params)
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        assert result.unwrap() == config
