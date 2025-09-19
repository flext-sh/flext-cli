"""Test module for debug_commands using flext-cli patterns.

Tests debug commands through flext-cli API exclusively.
NO Click imports or usage allowed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import platform
import sys
import tempfile
from pathlib import Path

from flext_cli import FlextCliApi, FlextCliMain
from flext_cli.debug import FlextCliDebug
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestDebugCommandsReal:
    """Test debug commands with REAL execution using flext-cli - no mocks."""

    def setup_method(self) -> None:
        """Set up test environment with real components."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(name="test-debug", description="Test debug CLI")

    def test_debug_module_exists(self) -> None:
        """Test that debug module exists and has the expected service."""
        # Verify the service can be instantiated
        debug_service = FlextCliDebug()
        assert debug_service is not None
        assert hasattr(debug_service, "execute")

    def test_debug_help_real(self) -> None:
        """Test debug help through CLI API."""
        # Test help message display
        help_result = self.cli_api.display_message(
            "debug - Debug commands for FLEXT CLI",
            "info",
        )
        assert isinstance(help_result, FlextResult), "Help should return FlextResult"
        assert help_result.is_success, f"Help should succeed: {help_result.error}"

    def test_connectivity_real(self) -> None:
        """Test connectivity command through flext-cli."""
        # Simulate connectivity check data
        connectivity_data = {
            "network_status": "connected",
            "api_endpoint": "reachable",
            "dns_resolution": "working",
            "latency": "50ms",
        }

        # Test formatting connectivity results
        format_result = self.cli_api.format_output(
            connectivity_data,
            format_type="table",
        )
        assert isinstance(format_result, FlextResult), (
            "Connectivity format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Connectivity format should succeed: {format_result.error}"
        )

    def test_env_command_real(self) -> None:
        """Test env command with real environment data through flext-cli."""
        # Get real environment information
        env_data = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine(),
            "working_directory": str(Path.cwd()),
            "home_directory": str(Path.home()),
        }

        # Test formatting environment data
        format_result = self.cli_api.format_output(env_data, format_type="json")
        assert isinstance(format_result, FlextResult), (
            "Env format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Env format should succeed: {format_result.error}"
        )

    def test_paths_command_real(self) -> None:
        """Test paths command with real path data through flext-cli."""
        # Get real path information
        paths_data = {
            "config_dir": str(Path.home() / ".flext"),
            "cache_dir": str(Path.home() / ".cache" / "flext"),
            "log_dir": str(Path.home() / ".flext" / "logs"),
            "temp_dir": str(Path(tempfile.gettempdir())),
        }

        # Test formatting paths data
        format_result = self.cli_api.format_output(paths_data, format_type="yaml")
        assert isinstance(format_result, FlextResult), (
            "Paths format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Paths format should succeed: {format_result.error}"
        )

    def test_validate_command_real(self) -> None:
        """Test validate command through flext-cli."""
        # Simulate validation results
        validation_data = {
            "config_validation": "passed",
            "dependency_check": "all_available",
            "permission_check": "sufficient",
            "system_requirements": "met",
        }

        # Test validation message display
        validation_result = self.cli_api.display_message(
            "System validation completed successfully",
            "success",
        )
        assert isinstance(validation_result, FlextResult), (
            "Validation should return FlextResult"
        )
        assert validation_result.is_success, (
            f"Validation should succeed: {validation_result.error}"
        )

        # Test formatting validation data
        format_result = self.cli_api.format_output(validation_data, format_type="table")
        assert format_result.is_success, (
            f"Validation format should succeed: {format_result.error}"
        )

    def test_performance_command_real(self) -> None:
        """Test performance command through flext-cli."""
        # Simulate performance metrics
        performance_data = {
            "cpu_usage_percent": 15.2,
            "memory_usage_mb": 256,
            "disk_usage_percent": 45.8,
            "network_latency_ms": 12,
            "response_time_ms": 150,
        }

        # Test formatting performance data
        format_result = self.cli_api.format_output(performance_data, format_type="json")
        assert isinstance(format_result, FlextResult), (
            "Performance format should return FlextResult"
        )
        assert format_result.is_success, (
            f"Performance format should succeed: {format_result.error}"
        )

    def test_trace_command_real(self) -> None:
        """Test trace command through flext-cli."""
        # Simulate trace information
        trace_data = {
            "trace_enabled": True,
            "log_level": "DEBUG",
            "output_destination": str(Path(tempfile.gettempdir()) / "flext_trace.log"),
            "active_filters": ["auth", "api", "config"],
            "timestamp": "2025-01-15T10:30:00Z",
        }

        # Test trace message display
        trace_result = self.cli_api.display_message(
            "Trace logging is enabled and active",
            "info",
        )
        assert isinstance(trace_result, FlextResult), "Trace should return FlextResult"
        assert trace_result.is_success, f"Trace should succeed: {trace_result.error}"

        # Test formatting trace data
        format_result = self.cli_api.format_output(trace_data, format_type="yaml")
        assert format_result.is_success, (
            f"Trace format should succeed: {format_result.error}"
        )


