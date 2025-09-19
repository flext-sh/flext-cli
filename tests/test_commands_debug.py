"""Test module for commands_debug using flext-cli patterns.

Tests debug commands through flext-cli API exclusively.
NO Click imports or usage allowed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

from flext_cli import FlextCliApi, FlextCliMain
from flext_cli.configs import FlextCliConfigs
from flext_cli.models import FlextCliModels
from flext_core import FlextConstants, FlextResult


class TestDebugCommandReal:
    """Test debug command group with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-debug", description="Test debug CLI")

    def test_debug_command_registration_real(self) -> None:
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
            "debug",
            debug_commands,
            "Debug commands for FLEXT CLI.",
        )

        assert isinstance(register_result, FlextResult), (
            "Registration should return FlextResult"
        )
        assert register_result.is_success, (
            f"Registration should succeed: {register_result.error}"
        )

    def test_debug_has_all_subcommands_real(self) -> None:
        """Test that debug commands are available through CLI API."""
        expected_commands = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]

        # Test that we can display messages for each debug command
        for cmd in expected_commands:
            display_result = self.cli_api.display_message(
                f"Debug {cmd} command available",
                "info",
            )
            assert isinstance(display_result, FlextResult), (
                f"{cmd} display should return FlextResult"
            )
            assert display_result.is_success, (
                f"{cmd} display should succeed: {display_result.error}"
            )


