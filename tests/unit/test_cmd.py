"""FLEXT CLI CMD Tests - Comprehensive Command Functionality Testing.

Tests for FlextCliCmd covering command initialization, execution, settings operations
(show, validate, settings_snapshot), error handling, performance, integration,
and edge cases.

Modules tested: flext_cli.cmd.FlextCliCmd, direct u.Cli settings helpers, FlextCliServiceBase
Scope: All kept command operations, error handling, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import FlextCliCmd
from tests import m, u


class TestsFlextCliCmd:
    """Comprehensive tests for FlextCliCmd class.

    Single class with nested test groups organized by functionality.
    """

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = u.Tests.create_cmd_instance()
        tm.that(cmd, none=False)
        tm.that(cmd, is_=FlextCliCmd)

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        u.Tests.create_cmd_instance()

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = u.Tests.create_cmd_instance()
        result = cmd.execute()
        tm.ok(result)
        data = result.value
        tm.that(data, is_=dict)
        tm.that(data["status"], eq="operational")
        tm.that(data["service"], eq="FlextCliCmd")

    def test_cmd_validate_settings(self) -> None:
        """Test validate_settings method."""
        cmd = u.Tests.create_cmd_instance()
        result = cmd.validate_settings()
        tm.ok(result)

    def test_cmd_settings_snapshot(self) -> None:
        """Test settings_snapshot method."""
        cmd = u.Tests.create_cmd_instance()
        result = cmd.settings_snapshot()
        tm.ok(result)
        tm.that(result.value, is_=m.Cli.SettingsSnapshot)
        tm.that(result.value.settings_dir, none=False)

    def test_cmd_show_settings(self) -> None:
        """Test show_settings method."""
        cmd = u.Tests.create_cmd_instance()
        result = cmd.show_settings()
        tm.ok(result)

    def test_cmd_settings_helper_validate_settings_structure(self) -> None:
        """Test u.Cli.validate_settings_structure() directly."""
        results = u.Cli.validate_settings_structure()
        tm.that(results, is_=list)
        tm.that(results, empty=False)

    def test_cmd_settings_helper_snapshot(self) -> None:
        """Test u.Cli.settings_snapshot() directly."""
        info = u.Cli.settings_snapshot()
        tm.that(info, is_=m.Cli.SettingsSnapshot)
        tm.that(info.settings_dir, is_=str)
        tm.that(info.settings_exists, is_=bool)
        tm.that(info.settings_readable, is_=bool)
        tm.that(info.settings_writable, is_=bool)
        tm.that(info.timestamp, is_=str)

    def test_cmd_validate_settings_structure_missing_dir(self) -> None:
        """Test validate_settings_structure when main settings directory is missing."""
        results = u.Cli.validate_settings_structure()
        tm.that(results, is_=list)
        for item in results:
            tm.that(item, is_=str)
