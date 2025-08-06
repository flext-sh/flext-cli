"""Tests for application commands.

Tests application command classes for coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from uuid import UUID, uuid4

from flext_cli.application.commands import (
    CancelCommandCommand,
    CreateConfigCommand,
    DeleteConfigCommand,
    DisablePluginCommand,
    EnablePluginCommand,
    EndSessionCommand,
    ExecuteCommandCommand,
    GetCommandHistoryCommand,
    GetCommandStatusCommand,
    GetSessionInfoCommand,
    InstallPluginCommand,
    ListCommandsCommand,
    ListConfigsCommand,
    ListPluginsCommand,
    StartSessionCommand,
    UninstallPluginCommand,
    UpdateConfigCommand,
    ValidateConfigCommand,
)
from flext_cli.domain.entities import CommandType

# Constants
EXPECTED_DATA_COUNT = 3


class TestExecuteCommandCommand:
    """Test ExecuteCommandCommand class."""

    def test_init_with_required_parameters(self) -> None:
        """Test initialization with required parameters only."""
        cmd = ExecuteCommandCommand(
            name="test_command",
            command_line="echo hello",
        )

        if cmd.name != "test_command":
            raise AssertionError(f"Expected {'test_command'}, got {cmd.name}")
        assert cmd.command_line == "echo hello"
        if cmd.command_type != CommandType.SYSTEM:
            raise AssertionError(
                f"Expected {CommandType.SYSTEM}, got {cmd.command_type}"
            )
        assert cmd.timeout_seconds is None

        # Check optional parameters have default values
        assert cmd.arguments is None
        assert cmd.options is None
        assert cmd.user_id is None
        assert cmd.session_id is None
        assert cmd.working_directory is None
        assert cmd.environment is None

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        cmd = ExecuteCommandCommand(
            name="complex_command",
            command_line="python script.py",
            command_type=CommandType.PIPELINE,
            timeout_seconds=30.0,
        )

        if cmd.name != "complex_command":
            raise AssertionError(f"Expected {'complex_command'}, got {cmd.name}")
        assert cmd.command_line == "python script.py"
        if cmd.command_type != CommandType.PIPELINE:
            raise AssertionError(
                f"Expected {CommandType.PIPELINE}, got {cmd.command_type}"
            )
        assert cmd.timeout_seconds == 30.0

    def test_optional_parameters_assignment(self) -> None:
        """Test assignment of optional parameters."""
        cmd = ExecuteCommandCommand("test", "echo test")

        # Assign optional parameters
        test_uuid = uuid4()
        cmd.user_id = test_uuid
        cmd.session_id = "session123"
        cmd.working_directory = "/test/tmp"
        cmd.arguments = {"arg1": "value1"}
        cmd.options = {"verbose": True}
        cmd.environment = {"ENV_VAR": "value"}

        if cmd.user_id != test_uuid:
            raise AssertionError(f"Expected {test_uuid}, got {cmd.user_id}")
        assert cmd.session_id == "session123"
        if cmd.working_directory != "/test/tmp":
            raise AssertionError(f"Expected {'/test/tmp'}, got {cmd.working_directory}")
        assert cmd.arguments == {"arg1": "value1"}
        if cmd.options != {"verbose": True}:
            raise AssertionError(f'Expected {{"verbose": True}}, got {cmd.options}')
        assert cmd.environment == {"ENV_VAR": "value"}

    def test_different_command_types(self) -> None:
        """Test with different command types."""
        command_types = [
            CommandType.SYSTEM,
            CommandType.PIPELINE,
            CommandType.PLUGIN,
            CommandType.DATA,
            CommandType.CONFIG,
            CommandType.AUTH,
            CommandType.MONITORING,
        ]

        for cmd_type in command_types:
            cmd = ExecuteCommandCommand(
                name=f"test_{cmd_type.value}",
                command_line="test command",
                command_type=cmd_type,
            )
            if cmd.command_type != cmd_type:
                raise AssertionError(f"Expected {cmd_type}, got {cmd.command_type}")


class TestCancelCommandCommand:
    """Test CancelCommandCommand class."""

    def test_init_with_required_parameters(self) -> None:
        """Test initialization with required parameters."""
        command_id = uuid4()
        cmd = CancelCommandCommand(command_id)

        if cmd.command_id != command_id:
            raise AssertionError(f"Expected {command_id}, got {cmd.command_id}")
        assert cmd.user_id is None

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        command_id = uuid4()
        user_id = uuid4()
        cmd = CancelCommandCommand(command_id, user_id)

        if cmd.command_id != command_id:
            raise AssertionError(f"Expected {command_id}, got {cmd.command_id}")
        assert cmd.user_id == user_id

    def test_command_id_type(self) -> None:
        """Test that command_id is a UUID."""
        command_id = uuid4()
        cmd = CancelCommandCommand(command_id)

        assert isinstance(cmd.command_id, UUID)
        if cmd.command_id != command_id:
            raise AssertionError(f"Expected {command_id}, got {cmd.command_id}")


class TestCreateConfigCommand:
    """Test CreateConfigCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = CreateConfigCommand()

        # Test default values
        assert cmd.description is None
        if cmd.version != "0.9.0":
            raise AssertionError(f"Expected {'1.0.0'}, got {cmd.version}")
        assert cmd.user_id is None
        if cmd.is_global:
            raise AssertionError(f"Expected False, got {cmd.is_global}")

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = CreateConfigCommand()

        cmd.name = "test_config"
        cmd.description = "Test configuration"
        cmd.config_data = {"key": "value"}
        cmd.config_type = "application"
        cmd.version = "0.9.0"
        cmd.user_id = uuid4()
        cmd.is_global = True

        if cmd.name != "test_config":
            raise AssertionError(f"Expected {'test_config'}, got {cmd.name}")
        assert cmd.description == "Test configuration"
        if cmd.config_data != {"key": "value"}:
            raise AssertionError(f'Expected {{"key": "value"}}, got {cmd.config_data}')
        assert cmd.config_type == "application"
        if cmd.version != "0.9.0":
            raise AssertionError(f"Expected {'2.0.0'}, got {cmd.version}")
        assert isinstance(cmd.user_id, UUID)
        if not (cmd.is_global):
            raise AssertionError(f"Expected True, got {cmd.is_global}")

    def test_config_data_types(self) -> None:
        """Test different config data types."""
        cmd = CreateConfigCommand()

        # Test with different data structures
        test_configs = [
            {"simple": "value"},
            {"nested": {"key": "value"}},
            {"list": [1, 2, 3]},
            {"mixed": {"string": "value", "number": 42, "boolean": True}},
        ]

        for config_data in test_configs:
            cmd.config_data = config_data
            if cmd.config_data != config_data:
                raise AssertionError(f"Expected {config_data}, got {cmd.config_data}")


