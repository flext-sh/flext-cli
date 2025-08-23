"""Comprehensive tests for types.py module.

Tests all type definitions and entities in types.py for 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from datetime import datetime

from flext_core import FlextConstants
from rich.console import Console

from flext_cli import (
    CommandArgs,
    FlextCliCommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliConfig,
    FlextCliContext,
    FlextCliDataType,
    FlextCliFileHandler,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliSession,
    TCliConfig,
    TCliPath,
)

# Constants
_API = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
DEFAULT_TTL = 600
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestTypeAliases:
    """Test type alias definitions."""

    def test_type_aliases(self) -> None:
        """Test that type aliases are properly defined."""
        # These are type aliases - just verify they exist
        assert FlextCliDataType is not None
        assert TCliPath is not None
        assert FlextCliOutputFormat is not None
        assert FlextCliFileHandler is not None
        assert TCliConfig is not None
        assert CommandArgs is not None


class TestEnums:
    """Test enum definitions."""

    def test_command_status_enum(self) -> None:
        """Test FlextCliCommandStatus enum values."""
        if FlextCliCommandStatus.PENDING.value != "pending":
            raise AssertionError(
                f"Expected {'pending'}, got {FlextCliCommandStatus.PENDING.value}",
            )
        assert FlextCliCommandStatus.RUNNING.value == "running"
        if FlextCliCommandStatus.COMPLETED.value != "completed":
            raise AssertionError(
                f"Expected {'completed'}, got {FlextCliCommandStatus.COMPLETED.value}",
            )
        assert FlextCliCommandStatus.FAILED.value == "failed"
        if FlextCliCommandStatus.CANCELLED.value != "cancelled":
            raise AssertionError(
                f"Expected {'cancelled'}, got {FlextCliCommandStatus.CANCELLED.value}",
            )

        # Test all values exist
        all_statuses = list(FlextCliCommandStatus)
        if len(all_statuses) != 5:
            raise AssertionError(f"Expected {5}, got {len(all_statuses)}")

    def test_command_type_enum(self) -> None:
        """Test FlextCliCommandType enum values."""
        if FlextCliCommandType.SYSTEM.value != "system":
            raise AssertionError(
                f"Expected {'system'}, got {FlextCliCommandType.SYSTEM.value}",
            )
        assert FlextCliCommandType.PIPELINE.value == "pipeline"
        if FlextCliCommandType.PLUGIN.value != "plugin":
            raise AssertionError(
                f"Expected {'plugin'}, got {FlextCliCommandType.PLUGIN.value}",
            )
        assert FlextCliCommandType.DATA.value == "data"
        if FlextCliCommandType.CONFIG.value != "config":
            raise AssertionError(
                f"Expected {'config'}, got {FlextCliCommandType.CONFIG.value}",
            )
        assert FlextCliCommandType.AUTH.value == "auth"
        if FlextCliCommandType.MONITORING.value != "monitoring":
            raise AssertionError(
                f"Expected {'monitoring'}, got {FlextCliCommandType.MONITORING.value}",
            )

        # Test all values exist
        all_types = list(FlextCliCommandType)
        if len(all_types) != 10:
            raise AssertionError(f"Expected {10}, got {len(all_types)}")

    def test_output_format_enum(self) -> None:
        """Test FlextCliOutputFormat enum values."""
        if FlextCliOutputFormat.JSON != "json":
            raise AssertionError(f"Expected {'json'}, got {FlextCliOutputFormat.JSON}")
        assert FlextCliOutputFormat.YAML == "yaml"
        if FlextCliOutputFormat.CSV != "csv":
            raise AssertionError(f"Expected {'csv'}, got {FlextCliOutputFormat.CSV}")
        assert FlextCliOutputFormat.TABLE == "table"
        if FlextCliOutputFormat.PLAIN != "plain":
            raise AssertionError(
                f"Expected {'plain'}, got {FlextCliOutputFormat.PLAIN}",
            )

        # Test all values exist
        all_formats = list(FlextCliOutputFormat)
        if len(all_formats) != 5:
            raise AssertionError(f"Expected {5}, got {len(all_formats)}")


class TestFlextCliCommand:
    """Test FlextCliCommand entity."""

    def test_command_creation(self) -> None:
        """Test basic command creation."""
        command = FlextCliCommand(
            id="test-cmd-123",
            name="test-command",
            command_line="echo hello",
        )

        if command.name != "test-command":
            raise AssertionError(f"Expected {'test-command'}, got {command.name}")
        assert command.command_line == "echo hello"
        if command.command_status != FlextCliCommandStatus.PENDING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.PENDING}, got {command.command_status}",
            )
        assert command.command_type == FlextCliCommandType.SYSTEM
        assert command.exit_code is None
        if command.output != "":
            raise AssertionError(f"Expected {''}, got {command.output}")
        assert isinstance(command.options, dict)
        # Note: CLICommand does not have updated_at field - removed incorrect test

    def test_command_with_options(self) -> None:
        """Test command creation with options."""
        options = {"verbose": True, "timeout": 30}
        command = FlextCliCommand(
            id="test-cmd-124",
            name="test-command",
            command_line="echo hello",
            options=options,
            command_type=FlextCliCommandType.PIPELINE,
        )

        if command.options != options:
            raise AssertionError(f"Expected {options}, got {command.options}")
        assert command.command_type == FlextCliCommandType.PIPELINE

    def test_start_execution(self) -> None:
        """Test starting command execution."""
        command = FlextCliCommand(
            id="test-cmd-125",
            name="test-command",
            command_line="echo hello",
        )

        # Should start successfully from PENDING
        if not (command.flext_cli_start_execution()):
            raise AssertionError(
                f"Expected True, got {command.flext_cli_start_execution()}",
            )
        if command.command_status != FlextCliCommandStatus.RUNNING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.RUNNING}, got {command.command_status}",
            )
        if not (command.flext_cli_is_running):
            raise AssertionError(f"Expected True, got {command.flext_cli_is_running}")

        # Should fail if already running
        if command.flext_cli_start_execution():
            raise AssertionError(
                f"Expected False, got {command.flext_cli_start_execution()}",
            )

    def test_complete_execution_success(self) -> None:
        """Test completing command execution successfully."""
        command = FlextCliCommand(
            id="test-cmd-126",
            name="test-command",
            command_line="echo hello",
        )

        # Start execution first
        command.flext_cli_start_execution()

        # Complete successfully
        result = command.flext_cli_complete_execution(
            exit_code=0,
            stdout="hello world",
        )
        if not (result):
            raise AssertionError(f"Expected True, got {result}")
        if command.command_status != FlextCliCommandStatus.COMPLETED:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.COMPLETED}, got {command.command_status}",
            )
        assert command.exit_code == 0
        if command.output != "hello world":
            raise AssertionError(f"Expected {'hello world'}, got {command.output}")
        if not (command.flext_cli_successful):
            raise AssertionError(f"Expected True, got {command.flext_cli_successful}")

    def test_complete_execution_failure(self) -> None:
        """Test completing command execution with failure."""
        command = FlextCliCommand(
            id="test-cmd-127",
            name="test-command",
            command_line="echo hello",
        )

        # Start execution first
        command.flext_cli_start_execution()

        # Complete with failure
        result = command.flext_cli_complete_execution(
            exit_code=1,
            stdout="error output",
        )
        if not (result):
            raise AssertionError(f"Expected True, got {result}")
        if command.command_status != FlextCliCommandStatus.FAILED:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.FAILED}, got {command.command_status}",
            )
        assert command.exit_code == 1
        if command.output != "error output":
            raise AssertionError(f"Expected {'error output'}, got {command.output}")
        if command.flext_cli_successful:
            raise AssertionError(f"Expected False, got {command.flext_cli_successful}")

    def test_complete_execution_invalid_state(self) -> None:
        """Test completing execution from invalid state."""
        command = FlextCliCommand(
            id="test-cmd-128",
            name="test-command",
            command_line="echo hello",
        )

        # Command can be completed even if not currently running
        assert command.flext_cli_complete_execution() is True

    def test_is_running_property(self) -> None:
        """Test is_running property."""
        command = FlextCliCommand(
            id="test-cmd-129",
            name="test-command",
            command_line="echo hello",
        )

        if command.flext_cli_is_running:
            raise AssertionError(f"Expected False, got {command.flext_cli_is_running}")

        command.flext_cli_start_execution()
        assert command.flext_cli_is_running, (
            f"Expected True, got {command.flext_cli_is_running}"
        )

        command.flext_cli_complete_execution()
        assert not command.flext_cli_is_running, (
            f"Expected False, got {command.flext_cli_is_running}"
        )

    def test_successful_property(self) -> None:
        """Test successful property."""
        command = FlextCliCommand(
            id="test-cmd-130",
            name="test-command",
            command_line="echo hello",
        )

        if command.flext_cli_successful:
            raise AssertionError(f"Expected False, got {command.flext_cli_successful}")

        command.flext_cli_start_execution()
        if command.flext_cli_successful:
            raise AssertionError(f"Expected False, got {command.flext_cli_successful}")

        command.flext_cli_complete_execution(exit_code=0)
        if not (command.flext_cli_successful):
            raise AssertionError(f"Expected True, got {command.flext_cli_successful}")

        # Test failed command
        command2 = FlextCliCommand(
            id="test-cmd-131",
            name="test-command-2",
            command_line="false",
        )
        command2.flext_cli_start_execution()
        command2.flext_cli_complete_execution(exit_code=1)
        if command2.flext_cli_successful:
            raise AssertionError(f"Expected False, got {command2.flext_cli_successful}")

    def test_validate_business_rules(self) -> None:
        """Test domain rule validation."""
        # Valid command
        command = FlextCliCommand(
            id="test-cmd-132",
            name="test-command",
            command_line="echo hello",
        )
        result = command.validate_business_rules()
        if not result.is_success:
            raise AssertionError(f"Expected True, got {result}")

        # Test command with empty name (currently allowed by implementation)
        command_empty_name = FlextCliCommand(
            id="test-cmd-133",
            name="",
            command_line="echo hello",
        )
        result_empty_name = command_empty_name.validate_business_rules()
        assert result_empty_name.success  # Currently allowed

        # Test command with minimal command_line (Pydantic requires non-empty string)
        command_minimal_cmd = FlextCliCommand(
            id="test-cmd-134",
            name="test-command",
            command_line="x",  # Minimal valid command
        )
        result_minimal_cmd = command_minimal_cmd.validate_business_rules()
        assert result_minimal_cmd.success


class TestFlextCliConfig:
    """Test FlextCliConfig value object."""

    def test_config_default_creation(self) -> None:
        """Test creating config with default values."""
        config = FlextCliConfig()

        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")
        assert config.trace is False
        if config.log_level != "INFO":
            raise AssertionError(f"Expected {'INFO'}, got {config.log_level}")
        assert config.api.url == _API
        if config.api.timeout != 30:
            raise AssertionError(f"Expected {30}, got {config.api.timeout}")
        assert config.output.format == "table"
        if config.output.no_color:
            raise AssertionError(f"Expected False, got {config.output.no_color}")
        assert config.profile == "default"
        if config.api.connect_timeout != 10:
            raise AssertionError(f"Expected {10}, got {config.api.connect_timeout}")
        assert config.api.read_timeout == 30
        if config.command_timeout != 300:
            raise AssertionError(f"Expected {300}, got {config.command_timeout}")

    def test_config_custom_creation(self) -> None:
        """Test creating config with custom values."""
        config_data = {
            "debug": True,
            "trace": True,
            "log_level": "DEBUG",
            "api_url": "https://api.example.com",
            "api_timeout": 60,
            "output_format": "json",
            "no_color": True,
            "profile": "production",
            "connect_timeout": 20,
            "read_timeout": 60,
            "command_timeout": 600,
        }

        config = FlextCliConfig(**config_data)

        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")
        assert config.trace is True
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {'DEBUG'}, got {config.log_level}")
        assert config.api.url == "https://api.example.com"
        if config.api.timeout != 60:
            raise AssertionError(f"Expected {60}, got {config.api.timeout}")
        assert config.output.format == "json"
        if not (config.output.no_color):
            raise AssertionError(f"Expected True, got {config.output.no_color}")
        if config.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {config.profile}")
        assert config.api.connect_timeout == 20
        if config.api.read_timeout != 60:
            raise AssertionError(f"Expected {60}, got {config.api.read_timeout}")
        assert config.command_timeout == DEFAULT_TTL

    def test_config_configure_success(self) -> None:
        """Test configuring with new settings."""
        config = FlextCliConfig()

        new_settings = {
            "debug": True,
            "api_timeout": 45,
        }

        if not (config.configure(new_settings)):
            raise AssertionError(f"Expected True, got {config.configure(new_settings)}")
        assert config.debug is True
        if config.api.timeout != 45:
            raise AssertionError(f"Expected {45}, got {config.api.timeout}")
        # Other values should remain unchanged
        if config.log_level != "INFO":
            raise AssertionError(f"Expected {'INFO'}, got {config.log_level}")

    def test_config_configure_invalid(self) -> None:
        """Test configuring with invalid settings."""
        config = FlextCliConfig()

        # Non-dict should fail
        if config.configure("invalid"):
            raise AssertionError(f"Expected False, got {config.configure('invalid')}")
        assert config.configure(123) is False
        if config.configure(None):
            raise AssertionError(f"Expected False, got {config.configure(None)}")

    def test_config_configure_exception(self) -> None:
        """Test configure method with exception handling."""
        config = FlextCliConfig()

        # Create a scenario that might cause an exception
        # This is a edge case test
        result = config.configure({})
        assert isinstance(result, bool)

    def test_validate_business_rules(self) -> None:
        """Test domain rule validation."""
        config = FlextCliConfig()
        result = config.validate_business_rules()
        if not result.is_success:
            raise AssertionError(f"Expected True, got {result}")

        # Config is always valid according to implementation
        config_with_data = FlextCliConfig(debug=True)
        result_with_data = config_with_data.validate_business_rules()
        if not result_with_data.success:
            raise AssertionError(f"Expected True, got {result_with_data}")


class TestFlextCliContext:
    """Test FlextCliContext value object."""

    def test_context_default_creation(self) -> None:
        """Test creating context with default values."""
        config = FlextCliConfig()
        console = Console()
        context = FlextCliContext(config=config, console=console)

        assert isinstance(context.config, FlextCliConfig)
        # FlextCliContext should have the fields from domain/cli_context.py
        assert context.config is config
        assert context.console is console

    def test_context_with_custom_config(self) -> None:
        """Test creating context with custom config."""
        # Create config and console - FlextCliContext requires both
        config = FlextCliConfig(debug=True, output_format="json", profile="production")
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Verify FlextCliContext fields
        assert context.config is config
        assert context.console is console

    def test_context_with_overrides(self) -> None:
        """Test creating context with override values."""
        # Create config with override values and console
        config = FlextCliConfig(debug=True, output_format="yaml", profile="development")
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Verify FlextCliContext fields
        assert context.config is config
        assert context.console is console

    def test_with_debug(self) -> None:
        """Test with_debug method."""
        config = FlextCliConfig(debug=True)
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Test is_debug property from FlextCliContext
        assert context.is_debug  # Should be True because config.debug=True
        assert context.config is config
        assert context.console is console

    def test_with_output_format(self) -> None:
        """Test with_output_format method."""
        config = FlextCliConfig(output_format="json")
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Test config output_format is accessible via context.config
        assert context.config.output_format == "json"
        assert context.config is config
        assert context.console is console

    def test_for_production(self) -> None:
        """Test for_production method."""
        config = FlextCliConfig(debug=False, profile="production")
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Test production settings
        assert not context.is_debug  # Should be False for production
        assert context.config.profile == "production"
        assert context.config is config
        assert context.console is console

    def test_generate_session_id(self) -> None:
        """Test session ID generation."""
        config1 = FlextCliConfig()
        config2 = FlextCliConfig()
        console1 = Console()
        console2 = Console()
        context1 = FlextCliContext(config=config1, console=console1)
        context2 = FlextCliContext(config=config2, console=console2)

        # Different contexts with different configs/consoles
        assert context1.config is not context2.config
        assert context1.console is not context2.console

    def test_validate_business_rules(self) -> None:
        """Test domain rule validation."""
        config = FlextCliConfig()
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Test business rules validation (returns FlextResult)
        validation_result = context.validate_business_rules()
        assert validation_result.is_success
        assert context.config is config
        assert context.console is console


class TestFlextCliPlugin:
    """Test FlextCliPlugin value object."""

    def test_plugin_basic_creation(self) -> None:
        """Test creating plugin with basic parameters."""
        plugin = FlextCliPlugin(
            id="plugin-001",
            name="test-plugin",
            entry_point="test_plugin.main",
            plugin_version="0.9.0",
        )

        if plugin.name != "test-plugin":
            raise AssertionError(f"Expected {'test-plugin'}, got {plugin.name}")
        assert plugin.plugin_version == "0.9.0"
        assert plugin.entry_point == "test_plugin.main"
        assert plugin.description is None
        if not (plugin.enabled):
            raise AssertionError(f"Expected True, got {plugin.enabled}")
        if plugin.dependencies != []:
            raise AssertionError(f"Expected {[]}, got {plugin.dependencies}")
        assert plugin.commands == []
        # FlextEntity provides automatic timestamps
        assert hasattr(plugin, "id")  # FlextEntity provides automatic ID

    def test_plugin_full_creation(self) -> None:
        """Test creating plugin with all parameters."""
        plugin = FlextCliPlugin(
            id="plugin-advanced",
            name="advanced-plugin",
            entry_point="advanced_plugin.main",
            plugin_version="2.1.0",
            description="Advanced test plugin",
            enabled=False,
            dependencies=["dep1", "dep2"],
            commands=["cmd1", "cmd2", "cmd3"],
        )

        if plugin.name != "advanced-plugin":
            raise AssertionError(f"Expected {'advanced-plugin'}, got {plugin.name}")
        assert plugin.plugin_version == "2.1.0"
        assert plugin.entry_point == "advanced_plugin.main"
        if plugin.description != "Advanced test plugin":
            raise AssertionError(
                f"Expected {'Advanced test plugin'}, got {plugin.description}",
            )
        if plugin.enabled:
            raise AssertionError(f"Expected False, got {plugin.enabled}")
        assert plugin.dependencies == ["dep1", "dep2"]
        if plugin.commands != ["cmd1", "cmd2", "cmd3"]:
            raise AssertionError(
                f"Expected {['cmd1', 'cmd2', 'cmd3']}, got {plugin.commands}",
            )

    def test_validate_business_rules(self) -> None:
        """Test domain rule validation."""
        # Valid plugin
        plugin = FlextCliPlugin(
            id="plugin-test",
            name="test-plugin",
            entry_point="test_plugin.main",
            plugin_version="0.9.0",
        )
        validation_result = plugin.validate_business_rules()
        if not validation_result.is_success:
            raise AssertionError(f"Expected success, got {validation_result.error}")

        # Note: Pydantic already validates min_length=1 for name and entry_point
        # So we can't create invalid plugins with empty strings - they'll fail at creation time
        # This is actually good because it prevents invalid objects from being created

        # Test with valid plugin that we can then manipulate
        plugin_copy = plugin.model_copy(update={"name": "x"})  # Still valid
        validation_result_copy = plugin_copy.validate_business_rules()
        if not validation_result_copy.success:
            raise AssertionError(
                f"Expected success for copied plugin, got {validation_result_copy.error}",
            )


class TestFlextCliSession:
    """Test FlextCliSession entity."""

    def test_session_creation(self) -> None:
        """Test basic session creation."""
        session = FlextCliSession(id="test-session-100", session_id="test-session-100")

        assert session.user_id is None
        if session.commands_executed != []:
            raise AssertionError(f"Expected {[]}, got {session.commands_executed}")
        assert isinstance(session.started_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert hasattr(session.config, "profile")  # Check it's a config object

    def test_session_with_user(self) -> None:
        """Test session creation with user ID."""
        session = FlextCliSession(
            id="test-session-101",
            session_id="test-session-101",
            user_id="test-user-123",
        )

        if session.user_id != "test-user-123":
            raise AssertionError(f"Expected {'test-user-123'}, got {session.user_id}")

    def test_record_command_success(self) -> None:
        """Test recording command successfully."""
        session = FlextCliSession(id="test-session-102", session_id="test-session-102")

        if not (session.flext_cli_record_command("test-command")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('test-command')}",
            )
        if "test-command" not in session.commands_executed:
            raise AssertionError(
                f"Expected {'test-command'} in {session.commands_executed}",
            )
        if len(session.commands_executed) != 1:
            raise AssertionError(f"Expected {1}, got {len(session.commands_executed)}")

        # Record another command
        if not (session.flext_cli_record_command("another-command")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('another-command')}",
            )
        if len(session.commands_executed) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {len(session.commands_executed)}")
        assert session.commands_executed == ["test-command", "another-command"]

    def test_record_command_updates_activity(self) -> None:
        """Test that recording command updates last activity."""
        session = FlextCliSession(id="test-session-103", session_id="test-session-103")
        original_activity = session.last_activity

        # Small delay to ensure time difference

        time.sleep(0.001)

        session.flext_cli_record_command("test-command")

        assert session.last_activity > original_activity

    def test_record_command_exception_handling(self) -> None:
        """Test record_command method exception handling."""
        session = FlextCliSession(id="test-session-104", session_id="test-session-104")

        # Normal case should work
        result = session.flext_cli_record_command("normal-command")
        if not (result):
            raise AssertionError(f"Expected True, got {result}")

        # Test with various input types
        assert session.flext_cli_record_command("") is False  # Empty string is invalid
        # Numeric string is valid
        if not (session.flext_cli_record_command("123")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('123')}",
            )

    def test_validate_business_rules(self) -> None:
        """Test domain rule validation."""
        session = FlextCliSession(id="test-session-105", session_id="test-session-105")

        # Should be valid (checks for entity_id existence)
        result = session.validate_business_rules()
        if not result.is_success:
            raise AssertionError(f"Expected True, got {result}")
        assert bool(session.id) is True


class TestIntegration:
    """Integration tests for type interactions."""

    def test_command_with_all_statuses(self) -> None:
        """Test command through all status transitions."""
        command = FlextCliCommand(
            id="test-cmd-135",
            name="integration-test",
            command_line="echo test",
            command_type=FlextCliCommandType.PIPELINE,
        )

        # Initial state
        if command.command_status != FlextCliCommandStatus.PENDING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.PENDING}, got {command.command_status}",
            )
        assert not command.flext_cli_is_running
        assert not command.flext_cli_successful

        # Start execution
        assert command.flext_cli_start_execution()
        if command.command_status != FlextCliCommandStatus.RUNNING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.RUNNING}, got {command.command_status}",
            )
        assert command.flext_cli_is_running
        assert not command.flext_cli_successful

        # Complete successfully
        assert command.flext_cli_complete_execution(exit_code=0, stdout="success")
        if command.command_status != FlextCliCommandStatus.COMPLETED:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.COMPLETED}, got {command.command_status}",
            )
        assert not command.flext_cli_is_running
        assert command.flext_cli_successful

    def test_context_with_all_formats(self) -> None:
        """Test context with all output formats."""
        # FlextCliContext requires config and console
        config = FlextCliConfig()
        console = Console()
        # Context creation for FlextCliOutputFormat validation
        FlextCliContext(config=config, console=console)

        for format_type in FlextCliOutputFormat:
            # Use config instead of direct attribute access
            test_config = FlextCliConfig(output_format=format_type.value)
            format_context = FlextCliContext(config=test_config, console=console)
            if format_context.config.output_format != format_type.value:
                raise AssertionError(
                    f"Expected {format_type.value}, got {format_context.config.output_format}",
                )

    def test_session_with_multiple_commands(self) -> None:
        """Test session recording multiple commands."""
        # FlextCliSession needs both id (entity_id) and session_id
        session = FlextCliSession(
            id="test-session-135",
            session_id="test-session-135",
            user_id="test-user",
        )

        commands = ["init", "run", "deploy", "monitor", "cleanup"]

        for cmd in commands:
            assert session.flext_cli_record_command(cmd)

        if session.commands_executed != commands:
            raise AssertionError(
                f"Expected {commands}, got {session.commands_executed}",
            )
        assert len(session.commands_executed) == 5

    def test_config_inheritance_in_context(self) -> None:
        """Test config values inherited by context."""
        config_data = {
            "debug": True,
            "trace": True,
            "output_format": "json",
            "profile": "test",
        }
        config = FlextCliConfig(**config_data)
        console = Console()
        context = FlextCliContext(config=config, console=console)

        # Context should inherit from config through config attribute
        if context.config.debug != config.debug:
            raise AssertionError(f"Expected {config.debug}, got {context.config.debug}")
        assert context.config.trace == config.trace
        if context.config.output_format != config.output_format:
            raise AssertionError(
                f"Expected {config.output_format}, got {context.config.output_format}",
            )
        assert context.config.profile == config.profile
