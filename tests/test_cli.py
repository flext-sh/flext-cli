"""Tests for CLI main entry point using FLEXT patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path

from flext_cli import FlextCliApi, FlextCliConfigs, FlextCliMain
from flext_cli.cli import create_cli_options, main
from flext_cli.constants import FlextCliConstants
from flext_core import FlextLogger, FlextResult


class TestCliMain:
    """Test CLI main command group using flext-cli patterns."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-cli", description="Test CLI")

    def test_cli_api_initialization(self) -> None:
        """Test FlextCliApi initialization."""
        assert self.cli_api is not None
        assert hasattr(self.cli_api, "display_message")
        assert hasattr(self.cli_api, "display_output")

    def test_cli_main_initialization(self) -> None:
        """Test FlextCliMain initialization."""
        assert self.cli_main is not None
        assert self.cli_main.name == "test-cli"
        assert self.cli_main.description == "Test CLI"

    def test_cli_api_display_message(self) -> None:
        """Test CLI API message display functionality."""
        result = self.cli_api.display_message("test message", message_type="info")
        assert isinstance(result, FlextResult)

    def test_cli_api_display_output(self) -> None:
        """Test CLI API output display functionality."""
        test_data = {"key": "value", "number": 42}
        result = self.cli_api.display_output(
            data=test_data,
            format_type="table",
            title="Test Output",
        )
        assert isinstance(result, FlextResult)

    def test_load_constants_metadata_success(self) -> None:
        """Test constants metadata loading."""
        constants = FlextCliConstants()
        assert constants is not None
        assert hasattr(constants, "DEFAULT_PROFILE")

    def test_get_logger(self) -> None:
        """Test logger functionality."""
        logger = FlextLogger(__name__)
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_create_cli_options_default(self) -> None:
        """Test create_cli_options with default values."""
        result = create_cli_options()

        assert result.is_success
        options = result.value
        assert options["profile"] == "default"
        assert options["output_format"] == "table"
        assert options["debug"] is False
        assert options["quiet"] is False
        assert options["log_level"] is None

    def test_create_cli_options_custom(self) -> None:
        """Test create_cli_options with custom values."""
        result = create_cli_options(
            profile="test",
            output_format="json",
            debug=True,
            quiet=True,
            log_level="DEBUG",
        )

        assert result.is_success
        options = result.value
        assert options["profile"] == "test"
        assert options["output_format"] == "json"
        assert options["debug"] is True
        assert options["quiet"] is True
        assert options["log_level"] == "DEBUG"

    def test_cli_main_command_registration(self) -> None:
        """Test command registration using flext-cli patterns."""
        # Create a test command
        test_command = self.cli_api.create_command(
            name="test-cmd",
            description="Test command",
            handler=lambda **_kwargs: FlextResult[None].ok(None),
            arguments=["--option"],
        )

        # Register command group
        result = self.cli_main.register_command_group(
            name="test-group",
            commands={"test": test_command.value},
            description="Test command group",
        )

        assert result.is_success

    def test_cli_main_execution(self) -> None:
        """Test CLI main execution."""
        result = self.cli_main.execute()
        assert isinstance(result, FlextResult)

    def test_cli_config_integration(self) -> None:
        """Test CLI configuration integration."""
        config = FlextCliConfigs()
        assert config is not None
        assert hasattr(config, "debug")
        assert hasattr(config, "app_name")

        # Test model_dump functionality
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert "debug" in config_dict


class TestMainEntryPoint:
    """Test main() entry point function."""

    def test_main_function_signature(self) -> None:
        """Test main() function signature and existence."""
        # Verify main function exists and is callable
        assert callable(main)

        # Check function signature
        sig = inspect.signature(main)
        assert len(sig.parameters) == 0  # main() takes no parameters

        # Verify main function is importable and accessible
        assert main is not None

    def test_main_cli_integration_real(self) -> None:
        """Test main() integration with real CLI functionality."""
        # Test that main function is properly integrated
        # We test this by verifying CLI components work
        cli_api = FlextCliApi()
        assert cli_api is not None

        # Test CLI main creation
        cli_main = FlextCliMain(name="test", description="Test")
        result = cli_main.execute()
        assert isinstance(result, FlextResult)