class TestUpdateConfigCommand:
    """Test UpdateConfigCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = UpdateConfigCommand()

        # Test default values
        assert cmd.name is None
        assert cmd.description is None
        assert cmd.config_data is None
        assert cmd.version is None
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = UpdateConfigCommand()
        config_id = uuid4()
        user_id = uuid4()

        cmd.config_id = config_id
        cmd.name = "updated_config"
        cmd.description = "Updated description"
        cmd.config_data = {"updated": "data"}
        cmd.version = "1.1.0"
        cmd.user_id = user_id

        if cmd.config_id != config_id:
            raise AssertionError(f"Expected {config_id}, got {cmd.config_id}")
        assert cmd.name == "updated_config"
        if cmd.description != "Updated description":
            raise AssertionError(
                f"Expected {'Updated description'}, got {cmd.description}"
            )
        assert cmd.config_data == {"updated": "data"}
        if cmd.version != "1.1.0":
            raise AssertionError(f"Expected {'1.1.0'}, got {cmd.version}")
        assert cmd.user_id == user_id

    def test_partial_updates(self) -> None:
        """Test partial update scenarios."""
        cmd = UpdateConfigCommand()
        cmd.config_id = uuid4()

        # Test updating only name
        cmd.name = "new_name"
        if cmd.name != "new_name":
            raise AssertionError(f"Expected {'new_name'}, got {cmd.name}")
        assert cmd.description is None

        # Test updating only description
        cmd.description = "new_description"
        if cmd.description != "new_description":
            raise AssertionError(f"Expected {'new_description'}, got {cmd.description}")
        assert cmd.config_data is None


class TestDeleteConfigCommand:
    """Test DeleteConfigCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = DeleteConfigCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = DeleteConfigCommand()
        config_id = uuid4()
        user_id = uuid4()

        cmd.config_id = config_id
        cmd.user_id = user_id

        if cmd.config_id != config_id:
            raise AssertionError(f"Expected {config_id}, got {cmd.config_id}")
        assert cmd.user_id == user_id


