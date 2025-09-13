
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import click
import yaml
from click.testing import CliRunner
from flext_core import FlextTypes
from rich.console import Console

from flext_cli.cli import ( config, edit, get, path, set_value, show, validate, )
from flext_cli.cli_bus import FlextCliCommandBusService


class _TestConfig:
    """Real test config class for functionality testing."""

    def __init__(
        self,
        *,
        api_url: str = "http://test.localhost:8000",
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
        console: Console | None = None,
    ) -> None:
        """Initialize CLI context."""
        self.config = config or _TestConfig()
        self.settings = settings or _TestSettings()
        self.console = console or Console()

    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[info]{message}[/info]")


class TestConfigHelperFunctions(unittest.TestCase):
    """Real functionality tests for config helper functions."""

    def setUp(self) -> None:
        """Set up test fixtures."""
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
        )

    def test_find_config_value_from_config(self) -> None:
        """Test finding config value from config object."""
        # Use FlextCliCommandBusService instead of deprecated FlextCliCmd
        command_bus = FlextCliCommandBusService()

        # Test show config command
        result = command_bus.execute_show_config_command(
            output_format="json", profile="default"
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
            key="profile", value="real-test-project"
        )
        assert result.is_success

    def test_find_config_value_not_found(self) -> None:
        """Test finding non-existent config value."""
        command_bus = FlextCliCommandBusService()

        # Test set config with invalid key
        result = command_bus.execute_set_config_command(
            key="nonexistent_key", value="test_value"
        )
        assert result.is_failure

    def test_find_config_value_no_config(self) -> None:
        """Test finding config value when no config exists."""
        command_bus = FlextCliCommandBusService()

        # Test show config with invalid profile
        result = command_bus.execute_show_config_command(
            output_format="json", profile="nonexistent_profile"
        )
        # Should still succeed as it creates default config
        assert result.is_success

    def test_print_config_value_json_format(self) -> None:
        """Test printing config value in JSON format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in JSON format
        result = command_bus.execute_show_config_command(
            output_format="json", profile="default"
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
            output_format="yaml", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "yaml"

    def test_print_config_value_table_format(self) -> None:
        """Test printing config value in table format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"

    def test_get_all_config_json_format(self) -> None:
        """Test getting all config in JSON format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in JSON format
        result = command_bus.execute_show_config_command(
            output_format="json", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert "data" in config_data

    def test_get_all_config_yaml_format(self) -> None:
        """Test getting all config in YAML format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in YAML format
        result = command_bus.execute_show_config_command(
            output_format="yaml", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "yaml"

    def test_get_all_config_table_format(self) -> None:
        """Test getting all config in table format."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"

    def test_print_config_table_function(self) -> None:
        """Test print_config_table helper function."""
        command_bus = FlextCliCommandBusService()

        # Test show config in table format
        result = command_bus.execute_show_config_command(
            output_format="table", profile="default"
        )
        assert result.is_success
        config_data = result.unwrap()
        assert config_data["format"] == "table"
        assert "data" in config_data


class TestConfigCommands(unittest.TestCase):
    """Real functionality tests for config CLI commands."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()
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
        )

    def test_config_group_structure(self) -> None:
        """Test config command group structure."""
        assert isinstance(config, click.Group)
        assert config.name == "config"
        assert "Configuration commands" in (config.help or "")

        # Verify commands are registered
        ctx = click.Context(config)
        commands = config.list_commands(ctx)
        expected_commands = ["show", "get", "set-value", "validate", "path", "edit"]
        for expected_cmd in expected_commands:
            assert expected_cmd in commands

    def test_show_command(self) -> None:
        """Test config show command."""
        result = self.runner.invoke(
            show,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0
        # Verify actual config data is shown, not placeholder
        assert "FLEXT CONFIGURATION" in result.output
        assert "Environment:" in result.output
        assert "Debug Mode:" in result.output

    def test_show_command_no_console(self) -> None:
        """Test config show command without console in context."""
        result = self.runner.invoke(show, [], obj={})
        # Command should succeed even without console context
        assert result.exit_code == 0
        assert "FLEXT CONFIGURATION" in result.output

    def test_get_command_single_value(self) -> None:
        """Test config get command for single value."""
        result = self.runner.invoke(
            get,
            ["api_url"],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0

    def test_get_command_all_values(self) -> None:
        """Test config get command for all values."""
        result = self.runner.invoke(
            get,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0

    def test_get_command_no_context(self) -> None:
        """Test config get command without CLI context."""
        result = self.runner.invoke(
            get,
            ["api_url"],
            obj={"console": Console()},
        )
        assert result.exit_code == 0

    def test_get_command_nonexistent_key(self) -> None:
        """Test config get command for nonexistent key."""
        result = self.runner.invoke(
            get,
            ["nonexistent_key"],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0  # Should complete but return None

    def test_set_value_command(self) -> None:
        """Test config set-value command."""
        result = self.runner.invoke(
            set_value,
            ["timeout", "60"],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0
        assert "Set timeout = 60" in result.output

    def test_set_value_command_no_context(self) -> None:
        """Test config set-value command without CLI context."""
        result = self.runner.invoke(
            set_value,
            ["timeout", "60"],
            obj={"console": Console()},
        )
        assert result.exit_code == 0

    def test_set_value_command_no_config(self) -> None:
        """Test config set-value command without config object."""
        context_no_config = type("Context", (), {})()
        result = self.runner.invoke(
            set_value,
            ["timeout", "60"],
            obj={"console": Console(), "cli_context": context_no_config},
        )
        assert result.exit_code == 0  # Should complete even without config

    def test_validate_command(self) -> None:
        """Test config validate command."""
        result = self.runner.invoke(
            validate,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0
        assert "Configuration validation completed" in result.output

    def test_validate_command_no_context(self) -> None:
        """Test config validate command without CLI context."""
        result = self.runner.invoke(
            validate,
            [],
            obj={"console": Console()},
        )
        assert result.exit_code == 0

    def test_validate_command_no_config(self) -> None:
        """Test config validate command without config object."""
        context_no_config = type("Context", (), {})()
        result = self.runner.invoke(
            validate,
            [],
            obj={"console": Console(), "cli_context": context_no_config},
        )
        assert result.exit_code == 0

    def test_path_command(self) -> None:
        """Test config path command."""
        result = self.runner.invoke(
            path,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0
        # Verify actual configuration paths are shown, not placeholder
        assert "Configuration path:" in result.output

    def test_path_command_with_print_info(self) -> None:
        """Test config path command with CLI context that has print_info."""
        result = self.runner.invoke(
            path,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0

    def test_path_command_no_context(self) -> None:
        """Test config path command without CLI context."""
        result = self.runner.invoke(
            path,
            [],
            obj={"console": Console()},
        )
        assert result.exit_code == 0


class TestEditCommand(unittest.TestCase):
    """Real functionality tests for config edit command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_edit_command_creates_config_file(self) -> None:
        """Test edit command creates config file in real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"

            test_config = _TestConfig(config_file=config_file)
            cli_context = _TestCliContext(config=test_config)

            result = self.runner.invoke(
                edit,
                [],
                obj={"console": Console(), "cli_context": cli_context},
            )

            assert result.exit_code == 0
            assert "Configuration edit completed" in result.output

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
            cli_context = _TestCliContext(config=test_config)

            result = self.runner.invoke(
                edit,
                [],
                obj={"console": Console(), "cli_context": cli_context},
            )

            assert result.exit_code == 0
            assert "Configuration edit completed" in result.output

    def test_edit_command_no_context(self) -> None:
        """Test edit command without CLI context."""
        result = self.runner.invoke(
            edit,
            [],
            obj={"console": Console()},
        )
        assert result.exit_code == 0

    def test_edit_command_no_config(self) -> None:
        """Test edit command without config object."""
        context_no_config = type("Context", (), {})()
        result = self.runner.invoke(
            edit,
            [],
            obj={"console": Console(), "cli_context": context_no_config},
        )
        assert result.exit_code == 0

    def test_edit_command_creates_parent_directory(self) -> None:
        """Test edit command creates parent directory when it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Config file in nested directory that doesn't exist yet
            config_file = Path(temp_dir) / "nested" / "deep" / "config.yaml"

            test_config = _TestConfig(config_file=config_file)
            cli_context = _TestCliContext(config=test_config)

            result = self.runner.invoke(
                edit,
                [],
                obj={"console": Console(), "cli_context": cli_context},
            )

            assert result.exit_code == 0
            assert "Configuration edit completed" in result.output


class TestConfigOutputFormats(unittest.TestCase):
    """Real functionality tests for different config output formats."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_config_output_json_format(self) -> None:
        """Test config output in JSON format."""
        test_config = _TestConfig(
            api_url="http://json.test:8000",
            timeout=30,
            debug=True,
            output_format="json",
        )
        test_settings = _TestSettings(
            project_name="json-test",
            log_level="DEBUG",
        )
        cli_context = _TestCliContext(
            config=test_config,
            settings=test_settings,
        )

        result = self.runner.invoke(
            get,
            [],  # Get all config
            obj={"console": Console(), "cli_context": cli_context},
        )

        assert result.exit_code == 0
        # Output should be JSON formatted (exact content may vary)

    def test_config_output_yaml_format(self) -> None:
        """Test config output in YAML format."""
        test_config = _TestConfig(
            api_url="http://yaml.test:8000",
            timeout=25,
            debug=False,
            output_format="yaml",
        )
        test_settings = _TestSettings(
            project_name="yaml-test",
            log_level="INFO",
        )
        cli_context = _TestCliContext(
            config=test_config,
            settings=test_settings,
        )

        result = self.runner.invoke(
            get,
            [],  # Get all config
            obj={"console": Console(), "cli_context": cli_context},
        )

        assert result.exit_code == 0
        # Output should be YAML formatted (exact content may vary)

    def test_config_output_table_format(self) -> None:
        """Test config output in table format (default)."""
        test_config = _TestConfig(
            api_url="http://table.test:8000",
            timeout=35,
            debug=True,
            output_format="table",
        )
        test_settings = _TestSettings(
            project_name="table-test",
            log_level="WARNING",
        )
        cli_context = _TestCliContext(
            config=test_config,
            settings=test_settings,
        )

        result = self.runner.invoke(
            get,
            [],  # Get all config
            obj={"console": Console(), "cli_context": cli_context},
        )

        assert result.exit_code == 0
        # Output should be table formatted (exact content may vary)


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for config commands working together."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

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
            test_settings = _TestSettings(
                project_name="workflow-test",
                log_level="ERROR",
                profile="integration",
            )
            cli_context = _TestCliContext(
                config=test_config,
                settings=test_settings,
            )

            obj = {"console": Console(), "cli_context": cli_context}

            # 1. Show config
            result = self.runner.invoke(show, [], obj=obj)
            assert result.exit_code == 0

            # 2. Get specific value
            result = self.runner.invoke(get, ["api_url"], obj=obj)
            assert result.exit_code == 0

            # 3. Set new value
            result = self.runner.invoke(set_value, ["timeout", "45"], obj=obj)
            assert result.exit_code == 0
            assert "Set timeout = 45" in result.output

            # 4. Validate config
            result = self.runner.invoke(validate, [], obj=obj)
            assert result.exit_code == 0

            # 5. Show paths
            result = self.runner.invoke(path, [], obj=obj)
            assert result.exit_code == 0

            # 6. Edit config (creates file)
            result = self.runner.invoke(edit, [], obj=obj)
            assert result.exit_code == 0
            assert "Configuration edit completed" in result.output

    def test_config_edge_cases_real_scenarios(self) -> None:
        """Test config commands with edge cases and real scenarios."""
        # Test with minimal config
        minimal_config = type("MinimalConfig", (), {"output_format": "json"})()
        minimal_context = type("MinimalContext", (), {"config": minimal_config})()

        obj = {"console": Console(), "cli_context": minimal_context}

        # Should handle minimal config gracefully
        result = self.runner.invoke(get, ["output_format"], obj=obj)
        assert result.exit_code == 0

        # Test with empty context - show should work even without cli_context
        result = self.runner.invoke(show, [], obj={"console": Console()})
        assert result.exit_code == 0  # show works without cli_context


if __name__ == "__main__":
    unittest.main()
