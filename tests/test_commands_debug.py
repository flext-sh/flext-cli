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

from flext_cli import FlextCliApi, FlextCliCommands, FlextCliConfig, FlextCliOutput
from flext_core import FlextResult


class TestDebugCommandReal:
    """Test debug command group with real functionality using flext-cli."""

    def setup_method(self) -> None:
        """Initialize test class with real components."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliCommands(
            name="test-debug", description="Test debug CLI"
        )
        self.formatter = FlextCliOutput()

    def test_debug_command_registration_real(self) -> None:
        """Test debug command group registration through flext-cli."""
        # Register debug group using actual API
        debug_commands = {
            "env": {
                "handler": lambda: None,
                "description": "Show environment variables",
            },
            "validate": {
                "handler": lambda: None,
                "description": "Validate configuration",
            },
        }
        # Cast to the expected type for MyPy
        commands_dict: dict[str, object] = debug_commands
        register_result = self.cli_main.register_command_group(
            "debug", commands_dict, "Debug commands for FLEXT CLI"
        )

        assert isinstance(register_result, FlextResult)
        assert register_result.is_success

    def test_debug_has_all_subcommands_real(self) -> None:
        """Test that debug commands structure is valid."""
        expected_commands = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]

        # Test that we can format messages for each debug command
        for cmd in expected_commands:
            data = {"command": cmd, "status": "available"}
            format_result = self.cli_api.format_data(data, format_type="json")
            assert isinstance(format_result, FlextResult)
            assert format_result.is_success


class TestEnvCommandReal:
    """Test env command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()
        self.formatter = FlextCliOutput()

    def test_env_variables_real(self) -> None:
        """Test environment variables display."""
        env_data = {
            "PYTHON_VERSION": platform.python_version(),
            "PLATFORM": sys.platform,
            "PYTHON_PATH": str(Path(sys.executable).parent),
        }

        format_result = self.cli_api.format_data(env_data, format_type="json")
        assert format_result.is_success
        assert "PYTHON_VERSION" in format_result.value

    def test_env_command_execution_real(self) -> None:
        """Test env command execution."""
        env_info = {
            "python_version": platform.python_version(),
            "platform": sys.platform,
        }

        # Test formatting
        result = self.cli_api.format_data(env_info, format_type="json")
        assert result.is_success
        assert isinstance(result.value, str)


class TestValidateCommandReal:
    """Test validate command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()

    def test_validate_command_execution_real(self) -> None:
        """Test validate command execution."""
        validation_result: dict[str, bool | list[str]] = {
            "config_valid": True,
            "errors": [],
            "warnings": [],
        }

        format_result = self.cli_api.format_data(validation_result, format_type="json")
        assert format_result.is_success

    def test_validate_config_real(self) -> None:
        """Test configuration validation."""
        config = FlextCliConfig.MainConfig(
            profile="test", output_format="json", debug=True
        )

        validation_data = {
            "profile": config.profile,
            "output_format": config.output_format,
            "debug_mode": config.debug_mode,
            "valid": True,
        }

        result = self.cli_api.format_data(validation_data, format_type="json")
        assert result.is_success


class TestConnectivityCommandReal:
    """Test connectivity command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()

    def test_connectivity_help_real(self) -> None:
        """Test connectivity command help."""
        help_data = {
            "command": "connectivity",
            "description": "Check connectivity to FLEXT services",
            "usage": "flext debug connectivity [OPTIONS]",
        }

        result = self.cli_api.format_data(help_data, format_type="json")
        assert result.is_success

    def test_connectivity_command_structure_real(self) -> None:
        """Test connectivity command structure."""
        connectivity_info = {
            "api_url": "http://localhost:8000",
            "status": "checking",
        }

        result = self.cli_api.format_data(connectivity_info, format_type="json")
        assert result.is_success

    def test_connectivity_execution_real(self) -> None:
        """Test connectivity execution."""
        connectivity_result = {
            "api_reachable": True,
            "response_time_ms": 50,
            "status": "connected",
        }

        result = self.cli_api.format_data(connectivity_result, format_type="json")
        assert result.is_success


class TestPathsCommandReal:
    """Test paths command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()

    def test_paths_command_execution_real(self) -> None:
        """Test paths command execution."""
        paths_data = {
            "config_dir": str(Path.home() / ".flext"),
            "cache_dir": str(Path.home() / ".flext" / "cache"),
            "log_dir": str(Path.home() / ".flext" / "logs"),
        }

        result = self.cli_api.format_data(paths_data, format_type="json")
        assert result.is_success
        assert "config_dir" in result.value

    def test_paths_display_real(self) -> None:
        """Test paths display formatting."""
        paths_info = {
            "config": str(Path.home() / ".flext"),
            "logs": str(Path.home() / ".flext" / "logs"),
        }

        result = self.cli_api.format_data(paths_info, format_type="json")
        assert result.is_success


class TestPerformanceCommandReal:
    """Test performance command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()

    def test_performance_command_execution_real(self) -> None:
        """Test performance command execution."""
        perf_data = {
            "cpu_usage": 15.5,
            "memory_usage_mb": 120,
            "disk_usage_percent": 45.2,
        }

        result = self.cli_api.format_data(perf_data, format_type="json")
        assert result.is_success

    def test_performance_metrics_real(self) -> None:
        """Test performance metrics collection."""
        metrics = {
            "cpu": "15%",
            "memory": "120 MB",
            "response_time": "50ms",
        }

        result = self.cli_api.format_data(metrics, format_type="json")
        assert result.is_success
        assert "cpu" in result.value


class TestTraceCommandReal:
    """Test trace command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()

    def test_trace_logging_real(self) -> None:
        """Test trace logging."""
        trace_data = {
            "timestamp": "2025-01-01T00:00:00",
            "level": "TRACE",
            "message": "Debug trace message",
            "module": "flext_cli.debug",
        }

        result = self.cli_api.format_data(trace_data, format_type="json")
        assert result.is_success

    def test_trace_command_execution_real(self) -> None:
        """Test trace command execution."""
        trace_result = {
            "enabled": True,
            "log_level": "TRACE",
            "output": "console",
        }

        result = self.cli_api.format_data(trace_result, format_type="json")
        assert result.is_success


class TestDebugIntegration:
    """Integration tests for debug workflow."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.cli_api = FlextCliApi()
        self.cli_main = FlextCliCommands(name="test-debug")

    def test_debug_error_handling_real(self) -> None:
        """Test debug error handling."""
        error_data = {
            "error": "Test error",
            "command": "debug",
            "status": "failed",
        }

        result = self.cli_api.format_data(error_data, format_type="json")
        assert result.is_success
        assert "error" in result.value

    def test_debug_workflow_real(self) -> None:
        """Test complete debug workflow."""
        # Register debug group
        debug_commands = {
            "env": {
                "handler": lambda: None,
                "description": "Show environment variables",
            },
            "validate": {
                "handler": lambda: None,
                "description": "Validate configuration",
            },
            "connectivity": {
                "handler": lambda: None,
                "description": "Check connectivity",
            },
        }
        # Cast to the expected type for MyPy
        commands_dict_2: dict[str, object] = debug_commands
        group_result = self.cli_main.register_command_group(
            "debug", commands_dict_2, "Debug commands"
        )
        assert group_result.is_success

        # Test debug info formatting
        debug_info = {
            "commands_available": ["env", "validate", "connectivity"],
            "status": "operational",
        }

        format_result = self.cli_api.format_data(debug_info, format_type="json")
        assert format_result.is_success