class TestValidateConfigCommand:
    """Test ValidateConfigCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = ValidateConfigCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = ValidateConfigCommand()
        config_id = uuid4()
        user_id = uuid4()

        cmd.config_id = config_id
        cmd.user_id = user_id

        if cmd.config_id != config_id:
            raise AssertionError(f"Expected {config_id}, got {cmd.config_id}")
        assert cmd.user_id == user_id


class TestStartSessionCommand:
    """Test StartSessionCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = StartSessionCommand()
        assert cmd.user_id is None
        assert cmd.working_directory is None
        assert cmd.environment is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = StartSessionCommand()

        cmd.session_id = "session_123"
        cmd.user_id = uuid4()
        cmd.working_directory = "/home/user"
        cmd.environment = {"PATH": "/usr/bin", "HOME": "/home/user"}

        if cmd.session_id != "session_123":
            raise AssertionError(f"Expected {'session_123'}, got {cmd.session_id}")
        assert isinstance(cmd.user_id, UUID)
        if cmd.working_directory != "/home/user":
            raise AssertionError(
                f"Expected {'/home/user'}, got {cmd.working_directory}"
            )
        assert cmd.environment == {"PATH": "/usr/bin", "HOME": "/home/user"}

    def test_environment_variations(self) -> None:
        """Test different environment configurations."""
        cmd = StartSessionCommand()

        # Test empty environment
        cmd.environment = {}
        if cmd.environment != {}:
            raise AssertionError(f"Expected {{}}, got {cmd.environment}")

        # Test None environment
        cmd.environment = None
        assert cmd.environment is None

        # Test complex environment
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "PYTHON_PATH": "/opt/python",
            "DEBUG": "true",
        }
        cmd.environment = env
        if cmd.environment != env:
            raise AssertionError(f"Expected {env}, got {cmd.environment}")


class TestEndSessionCommand:
    """Test EndSessionCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = EndSessionCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = EndSessionCommand()
        session_id = uuid4()
        user_id = uuid4()

        cmd.session_id = session_id
        cmd.user_id = user_id

        if cmd.session_id != session_id:
            raise AssertionError(f"Expected {session_id}, got {cmd.session_id}")
        assert cmd.user_id == user_id


class TestInstallPluginCommand:
    """Test InstallPluginCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = InstallPluginCommand()

        # Test default values
        assert cmd.version is None
        assert cmd.commands is None
        assert cmd.dependencies is None
        assert cmd.author is None
        assert cmd.license is None
        assert cmd.repository_url is None
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = InstallPluginCommand()
        user_id = uuid4()

        cmd.name = "test_plugin"
        cmd.version = "0.9.0"
        cmd.entry_point = "test_plugin.main"
        cmd.commands = ["cmd1", "cmd2"]
        cmd.dependencies = ["dep1", "dep2"]
        cmd.author = "Test Author"
        cmd.license = "MIT"
        cmd.repository_url = "https://github.com/test/plugin"
        cmd.user_id = user_id

        if cmd.name != "test_plugin":
            raise AssertionError(f"Expected {'test_plugin'}, got {cmd.name}")
        assert cmd.version == "0.9.0"
        if cmd.entry_point != "test_plugin.main":
            raise AssertionError(
                f"Expected {'test_plugin.main'}, got {cmd.entry_point}"
            )
        assert cmd.commands == ["cmd1", "cmd2"]
        if cmd.dependencies != ["dep1", "dep2"]:
            raise AssertionError(f"Expected {['dep1', 'dep2']}, got {cmd.dependencies}")
        assert cmd.author == "Test Author"
        if cmd.license != "MIT":
            raise AssertionError(f"Expected {'MIT'}, got {cmd.license}")
        assert cmd.repository_url == "https://github.com/test/plugin"
        if cmd.user_id != user_id:
            raise AssertionError(f"Expected {user_id}, got {cmd.user_id}")

    def test_empty_lists(self) -> None:
        """Test with empty lists for commands and dependencies."""
        cmd = InstallPluginCommand()

        cmd.commands = []
        cmd.dependencies = []

        if cmd.commands != []:
            raise AssertionError(f"Expected {[]}, got {cmd.commands}")
        assert cmd.dependencies == []


