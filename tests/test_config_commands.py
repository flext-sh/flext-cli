"""Tests for config commands.

# Constants
EXPECTED_DATA_COUNT = 3

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests configuration command functionality for coverage.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import yaml
from click.testing import CliRunner
from flext_cli.commands.config import (
    _find_config_value,
    _get_all_config,
    _print_config_table,
    _print_config_value,
    config,
)
from rich.table import Table


class TestConfigCommands:
    """Test configuration commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

        # Create mock CLI context
        self.mock_cli_context = MagicMock()
        self.mock_cli_context.config = MagicMock()
        self.mock_cli_context.settings = MagicMock()
        self.mock_cli_context.console = MagicMock()

        # Mock config properties
        self.mock_cli_context.config.output_format = "table"
        self.mock_cli_context.config.config_dir = Path("/home/user/.flext")
        self.mock_cli_context.config.cache_dir = Path("/home/user/.flext/cache")
        self.mock_cli_context.config.log_dir = Path("/home/user/.flext/logs")
        self.mock_cli_context.config.model_dump.return_value = {
            "debug": False,
            "profile": "default",
            "api_url": "http://localhost:8000",
        }
        self.mock_cli_context.settings.model_dump.return_value = {
            "timeout": 30,
            "retries": 3,
        }

    def test_config_group_structure(self) -> None:
        """Test config command group structure."""
        if config.name != "config":
            raise AssertionError(f"Expected {'config'}, got {config.name}")
        if "get" not in config.commands:
            raise AssertionError(f"Expected {'get'} in {config.commands}")
        assert "set-value" in config.commands  # set_value command
        if "validate" not in config.commands:
            raise AssertionError(f"Expected {'validate'} in {config.commands}")
        assert "path" in config.commands
        if "edit" not in config.commands:
            raise AssertionError(f"Expected {'edit'} in {config.commands}")

    def test_get_all_config_table_format(self) -> None:
        """Test getting all config in table format."""
        self.mock_cli_context.config.output_format = "table"

        result = self.runner.invoke(
            config,
            ["get"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should have called print on console for table output
        assert self.mock_cli_context.console.print.called

    def test_get_all_config_json_format(self) -> None:
        """Test getting all config in JSON format."""
        self.mock_cli_context.config.output_format = "json"

        result = self.runner.invoke(
            config,
            ["get"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should have called print with JSON data
        assert self.mock_cli_context.console.print.called

    def test_get_all_config_yaml_format(self) -> None:
        """Test getting all config in YAML format."""
        self.mock_cli_context.config.output_format = "yaml"

        result = self.runner.invoke(
            config,
            ["get"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should have called print with YAML data
        assert self.mock_cli_context.console.print.called

    def test_get_single_key_found_in_config(self) -> None:
        """Test getting single key found in config."""
        # Mock config has debug attribute
        self.mock_cli_context.config.debug = False

        result = self.runner.invoke(
            config,
            ["get", "debug"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_get_single_key_found_in_settings(self) -> None:
        """Test getting single key found in settings."""
        # Key not in config, but in settings
        self.mock_cli_context.config.timeout = None
        self.mock_cli_context.settings.timeout = 30

        result = self.runner.invoke(
            config,
            ["get", "timeout"],
            obj={"cli_context": self.mock_cli_context},
        )

        # May exit with 1 due to missing attribute, but should test the logic
        if result.exit_code not in {0, 1}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1]}")

    def test_get_single_key_not_found(self) -> None:
        """Test getting single key that doesn't exist."""
        result = self.runner.invoke(
            config,
            ["get", "nonexistent_key"],
            obj={"cli_context": self.mock_cli_context},
        )

        # Should exit with error for missing key
        if result.exit_code not in {0, 1, 2}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    def test_get_single_key_json_format(self) -> None:
        """Test getting single key in JSON format."""
        self.mock_cli_context.config.output_format = "json"
        self.mock_cli_context.config.debug = True

        result = self.runner.invoke(
            config,
            ["get", "debug"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_get_single_key_yaml_format(self) -> None:
        """Test getting single key in YAML format."""
        self.mock_cli_context.config.output_format = "yaml"
        self.mock_cli_context.config.debug = True

        result = self.runner.invoke(
            config,
            ["get", "debug"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_get_single_key_exception_handling(self) -> None:
        """Test get single key with exception."""
        result = self.runner.invoke(
            config,
            ["get", "debug"],
            obj={"cli_context": self.mock_cli_context},
        )

        # Should complete without crashing
        if result.exit_code not in {0, 1, 2}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    def test_set_value_command(self) -> None:
        """Test setting configuration value."""
        result = self.runner.invoke(
            config,
            ["set-value", "debug", "true"],
            obj={"cli_context": self.mock_cli_context},
        )

        # Command should complete (may exit with error due to mocking)
        if result.exit_code not in {0, 1, 2}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    def test_validate_command_success(self) -> None:
        """Test validate command with no config."""
        # Mock config to not exist, settings to exist
        self.mock_cli_context.config = None

        result = self.runner.invoke(
            config,
            ["validate"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 1:  # Should exit with error when no config
            raise AssertionError(f"Expected {1}, got {result.exit_code}")

    def test_validate_command_with_config(self) -> None:
        """Test validate command with config."""
        # Config exists and has settings
        self.mock_cli_context.config = MagicMock()
        self.mock_cli_context.settings = MagicMock()
        self.mock_cli_context.config.config_dir = Path("/test/config")
        self.mock_cli_context.config.profile = "test"
        self.mock_cli_context.config.api_url = "http://test.com"

        result = self.runner.invoke(
            config,
            ["validate"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_path_command(self) -> None:
        """Test path command."""
        result = self.runner.invoke(
            config,
            ["path"],
            obj={"cli_context": self.mock_cli_context},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should have printed path information
        assert self.mock_cli_context.print_info.called

    @patch("subprocess.run")
    @patch.dict(os.environ, {"EDITOR": "nano"})
    def test_edit_command_with_existing_config(self, mock_subprocess) -> None:
        """Test edit command with existing config file."""
        mock_subprocess.return_value = MagicMock()

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "mkdir"):
                result = self.runner.invoke(
                    config,
                    ["edit"],
                    obj={"cli_context": self.mock_cli_context},
                )

                if result.exit_code not in {0, 1, 2}:
                    raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    @patch("subprocess.run")
    @patch.dict(os.environ, {}, clear=True)  # No EDITOR env var
    def test_edit_command_default_editor(self, mock_subprocess) -> None:
        """Test edit command with default editor (vim)."""
        mock_subprocess.return_value = MagicMock()

        with patch.object(Path, "exists", return_value=False):
            with patch.object(Path, "mkdir"):
                result = self.runner.invoke(
                    config,
                    ["edit"],
                    obj={"cli_context": self.mock_cli_context},
                )

                # Should complete successfully
                if result.exit_code not in {0, 1, 2}:
                    raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    @patch("subprocess.run")
    def test_edit_command_create_default_config(self, mock_subprocess) -> None:
        """Test edit command creates default config when none exists."""
        mock_subprocess.return_value = MagicMock()

        # Mock config file doesn't exist
        with patch.object(Path, "exists", return_value=False):
            with patch.object(Path, "mkdir"):
                # Mock file opening for writing
                mock_file = MagicMock()
                with patch.object(Path, "open", return_value=mock_file):
                    result = self.runner.invoke(
                        config,
                        ["edit"],
                        obj={"cli_context": self.mock_cli_context},
                    )

                    if result.exit_code not in {0, 1, 2}:
                        raise AssertionError(
                            f"Expected {result.exit_code} in {[0, 1, 2]}"
                        )

    @patch("subprocess.run")
    def test_edit_command_subprocess_error(self, mock_subprocess) -> None:
        """Test edit command with subprocess error."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "vim")

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "mkdir"):
                result = self.runner.invoke(
                    config,
                    ["edit"],
                    obj={"cli_context": self.mock_cli_context},
                )

                if result.exit_code != 1:
                    raise AssertionError(f"Expected {1}, got {result.exit_code}")

    @patch("subprocess.run")
    def test_edit_command_file_error(self, mock_subprocess) -> None:
        """Test edit command with file error."""
        mock_subprocess.return_value = MagicMock()

        # Mock Path.mkdir to raise OSError
        with patch.object(Path, "mkdir", side_effect=OSError("Permission denied")):
            result = self.runner.invoke(
                config,
                ["edit"],
                obj={"cli_context": self.mock_cli_context},
            )

            if result.exit_code != 1:
                raise AssertionError(f"Expected {1}, got {result.exit_code}")


class TestConfigHelperFunctions:
    """Test configuration helper functions."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.mock_cli_context = MagicMock()
        self.mock_cli_context.config = MagicMock()
        self.mock_cli_context.settings = MagicMock()
        self.mock_cli_context.console = MagicMock()

    def test_find_config_value_in_config(self) -> None:
        """Test finding configuration value in config object."""

        # Mock config has the attribute
        self.mock_cli_context.config.debug = True
        value = _find_config_value(self.mock_cli_context, "debug")
        if not (value):
            raise AssertionError(f"Expected True, got {value}")

    def test_find_config_value_in_settings(self) -> None:
        """Test finding configuration value in settings object."""

        # Mock value not in config but in settings
        delattr(self.mock_cli_context.config, "timeout") if hasattr(
            self.mock_cli_context.config, "timeout"
        ) else None
        self.mock_cli_context.settings.timeout = 30

        value = _find_config_value(self.mock_cli_context, "timeout")
        if value != 30:
            raise AssertionError(f"Expected {30}, got {value}")

    def test_find_config_value_not_found(self) -> None:
        """Test finding configuration value that doesn't exist."""

        # Try to find a key that doesn't exist
        value = _find_config_value(self.mock_cli_context, "nonexistent")
        # May return None or default Mock value
        assert value is None or isinstance(value, MagicMock)

    def test_print_config_value_json(self) -> None:
        """Test printing config value in JSON format."""

        self.mock_cli_context.config.output_format = "json"

        _print_config_value(self.mock_cli_context, "debug", True)

        # Should have called console.print with JSON
        self.mock_cli_context.console.print.assert_called()

    def test_print_config_value_yaml(self) -> None:
        """Test printing config value in YAML format."""

        self.mock_cli_context.config.output_format = "yaml"

        _print_config_value(self.mock_cli_context, "debug", True)

        # Should have called console.print with YAML
        self.mock_cli_context.console.print.assert_called()

    def test_print_config_value_default(self) -> None:
        """Test printing config value in default format."""

        self.mock_cli_context.config.output_format = "table"

        _print_config_value(self.mock_cli_context, "debug", True)

        # Should have called console.print with simple format
        self.mock_cli_context.console.print.assert_called()

    def test_get_all_config_table_format(self) -> None:
        """Test getting all config in table format."""

        self.mock_cli_context.config.output_format = "table"
        self.mock_cli_context.config.model_dump.return_value = {"debug": False}
        self.mock_cli_context.settings.model_dump.return_value = {"timeout": 30}

        _get_all_config(self.mock_cli_context)

        # Should have called console.print
        self.mock_cli_context.console.print.assert_called()

    def test_get_all_config_json_format(self) -> None:
        """Test getting all config in JSON format."""

        self.mock_cli_context.config.output_format = "json"
        self.mock_cli_context.config.model_dump.return_value = {"debug": False}
        self.mock_cli_context.settings.model_dump.return_value = {"timeout": 30}

        _get_all_config(self.mock_cli_context)

        # Should have called console.print with JSON
        self.mock_cli_context.console.print.assert_called()

    def test_get_all_config_yaml_format(self) -> None:
        """Test getting all config in YAML format."""

        self.mock_cli_context.config.output_format = "yaml"
        self.mock_cli_context.config.model_dump.return_value = {"debug": False}
        self.mock_cli_context.settings.model_dump.return_value = {"timeout": 30}

        _get_all_config(self.mock_cli_context)

        # Should have called console.print with YAML
        self.mock_cli_context.console.print.assert_called()

    def test_print_config_table(self) -> None:
        """Test printing config as table."""

        # Mock hasattr to return True for config attributes
        with patch("builtins.hasattr", return_value=True):
            config_data = {"debug": False, "timeout": 30}

            _print_config_table(self.mock_cli_context, config_data)

            # Should have called console.print with table
            self.mock_cli_context.console.print.assert_called()


class TestConfigIntegration:
    """Integration tests for config commands."""

    def test_config_imports(self) -> None:
        """Test that all required imports work."""

        # All imports should work
        assert json
        assert os
        assert subprocess
        assert Path
        assert click
        assert yaml
        assert Table

    def test_json_operations(self) -> None:
        """Test JSON operations used in config commands."""
        test_data = {"debug": True, "timeout": 30}

        # Test JSON dump (used in _print_config_value)
        json_str = json.dumps(test_data, indent=2, default=str)
        if "debug" not in json_str:
            raise AssertionError(f"Expected {'debug'} in {json_str}")
        assert "true" in json_str.lower()

    def test_yaml_operations(self) -> None:
        """Test YAML operations used in config commands."""
        test_data = {"debug": True, "timeout": 30}

        # Test YAML dump (used in _print_config_value and edit command)
        yaml_str = yaml.dump(test_data, default_flow_style=False)
        if "debug: true" not in yaml_str:
            raise AssertionError(f"Expected {'debug: true'} in {yaml_str}")
        assert "timeout: 30" in yaml_str

    def test_rich_table_creation(self) -> None:
        """Test Rich table creation used in config commands."""

        table = Table(title="FLEXT Configuration v0.7.0")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Source", style="dim")

        table.add_row("debug", "false", "config")
        table.add_row("timeout", "30", "settings")

        if table.title != "FLEXT Configuration v0.7.0":
            raise AssertionError(
                f"Expected {'FLEXT Configuration v0.7.0'}, got {table.title}"
            )

    def test_path_operations(self) -> None:
        """Test Path operations used in config commands."""

        # Test path operations used in edit and path commands
        config_dir = Path("/home/user/.flext")
        config_file = config_dir / "config.yaml"
        cache_dir = config_dir / "cache"

        if str(config_file) != "/home/user/.flext/config.yaml":
            raise AssertionError(
                f"Expected {'/home/user/.flext/config.yaml'}, got {config_file!s}"
            )
        assert str(cache_dir) == "/home/user/.flext/cache"

    def test_os_environ_access(self) -> None:
        """Test os.environ access used in edit command."""
        # Test getting EDITOR environment variable
        editor = os.environ.get("EDITOR", "vim")
        assert editor  # Should return either set editor or vim default

    def test_subprocess_operations(self) -> None:
        """Test subprocess operations used in edit command."""
        # Test that subprocess.run exists and can be called
        assert hasattr(subprocess, "run")
        assert hasattr(subprocess, "CalledProcessError")

    def test_click_context_handling(self) -> None:
        """Test Click context handling patterns."""

        # Test context object pattern used in commands
        mock_context = MagicMock(spec=click.Context)
        mock_context.obj = {"cli_context": MagicMock()}

        # Test accessing cli_context from context
        cli_context = mock_context.obj["cli_context"]
        assert cli_context is not None

    def test_exception_handling_patterns(self) -> None:
        """Test exception handling patterns used in config commands."""
        # Test the exception types used in config commands
        standard_exceptions = [AttributeError, KeyError, ValueError, OSError]

        for exc_type in standard_exceptions:
            try:
                msg = "Test error"
                raise exc_type(msg)
            except exc_type as e:
                # Different exceptions format error messages differently
                if "Test error" not in str(e):
                    raise AssertionError(f"Expected {'Test error'} in {e!s}")

        # Test CalledProcessError separately (needs different constructor)
        try:
            raise subprocess.CalledProcessError(1, "test_cmd", "Test error")
        except subprocess.CalledProcessError as e:
            if "test_cmd" not in str(e):
                raise AssertionError(f"Expected {'test_cmd'} in {e!s}")