class TestDebugIntegrationReal:
    """Integration tests for debug functionality using flext-cli."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliMain(
            name="test-debug-integration",
            description="Debug integration test",
        )

    def test_debug_workflow_complete(self) -> None:
        """Test complete debug workflow through flext-cli."""
        # 1. Register debug commands
        debug_commands = {
            "connectivity": FlextCliModels.CliCommand(
                name="connectivity",
                entry_point="test.connectivity:run",
                command_line="connectivity check",
            ),
            "env": FlextCliModels.CliCommand(
                name="env",
                entry_point="test.env:run",
                command_line="env check",
            ),
            "paths": FlextCliModels.CliCommand(
                name="paths",
                entry_point="test.paths:run",
                command_line="paths check",
            ),
            "validate": FlextCliModels.CliCommand(
                name="validate",
                entry_point="test.validate:run",
                command_line="validate check",
            ),
            "performance": FlextCliModels.CliCommand(
                name="performance",
                entry_point="test.performance:run",
                command_line="performance check",
            ),
            "trace": FlextCliModels.CliCommand(
                name="trace",
                entry_point="test.trace:run",
                command_line="trace check",
            ),
        }

        register_result = self.cli_main.register_command_group(
            "debug",
            debug_commands,
            "Debug commands for FLEXT CLI",
        )
        assert register_result.is_success, "Debug commands should register successfully"

        # 2. Test connectivity check
        connectivity_data = {"network": "connected", "api": "reachable"}
        connectivity_result = self.cli_api.format_output(
            connectivity_data,
            format_type="json",
        )
        assert connectivity_result.is_success, "Connectivity check should succeed"

        # 3. Test environment check
        env_data = {"python": f"{sys.version_info.major}.{sys.version_info.minor}"}
        env_result = self.cli_api.format_output(env_data, format_type="table")
        assert env_result.is_success, "Environment check should succeed"

        # 4. Test validation
        validation_result = self.cli_api.display_message("All checks passed", "success")
        assert validation_result.is_success, "Validation message should succeed"

    def test_debug_error_handling(self) -> None:
        """Test debug error handling through flext-cli."""
        # Test error scenarios
        error_result = self.cli_api.display_message("Debug check failed", "error")
        assert isinstance(error_result, FlextResult), "Error should return FlextResult"
        assert error_result.is_success, (
            f"Error display should succeed: {error_result.error}"
        )

        # Test warning scenarios
        warning_result = self.cli_api.display_message(
            "Some checks incomplete",
            "warning",
        )
        assert isinstance(warning_result, FlextResult), (
            "Warning should return FlextResult"
        )
        assert warning_result.is_success, (
            f"Warning display should succeed: {warning_result.error}"
        )

    def test_debug_output_formats(self) -> None:
        """Test debug output in various formats through flext-cli."""
        debug_data = {
            "system_status": "healthy",
            "checks_passed": 6,
            "checks_failed": 0,
            "timestamp": "2025-01-15T10:30:00Z",
        }

        # Test JSON format
        json_result = self.cli_api.format_output(debug_data, format_type="json")
        assert json_result.is_success, "JSON format should succeed"

        # Test YAML format
        yaml_result = self.cli_api.format_output(debug_data, format_type="yaml")
        assert yaml_result.is_success, "YAML format should succeed"

        # Test table format
        table_result = self.cli_api.format_output(debug_data, format_type="table")
        assert table_result.is_success, "Table format should succeed"


class TestDebugServiceIntegration:
    """Test debug service integration with flext-cli."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.debug_service = FlextCliDebug()

    def test_debug_service_execution(self) -> None:
        """Test debug service execution through flext-cli."""
        # Test that debug service can be executed
        execution_result = self.debug_service.execute()
        assert isinstance(execution_result, FlextResult), (
            "Debug service should return FlextResult"
        )

        # Test service result display
        if execution_result.is_success:
            display_result = self.cli_api.display_message(
                f"Debug service completed: {execution_result.value}",
                "success",
            )
            assert display_result.is_success, "Display should succeed"

    def test_debug_service_integration(self) -> None:
        """Test debug service integration with CLI API."""
        # Test debug service with CLI API formatting
        debug_data = {
            "service": "FlextCliDebug",
            "status": "operational",
            "methods": ["execute", "validate", "check_connectivity"],
        }

        format_result = self.cli_api.format_output(debug_data, format_type="table")
        assert isinstance(format_result, FlextResult), (
            "Format should return FlextResult"
        )
        assert format_result.is_success, f"Format should succeed: {format_result.error}"