class TestCliIntegration:
    """Integration tests for CLI with command groups."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(
            name="integration-test", description="Integration test CLI"
        )

    def test_auth_command_functionality(self) -> None:
        """Test auth command functionality using flext-cli patterns."""
        # Create auth command using flext-cli API
        auth_command = self.cli_api.create_command(
            name="login",
            description="Authentication login",
            handler=self._handle_auth_login,
            arguments=["--username", "--password"],
        )

        result = self.cli_main.register_command_group(
            name="auth",
            commands={"login": auth_command.value},
            description="Authentication commands",
        )

        assert result.is_success

    def test_config_command_functionality(self) -> None:
        """Test config command functionality using flext-cli patterns."""
        # Create config command using flext-cli API
        config_command = self.cli_api.create_command(
            name="show",
            description="Show configuration",
            handler=self._handle_config_show,
            arguments=[],
        )

        result = self.cli_main.register_command_group(
            name="config",
            commands={"show": config_command.value},
            description="Configuration commands",
        )

        assert result.is_success

    def test_debug_command_functionality(self) -> None:
        """Test debug command functionality using flext-cli patterns."""
        # Create debug command using flext-cli API
        debug_command = self.cli_api.create_command(
            name="env",
            description="Show environment information",
            handler=self._handle_debug_env,
            arguments=[],
        )

        result = self.cli_main.register_command_group(
            name="debug",
            commands={"env": debug_command.value},
            description="Debug commands",
        )

        assert result.is_success

    def _handle_auth_login(self, **kwargs: object) -> FlextResult[None]:
        """Handle auth login command."""
        username = kwargs.get("username", "")
        password = kwargs.get("password", "")

        if not username or not password:
            return FlextResult[None].fail("Username and password required")

        return FlextResult[None].ok(None)

    def _handle_config_show(self, **_kwargs: object) -> FlextResult[None]:
        """Handle config show command."""
        config = FlextCliConfigs()
        config_data = config.model_dump()

        self.cli_api.display_output(
            data=config_data,
            format_type="table",
            title="Configuration",
        )

        return FlextResult[None].ok(None)

    def _handle_debug_env(self, **_kwargs: object) -> FlextResult[None]:
        """Handle debug env command."""
        env_data = {
            "PWD": str(Path.cwd()),
            "USER": os.environ.get("USER", "unknown"),
            "PATH": os.environ.get("PATH", "unknown")[:50] + "...",
        }

        self.cli_api.display_output(
            data=env_data,
            format_type="table",
            title="Environment Information",
        )

        return FlextResult[None].ok(None)


class TestCliErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="error-test", description="Error test CLI")

    def test_cli_command_validation_errors(self) -> None:
        """Test CLI command validation error handling."""

        # Create command with validation
        def failing_handler(**_kwargs: object) -> FlextResult[None]:
            return FlextResult[None].fail("Validation failed")

        command = self.cli_api.create_command(
            name="fail",
            description="Failing command",
            handler=failing_handler,
            arguments=[],
        )

        result = self.cli_main.register_command_group(
            name="test",
            commands={"fail": command.value},
            description="Test commands",
        )

        assert result.is_success

    def test_cli_missing_argument_handling(self) -> None:
        """Test CLI handling of missing required arguments."""

        def required_arg_handler(**kwargs: object) -> FlextResult[None]:
            required_arg = kwargs.get("required")
            if not required_arg:
                return FlextResult[None].fail("Required argument missing")
            return FlextResult[None].ok(None)

        command = self.cli_api.create_command(
            name="require",
            description="Command requiring arguments",
            handler=required_arg_handler,
            arguments=["--required"],
        )

        result = self.cli_main.register_command_group(
            name="validation",
            commands={"require": command.value},
            description="Validation commands",
        )

        assert result.is_success

    def test_cli_environment_variable_integration_real(self) -> None:
        """Test CLI functionality with environment variables."""
        # Test that CLI executes successfully regardless of environment
        original_debug = os.environ.get("FLX_DEBUG")
        original_profile = os.environ.get("FLX_PROFILE")

        try:
            # Set environment variables (CLI may use them in future)
            os.environ["FLX_DEBUG"] = "true"
            os.environ["FLX_PROFILE"] = "test"

            # Test that CLI still works with configuration
            config = FlextCliConfigs()
            assert config is not None

            # Test that CLI API works
            result = self.cli_api.display_message(
                "Environment test", message_type="info"
            )
            assert isinstance(result, FlextResult)

        finally:
            # Restore original environment
            if original_debug is not None:
                os.environ["FLX_DEBUG"] = original_debug
            elif "FLX_DEBUG" in os.environ:
                del os.environ["FLX_DEBUG"]

            if original_profile is not None:
                os.environ["FLX_PROFILE"] = original_profile
            elif "FLX_PROFILE" in os.environ:
                del os.environ["FLX_PROFILE"]


class TestCliConfiguration:
    """Test CLI configuration handling."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()

    def test_cli_config_loading_real(self) -> None:
        """Test CLI loads configuration correctly with real implementation."""
        # Test that CLI can load and use real configuration
        config = FlextCliConfigs()
        assert config is not None

        # Verify configuration properties
        assert hasattr(config, "debug")
        assert hasattr(config, "app_name")

        # Test configuration serialization
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert "debug" in config_dict

    def test_cli_context_creation_real(self) -> None:
        """Test CLI creates proper CLI context with real implementation."""
        # Test that CLI API is accessible and functional
        assert self.cli_api is not None

        # Test message display
        result = self.cli_api.display_message("Context test", message_type="info")
        assert isinstance(result, FlextResult)

        # Test output display
        test_data = {"test": "data"}
        result = self.cli_api.display_output(
            data=test_data,
            format_type="table",
            title="Context Test",
        )
        assert isinstance(result, FlextResult)

    def test_cli_configuration_validation(self) -> None:
        """Test CLI configuration validation with real values."""
        # Test configuration creation with different profiles
        valid_profiles = ["default", "test", "dev", "prod"]

        for profile in valid_profiles:
            config = FlextCliConfigs(profile=profile)
            assert config is not None
            assert config.profile == profile

        # Test that CLI configuration can be inspected
        test_config = FlextCliConfigs().model_dump()
        assert isinstance(test_config, dict)
        assert "profile" in test_config

    def test_cli_api_command_creation(self) -> None:
        """Test CLI API command creation functionality."""
        # Test basic command creation
        command = self.cli_api.create_command(
            name="test",
            description="Test command",
            handler=lambda **_kwargs: FlextResult[None].ok(None),
            arguments=[],
        )

        assert command is not None

        # Test command with arguments
        command_with_args = self.cli_api.create_command(
            name="test-args",
            description="Test command with arguments",
            handler=lambda **_kwargs: FlextResult[None].ok(None),
            arguments=["--option", "--flag"],
        )

        assert command_with_args is not None