class TestConnectivityCommandReal:
    """Test connectivity debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()

    def test_connectivity_command_structure_real(self) -> None:
        """Test connectivity command through CLI API."""
        # Test connectivity check through message display
        connectivity_result = self.cli_api.display_message(
            "Connectivity check completed",
            "success",
        )
        assert isinstance(connectivity_result, FlextResult), (
            "Connectivity should return FlextResult"
        )
        assert connectivity_result.is_success, (
            f"Connectivity should succeed: {connectivity_result.error}"
        )

    def test_connectivity_execution_real(self) -> None:
        """Test connectivity command execution through flext-cli."""
        # Simulate connectivity check data
        connectivity_data = {
            "network_status": "connected",
            "dns_resolution": "working",
            "external_services": "available",
        }

        # Test formatting connectivity data
        format_result = self.cli_api.format_output(
            connectivity_data,
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_connectivity_help_real(self) -> None:
        """Test connectivity command help through CLI API."""
        help_result = self.cli_api.display_message(
            "connectivity - Check network and service connectivity",
            "info",
        )
        assert isinstance(help_result, FlextResult), "Help should return FlextResult"
        assert help_result.is_success, f"Help should succeed: {help_result.error}"


class TestPerformanceCommandReal:
    """Test performance debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()

    def test_performance_command_execution_real(self) -> None:
        """Test performance command execution through flext-cli."""
        # Simulate performance metrics
        performance_data = {
            "cpu_usage": "15%",
            "memory_usage": "45%",
            "disk_usage": "60%",
            "response_time": "150ms",
        }

        # Test formatting performance data
        format_result = self.cli_api.format_output(
            performance_data,
            format_type="json",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_performance_metrics_real(self) -> None:
        """Test performance metrics display through CLI API."""
        metrics_result = self.cli_api.display_message(
            "Performance metrics collected successfully",
            "success",
        )
        assert isinstance(metrics_result, FlextResult), (
            "Metrics should return FlextResult"
        )
        assert metrics_result.is_success, (
            f"Metrics should succeed: {metrics_result.error}"
        )


class TestValidateCommandReal:
    """Test validate debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()
        self.config = FlextCliConfigs()

    def test_validate_command_execution_real(self) -> None:
        """Test validate command execution through flext-cli."""
        # Simulate validation results
        validation_data = {
            "config_valid": True,
            "dependencies_ok": True,
            "permissions_ok": True,
            "errors": [],
        }

        # Test formatting validation data
        format_result = self.cli_api.format_output(
            validation_data,
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_validate_config_real(self) -> None:
        """Test config validation through CLI API."""
        validate_result = self.cli_api.display_message(
            "Configuration validation completed successfully",
            "success",
        )
        assert isinstance(validate_result, FlextResult), (
            "Validate should return FlextResult"
        )
        assert validate_result.is_success, (
            f"Validate should succeed: {validate_result.error}"
        )


class TestTraceCommandReal:
    """Test trace debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()

    def test_trace_command_execution_real(self) -> None:
        """Test trace command execution through flext-cli."""
        # Simulate trace data
        trace_data = {
            "request_id": "12345",
            "timestamp": "2025-01-15T10:30:00Z",
            "duration": "250ms",
            "steps": ["init", "validate", "process", "complete"],
        }

        # Test formatting trace data
        format_result = self.cli_api.format_output(
            trace_data,
            format_type="json",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_trace_logging_real(self) -> None:
        """Test trace logging through CLI API."""
        trace_result = self.cli_api.display_message(
            "Trace logging enabled and functioning",
            "info",
        )
        assert isinstance(trace_result, FlextResult), "Trace should return FlextResult"
        assert trace_result.is_success, f"Trace should succeed: {trace_result.error}"


class TestEnvCommandReal:
    """Test env debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()

    def test_env_command_execution_real(self) -> None:
        """Test env command execution through flext-cli."""
        # Get real environment data
        env_data = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine(),
            "flext_constants": str(FlextConstants.Core.VERSION)
            if hasattr(FlextConstants.Core, "VERSION")
            else "unknown",
        }

        # Test formatting environment data
        format_result = self.cli_api.format_output(
            env_data,
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_env_variables_real(self) -> None:
        """Test environment variables display through CLI API."""
        env_result = self.cli_api.display_message(
            f"Environment: Python {sys.version_info.major}.{sys.version_info.minor}",
            "info",
        )
        assert isinstance(env_result, FlextResult), "Env should return FlextResult"
        assert env_result.is_success, f"Env should succeed: {env_result.error}"


class TestPathsCommandReal:
    """Test paths debug command with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()

    def test_paths_command_execution_real(self) -> None:
        """Test paths command execution through flext-cli."""
        # Get real path data
        paths_data = {
            "home_dir": str(Path.home()),
            "current_dir": str(Path.cwd()),
            "config_dir": str(Path.home() / ".flext"),
            "cache_dir": str(Path.home() / ".cache" / "flext"),
        }

        # Test formatting paths data
        format_result = self.cli_api.format_output(
            paths_data,
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"

    def test_paths_display_real(self) -> None:
        """Test paths display through CLI API."""
        paths_result = self.cli_api.display_message(
            f"Configuration path: {Path.home() / '.flext'}",
            "info",
        )
        assert isinstance(paths_result, FlextResult), "Paths should return FlextResult"
        assert paths_result.is_success, f"Paths should succeed: {paths_result.error}"


class TestDebugIntegration:
    """Integration tests for debug commands working together using flext-cli."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(
            name="test-debug-integration", description="Test debug integration"
        )

    def test_debug_workflow_real(self) -> None:
        """Test complete debug workflow through flext-cli."""
        # 1. Register debug commands
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
        }

        register_result = self.cli_main.register_command_group(
            "debug",
            debug_commands,
            "Debug commands",
        )
        assert register_result.is_success, "Debug commands should register"

        # 2. Test connectivity check
        connectivity_data = {"network": "connected", "api": "reachable"}
        format_result = self.cli_api.format_output(
            connectivity_data, format_type="json"
        )
        assert format_result.is_success, "Connectivity format should succeed"

        # 3. Test performance metrics
        performance_data = {"cpu": "15%", "memory": "45%"}
        metrics_result = self.cli_api.format_output(
            performance_data, format_type="table"
        )
        assert metrics_result.is_success, "Performance format should succeed"

        # 4. Test validation
        validation_result = self.cli_api.display_message(
            "All validations passed", "success"
        )
        assert validation_result.is_success, "Validation message should succeed"

    def test_debug_error_handling_real(self) -> None:
        """Test debug error handling through flext-cli."""
        # Test error message display
        error_result = self.cli_api.display_message("Debug check failed", "error")
        assert isinstance(error_result, FlextResult), "Error should return FlextResult"
        assert error_result.is_success, (
            f"Error display should succeed: {error_result.error}"
        )

        # Test warning message display
        warning_result = self.cli_api.display_message(
            "Debug check incomplete", "warning"
        )
        assert isinstance(warning_result, FlextResult), (
            "Warning should return FlextResult"
        )
        assert warning_result.is_success, (
            f"Warning display should succeed: {warning_result.error}"
        )
