"""Test module for cmd_debug using flext-cli patterns.

Tests debug commands through flext-cli API exclusively.
NO Click imports or usage allowed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flext_cli import FlextCliApi, FlextCliMain
from flext_cli.client import FlextCliClient as FlextApiClient
from flext_cli.config import FlextCliConfig
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestDebugBasicFunctions(unittest.TestCase):
    """Test basic debug functions and utilities using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-debug", description="Test debug CLI")

    def test_config_creation(self) -> None:
        """Test FlextCliConfig creation returns proper configuration."""
        config = FlextCliConfig()

        # Verify config has required attributes
        assert hasattr(config, "api_url")
        assert hasattr(config, "timeout_seconds")
        assert hasattr(config, "config_dir")

        # Verify config is properly initialized
        assert isinstance(config.config_dir, Path)

    def test_cli_client_creation(self) -> None:
        """Test FlextApiClient can be created."""
        client = FlextApiClient()
        assert client is not None
        assert hasattr(client, "base_url")

    def test_debug_command_registration(self) -> None:
        """Test debug command group registration through flext-cli."""
        # Create debug command group
        debug_commands = {
            "connectivity": FlextCliModels.CliCommand(
                name="connectivity",
                entry_point="debug.connectivity:run",
                command_line="connectivity check",
            ),
            "performance": FlextCliModels.CliCommand(
                name="performance",
                entry_point="debug.performance:run",
                command_line="performance check",
            ),
            "validate": FlextCliModels.CliCommand(
                name="validate",
                entry_point="debug.validate:run",
                command_line="validate check",
            ),
            "trace": FlextCliModels.CliCommand(
                name="trace",
                entry_point="debug.trace:run",
                command_line="trace check",
            ),
            "env": FlextCliModels.CliCommand(
                name="env",
                entry_point="debug.env:run",
                command_line="env check",
            ),
            "paths": FlextCliModels.CliCommand(
                name="paths",
                entry_point="debug.paths:run",
                command_line="paths check",
            ),
        }

        # Register debug command group
        register_result = self.cli_main.register_command_group(
            "debug", debug_commands, "Debug commands for FLEXT CLI",
        )

        assert isinstance(register_result, FlextResult), "Registration should return FlextResult"
        assert register_result.is_success, f"Registration should succeed: {register_result.error}"


class TestDebugCommands(unittest.TestCase):
    """Test debug CLI commands using flext-cli patterns."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()

    def test_env_command_functionality(self) -> None:
        """Test env command functionality through flext-cli."""
        # Simulate environment data
        env_data = {
            "PYTHON_VERSION": "3.13.0",
            "PLATFORM": "Linux",
            "HOME": str(Path.home()),
            "PWD": str(Path.cwd()),
        }

        # Test formatting environment data
        format_result = self.cli_api.format_output(env_data, format_type="table")
        assert isinstance(format_result, FlextResult), "Format should return FlextResult"
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_paths_command_functionality(self) -> None:
        """Test paths command functionality through flext-cli."""
        # Get real path information
        paths_data = {
            "config_dir": str(Path.home() / ".flext"),
            "cache_dir": str(Path.home() / ".cache" / "flext"),
            "temp_dir": str(Path(tempfile.gettempdir())),
            "current_dir": str(Path.cwd()),
        }

        # Test formatting paths data
        format_result = self.cli_api.format_output(paths_data, format_type="yaml")
        assert isinstance(format_result, FlextResult), "Format should return FlextResult"
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_validate_command_functionality(self) -> None:
        """Test validate command functionality through flext-cli."""
        # Simulate validation results
        validation_data = {
            "config_valid": True,
            "dependencies_available": True,
            "permissions_ok": True,
            "tests_passed": True,
        }

        # Test formatting validation data
        format_result = self.cli_api.format_output(validation_data, format_type="json")
        assert isinstance(format_result, FlextResult), "Format should return FlextResult"
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_trace_command_functionality(self) -> None:
        """Test trace command functionality through flext-cli."""
        # Simulate trace information
        trace_data = {
            "enabled": True,
            "log_level": "DEBUG",
            "output_file": str(Path(tempfile.gettempdir()) / "flext_trace.log"),
            "filters": ["auth", "config", "api"],
        }

        # Test formatting trace data
        format_result = self.cli_api.format_output(trace_data, format_type="table")
        assert isinstance(format_result, FlextResult), "Format should return FlextResult"
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_check_command_functionality(self) -> None:
        """Test check command functionality through flext-cli."""
        # Simulate system check results
        check_data = {
            "system_health": "good",
            "api_connectivity": "connected",
            "database_status": "available",
            "cache_status": "operational",
        }

        # Test displaying check results
        display_result = self.cli_api.display_message(
            f"System check completed: {check_data['system_health']}", "success",
        )
        assert isinstance(display_result, FlextResult), "Display should return FlextResult"
        assert display_result.is_success, f"Display should succeed: {display_result.error}"


class TestDebugOutputFormats(unittest.TestCase):
    """Test debug command output formats using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()

    def test_debug_output_json_format(self) -> None:
        """Test debug output in JSON format."""
        debug_data = {
            "timestamp": "2025-01-15T10:30:00Z",
            "command": "debug",
            "status": "success",
            "details": {"checks": 5, "passed": 5, "failed": 0},
        }

        format_result = self.cli_api.format_output(debug_data, format_type="json")
        assert isinstance(format_result, FlextResult), "JSON format should return FlextResult"
        assert format_result.is_success, f"JSON format should succeed: {format_result.error}"

    def test_debug_output_yaml_format(self) -> None:
        """Test debug output in YAML format."""
        debug_data = {
            "environment": {
                "python": "3.13.0",
                "platform": "linux",
                "architecture": "x86_64",
            },
            "paths": {
                "config": "/home/user/.flext",
                "cache": "/home/user/.cache/flext",
            },
        }

        format_result = self.cli_api.format_output(debug_data, format_type="yaml")
        assert isinstance(format_result, FlextResult), "YAML format should return FlextResult"
        assert format_result.is_success, f"YAML format should succeed: {format_result.error}"

    def test_debug_output_table_format(self) -> None:
        """Test debug output in table format."""
        debug_data = {
            "Component": "Status",
            "API": "Connected",
            "Database": "Available",
            "Cache": "Operational",
            "Configuration": "Valid",
        }

        format_result = self.cli_api.format_output(debug_data, format_type="table")
        assert isinstance(format_result, FlextResult), "Table format should return FlextResult"
        assert format_result.is_success, f"Table format should succeed: {format_result.error}"


