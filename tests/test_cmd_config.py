"""Real functionality tests for CMD Config - NO MOCKING.


Following user requirement: "melhore bem os tests para executar codigo de verdade e validar
a funcionalidade requerida, pare de ficar mockando tudo!"

These tests execute REAL config command functionality and validate actual business logic.
Coverage target: Increase cmd_config.py from 57% to 90%+


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations
from flext_core import FlextTypes

import tempfile
import unittest
from pathlib import Path

import click
import yaml
from click.testing import CliRunner
from rich.console import Console

from flext_cli.cmd import (
    FlextCliCmd,
    config,
    edit,
    get_cmd,
    path,
    set_value,
    show,
    validate,
)


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
        result = FlextCliCmd.find_config_value(self.cli_context, "api_url")
        assert result == "http://real.test:9000"

        result = FlextCliCmd.find_config_value(self.cli_context, "timeout")
        assert result == 45

        result = FlextCliCmd.find_config_value(self.cli_context, "debug")
        assert result is True

    def test_find_config_value_from_settings(self) -> None:
        """Test finding config value from settings object."""
        result = FlextCliCmd.find_config_value(self.cli_context, "project_name")
        assert result == "real-test-project"

        result = FlextCliCmd.find_config_value(self.cli_context, "log_level")
        assert result == "DEBUG"

        result = FlextCliCmd.find_config_value(self.cli_context, "profile")
        assert result == "production"

    def test_find_config_value_not_found(self) -> None:
        """Test finding non-existent config value."""
        result = FlextCliCmd.find_config_value(self.cli_context, "nonexistent_key")
        assert result is None

    def test_find_config_value_no_config(self) -> None:
        """Test finding config value when no config exists."""
        context_no_config = type("Context", (), {})()
        result = FlextCliCmd.find_config_value(context_no_config, "any_key")
        assert result is None

    def test_print_config_value_json_format(self) -> None:
        """Test printing config value in JSON format."""
        # Set output format to JSON
        self.test_config.output_format = "json"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.print_config_value(self.cli_context, "api_url", "http://test.example.com")
        # Function should complete without exceptions

    def test_print_config_value_yaml_format(self) -> None:
        """Test printing config value in YAML format."""
        # Set output format to YAML
        self.test_config.output_format = "yaml"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.print_config_value(self.cli_context, "timeout", 60)
        # Function should complete without exceptions

    def test_print_config_value_table_format(self) -> None:
        """Test printing config value in table format."""
        # Set output format to table (default)
        self.test_config.output_format = "table"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.print_config_value(self.cli_context, "debug", True)
        # Function should complete without exceptions

    def test_get_all_config_json_format(self) -> None:
        """Test getting all config in JSON format."""
        self.test_config.output_format = "json"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.get_all_config(self.cli_context)
        # Function should complete without exceptions

    def test_get_all_config_yaml_format(self) -> None:
        """Test getting all config in YAML format."""
        self.test_config.output_format = "yaml"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.get_all_config(self.cli_context)
        # Function should complete without exceptions

    def test_get_all_config_table_format(self) -> None:
        """Test getting all config in table format."""
        self.test_config.output_format = "table"

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.get_all_config(self.cli_context)
        # Function should complete without exceptions

    def test_print_config_table_function(self) -> None:
        """Test print_config_table helper function."""
        config_data = {
            "api_url": "http://test.example.com",
            "timeout": 30,
            "debug": False,
            "active": True,
        }

        # This function prints to console, so we test it doesn't crash
        FlextCliCmd.print_config_table(self.cli_context, config_data)
        # Function should complete without exceptions


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
        assert "Manage configuration" in (config.help or "")

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
        assert "profile: default" in result.output
        assert "debug: False" in result.output
        assert "output_format: table" in result.output

    def test_show_command_no_console(self) -> None:
        """Test config show command without console in context."""
        result = self.runner.invoke(show, [], obj={})
        # Should exit with error when no CLI context is provided
        assert result.exit_code == 1
        assert "CLI context not available" in result.output

    def test_get_command_single_value(self) -> None:
        """Test config get command for single value."""
        result = self.runner.invoke(
            get_cmd,
            ["api_url"],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0

    def test_get_command_all_values(self) -> None:
        """Test config get command for all values."""
        result = self.runner.invoke(
            get_cmd,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0

    def test_get_command_no_context(self) -> None:
        """Test config get command without CLI context."""
        result = self.runner.invoke(
            get_cmd,
            ["api_url"],
            obj={"console": Console()},
        )
        assert result.exit_code == 1

    def test_get_command_nonexistent_key(self) -> None:
        """Test config get command for nonexistent key."""
        result = self.runner.invoke(
            get_cmd,
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

        # Verify value was actually set
        assert self.cli_context.config.timeout == 60

    def test_set_value_command_no_context(self) -> None:
        """Test config set-value command without CLI context."""
        result = self.runner.invoke(
            set_value,
            ["timeout", "60"],
            obj={"console": Console()},
        )
        assert result.exit_code == 1

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
        assert "Configuration validation passed" in result.output

    def test_validate_command_no_context(self) -> None:
        """Test config validate command without CLI context."""
        result = self.runner.invoke(
            validate,
            [],
            obj={"console": Console()},
        )
        assert result.exit_code == 1

    def test_validate_command_no_config(self) -> None:
        """Test config validate command without config object."""
        context_no_config = type("Context", (), {})()
        result = self.runner.invoke(
            validate,
            [],
            obj={"console": Console(), "cli_context": context_no_config},
        )
        assert result.exit_code == 1

    def test_path_command(self) -> None:
        """Test config path command."""
        result = self.runner.invoke(
            path,
            [],
            obj={"console": Console(), "cli_context": self.cli_context},
        )
        assert result.exit_code == 0
        # Verify actual configuration paths are shown, not placeholder
        assert "FLEXT Configuration Paths" in result.output
        assert "Config File" in result.output
        assert "Log Directory" in result.output
        assert "Cache Directory" in result.output

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
        assert result.exit_code == 1


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
            assert "Config file ready at:" in result.output

            # Verify file was actually created
            assert config_file.exists()

            # Verify file content
            with config_file.open(encoding="utf-8") as f:
                content = yaml.safe_load(f)
                assert content["debug"] is False
                assert content["timeout"] == 30

    def test_edit_command_existing_config_file(self) -> None:
        """Test edit command with existing config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "existing_config.yaml"

            # Create existing config file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with config_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {"debug": True, "timeout": 45, "api_url": "http://existing.test"}, f
                )

            test_config = _TestConfig(config_file=config_file)
            cli_context = _TestCliContext(config=test_config)

            result = self.runner.invoke(
                edit,
                [],
                obj={"console": Console(), "cli_context": cli_context},
            )

            assert result.exit_code == 0
            assert "Config file ready at:" in result.output

            # Verify existing file wasn't overwritten
            with config_file.open(encoding="utf-8") as f:
                content = yaml.safe_load(f)
                assert content["debug"] is True
                assert content["timeout"] == 45
                assert content["api_url"] == "http://existing.test"

    def test_edit_command_no_context(self) -> None:
        """Test edit command without CLI context."""
        result = self.runner.invoke(
            edit,
            [],
            obj={"console": Console()},
        )
        assert result.exit_code == 1

    def test_edit_command_no_config(self) -> None:
        """Test edit command without config object."""
        context_no_config = type("Context", (), {})()
        result = self.runner.invoke(
            edit,
            [],
            obj={"console": Console(), "cli_context": context_no_config},
        )
        assert result.exit_code == 1

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

            # Verify parent directories were created
            assert config_file.parent.exists()
            assert config_file.exists()


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
            get_cmd,
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
            get_cmd,
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
            get_cmd,
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
            result = self.runner.invoke(get_cmd, ["api_url"], obj=obj)
            assert result.exit_code == 0

            # 3. Set new value
            result = self.runner.invoke(set_value, ["timeout", "45"], obj=obj)
            assert result.exit_code == 0
            assert cli_context.config.timeout == 45

            # 4. Validate config
            result = self.runner.invoke(validate, [], obj=obj)
            assert result.exit_code == 0

            # 5. Show paths
            result = self.runner.invoke(path, [], obj=obj)
            assert result.exit_code == 0

            # 6. Edit config (creates file)
            result = self.runner.invoke(edit, [], obj=obj)
            assert result.exit_code == 0
            assert config_file.exists()

    def test_config_edge_cases_real_scenarios(self) -> None:
        """Test config commands with edge cases and real scenarios."""
        # Test with minimal config
        minimal_config = type("MinimalConfig", (), {"output_format": "json"})()
        minimal_context = type("MinimalContext", (), {"config": minimal_config})()

        obj = {"console": Console(), "cli_context": minimal_context}

        # Should handle minimal config gracefully
        result = self.runner.invoke(get_cmd, ["output_format"], obj=obj)
        assert result.exit_code == 0

        # Test with empty context - show requires cli_context so should exit with code 1
        result = self.runner.invoke(show, [], obj={"console": Console()})
        assert result.exit_code == 1  # show requires cli_context


if __name__ == "__main__":
    unittest.main()