class TestUninstallPluginCommand:
    """Test UninstallPluginCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = UninstallPluginCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = UninstallPluginCommand()
        plugin_id = uuid4()
        user_id = uuid4()

        cmd.plugin_id = plugin_id
        cmd.user_id = user_id

        if cmd.plugin_id != plugin_id:
            raise AssertionError(f"Expected {plugin_id}, got {cmd.plugin_id}")
        assert cmd.user_id == user_id


class TestEnablePluginCommand:
    """Test EnablePluginCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = EnablePluginCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = EnablePluginCommand()
        plugin_id = uuid4()
        user_id = uuid4()

        cmd.plugin_id = plugin_id
        cmd.user_id = user_id

        if cmd.plugin_id != plugin_id:
            raise AssertionError(f"Expected {plugin_id}, got {cmd.plugin_id}")
        assert cmd.user_id == user_id


class TestDisablePluginCommand:
    """Test DisablePluginCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = DisablePluginCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = DisablePluginCommand()
        plugin_id = uuid4()
        user_id = uuid4()

        cmd.plugin_id = plugin_id
        cmd.user_id = user_id

        if cmd.plugin_id != plugin_id:
            raise AssertionError(f"Expected {plugin_id}, got {cmd.plugin_id}")
        assert cmd.user_id == user_id


class TestListCommandsCommand:
    """Test ListCommandsCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = ListCommandsCommand()

        assert cmd.command_type is None
        assert cmd.user_id is None
        assert cmd.session_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = ListCommandsCommand()
        user_id = uuid4()

        cmd.command_type = CommandType.PIPELINE
        cmd.user_id = user_id
        cmd.session_id = "session_456"

        if cmd.command_type != CommandType.PIPELINE:
            raise AssertionError(
                f"Expected {CommandType.PIPELINE}, got {cmd.command_type}"
            )
        assert cmd.user_id == user_id
        if cmd.session_id != "session_456":
            raise AssertionError(f"Expected {'session_456'}, got {cmd.session_id}")

    def test_all_command_types(self) -> None:
        """Test with all command types."""
        cmd = ListCommandsCommand()

        for cmd_type in CommandType:
            cmd.command_type = cmd_type
            if cmd.command_type != cmd_type:
                raise AssertionError(f"Expected {cmd_type}, got {cmd.command_type}")


class TestGetCommandHistoryCommand:
    """Test GetCommandHistoryCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = GetCommandHistoryCommand()

        assert cmd.user_id is None
        assert cmd.session_id is None
        if cmd.limit != 100:
            raise AssertionError(f"Expected {100}, got {cmd.limit}")
        assert cmd.command_type is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = GetCommandHistoryCommand()
        user_id = uuid4()

        cmd.user_id = user_id
        cmd.session_id = "session_789"
        cmd.limit = 50
        cmd.command_type = CommandType.DATA

        if cmd.user_id != user_id:
            raise AssertionError(f"Expected {user_id}, got {cmd.user_id}")
        assert cmd.session_id == "session_789"
        if cmd.limit != 50:
            raise AssertionError(f"Expected {50}, got {cmd.limit}")
        assert cmd.command_type == CommandType.DATA

    def test_limit_variations(self) -> None:
        """Test different limit values."""
        cmd = GetCommandHistoryCommand()

        limits = [1, 10, 50, 100, 1000]
        for limit in limits:
            cmd.limit = limit
            if cmd.limit != limit:
                raise AssertionError(f"Expected {limit}, got {cmd.limit}")


class TestGetCommandStatusCommand:
    """Test GetCommandStatusCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = GetCommandStatusCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = GetCommandStatusCommand()
        command_id = uuid4()
        user_id = uuid4()

        cmd.command_id = command_id
        cmd.user_id = user_id

        if cmd.command_id != command_id:
            raise AssertionError(f"Expected {command_id}, got {cmd.command_id}")
        assert cmd.user_id == user_id


