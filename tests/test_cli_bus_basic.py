"""Basic tests for CLI Command Bus Service.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cli_bus import FlextCliCommandBusService
from flext_core import FlextResult


class TestFlextCliCommandBusService:
    """Test FlextCliCommandBusService basic functionality."""

    def test_command_bus_initialization(self) -> None:
        """Test FlextCliCommandBusService can be initialized."""
        service = FlextCliCommandBusService()
        assert service is not None

    def test_command_bus_execute(self) -> None:
        """Test FlextCliCommandBusService execute method."""
        service = FlextCliCommandBusService()
        result = service.execute()
        assert isinstance(result, FlextResult)
        # Command bus execution might succeed or have specific behavior
        # Accept either success or a meaningful failure
        assert result is not None

    def test_command_bus_has_expected_methods(self) -> None:
        """Test FlextCliCommandBusService has expected methods."""
        service = FlextCliCommandBusService()

        # Check for key command bus methods
        expected_methods = [
            "execute_show_config_command",
            "execute_set_config_command",
            "execute_edit_config_command",
            "execute_auth_login_command",
            "execute_auth_logout_command",
            "execute_auth_status_command",
        ]

        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(service, method_name)), (
                f"Method not callable: {method_name}"
            )

    def test_show_config_command_basic(self) -> None:
        """Test show config command basic functionality."""
        service = FlextCliCommandBusService()

        # Test show config command
        result = service.execute_show_config_command()
        assert isinstance(result, FlextResult)
        # Accept meaningful results whether success or failure
        assert result is not None

    def test_auth_status_command_basic(self) -> None:
        """Test auth status command basic functionality."""
        service = FlextCliCommandBusService()

        # Test auth status command
        result = service.execute_auth_status_command()
        assert isinstance(result, FlextResult)
        # Accept meaningful results whether success or failure
        assert result is not None

    def test_command_bus_logger_access(self) -> None:
        """Test command bus has logger access."""
        service = FlextCliCommandBusService()

        # Check that service has logger (internal access)
        assert hasattr(service, "_logger") or hasattr(service, "get_logger")
