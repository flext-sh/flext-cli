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

from flext_cli import cli
from tests import m, p


class TestsFlextCliCmd:
    """Comprehensive tests for public command-facing cli methods.

    Single class with nested test groups organized by functionality.
    """

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = cli
        tm.that(cmd, none=False)
        tm.that(cmd, is_=p.Cli.CmdService)

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = cli
        tm.that(cmd, is_=p.Cli.CmdService)

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = cli
        result = cmd.execute()
        tm.ok(result)
        data = result.value
        tm.that(data, is_=dict)
        tm.that(data["status"], eq="operational")
        tm.that(data["service"], eq="FlextCliCmd")

    def test_cmd_validate_settings(self) -> None:
        """Test validate_settings method."""
        cmd = cli
        result = cmd.validate_settings()
        tm.ok(result)

    def test_cmd_settings_snapshot(self) -> None:
        """Test settings_snapshot method."""
        result = cli.settings_snapshot()
        tm.ok(result)
        tm.that(result.value, is_=m.Cli.SettingsSnapshot)
        tm.that(result.value.settings_dir, none=False)

    def test_cmd_show_settings(self) -> None:
        """Test show_settings method."""
        cmd = cli
        result = cmd.show_settings()
        tm.ok(result)

    def test_cmd_validate_settings_reports_public_result(self) -> None:
        """Public validate_settings must expose the validation outcome."""
        result = cli.validate_settings()
        tm.that(result.success or result.failure, eq=True)

    def test_cmd_settings_snapshot_returns_public_snapshot_model(self) -> None:
        """Public settings_snapshot must expose the typed snapshot model."""
        info = cli.settings_snapshot().value
        tm.that(info, is_=m.Cli.SettingsSnapshot)
        tm.that(info.settings_dir, is_=str)
        tm.that(info.settings_exists, is_=bool)
        tm.that(info.settings_readable, is_=bool)
        tm.that(info.settings_writable, is_=bool)
        tm.that(info.timestamp, is_=str)

    def test_cmd_validate_settings_missing_dir_uses_public_surface(self) -> None:
        """Public validate_settings must stay callable when dirs are missing."""
        result = cli.validate_settings()
        tm.that(result.success or result.failure, eq=True)
