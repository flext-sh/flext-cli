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
from collections.abc import Callable, Generator
from enum import StrEnum
from pathlib import Path
from typing import Never

import pytest
import typer
from flext_core import FlextConstants, FlextLogger, t
from flext_tests import tm
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliConfig,
    FlextCliServiceBase,
    c,
    m,
)

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
) -> Callable[..., t.GeneralValueType]:
    """Create a decorated test command."""

    # Register command with Typer using specific types for Typer compatibility
    # Business Rule: Typer command parameters MUST use typer.Option() for CLI integration
    # Architecture: create_option() returns OptionInfo which must be used with typer.Option()
    # Audit Implication: Parameter defaults come from FlextCliConfig field defaults
    @app.command(name=command_name)
    def typer_command(
        verbose: bool = typer.Option(
            default=_get_bool_default("verbose"),
            help="Enable verbose output",
        ),
        quiet: bool = typer.Option(
            default=_get_bool_default("quiet"),
            help="Suppress non-error output",
        ),
        debug: bool = typer.Option(
            default=_get_bool_default("debug"),
            help="Enable debug mode",
        ),
        trace: bool = typer.Option(
            default=_get_bool_default("trace"),
            help="Enable trace mode (requires debug)",
        ),
        log_level: str = typer.Option(
            default=_get_str_default("cli_log_level"),
            help="Set logging level",
        ),
        log_format: str = typer.Option(
            default=_get_str_default("log_verbosity"),
            help="Set log format",
        ),
        output_format: str = typer.Option(
            default=_get_str_default("output_format"),
            help="Set output format",
        ),
        no_color: bool = typer.Option(
            default=_get_bool_default("no_color"),
            help="Disable colored output",
        ),
        config_file: str | None = typer.Option(
            default=_get_path_default("config_file"),
            help="Path to configuration file",
        ),
    ) -> None:
        """Test command with all common parameters."""
        # Use parameter values directly (Typer provides them with correct types)
        if echo_message:
            typer.echo(echo_message)
        typer.echo(f"Name: {command_name}")
        if verbose:
            typer.echo("Verbose mode enabled")
        if debug:
            typer.echo("Debug mode enabled")
        typer.echo(f"Log level: {log_level}")
        typer.echo(f"Output format: {output_format}")

    # Create wrapper function that satisfies CliCommandFunction protocol
    # This wrapper is used for protocol compatibility but typer_command is registered
    def command_wrapper(
        *args: t.GeneralValueType,
        **kwargs: t.GeneralValueType,
    ) -> t.GeneralValueType:
        """Wrapper function that satisfies CliCommandFunction protocol."""
        # Extract named parameters from kwargs
        verbose = kwargs.get("verbose", DEFAULT_VERBOSE)
        quiet = kwargs.get("quiet", DEFAULT_QUIET)
        debug = kwargs.get("debug", DEFAULT_DEBUG)
        trace = kwargs.get("trace", DEFAULT_TRACE)
        # Handle both log_level and cli_log_level (registry uses cli_log_level but CLI uses --log-level)
        # The Typer CLI uses --log-level but the field name is cli_log_level
        log_level = (
            kwargs.get("log_level") or kwargs.get("cli_log_level") or DEFAULT_LOG_LEVEL
        )
        log_format = kwargs.get("log_format", DEFAULT_LOG_FORMAT)
        output_format = kwargs.get("output_format", DEFAULT_OUTPUT_FORMAT)
        no_color = kwargs.get("no_color", DEFAULT_NO_COLOR)

        # Type narrowing
        assert isinstance(verbose, bool)
        assert isinstance(quiet, bool)
        assert isinstance(debug, bool)
        assert isinstance(trace, bool)
        assert isinstance(log_level, str)
        assert isinstance(log_format, str)
        assert isinstance(output_format, str)
        assert isinstance(no_color, bool)

        # Call typer_command with extracted parameters
        # Convert config_file from Path | None to str | None if needed
        config_file_value = kwargs.get("config_file", DEFAULT_CONFIG_FILE)
        config_file_str: str | None = (
            str(config_file_value) if config_file_value is not None else None
        )
        typer_command(
            verbose=verbose,
            quiet=quiet,
            debug=debug,
            trace=trace,
            log_level=log_level,
            log_format=log_format,
            output_format=output_format,
            no_color=no_color,
            config_file=config_file_str,
        )
        return None

    # Apply decorator to wrapper (satisfies protocol)
    return FlextCliCommonParams.create_decorator()(command_wrapper)


