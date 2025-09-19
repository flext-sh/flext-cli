"""Test FlextCliCmd functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cmd import FlextCliCmd
from flext_core import FlextResult


class TestFlextCliCmd:
    """Test suite for FlextCliCmd class."""

    def test_cmd_initialization(self) -> None:
        """Test cmd can be initialized."""
        cmd = FlextCliCmd()
        assert cmd is not None
        assert hasattr(cmd, "execute")
        assert hasattr(cmd, "command_bus_service")

    def test_command_bus_service_property(self) -> None:
        """Test command bus service property with lazy loading."""
        cmd = FlextCliCmd()

        # Initially should be None
        assert cmd._command_bus_service is None

        # Accessing property should create the service
        bus_service = cmd.command_bus_service
        assert bus_service is not None
        assert cmd._command_bus_service is not None

    def test_execute_method(self) -> None:
        """Test execute method."""
        cmd = FlextCliCmd()

        # Test execute method
        result = cmd.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "Command bus integration ready" in result.unwrap()

    def test_config_display_helper(self) -> None:
        """Test config display helper."""
        cmd = FlextCliCmd()

        # Test the nested helper class
        helper = FlextCliCmd._ConfigDisplayHelper()
        assert helper is not None

        # Test show_config method
        result = FlextCliCmd._ConfigDisplayHelper.show_config(cmd._logger)
        assert isinstance(result, FlextResult)
        assert result.is_success
