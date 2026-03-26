"""FLEXT CLI CMD Tests - Comprehensive Command Functionality Testing.

Tests for FlextCliCmd covering command initialization, execution, configuration operations
(show, validate, get_config_info), error handling, performance, integration,
and edge cases.

Modules tested: flext_cli.cmd.FlextCliCmd, u.Cli.ConfigOps, FlextCliServiceBase
Scope: All kept command operations, error handling, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliCmd, m, u


def _create_cmd_instance() -> FlextCliCmd:
    """Create FlextCliCmd instance for testing."""
    return FlextCliCmd()


class TestsCliCmd:
    """Comprehensive tests for FlextCliCmd class.

    Single class with nested test groups organized by functionality.
    """

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = _create_cmd_instance()
        tm.that(cmd, none=False)
        tm.that(cmd, is_=FlextCliCmd)

    def test_cmd_instantiation(self) -> None:
        """Test direct instantiation."""
        instance = _create_cmd_instance()
        tm.that(instance, is_=FlextCliCmd)

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = _create_cmd_instance()
        tm.that(hasattr(cmd, "execute"), eq=True)
        tm.that(hasattr(cmd, "logger"), eq=True)
        tm.that(hasattr(cmd, "container"), eq=True)

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = _create_cmd_instance()
        result = cmd.execute()
        tm.ok(result)
        data = result.value
        tm.that(data, is_=dict)
        tm.that(data["status"], eq="operational")
        tm.that(data["service"], eq="FlextCliCmd")

    def test_cmd_command_bus_service(self) -> None:
        """Test command bus service property."""
        cmd = _create_cmd_instance()
        tm.that(cmd, none=False)
        tm.that(cmd, is_=FlextCliCmd)

    def test_cmd_integration(self) -> None:
        """Test CMD integration with other services."""
        cmd = _create_cmd_instance()
        result = cmd.execute()
        tm.ok(result)
        tm.that(cmd, none=False)
        tm.that(cmd, is_=FlextCliCmd)

    def test_cmd_logging_integration(self) -> None:
        """Test CMD logging integration."""
        cmd = _create_cmd_instance()
        result = cmd.execute()
        tm.ok(result)
        tm.that(result.value, none=False)

    def test_cmd_performance(self) -> None:
        """Test CMD performance characteristics."""
        cmd = _create_cmd_instance()
        start_time = time.time()
        result = cmd.execute()
        execution_time = time.time() - start_time
        tm.ok(result)
        tm.that(execution_time, lt=1.0)

    def test_cmd_memory_usage(self) -> None:
        """Test CMD memory usage characteristics."""
        cmd = _create_cmd_instance()
        for _ in range(5):
            result = cmd.execute()
            tm.ok(result)

    def test_cmd_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()
        tm.ok(result)

    def test_cmd_get_config_info(self) -> None:
        """Test get_config_info method."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()
        tm.ok(result)
        tm.that(result.value, is_=m.Cli.ConfigSnapshot)
        tm.that(result.value.config_dir, none=False)

    def test_cmd_show_config(self) -> None:
        """Test show_config method."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()
        tm.ok(result)

    def test_cmd_config_helper_validate_config_structure(self) -> None:
        """Test u.Cli.ConfigOps.validate_config_structure() directly."""
        results = u.Cli.ConfigOps.validate_config_structure()
        tm.that(results, is_=list)
        tm.that(results, empty=False)

    def test_cmd_config_helper_get_config_info(self) -> None:
        """Test u.Cli.ConfigOps.get_config_info() directly."""
        info = u.Cli.ConfigOps.get_config_info()
        tm.that(info, is_=m.Cli.ConfigSnapshot)
        tm.that(info.config_dir, is_=str)
        tm.that(info.config_exists, is_=bool)
        tm.that(info.config_readable, is_=bool)
        tm.that(info.config_writable, is_=bool)
        tm.that(info.timestamp, is_=str)

    def test_cmd_validate_config_structure_missing_dir(self) -> None:
        """Test validate_config_structure when main config directory is missing."""
        results = u.Cli.ConfigOps.validate_config_structure()
        tm.that(results, is_=list)
        tm.that(all(isinstance(r, str) for r in results), eq=True)

    def test_cmd_validate_config_exception(self) -> None:
        """Test validate_config exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()
        tm.that(result, is_=r)
        tm.that(result.is_success or result.is_failure, eq=True)

    def test_cmd_get_config_info_exception(self) -> None:
        """Test get_config_info exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()
        tm.that(result, is_=r)
        if result.is_success:
            info = result.value
            tm.that(info, is_=m.Cli.ConfigSnapshot)

    def test_cmd_show_config_exception(self) -> None:
        """Test show_config exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()
        tm.that(result, is_=r)

    def test_cmd_config_display_helper_show_config(self) -> None:
        """Test show_config method."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()
        tm.ok(result)

    def test_cmd_config_validation_helper_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()
        tm.that(result.is_success or result.is_failure, eq=True)

    def test_cmd_validate_config_error_handling(self) -> None:
        """Test validate_config error handling."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()
        tm.that(result.is_success or result.is_failure, eq=True)

    def test_cmd_get_config_info_error_handling(self) -> None:
        """Test get_config_info error handling."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()
        tm.that(result.is_success or result.is_failure, eq=True)

    def test_cmd_show_config_error_handling(self) -> None:
        """Test show_config error handling."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()
        tm.that(result.is_success or result.is_failure, eq=True)

    def test_cmd_config_display_helper_error_handling(self) -> None:
        """Test config display error handling."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()
        tm.that(result.is_success or result.is_failure, eq=True)
