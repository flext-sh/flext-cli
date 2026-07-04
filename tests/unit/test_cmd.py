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

import io
import time
from contextlib import redirect_stdout
from datetime import datetime
from typing import TYPE_CHECKING

from flext_tests import tm

from flext_cli import cli
from tests.constants import c
from tests.protocols import p
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


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
        tm.that(cli, is_=p.Cli.CmdService)

    def test_cmd_execute_sync(self) -> None:
        """Public cli.execute must report facade-level runtime status."""
        cmd = cli
        result = cmd.execute()
        tm.ok(result)
        data = result.value
        tm.that(data, is_=dict)
        tm.that(data["status"], eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(data["service"], eq=c.Cli.FLEXT_CLI)

    def test_cmd_settings_snapshot_reflects_real_home_state(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """settings_snapshot must expose the canonical HOME-based state."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cli.settings_snapshot()

        tm.ok(result)
        info = result.value
        tm.that(info.settings_dir, eq=str(tmp_path / c.Cli.PATH_FLEXT_DIR_NAME))
        tm.that(info.settings_exists, eq=False)
        tm.that(info.settings_readable, eq=False)
        tm.that(info.settings_writable, eq=False)
        _ = datetime.fromisoformat(info.timestamp)

    def test_cmd_show_settings_logs_real_snapshot_payload(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """show_settings must log the serialized public snapshot payload."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))
        logger = u.create_module_logger("tests.cmd")
        stream = io.StringIO()

        with redirect_stdout(stream):
            result = u.Cli.cmd_show_settings(logger)
            deadline = time.monotonic() + 0.25
            while time.monotonic() < deadline:
                output = stream.getvalue()
                if c.Cli.LOG_MSG_SETTINGS_DISPLAYED in output:
                    break
                time.sleep(0.01)

        tm.ok(result)
        tm.that(result.value, eq=True)
        output = stream.getvalue()
        tm.that(c.Cli.LOG_MSG_SETTINGS_DISPLAYED in output, eq=True)
        tm.that(f'"settings_dir":"{settings_dir}"' in output, eq=True)
        tm.that('"settings_exists":true' in output, eq=True)
        tm.that('"settings_readable":true' in output, eq=True)
        tm.that('"settings_writable":true' in output, eq=True)

    def test_cmd_validate_settings_logs_real_structure_results(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """validate_settings must log the exact canonical structure results."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        (settings_dir / c.Cli.STANDARD_SUBDIRS[0]).mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))
        logger = u.create_module_logger("tests.cmd")
        stream = io.StringIO()
        expected_results = list(u.Cli.validate_settings_structure())

        with redirect_stdout(stream):
            result = u.Cli.cmd_validate_settings(logger)
            deadline = time.monotonic() + 0.25
            expected_message = c.Cli.LOG_MSG_SETTINGS_VALIDATION_RESULTS.format(
                results=expected_results,
            )
            while time.monotonic() < deadline:
                output = stream.getvalue()
                if expected_message in output:
                    break
                time.sleep(0.01)

        tm.ok(result)
        tm.that(result.value, eq=True)
        output = stream.getvalue()
        tm.that(expected_message in output, eq=True)
        tm.that("settings='" in output, eq=False)
        tm.that(
            expected_results[0],
            eq=f"{c.Cli.SYMBOL_SUCCESS_MARK} Settings directory exists",
        )
        tm.that(expected_results[1], has=c.Cli.STANDARD_SUBDIRS[0])
        tm.that(expected_results[2], has=c.Cli.STANDARD_SUBDIRS[1])