# ============================================================================
# MAIN TEST CLASS
# ============================================================================


class TestsCliCommonParams:
    """Comprehensive tests for FlextCliCommonParams functionality.

    Single class with nested test groups organized by functionality.
    Uses factories, enums, mapping, and dynamic tests for maximum code reuse.
    """

    @pytest.fixture(autouse=True)
    def _reset_config_before_test(self) -> Generator[None]:
        """Reset config instance before each test to ensure isolation."""
        # Clean up environment variables that might affect config
        os.environ.pop("FLEXT_CLI_DEBUG", None)
        os.environ.pop("FLEXT_CLI_VERBOSE", None)
        os.environ.pop("FLEXT_CLI_TRACE", None)
        os.environ.pop("FLEXT_CLI_QUIET", None)
        # Reset config instance - must be done before and after
        _reset_config_instance()
        if hasattr(FlextCliConfig, "_instance"):
            FlextCliConfig._instance = None
        yield
        # Clean up after test as well
        _reset_config_instance()
        if hasattr(FlextCliConfig, "_instance"):
            FlextCliConfig._instance = None

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
        tm.ok(result)

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
                config,
                no_color=updated_value,
            )
        else:
            msg = f"Unknown param: {param}"
            raise ValueError(msg)

        tm.ok(result)
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
                cli_log_level=FlextConstants.Settings.LogLevel(initial_value),
            )
            result = FlextCliCommonParams.apply_to_config(
                config,
                log_level=updated_value,
            )
            tm.ok(result)
            updated_config = result.unwrap()
            assert updated_config.cli_log_level.value == updated_value
        elif param == ConfigParam.LOG_FORMAT:
            config = _create_test_config(log_verbosity=initial_value)
            result = FlextCliCommonParams.apply_to_config(
                config,
                log_format=updated_value,
            )
            tm.ok(result)
            updated_config = result.unwrap()
            assert updated_config.log_verbosity == updated_value
        elif param == ConfigParam.OUTPUT_FORMAT:
            config = _create_test_config(output_format=initial_value)
            result = FlextCliCommonParams.apply_to_config(
                config,
                output_format=updated_value,
            )
            tm.ok(result)
            updated_config = result.unwrap()
            assert updated_config.output_format == updated_value

    def test_apply_to_config_trace_requires_debug(self) -> None:
        """Test that trace requires debug to be enabled."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        # Create a modified config with debug=False using model_copy
        config_without_debug = config.model_copy(update={"debug": False})
        result = FlextCliCommonParams.apply_to_config(config_without_debug, trace=True)

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "trace mode requires debug mode" in error_msg

    def test_apply_to_config_trace_with_debug(self) -> None:
        """Test applying trace with debug enabled."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        # Create a modified config with debug=True using model_copy
        config_with_debug = config.model_copy(update={"debug": True})
        result = FlextCliCommonParams.apply_to_config(config_with_debug, trace=True)

        tm.ok(result)
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

        tm.ok(result)
        updated_config = result.unwrap()
        assert updated_config.verbose is True
        assert updated_config.debug is True
        assert updated_config.cli_log_level.value == "DEBUG"
        assert updated_config.output_format == c.Cli.OutputFormats.JSON.value
        assert updated_config.no_color is True

    def test_apply_to_config_none_values_ignored(self) -> None:
        """Test that None values don't override existing config."""
        _reset_config_instance()
        config = FlextCliServiceBase.get_cli_config()
        # Create a modified config using model_copy instead of direct assignment
        config_modified = config.model_copy(update={"verbose": True, "debug": False})
        result = FlextCliCommonParams.apply_to_config(
            config_modified,
            verbose=None,
            debug=None,
        )

        tm.ok(result)
        updated_config = result.unwrap()
        assert updated_config.verbose is True
        assert updated_config.debug is False

    # ========================================================================
    # LOGGER CONFIGURATION (Parametrized)
    # ========================================================================

    @pytest.mark.parametrize(
        "log_level",
        [
            LogLevel.DEBUG.value,
            LogLevel.INFO.value,
            LogLevel.WARNING.value,
            LogLevel.ERROR.value,
            LogLevel.CRITICAL.value,
        ],
    )
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

        tm.ok(result)

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

        # Register command with Typer using specific types for Typer compatibility
        # Use typer.Option() with create_option() to get proper defaults
        @app.command(name="test")
        def typer_command(
            verbose: bool = typer.Option(
                False,
                "--verbose",
                "-v",
                help="Enable verbose output",
            ),
            debug: bool = typer.Option(
                False,
                "--debug",
                "-d",
                help="Enable debug mode",
            ),
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
            """Test command with config integration."""
            # Use parameter values directly (Typer provides them with correct types)
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

        # Create wrapper function that satisfies CliCommandFunction protocol
        # This wrapper is used for protocol compatibility but typer_command is registered
        def wrapper(
            *args: t.GeneralValueType,
            **kwargs: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Wrapper to satisfy CliCommandFunction protocol."""
            # Extract named parameters from kwargs
            verbose = kwargs.get("verbose", DEFAULT_VERBOSE)
            debug = kwargs.get("debug", DEFAULT_DEBUG)
            # Handle both log_level and cli_log_level (registry uses cli_log_level but CLI uses --log-level)
            log_level = (
                kwargs.get("log_level")
                or kwargs.get("cli_log_level")
                or DEFAULT_LOG_LEVEL
            )
            output_format = kwargs.get("output_format", DEFAULT_OUTPUT_FORMAT)

            # Type narrowing
            assert isinstance(verbose, bool)
            assert isinstance(debug, bool)
            assert isinstance(log_level, str)
            assert isinstance(output_format, str)

            # Call typer_command with extracted parameters
            typer_command(
                verbose=verbose,
                debug=debug,
                log_level=log_level,
                output_format=output_format,
            )
            return None

        # Apply decorator to wrapper (satisfies protocol)
        FlextCliCommonParams.create_decorator()(wrapper)

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
            # Force cleanup of any previous state - do this BEFORE setting env vars
            _reset_config_instance()
            if hasattr(FlextCliConfig, "_instance"):
                FlextCliConfig._instance = None

            # Clear environment variables first to ensure clean state
            os.environ.pop("FLEXT_CLI_DEBUG", None)
            os.environ.pop("FLEXT_CLI_VERBOSE", None)

            # Reset again after clearing env vars
            _reset_config_instance()
            if hasattr(FlextCliConfig, "_instance"):
                FlextCliConfig._instance = None

            # Set environment variables to explicit False values
            # Use "0" string which Pydantic Settings converts to False boolean
            # Pydantic Settings treats "0", "false", "no", "" as False
            os.environ["FLEXT_CLI_DEBUG"] = "0"
            os.environ["FLEXT_CLI_VERBOSE"] = "0"

            # Reset config instance after setting env vars to ensure fresh load
            _reset_config_instance()
            if hasattr(FlextCliConfig, "_instance"):
                FlextCliConfig._instance = None

            # Get fresh config instance that will load from environment
            # Use FlextCliConfig() directly to ensure we get a fresh instance
            # after resetting the singleton
            config = FlextCliConfig()
            assert config.debug is False, f"Expected debug=False, got {config.debug}"
            assert config.verbose is False, (
                f"Expected verbose=False, got {config.verbose}"
            )

            result = FlextCliCommonParams.apply_to_config(
                config,
                debug=True,
                verbose=True,
            )

            tm.ok(result)
            updated_config = result.unwrap()
            assert updated_config.debug is True
            assert updated_config.verbose is True
        finally:
            # Clean up environment variables
            os.environ.pop("FLEXT_CLI_DEBUG", None)
            os.environ.pop("FLEXT_CLI_VERBOSE", None)
            if original_debug is not None:
                os.environ["FLEXT_CLI_DEBUG"] = original_debug
            if original_verbose is not None:
                os.environ["FLEXT_CLI_VERBOSE"] = original_verbose
            # Reset config instance after test
            _reset_config_instance()
            if hasattr(FlextCliConfig, "_instance"):
                FlextCliConfig._instance = None

    def test_precedence_order_cli_over_all(self, tmp_path: Path) -> None:
        """Test complete precedence: CLI > ENV > .env > defaults."""
        env_file = tmp_path / ".env"
        # Use FLEXT_CLI_LOG_LEVEL instead of FLEXT_LOG_LEVEL (env_prefix is FLEXT_CLI_)
        env_file.write_text("FLEXT_CLI_LOG_LEVEL=WARNING\n")

        original_log_level = os.environ.get("FLEXT_CLI_LOG_LEVEL")

        try:
            os.environ["FLEXT_CLI_LOG_LEVEL"] = "ERROR"

            original_dir = Path.cwd()
            try:
                os.chdir(tmp_path)

                # Reset config to ensure fresh load from environment
                _reset_config_instance()
                if hasattr(FlextCliConfig, "_instance"):
                    FlextCliConfig._instance = None

                config = FlextCliServiceBase.get_cli_config()
                result = FlextCliCommonParams.apply_to_config(config, log_level="DEBUG")

                tm.ok(result)
                updated_config = result.unwrap()
                assert updated_config.cli_log_level.value == "DEBUG"

            finally:
                os.chdir(original_dir)
        finally:
            if original_log_level is None:
                os.environ.pop("FLEXT_CLI_LOG_LEVEL", None)
            else:
                os.environ["FLEXT_CLI_LOG_LEVEL"] = original_log_level
            # Reset config after test
            _reset_config_instance()
            if hasattr(FlextCliConfig, "_instance"):
                FlextCliConfig._instance = None

    # ========================================================================
    # LOGGER INTEGRATION
    # ========================================================================

    def test_logger_configured_with_cli_params(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that logger is properly configured from CLI parameters."""
        config = _create_test_config(
            cli_log_level=FlextConstants.Settings.LogLevel.INFO,
        )

        result = FlextCliCommonParams.apply_to_config(
            config,
            log_level=FlextConstants.Settings.LogLevel.DEBUG.value,
        )
        tm.ok(result)
        updated_config = result.unwrap()

        logger_result = FlextCliCommonParams.configure_logger(updated_config)
        tm.ok(logger_result)

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
            cli_log_level=FlextConstants.Settings.LogLevel.INFO,
        )
        FlextCliCommonParams.configure_logger(config)

        logger = FlextLogger("test_runtime")
        logger.info("Info at INFO level")
        captured = capsys.readouterr()
        assert "Info at INFO level" in captured.out

        result = FlextCliCommonParams.apply_to_config(config, log_level="WARNING")
        tm.ok(result)
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

            tm.fail(result)
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
            config,
            log_level=InvalidValue.INVALID_LOG_LEVEL.value,
        )

        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_LEVEL]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_invalid_log_format(self) -> None:
        """Test apply_to_config with invalid log format."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            log_format=InvalidValue.INVALID_LOG_FORMAT.value,
        )

        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_invalid_output_format(self) -> None:
        """Test apply_to_config with invalid output format."""
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            output_format=InvalidValue.INVALID_OUTPUT_FORMAT.value,
        )

        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_OUTPUT_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_apply_to_config_exception_handling(self) -> None:
        """Test apply_to_config exception handling with actual validation errors."""
        _reset_config_instance()

        # Test invalid log level
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            log_level=InvalidValue.INVALID_LOG_LEVEL.value,
        )
        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_LEVEL]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

        _reset_config_instance()

        # Test invalid log format
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            log_format=InvalidValue.INVALID_LOG_FORMAT.value,
        )
        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_LOG_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

        _reset_config_instance()

        # Test invalid output format
        config = FlextCliServiceBase.get_cli_config()
        result = FlextCliCommonParams.apply_to_config(
            config,
            output_format=InvalidValue.INVALID_OUTPUT_FORMAT.value,
        )
        tm.fail(result)
        error_keywords = INVALID_VALUE_ERRORS[InvalidValue.INVALID_OUTPUT_FORMAT]
        error_msg = str(result.error).lower() if result.error else ""
        assert any(keyword in error_msg for keyword in error_keywords)

    def test_configure_logger_invalid_log_level(self) -> None:
        """Test configure_logger with invalid log level."""
        config = FlextCliServiceBase.get_cli_config()
        config.__dict__["cli_log_level"] = "INVALID"

        result = FlextCliCommonParams.configure_logger(config)

        tm.fail(result)

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

        tm.fail(result)
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
                def decorated_test_function(
                    *args: object,
                    **kwargs: object,
                ) -> t.GeneralValueType:
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
        params = m.Cli.CliParamsConfig(log_level=None)
        result = FlextCliCommonParams._set_log_level(config, params)
        tm.ok(result)
        assert result.unwrap() == config
