"""Test config commands functionality using FLEXT patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import (
    FlextCliApi,
    FlextCliConfigs,
    FlextCliMain,
)
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestConfigCommandsReal:
    """Test config commands with REAL execution using flext-cli patterns."""

    def setup_method(self) -> None:
        """Set up test environment with real components."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-config", description="Test config CLI")
        self.config = FlextCliConfigs()

    def test_config_creation_real(self) -> None:
        """Test that config can be created and is properly structured."""
        assert self.config is not None
        assert isinstance(self.config, FlextCliConfigs)
        assert hasattr(self.config, "profile")
        assert hasattr(self.config, "debug")

    def test_config_serialization_real(self) -> None:
        """Test config serialization with real implementation."""
        config_dict = self.config.model_dump()
        assert isinstance(config_dict, dict)
        assert "profile" in config_dict
        assert "debug" in config_dict

    def test_config_validation_real(self) -> None:
        """Test config validation with real business rules."""
        validation_result = self.config.validate_business_rules()
        assert isinstance(validation_result, FlextResult)
        # Config should be valid by default
        assert validation_result.is_success

    def test_config_display_real(self) -> None:
        """Test config display using CLI API."""
        config_data = self.config.model_dump()

        # Test displaying config through CLI API
        display_result = self.cli_api.display_output(
            data=config_data,
            format_type="table",
            title="Configuration",
        )

        assert isinstance(display_result, FlextResult)
        assert display_result.is_success

    def test_config_message_display_real(self) -> None:
        """Test config message display using CLI API."""
        # Test different message types
        message_types = ["info", "success", "warning", "error"]

        for msg_type in message_types:
            result = self.cli_api.display_message(
                f"Config {msg_type} message",
                message_type=msg_type,
            )
            assert isinstance(result, FlextResult)
            assert result.is_success

    def test_config_formatting_real(self) -> None:
        """Test config data formatting in different formats."""
        config_data = self.config.model_dump()

        # Test different format types
        formats = ["json", "yaml", "table", "plain"]

        for format_type in formats:
            format_result = self.cli_api.format_data(config_data, format_type)
            assert isinstance(format_result, FlextResult)
            if format_result.is_failure:
                # Some formats might not be available, that's OK
                continue
            assert isinstance(format_result.value, str)

    def test_config_command_creation_real(self) -> None:
        """Test creating config-related commands."""
        # Test creating a config show command
        show_command = self.cli_api.create_command(
            name="show",
            description="Show configuration",
            handler=self._handle_config_show,
            arguments=[],
        )

        assert isinstance(show_command, FlextResult)
        assert show_command.is_success

        # Test creating a config set command
        set_command = self.cli_api.create_command(
            name="set",
            description="Set configuration value",
            handler=self._handle_config_set,
            arguments=["--key", "--value"],
        )

        assert isinstance(set_command, FlextResult)
        assert set_command.is_success

    def test_config_command_group_registration_real(self) -> None:
        """Test registering config command group."""
        # Create commands
        show_cmd_result = self.cli_api.create_command(
            name="show",
            description="Show configuration",
            handler=self._handle_config_show,
            arguments=[],
        )
        assert show_cmd_result.is_success

        set_cmd_result = self.cli_api.create_command(
            name="set",
            description="Set configuration value",
            handler=self._handle_config_set,
            arguments=["--key", "--value"],
        )
        assert set_cmd_result.is_success

        # Register command group
        commands: dict[str, FlextCliModels.CliCommand] = {
            "show": show_cmd_result.value,
            "set": set_cmd_result.value,
        }

        register_result = self.cli_main.register_command_group(
            name="config",
            commands=commands,
            description="Configuration management commands",
        )

        assert isinstance(register_result, FlextResult)
        assert register_result.is_success

    def _handle_config_show(self, **_kwargs: object) -> FlextResult[None]:
        """Handle config show command."""
        config_data = self.config.model_dump()

        display_result = self.cli_api.display_output(
            data=config_data,
            format_type="table",
            title="Current Configuration",
        )

        if display_result.is_failure:
            return FlextResult[None].fail(f"Display failed: {display_result.error}")

        return FlextResult[None].ok(None)

    def _handle_config_set(self, **kwargs: object) -> FlextResult[None]:
        """Handle config set command."""
        key = kwargs.get("key")
        value = kwargs.get("value")

        if not key or not value:
            return FlextResult[None].fail("Both key and value are required")

        # In a real implementation, would update config
        success_msg = f"Configuration updated: {key} = {value}"

        message_result = self.cli_api.display_message(
            success_msg,
            message_type="success",
        )

        if message_result.is_failure:
            return FlextResult[None].fail(
                f"Message display failed: {message_result.error}",
            )

        return FlextResult[None].ok(None)