class TestListConfigsCommand:
    """Test ListConfigsCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = ListConfigsCommand()

        assert cmd.config_type is None
        assert cmd.user_id is None
        if not (cmd.include_global):
            raise AssertionError(f"Expected True, got {cmd.include_global}")

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = ListConfigsCommand()
        user_id = uuid4()

        cmd.config_type = "application"
        cmd.user_id = user_id
        cmd.include_global = False

        if cmd.config_type != "application":
            raise AssertionError(f"Expected {'application'}, got {cmd.config_type}")
        assert cmd.user_id == user_id
        if cmd.include_global:
            raise AssertionError(f"Expected False, got {cmd.include_global}")

    def test_config_type_variations(self) -> None:
        """Test different config type values."""
        cmd = ListConfigsCommand()

        config_types = ["application", "system", "user", "global", None]
        for config_type in config_types:
            cmd.config_type = config_type
            if cmd.config_type != config_type:
                raise AssertionError(f"Expected {config_type}, got {cmd.config_type}")


class TestListPluginsCommand:
    """Test ListPluginsCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and default attributes."""
        cmd = ListPluginsCommand()

        if cmd.enabled_only:
            raise AssertionError(f"Expected False, got {cmd.enabled_only}")
        assert cmd.installed_only is False
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = ListPluginsCommand()
        user_id = uuid4()

        cmd.enabled_only = True
        cmd.installed_only = True
        cmd.user_id = user_id

        if not (cmd.enabled_only):
            raise AssertionError(f"Expected True, got {cmd.enabled_only}")
        assert cmd.installed_only is True
        if cmd.user_id != user_id:
            raise AssertionError(f"Expected {user_id}, got {cmd.user_id}")

    def test_boolean_combinations(self) -> None:
        """Test different boolean combinations."""
        cmd = ListPluginsCommand()

        combinations = [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ]

        for enabled, installed in combinations:
            cmd.enabled_only = enabled
            cmd.installed_only = installed
            if cmd.enabled_only != enabled:
                raise AssertionError(f"Expected {enabled}, got {cmd.enabled_only}")
            assert cmd.installed_only == installed


class TestGetSessionInfoCommand:
    """Test GetSessionInfoCommand class."""

    def test_init_and_attributes(self) -> None:
        """Test initialization and attributes."""
        cmd = GetSessionInfoCommand()
        assert cmd.user_id is None

    def test_attribute_assignment(self) -> None:
        """Test attribute assignment."""
        cmd = GetSessionInfoCommand()
        session_id = uuid4()
        user_id = uuid4()

        cmd.session_id = session_id
        cmd.user_id = user_id

        if cmd.session_id != session_id:
            raise AssertionError(f"Expected {session_id}, got {cmd.session_id}")
        assert cmd.user_id == user_id


class TestCommandImports:
    """Test that all commands can be imported."""

    def test_all_imports_work(self) -> None:
        """Test that all command classes can be imported."""
        # Test that all classes are importable
        from flext_cli.application.commands import (
            CancelCommandCommand,
            CreateConfigCommand,
            DeleteConfigCommand,
            DisablePluginCommand,
            EnablePluginCommand,
            EndSessionCommand,
            ExecuteCommandCommand,
            GetCommandHistoryCommand,
            GetCommandStatusCommand,
            GetSessionInfoCommand,
            InstallPluginCommand,
            ListCommandsCommand,
            ListConfigsCommand,
            ListPluginsCommand,
            StartSessionCommand,
            UninstallPluginCommand,
            UpdateConfigCommand,
            ValidateConfigCommand,
        )

        # All classes should be available
        assert ExecuteCommandCommand
        assert CancelCommandCommand
        assert CreateConfigCommand
        assert UpdateConfigCommand
        assert DeleteConfigCommand
        assert ValidateConfigCommand
        assert StartSessionCommand
        assert EndSessionCommand
        assert InstallPluginCommand
        assert UninstallPluginCommand
        assert EnablePluginCommand
        assert DisablePluginCommand
        assert ListCommandsCommand
        assert GetCommandHistoryCommand
        assert GetCommandStatusCommand
        assert ListConfigsCommand
        assert ListPluginsCommand
        assert GetSessionInfoCommand

    def test_command_type_import(self) -> None:
        """Test CommandType import."""

        assert CommandType
        assert CommandType.SYSTEM
        assert CommandType.PIPELINE
        assert CommandType.PLUGIN
        assert CommandType.DATA
        assert CommandType.CONFIG
        assert CommandType.AUTH
        assert CommandType.MONITORING

    def test_uuid_import(self) -> None:
        """Test UUID import and usage."""

        # Test that UUID works as expected
        test_uuid = uuid4()
        assert isinstance(test_uuid, UUID)

        # Test string conversion
        uuid_str = str(test_uuid)
        assert isinstance(uuid_str, str)
        if len(uuid_str) != 36:  # Standard UUID string length
            raise AssertionError(f"Expected {36}, got {len(uuid_str)}")


class TestCommandInstantiation:
    """Test instantiation of all command classes."""

    def test_instantiate_all_commands(self) -> None:
        """Test that all command classes can be instantiated."""
        # Commands that can be instantiated with no arguments
        no_args_commands = [
            CreateConfigCommand,
            UpdateConfigCommand,
            DeleteConfigCommand,
            ValidateConfigCommand,
            StartSessionCommand,
            EndSessionCommand,
            InstallPluginCommand,
            UninstallPluginCommand,
            EnablePluginCommand,
            DisablePluginCommand,
            ListCommandsCommand,
            GetCommandHistoryCommand,
            GetCommandStatusCommand,
            ListConfigsCommand,
            ListPluginsCommand,
            GetSessionInfoCommand,
        ]

        for command_class in no_args_commands:
            cmd = command_class()
            assert cmd is not None

        # Commands that require arguments
        execute_cmd = ExecuteCommandCommand("test", "echo test")
        assert execute_cmd is not None

        cancel_cmd = CancelCommandCommand(uuid4())
        assert cancel_cmd is not None

    def test_command_attributes_exist(self) -> None:
        """Test that expected attributes exist on command instances."""
        # Test ExecuteCommandCommand attributes
        execute_cmd = ExecuteCommandCommand("test", "echo test")
        assert hasattr(execute_cmd, "name")
        assert hasattr(execute_cmd, "command_line")
        assert hasattr(execute_cmd, "command_type")
        assert hasattr(execute_cmd, "timeout_seconds")
        assert hasattr(execute_cmd, "arguments")
        assert hasattr(execute_cmd, "options")
        assert hasattr(execute_cmd, "user_id")
        assert hasattr(execute_cmd, "session_id")
        assert hasattr(execute_cmd, "working_directory")
        assert hasattr(execute_cmd, "environment")

        # Test CancelCommandCommand attributes
        cancel_cmd = CancelCommandCommand(uuid4())
        assert hasattr(cancel_cmd, "command_id")
        assert hasattr(cancel_cmd, "user_id")

        # Test CreateConfigCommand attributes (these are class attributes)
        config_cmd = CreateConfigCommand()
        # These are defined as class attributes in the command classes
        assert config_cmd.description is None
        if config_cmd.version != "0.9.0":
            raise AssertionError(f"Expected {'1.0.0'}, got {config_cmd.version}")
        assert config_cmd.user_id is None
        if config_cmd.is_global:
            raise AssertionError(f"Expected False, got {config_cmd.is_global}")


class TestCommandTypeCompatibility:
    """Test CommandType compatibility across commands."""

    def test_command_type_usage_in_execute_command(self) -> None:
        """Test CommandType usage in ExecuteCommandCommand."""
        for cmd_type in CommandType:
            cmd = ExecuteCommandCommand(
                name=f"test_{cmd_type.value}",
                command_line="test",
                command_type=cmd_type,
            )
            if cmd.command_type != cmd_type:
                raise AssertionError(f"Expected {cmd_type}, got {cmd.command_type}")
            if cmd.command_type.value not in {
                "cli",
                "system",
                "script",
                "sql",
                "pipeline",
                "plugin",
                "data",
                "config",
                "auth",
                "monitoring",
            }:
                raise AssertionError(
                    f"Expected {cmd.command_type.value} is not in {
                        [
                            'cli',
                            'system',
                            'script',
                            'sql',
                            'pipeline',
                            'plugin',
                            'data',
                            'config',
                            'auth',
                            'monitoring',
                        ]
                    }"
                )

    def test_command_type_usage_in_list_commands(self) -> None:
        """Test CommandType usage in ListCommandsCommand."""
        cmd = ListCommandsCommand()

        # Test with each command type
        for cmd_type in CommandType:
            cmd.command_type = cmd_type
            if cmd.command_type != cmd_type:
                raise AssertionError(f"Expected {cmd_type}, got {cmd.command_type}")

        # Test with None
        cmd.command_type = None
        assert cmd.command_type is None

    def test_command_type_usage_in_history_command(self) -> None:
        """Test CommandType usage in GetCommandHistoryCommand."""
        cmd = GetCommandHistoryCommand()

        # Test with each command type
        for cmd_type in CommandType:
            cmd.command_type = cmd_type
            if cmd.command_type != cmd_type:
                raise AssertionError(f"Expected {cmd_type}, got {cmd.command_type}")

        # Test with None
        cmd.command_type = None
        assert cmd.command_type is None