class TestDebugIntegration(unittest.TestCase):
    """Integration tests for debug commands using flext-cli."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-debug-integration", description="Debug integration test")
        self.config = FlextCliConfig()

    def test_debug_workflow_complete(self) -> None:
        """Test complete debug workflow through flext-cli."""
        # 1. Register debug commands
        debug_commands = {
            "env": FlextCliModels.CliCommand(
                name="env",
                entry_point="debug.env:run",
                command_line="env check",
            ),
            "paths": FlextCliModels.CliCommand(
                name="paths",
                entry_point="debug.paths:run",
                command_line="paths check",
            ),
            "validate": FlextCliModels.CliCommand(
                name="validate",
                entry_point="debug.validate:run",
                command_line="validate check",
            ),
            "check": FlextCliModels.CliCommand(
                name="check",
                entry_point="debug.check:run",
                command_line="health check",
            ),
        }

        register_result = self.cli_main.register_command_group(
            "debug", debug_commands, "Debug commands",
        )
        assert register_result.is_success, "Debug command registration should succeed"

        # 2. Test environment check
        env_data = {"python_version": "3.13.0", "os": "linux"}
        env_result = self.cli_api.format_output(env_data, format_type="json")
        assert env_result.is_success, "Environment format should succeed"

        # 3. Test paths check
        paths_data = {"config_dir": str(self.config.config_dir)}
        paths_result = self.cli_api.format_output(paths_data, format_type="table")
        assert paths_result.is_success, "Paths format should succeed"

        # 4. Test validation
        validation_result = self.cli_api.display_message("All validations passed", "success")
        assert validation_result.is_success, "Validation message should succeed"

    def test_debug_error_scenarios(self) -> None:
        """Test debug error scenarios through flext-cli."""
        # Test error message display
        error_result = self.cli_api.display_message("Debug check failed", "error")
        assert isinstance(error_result, FlextResult), "Error should return FlextResult"
        assert error_result.is_success, f"Error display should succeed: {error_result.error}"

        # Test warning message display
        warning_result = self.cli_api.display_message("Some checks incomplete", "warning")
        assert isinstance(warning_result, FlextResult), "Warning should return FlextResult"
        assert warning_result.is_success, f"Warning display should succeed: {warning_result.error}"

    def test_debug_file_operations(self) -> None:
        """Test debug file operations through flext-cli."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Simulate debug file data
            debug_file_data = {
                "temp_directory": str(temp_path),
                "permissions": "read/write",
                "available_space": "500MB",
            }

            # Test formatting file information
            file_result = self.cli_api.format_output(debug_file_data, format_type="yaml")
            assert isinstance(file_result, FlextResult), "File format should return FlextResult"
            assert file_result.is_success, f"File format should succeed: {file_result.error}"


if __name__ == "__main__":
    unittest.main()
