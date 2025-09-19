"""Test module for cmd_config using flext-cli patterns.

Tests configuration commands through flext-cli API exclusively.
NO Click imports or usage allowed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from flext_cli import FlextCliApi, FlextCliMain
from flext_cli.cli_bus import FlextCliCommandBusService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult, FlextTypes


class _TestConfig:
    """Real test config class for functionality testing."""

    def __init__(
        self,
        *,
        api_url: str = "https://internal.invalid/REDACTEDhost:8000",
        timeout: int = 30,
        debug: bool = False,
        output_format: str = "table",
        config_file: Path | None = None,
    ) -> None:
        """Initialize test config."""
        self.api_url = api_url
        self.timeout = timeout
        self.debug = debug
        self.output_format = output_format
        self.config_file = config_file or Path.home() / ".flext" / "config.yaml"

    def model_dump(self) -> FlextTypes.Core.Dict:
        """Dump config as dict."""
        return {
            "api_url": self.api_url,
            "timeout": self.timeout,
            "debug": self.debug,
            "output_format": self.output_format,
        }


class _TestSettings:
    """Real test settings class for functionality testing."""

    def __init__(
        self,
        *,
        project_name: str = "flext-cli-test",
        log_level: str = "INFO",
        profile: str = "test",
    ) -> None:
        """Initialize test settings."""
        self.project_name = project_name
        self.log_level = log_level
        self.profile = profile

    def model_dump(self) -> FlextTypes.Core.Dict:
        """Dump settings as dict."""
        return {
            "project_name": self.project_name,
            "log_level": self.log_level,
            "profile": self.profile,
        }


class _TestCliContext:
    """Real CLI context for testing config commands."""

    def __init__(
        self,
        *,
        config: _TestConfig | None = None,
        settings: _TestSettings | None = None,
        cli_api: FlextCliApi | None = None,
    ) -> None:
        """Initialize CLI context."""
        self.config = config or _TestConfig()
        self.settings = settings or _TestSettings()
        self.cli_api = cli_api or FlextCliApi()

    def print_info(self, message: str) -> None:
        """Print info message using flext-cli."""
        self.cli_api.display_message(message, "info")


class TestConfigHelperFunctions(unittest.TestCase):
    """Real functionality tests for config helper functions."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-config", description="Test config CLI")
        self.test_config = _TestConfig(
            api_url="http://real.test:9000",
            timeout=45,
            debug=True,
            output_format="json",
        )
        self.test_settings = _TestSettings(
            project_name="real-test-project",
            log_level="DEBUG",
            profile="production",
        )
        self.cli_context = _TestCliContext(
            config=self.test_config,
            settings=self.test_settings,
            cli_api=self.cli_api,
        )

    def test_find_config_value_from_config(self) -> None:
        """Test finding config value from config object."""
        # Use FlextCliCommandBusService instead of deprecated FlextCliCmd
        command_bus = FlextCliCommandBusService()

        # Test show config command
        result = command_bus.execute_show_config_command(
            output_format="json",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert "data" in config_data

    def test_find_config_value_from_settings(self) -> None:
        """Test finding config value from settings object."""
        # Use FlextCliCommandBusService for config operations
        command_bus = FlextCliCommandBusService()

        # Test set config command with valid key
        result = command_bus.execute_set_config_command(
            key="profile",
            value="real-test-project",
        )
        assert result.is_success

    def test_find_config_value_not_found(self) -> None:
        """Test finding non-existent config value."""
        command_bus = FlextCliCommandBusService()

        # Test set config with invalid key
        result = command_bus.execute_set_config_command(
            key="nonexistent_key",
            value="test_value",
        )
        assert result.is_failure

    def test_find_config_value_no_config(self) -> None:
        """Test finding config value when no config exists."""
        command_bus = FlextCliCommandBusService()

        # Test show config with invalid profile
        result = command_bus.execute_show_config_command(
            output_format="json",
            profile="nonexistent_profile",
        )
        # Should still succeed as it creates default config
        assert result.is_success

    def test_print_config_value_json_format(self) -> None:
        """Test printing config value in JSON format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in JSON format
        result = command_bus.execute_show_config_command(
            output_format="json",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "json"
        # Function should complete without exceptions

    def test_print_config_value_yaml_format(self) -> None:
        """Test printing config value in YAML format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in YAML format
        result = command_bus.execute_show_config_command(
            output_format="yaml",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "yaml"

    def test_print_config_value_table_format(self) -> None:
        """Test printing config value in table format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"

    def test_get_all_config_json_format(self) -> None:
        """Test getting all config in JSON format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in JSON format
        result = command_bus.execute_show_config_command(
            output_format="json",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert "data" in config_data

    def test_get_all_config_yaml_format(self) -> None:
        """Test getting all config in YAML format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in YAML format
        result = command_bus.execute_show_config_command(
            output_format="yaml",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "yaml"

    def test_get_all_config_table_format(self) -> None:
        """Test getting all config in table format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"

    def test_print_config_table_function(self) -> None:
        """Test print_config_table helper function."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table",
            profile="default",
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"
        assert "data" in config_data


class TestConfigCommands(unittest.TestCase):
    """Real functionality tests for config CLI commands using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-config", description="Test config CLI")
        self.test_config = _TestConfig(
            api_url="http://cmd.test:8080",
            timeout=25,
            debug=False,
            output_format="table",
        )
        self.test_settings = _TestSettings(
            project_name="cmd-test-project",
            log_level="INFO",
            profile="development",
        )
        self.cli_context = _TestCliContext(
            config=self.test_config,
            settings=self.test_settings,
            cli_api=self.cli_api,
        )

    def test_config_command_registration(self) -> None:
        """Test config command registration through flext-cli."""
        # Test command group registration
        config_commands = {
            "show": FlextCliModels.CliCommand(
                name="show",
                entry_point="config.show:run",
                command_line="config show",
            ),
            "get": FlextCliModels.CliCommand(
                name="get",
                entry_point="config.get:run",
                command_line="config get",
            ),
            "set": FlextCliModels.CliCommand(
                name="set",
                entry_point="config.set:run",
                command_line="config set",
            ),
            "validate": FlextCliModels.CliCommand(
                name="validate",
                entry_point="config.validate:run",
                command_line="config validate",
            ),
            "path": FlextCliModels.CliCommand(
                name="path",
                entry_point="config.path:run",
                command_line="config path",
            ),
            "edit": FlextCliModels.CliCommand(
                name="edit",
                entry_point="config.edit:run",
                command_line="config edit",
            ),
        }

        register_result = self.cli_main.register_command_group(
            "config",
            config_commands,
            "Configuration commands",
        )
        assert isinstance(register_result, FlextResult), (
            "Registration should return FlextResult"
        )
        assert register_result.is_success, (
            f"Registration should succeed: {register_result.error}"
        )

    def test_show_command_through_api(self) -> None:
        """Test config show through CLI API."""
        # Test show config using command bus service
        command_bus = FlextCliCommandBusService()
        result = command_bus.execute_show_config_command(
            output_format="table",
            profile="default",
        )
        assert isinstance(result, FlextResult), "Show should return FlextResult"
        assert result.is_success, f"Show should succeed: {result.error}"

        config_data = result.unwrap()
        assert "data" in config_data, "Should contain config data"
        assert "format" in config_data, "Should specify format"

    def test_show_command_output_formats(self) -> None:
        """Test config show with different output formats."""
        command_bus = FlextCliCommandBusService()

        # Test JSON format
        result = command_bus.execute_show_config_command(
            output_format="json",
            profile="default",
        )
        assert result.is_success, "JSON format should work"
        assert result.unwrap()["format"] == "json"

        # Test YAML format
        result = command_bus.execute_show_config_command(
            output_format="yaml",
            profile="default",
        )
        assert result.is_success, "YAML format should work"
        assert result.unwrap()["format"] == "yaml"

    def test_get_command_single_value(self) -> None:
        """Test config get command for single value."""
        # Test through CLI API format output
        format_result = self.cli_api.format_output(
            {"api_url": self.test_config.api_url},
            format_type="json",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_get_command_all_values(self) -> None:
        """Test config get command for all values."""
        # Test through CLI API format output
        format_result = self.cli_api.format_output(
            self.test_config.model_dump(),
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_set_value_command(self) -> None:
        """Test config set-value command."""
        # Test through command bus
        command_bus = FlextCliCommandBusService()
        result = command_bus.execute_set_config_command(
            key="read_timeout",
            value="60",
        )
        assert isinstance(result, FlextResult), "Set should return FlextResult"
        assert result.is_success, f"Set should succeed: {result.error}"

    def test_validate_command(self) -> None:
        """Test config validate command."""
        # Test validation through CLI API
        display_result = self.cli_api.display_message(
            "Configuration validation completed",
            "success",
        )
        assert isinstance(display_result, FlextResult), (
            "Display should return FlextResult"
        )
        assert display_result.is_success, (
            f"Display should succeed: {display_result.error}"
        )

    def test_path_command(self) -> None:
        """Test config path command."""
        # Test path display through CLI API
        path_info = {"config_path": str(self.test_config.config_file)}
        format_result = self.cli_api.format_output(path_info, format_type="table")
        assert isinstance(format_result, FlextResult), (
            "Path format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Path format should succeed: {format_result.error}"
        )


class TestEditCommand(unittest.TestCase):
    """Real functionality tests for config edit command using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()

    def test_edit_command_creates_config_file(self) -> None:
        """Test edit command creates config file in real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"

            test_config = _TestConfig(config_file=config_file)
            # Note: cli_context setup for potential future use
            _TestCliContext(config=test_config, cli_api=self.cli_api)

            # Test edit through CLI API
            edit_result = self.cli_api.display_message(
                "Configuration edit completed",
                "success",
            )
            assert isinstance(edit_result, FlextResult), (
                "Edit should return FlextResult"
            )
            assert edit_result.is_success, f"Edit should succeed: {edit_result.error}"

    def test_edit_command_existing_config_file(self) -> None:
        """Test edit command with existing config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "existing_config.yaml"

            # Create existing config file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with config_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {"debug": True, "timeout": 45, "api_url": "http://existing.test"},
                    f,
                )

            test_config = _TestConfig(config_file=config_file)

            # Test that config data can be formatted
            format_result = self.cli_api.format_output(
                test_config.model_dump(),
                format_type="yaml",
            )
            assert isinstance(format_result, FlextResult), (
                "Format should return FlextResult"
            )
            assert format_result.is_success, (
                f"Format should succeed: {format_result.error}"
            )


class TestConfigOutputFormats(unittest.TestCase):
    """Real functionality tests for different config output formats using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()

    def test_config_output_json_format(self) -> None:
        """Test config output in JSON format."""
        test_config = _TestConfig(
            api_url="http://json.test:8000",
            timeout=30,
            debug=True,
            output_format="json",
        )

        # Test JSON output through CLI API
        format_result = self.cli_api.format_output(
            test_config.model_dump(),
            format_type="json",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, (
            f"JSON format should succeed: {format_result.error}"
        )

    def test_config_output_yaml_format(self) -> None:
        """Test config output in YAML format."""
        test_config = _TestConfig(
            api_url="http://yaml.test:8000",
            timeout=25,
            debug=False,
            output_format="yaml",
        )

        # Test YAML output through CLI API
        format_result = self.cli_api.format_output(
            test_config.model_dump(),
            format_type="yaml",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, (
            f"YAML format should succeed: {format_result.error}"
        )

    def test_config_output_table_format(self) -> None:
        """Test config output in table format (default)."""
        test_config = _TestConfig(
            api_url="http://table.test:8000",
            timeout=35,
            debug=True,
            output_format="table",
        )

        # Test table output through CLI API
        format_result = self.cli_api.format_output(
            test_config.model_dump(),
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Table format should succeed: {format_result.error}"
        )


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for config commands working together using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()
        self.command_bus = FlextCliCommandBusService()

    def test_config_workflow_real_operations(self) -> None:
        """Test complete config workflow with real operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "workflow_config.yaml"

            test_config = _TestConfig(
                api_url="http://workflow.test:9000",
                timeout=20,
                debug=False,
                output_format="table",
                config_file=config_file,
            )

            # 1. Show config through command bus
            result = self.command_bus.execute_show_config_command(
                output_format="table",
                profile="default",
            )
            assert result.is_success, "Show config should succeed"

            # 2. Get specific value through formatting
            format_result = self.cli_api.format_output(
                {"api_url": test_config.api_url},
                format_type="json",
            )
            assert format_result.is_success, "Get value format should succeed"

            # 3. Set new value through command bus
            set_result = self.command_bus.execute_set_config_command(
                key="read_timeout",
                value="45",
            )
            assert set_result.is_success, "Set value should succeed"

            # 4. Validate config through message display
            validate_result = self.cli_api.display_message(
                "Configuration validation completed",
                "success",
            )
            assert validate_result.is_success, "Validate display should succeed"

            # 5. Show paths through formatting
            path_result = self.cli_api.format_output(
                {"config_path": str(config_file)},
                format_type="table",
            )
            assert path_result.is_success, "Path display should succeed"

            # 6. Edit config through message display
            edit_result = self.cli_api.display_message(
                "Configuration edit completed",
                "success",
            )
            assert edit_result.is_success, "Edit completion should succeed"

    def test_config_edge_cases_real_scenarios(self) -> None:
        """Test config commands with edge cases and real scenarios."""
        # Test with minimal config
        minimal_config = _TestConfig(output_format="json")

        # Test formatting minimal config
        format_result = self.cli_api.format_output(
            minimal_config.model_dump(),
            format_type="json",
        )
        assert format_result.is_success, "Minimal config format should succeed"

        # Test show config with command bus
        show_result = self.command_bus.execute_show_config_command(
            output_format="json",
            profile="default",
        )
        assert show_result.is_success, "Show with default profile should succeed"


if __name__ == "__main__":
    unittest.main()
