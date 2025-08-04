"""Comprehensive tests for types.py module.

Tests all type definitions and entities in types.py for 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from datetime import datetime

from flext_cli.types import (
    FlextCliCommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliConfig,
    FlextCliContext,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliSession,
    TCliArgs,
    TCliConfig,
    TCliData,
    TCliFormat,
    TCliHandler,
    TCliPath,
)

# Constants
DEFAULT_TTL = 600
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestTypeAliases:
    """Test type alias definitions."""

    def test_type_aliases(self) -> None:
        """Test that type aliases are properly defined."""
        # These are type aliases - just verify they exist
        assert TCliData is not None
        assert TCliPath is not None
        assert TCliFormat is not None
        assert TCliHandler is not None
        assert TCliConfig is not None
        assert TCliArgs is not None


class TestEnums:
    """Test enum definitions."""

    def test_command_status_enum(self) -> None:
        """Test FlextCliCommandStatus enum values."""
        if FlextCliCommandStatus.PENDING.value != "pending":
            raise AssertionError(
                f"Expected {'pending'}, got {FlextCliCommandStatus.PENDING.value}"
            )
        assert FlextCliCommandStatus.RUNNING.value == "running"
        if FlextCliCommandStatus.COMPLETED.value != "completed":
            raise AssertionError(
                f"Expected {'completed'}, got {FlextCliCommandStatus.COMPLETED.value}"
            )
        assert FlextCliCommandStatus.FAILED.value == "failed"
        if FlextCliCommandStatus.CANCELLED.value != "cancelled":
            raise AssertionError(
                f"Expected {'cancelled'}, got {FlextCliCommandStatus.CANCELLED.value}"
            )

        # Test all values exist
        all_statuses = list(FlextCliCommandStatus)
        if len(all_statuses) != 5:
            raise AssertionError(f"Expected {5}, got {len(all_statuses)}")

    def test_command_type_enum(self) -> None:
        """Test FlextCliCommandType enum values."""
        if FlextCliCommandType.SYSTEM.value != "system":
            raise AssertionError(
                f"Expected {'system'}, got {FlextCliCommandType.SYSTEM.value}"
            )
        assert FlextCliCommandType.PIPELINE.value == "pipeline"
        if FlextCliCommandType.PLUGIN.value != "plugin":
            raise AssertionError(
                f"Expected {'plugin'}, got {FlextCliCommandType.PLUGIN.value}"
            )
        assert FlextCliCommandType.DATA.value == "data"
        if FlextCliCommandType.CONFIG.value != "config":
            raise AssertionError(
                f"Expected {'config'}, got {FlextCliCommandType.CONFIG.value}"
            )
        assert FlextCliCommandType.AUTH.value == "auth"
        if FlextCliCommandType.MONITORING.value != "monitoring":
            raise AssertionError(
                f"Expected {'monitoring'}, got {FlextCliCommandType.MONITORING.value}"
            )

        # Test all values exist
        all_types = list(FlextCliCommandType)
        if len(all_types) != 7:
            raise AssertionError(f"Expected {7}, got {len(all_types)}")

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
                f"Expected {'plain'}, got {FlextCliOutputFormat.PLAIN}"
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
                f"Expected {FlextCliCommandStatus.PENDING}, got {command.command_status}"
            )
        assert command.command_type == FlextCliCommandType.SYSTEM
        assert command.exit_code is None
        if command.output != "":
            raise AssertionError(f"Expected {''}, got {command.output}")
        assert isinstance(command.options, dict)
        assert isinstance(command.updated_at, datetime)

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
                f"Expected True, got {command.flext_cli_start_execution()}"
            )
        if command.command_status != FlextCliCommandStatus.RUNNING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.RUNNING}, got {command.command_status}"
            )
        if not (command.flext_cli_is_running):
            raise AssertionError(f"Expected True, got {command.flext_cli_is_running}")

        # Should fail if already running
        if command.flext_cli_start_execution():
            raise AssertionError(
                f"Expected False, got {command.flext_cli_start_execution()}"
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
                f"Expected {FlextCliCommandStatus.COMPLETED}, got {command.command_status}"
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
                f"Expected {FlextCliCommandStatus.FAILED}, got {command.command_status}"
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

        # Should fail if not running
        if command.flext_cli_complete_execution():
            raise AssertionError(
                f"Expected False, got {command.flext_cli_complete_execution()}"
            )

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
        if not (command.flext_cli_is_running):
            raise AssertionError(f"Expected True, got {command.flext_cli_is_running}")

        command.flext_cli_complete_execution()
        if command.flext_cli_is_running:
            raise AssertionError(f"Expected False, got {command.flext_cli_is_running}")

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

    def test_validate_domain_rules(self) -> None:
        """Test domain rule validation."""
        # Valid command
        command = FlextCliCommand(
            id="test-cmd-132",
            name="test-command",
            command_line="echo hello",
        )
        if not (command.validate_domain_rules()):
            raise AssertionError(
                f"Expected True, got {command.validate_domain_rules()}"
            )

        # Invalid command - empty name
        command_invalid = FlextCliCommand(
            id="test-cmd-133",
            name="",
            command_line="echo hello",
        )
        if command_invalid.validate_domain_rules():
            raise AssertionError(
                f"Expected False, got {command_invalid.validate_domain_rules()}"
            )

        # Invalid command - empty command_line
        command_invalid2 = FlextCliCommand(
            id="test-cmd-134",
            name="test-command",
            command_line="",
        )
        if command_invalid2.validate_domain_rules():
            raise AssertionError(
                f"Expected False, got {command_invalid2.validate_domain_rules()}"
            )


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
        assert config.api_url == "http://localhost:8000"
        if config.api_timeout != 30:
            raise AssertionError(f"Expected {30}, got {config.api_timeout}")
        assert config.format_type == "table"
        if config.no_color:
            raise AssertionError(f"Expected False, got {config.no_color}")
        assert config.profile == "default"
        if config.connect_timeout != 10:
            raise AssertionError(f"Expected {10}, got {config.connect_timeout}")
        assert config.read_timeout == 30
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

        config = FlextCliConfig(config_data)

        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")
        assert config.trace is True
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {'DEBUG'}, got {config.log_level}")
        assert config.api_url == "https://api.example.com"
        if config.api_timeout != 60:
            raise AssertionError(f"Expected {60}, got {config.api_timeout}")
        assert config.format_type == "json"
        if not (config.no_color):
            raise AssertionError(f"Expected True, got {config.no_color}")
        if config.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {config.profile}")
        assert config.connect_timeout == 20
        if config.read_timeout != 60:
            raise AssertionError(f"Expected {60}, got {config.read_timeout}")
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
        if config.api_timeout != 45:
            raise AssertionError(f"Expected {45}, got {config.api_timeout}")
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

    def test_validate_domain_rules(self) -> None:
        """Test domain rule validation."""
        config = FlextCliConfig()
        if not (config.validate_domain_rules()):
            raise AssertionError(f"Expected True, got {config.validate_domain_rules()}")

        # Config is always valid according to implementation
        config_with_data = FlextCliConfig({"debug": True})
        if not (config_with_data.validate_domain_rules()):
            raise AssertionError(
                f"Expected True, got {config_with_data.validate_domain_rules()}"
            )


class TestFlextCliContext:
    """Test FlextCliContext value object."""

    def test_context_default_creation(self) -> None:
        """Test creating context with default values."""
        context = FlextCliContext()

        assert isinstance(context.config, FlextCliConfig)
        assert isinstance(context.session_id, str)
        assert len(context.session_id) > 0
        if context.debug:
            raise AssertionError(f"Expected False, got {context.debug}")
        assert context.trace is False
        if context.output_format != "table":
            raise AssertionError(f"Expected {'table'}, got {context.output_format}")
        if context.no_color:
            raise AssertionError(f"Expected False, got {context.no_color}")
        assert context.profile == "default"

    def test_context_with_custom_config(self) -> None:
        """Test creating context with custom config."""
        config_data = {
            "debug": True,
            "output_format": "json",
            "no_color": True,
            "profile": "production",
        }
        config = FlextCliConfig(config_data)
        context = FlextCliContext(config=config)

        assert context.config is config
        if not (context.debug):
            raise AssertionError(f"Expected True, got {context.debug}")
        if context.output_format != "json":
            raise AssertionError(f"Expected {'json'}, got {context.output_format}")
        if not (context.no_color):
            raise AssertionError(f"Expected True, got {context.no_color}")
        if context.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {context.profile}")

    def test_context_with_overrides(self) -> None:
        """Test creating context with override values."""
        context = FlextCliContext(
            debug=True,
            trace=True,
            output_format="yaml",
            no_color=True,
            profile="development",
        )

        if not (context.debug):
            raise AssertionError(f"Expected True, got {context.debug}")
        assert context.trace is True
        if context.output_format != "yaml":
            raise AssertionError(f"Expected {'yaml'}, got {context.output_format}")
        if not (context.no_color):
            raise AssertionError(f"Expected True, got {context.no_color}")
        if context.profile != "development":
            raise AssertionError(f"Expected {'development'}, got {context.profile}")

    def test_with_debug(self) -> None:
        """Test with_debug method."""
        context = FlextCliContext()
        debug_context = context.flext_cli_with_debug(debug=True)

        if not (debug_context.debug):
            raise AssertionError(f"Expected True, got {debug_context.debug}")
        assert debug_context is not context  # Should be new instance

        # Test with False
        no_debug_context = context.flext_cli_with_debug(debug=False)
        if no_debug_context.debug:
            raise AssertionError(f"Expected False, got {no_debug_context.debug}")

    def test_with_output_format(self) -> None:
        """Test with_output_format method."""
        context = FlextCliContext()
        json_context = context.flext_cli_with_output_format(FlextCliOutputFormat.JSON)

        if json_context.output_format != "json":
            raise AssertionError(f"Expected {'json'}, got {json_context.output_format}")
        assert json_context is not context  # Should be new instance

        # Test with different format
        yaml_context = context.flext_cli_with_output_format(FlextCliOutputFormat.YAML)
        if yaml_context.output_format != "yaml":
            raise AssertionError(f"Expected {'yaml'}, got {yaml_context.output_format}")

    def test_for_production(self) -> None:
        """Test for_production method."""
        context = FlextCliContext(debug=True, trace=True)
        prod_context = context.flext_cli_for_production()

        if prod_context.debug:
            raise AssertionError(f"Expected False, got {prod_context.debug}")
        assert prod_context.trace is False
        if prod_context.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {prod_context.profile}")
        assert prod_context is not context  # Should be new instance

    def test_generate_session_id(self) -> None:
        """Test session ID generation."""
        context1 = FlextCliContext()
        context2 = FlextCliContext()

        # Should generate different session IDs
        assert context1.session_id != context2.session_id
        assert len(context1.session_id) > 0
        assert len(context2.session_id) > 0

    def test_validate_domain_rules(self) -> None:
        """Test domain rule validation."""
        context = FlextCliContext()
        if not (context.validate_domain_rules()):
            raise AssertionError(
                f"Expected True, got {context.validate_domain_rules()}"
            )

        # Validation checks for session_id existence
        if not (bool(context.session_id)):
            raise AssertionError(f"Expected True, got {bool(context.session_id)}")


class TestFlextCliPlugin:
    """Test FlextCliPlugin value object."""

    def test_plugin_basic_creation(self) -> None:
        """Test creating plugin with basic parameters."""
        plugin = FlextCliPlugin(name="test-plugin", version="0.9.0")

        if plugin.name != "test-plugin":
            raise AssertionError(f"Expected {'test-plugin'}, got {plugin.name}")
        assert plugin.version == "0.9.0"
        assert plugin.description is None
        if not (plugin.enabled):
            raise AssertionError(f"Expected True, got {plugin.enabled}")
        if plugin.dependencies != []:
            raise AssertionError(f"Expected {[]}, got {plugin.dependencies}")
        assert plugin.commands == []
        assert isinstance(plugin.created_at, datetime)

    def test_plugin_full_creation(self) -> None:
        """Test creating plugin with all parameters."""
        plugin = FlextCliPlugin(
            name="advanced-plugin",
            version="2.1.0",
            description="Advanced test plugin",
            enabled=False,
            dependencies=["dep1", "dep2"],
            commands=["cmd1", "cmd2", "cmd3"],
        )

        if plugin.name != "advanced-plugin":
            raise AssertionError(f"Expected {'advanced-plugin'}, got {plugin.name}")
        assert plugin.version == "2.1.0"
        if plugin.description != "Advanced test plugin":
            raise AssertionError(
                f"Expected {'Advanced test plugin'}, got {plugin.description}"
            )
        if plugin.enabled:
            raise AssertionError(f"Expected False, got {plugin.enabled}")
        assert plugin.dependencies == ["dep1", "dep2"]
        if plugin.commands != ["cmd1", "cmd2", "cmd3"]:
            raise AssertionError(
                f"Expected {['cmd1', 'cmd2', 'cmd3']}, got {plugin.commands}"
            )

    def test_validate_domain_rules(self) -> None:
        """Test domain rule validation."""
        # Valid plugin
        plugin = FlextCliPlugin(name="test-plugin", version="0.9.0")
        if not (plugin.validate_domain_rules()):
            raise AssertionError(f"Expected True, got {plugin.validate_domain_rules()}")

        # Invalid plugin - empty name
        plugin_invalid = FlextCliPlugin(name="", version="0.9.0")
        if plugin_invalid.validate_domain_rules():
            raise AssertionError(
                f"Expected False, got {plugin_invalid.validate_domain_rules()}"
            )

        # Invalid plugin - empty version
        plugin_invalid2 = FlextCliPlugin(name="test-plugin", version="")
        if plugin_invalid2.validate_domain_rules():
            raise AssertionError(
                f"Expected False, got {plugin_invalid2.validate_domain_rules()}"
            )


class TestFlextCliSession:
    """Test FlextCliSession entity."""

    def test_session_creation(self) -> None:
        """Test basic session creation."""
        session = FlextCliSession(id="test-session-100")

        assert session.user_id is None
        if session.commands_executed != []:
            raise AssertionError(f"Expected {[]}, got {session.commands_executed}")
        assert isinstance(session.started_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert isinstance(session.config, FlextCliConfig)

    def test_session_with_user(self) -> None:
        """Test session creation with user ID."""
        session = FlextCliSession(id="test-session-101", user_id="test-user-123")

        if session.user_id != "test-user-123":
            raise AssertionError(f"Expected {'test-user-123'}, got {session.user_id}")

    def test_record_command_success(self) -> None:
        """Test recording command successfully."""
        session = FlextCliSession(id="test-session-102")

        if not (session.flext_cli_record_command("test-command")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('test-command')}"
            )
        if "test-command" not in session.commands_executed:
            raise AssertionError(
                f"Expected {'test-command'} in {session.commands_executed}"
            )
        if len(session.commands_executed) != 1:
            raise AssertionError(f"Expected {1}, got {len(session.commands_executed)}")

        # Record another command
        if not (session.flext_cli_record_command("another-command")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('another-command')}"
            )
        if len(session.commands_executed) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {len(session.commands_executed)}")
        assert session.commands_executed == ["test-command", "another-command"]

    def test_record_command_updates_activity(self) -> None:
        """Test that recording command updates last activity."""
        session = FlextCliSession(id="test-session-103")
        original_activity = session.last_activity

        # Small delay to ensure time difference

        time.sleep(0.001)

        session.flext_cli_record_command("test-command")

        assert session.last_activity > original_activity

    def test_record_command_exception_handling(self) -> None:
        """Test record_command method exception handling."""
        session = FlextCliSession(id="test-session-104")

        # Normal case should work
        result = session.flext_cli_record_command("normal-command")
        if not (result):
            raise AssertionError(f"Expected True, got {result}")

        # Test with various input types
        assert session.flext_cli_record_command("") is True  # Empty string is valid
        # Numeric string is valid
        if not (session.flext_cli_record_command("123")):
            raise AssertionError(
                f"Expected True, got {session.flext_cli_record_command('123')}"
            )

    def test_validate_domain_rules(self) -> None:
        """Test domain rule validation."""
        session = FlextCliSession(id="test-session-105")

        # Should be valid (checks for entity_id existence)
        if not (session.validate_domain_rules()):
            raise AssertionError(
                f"Expected True, got {session.validate_domain_rules()}"
            )
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
                f"Expected {FlextCliCommandStatus.PENDING}, got {command.command_status}"
            )
        assert not command.flext_cli_is_running
        assert not command.flext_cli_successful

        # Start execution
        assert command.flext_cli_start_execution()
        if command.command_status != FlextCliCommandStatus.RUNNING:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.RUNNING}, got {command.command_status}"
            )
        assert command.flext_cli_is_running
        assert not command.flext_cli_successful

        # Complete successfully
        assert command.flext_cli_complete_execution(exit_code=0, stdout="success")
        if command.command_status != FlextCliCommandStatus.COMPLETED:
            raise AssertionError(
                f"Expected {FlextCliCommandStatus.COMPLETED}, got {command.command_status}"
            )
        assert not command.flext_cli_is_running
        assert command.flext_cli_successful

    def test_context_with_all_formats(self) -> None:
        """Test context with all output formats."""
        context = FlextCliContext()

        for format_type in FlextCliOutputFormat:
            format_context = context.flext_cli_with_output_format(format_type)
            if format_context.output_format != format_type.value:
                raise AssertionError(
                    f"Expected {format_type.value}, got {format_context.output_format}"
                )

    def test_session_with_multiple_commands(self) -> None:
        """Test session recording multiple commands."""
        session = FlextCliSession(id="test-session-135", user_id="test-user")

        commands = ["init", "run", "deploy", "monitor", "cleanup"]

        for cmd in commands:
            assert session.flext_cli_record_command(cmd)

        if session.commands_executed != commands:
            raise AssertionError(
                f"Expected {commands}, got {session.commands_executed}"
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
        config = FlextCliConfig(config_data)
        context = FlextCliContext(config=config)

        # Context should inherit from config
        if context.debug != config.debug:
            raise AssertionError(f"Expected {config.debug}, got {context.debug}")
        assert context.trace == config.trace
        if context.output_format != config.format_type:
            raise AssertionError(
                f"Expected {config.format_type}, got {context.output_format}"
            )
        assert context.profile == config.profile