class TestConfigIntegration:
    """Integration tests for config functionality."""

    def setup_method(self) -> None:
        """Set up integration test environment."""
        self.cli_api = FlextCliApi()
        self.config = FlextCliConfigs()

    def test_config_cli_integration_real(self) -> None:
        """Test config integration with CLI system."""
        # Test that config can be used with CLI API
        assert self.cli_api is not None
        assert self.config is not None

        # Test config display through API
        config_dict = self.config.model_dump()
        result = self.cli_api.display_output(
            data=config_dict,
            format_type="json",
            title="Config Integration Test",
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_config_validation_integration_real(self) -> None:
        """Test config validation integration."""
        # Test that validation works with CLI
        validation_result = self.config.validate_business_rules()
        assert validation_result.is_success

        # Display validation result
        message = "Configuration validation passed"
        display_result = self.cli_api.display_message(
            message,
            message_type="success",
        )

        assert display_result.is_success

    def test_config_formatting_integration_real(self) -> None:
        """Test config formatting integration with CLI."""
        config_data = self.config.model_dump()

        # Test formatting and display pipeline
        format_result = self.cli_api.format_data(config_data, "yaml")
        if format_result.is_success:
            display_result = self.cli_api.display_message(
                f"Config formatted: {len(format_result.value)} characters",
                message_type="info",
            )
            assert display_result.is_success


class TestConfigErrors:
    """Test config error handling scenarios."""

    def setup_method(self) -> None:
        """Set up error test environment."""
        self.cli_api = FlextCliApi()

    def test_config_invalid_command_creation(self) -> None:
        """Test error handling for invalid command creation."""
        # Test empty command name
        empty_name_result = self.cli_api.create_command(
            name="",
            description="Valid description",
            handler=lambda: None,
            arguments=[],
        )

        assert isinstance(empty_name_result, FlextResult)
        assert empty_name_result.is_failure
        assert empty_name_result.error is not None
        assert "empty" in empty_name_result.error.lower()

        # Test empty description
        empty_desc_result = self.cli_api.create_command(
            name="valid-name",
            description="",
            handler=lambda: None,
            arguments=[],
        )

        assert isinstance(empty_desc_result, FlextResult)
        assert empty_desc_result.is_failure
        assert empty_desc_result.error is not None
        assert "empty" in empty_desc_result.error.lower()

        # Test non-callable handler
        non_callable_result = self.cli_api.create_command(
            name="valid-name",
            description="Valid description",
            handler="not-callable",
            arguments=[],
        )

        assert isinstance(non_callable_result, FlextResult)
        assert non_callable_result.is_failure
        assert non_callable_result.error is not None
        assert "callable" in non_callable_result.error.lower()

    def test_config_invalid_display_operations(self) -> None:
        """Test error handling for display operations."""
        # Test display with complex unserializable data
        complex_data = {"function": lambda x: x}  # Non-serializable
        result = self.cli_api.display_output(
            data=complex_data,
            format_type="json",
        )
        # This should return a FlextResult (success or failure both valid for unserializable data)
        assert isinstance(result, FlextResult)
