"""Behavioral tests for the public CLI command surface (FlextCliCmd via ``cli``).

Exercises the observable public contract of the process-wide ``cli`` facade:
``execute``, ``settings_snapshot``, ``show_settings``, and ``validate_settings``.
Every assertion targets a return value (``r[T]`` outcome / public model state)
reachable through the public API — never logging format, private attributes, or
internal collaborators.

Module tested: flext_cli.services.cmd.FlextCliCmd (surfaced on flext_cli.cli)
Data I/O: reads the real ``$HOME/.flext`` directory state via a monkeypatched
HOME pointing at pytest ``tmp_path``; creates directories to drive filesystem
state. No production data is written.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import cli, m
from tests import c
from tests import p

from pathlib import Path



class TestsFlextCliCmd:
    """Public behavioral contract of the CLI command service facade."""

    def test_cli_satisfies_cmd_service_contract(self) -> None:
        """The public facade must satisfy the CmdService protocol."""
        tm.that(cli, none=False, is_=p.Cli.CmdService)

    def test_execute_reports_operational_runtime_payload(self) -> None:
        """execute() must succeed and expose the canonical status payload."""
        result = cli.execute()
        tm.ok(result, is_=m.Cli.RuntimeStatus)
        status = result.value

        tm.that(
            status,
            attr_eq={
                "status": c.Cli.ServiceStatus.OPERATIONAL,
                "service": c.Cli.FLEXT_CLI,
                "version": c.Cli.CLI_VERSION,
            },
        )
        tm.that(status.timestamp, is_=str)
        tm.that(status.components, is_=m.Cli.RuntimeComponents)

    def test_execute_is_deterministic_across_calls(self) -> None:
        """Repeated execute() calls must report identical stable identity fields."""
        first_result = cli.execute()
        second_result = cli.execute()
        tm.ok(first_result, is_=m.Cli.RuntimeStatus)
        tm.ok(second_result, is_=m.Cli.RuntimeStatus)
        first = first_result.value
        second = second_result.value

        tm.that(first.status, eq=second.status)
        tm.that(first.service, eq=second.service)
        tm.that(first.version, eq=second.version)

    def test_settings_snapshot_reports_absent_home_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A missing settings dir must yield a fully-negative snapshot."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cli.settings_snapshot()
        tm.ok(result)
        info = result.value

        tm.that(
            info,
            attr_eq={
                "settings_dir": str(tmp_path / c.Cli.PATH_FLEXT_DIR_NAME),
                "settings_exists": False,
                "settings_readable": False,
                "settings_writable": False,
            },
        )

    def test_settings_snapshot_reports_present_home_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An existing, accessible settings dir must yield a positive snapshot."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cli.settings_snapshot()
        tm.ok(result)
        info = result.value

        tm.that(
            info,
            attr_eq={
                "settings_dir": str(settings_dir),
                "settings_exists": True,
                "settings_readable": True,
                "settings_writable": True,
            },
        )

    def test_settings_snapshot_timestamp_is_iso8601(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The snapshot timestamp must be a parseable ISO-8601 instant."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cli.settings_snapshot()
        tm.ok(result)
        info = result.value
        parsed = datetime.fromisoformat(info.timestamp)

        tm.that(parsed, is_=datetime)

    def test_settings_snapshot_is_a_settings_snapshot_model(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The snapshot value must be the public SettingsSnapshot model."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cli.settings_snapshot()
        tm.ok(result, is_=m.Cli.SettingsSnapshot)

        tm.that(
            result.value.model_dump(),
            keys=(
                "settings_dir",
                "settings_exists",
                "settings_readable",
                "settings_writable",
                "timestamp",
            ),
        )

    @pytest.mark.parametrize("dir_present", [False, True])
    def test_show_settings_succeeds_for_any_home_state(
        self, *, dir_present: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """show_settings() must report success regardless of settings-dir presence."""
        if dir_present:
            (tmp_path / c.Cli.PATH_FLEXT_DIR_NAME).mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))

        tm.that(tm.ok(cli.show_settings()), eq=True)

    def test_show_settings_reflects_snapshot_presence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """show_settings() success must coincide with the snapshot it displays."""
        (tmp_path / c.Cli.PATH_FLEXT_DIR_NAME).mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))

        displayed_result = cli.show_settings()
        snapshot_result = cli.settings_snapshot()
        tm.ok(displayed_result)
        tm.ok(snapshot_result)
        displayed = displayed_result.value
        snapshot = snapshot_result.value

        tm.that(displayed, eq=True)
        tm.that(snapshot.settings_exists, eq=True)

    @pytest.mark.parametrize("with_subdirs", [False, True])
    def test_validate_settings_succeeds_for_any_structure(
        self, *, with_subdirs: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_settings() must succeed whether or not subdirs exist."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        if with_subdirs:
            for subdir in c.Cli.STANDARD_SUBDIRS:
                (settings_dir / subdir).mkdir()
        monkeypatch.setenv("HOME", str(tmp_path))

        tm.that(tm.ok(cli.validate_settings()), eq=True)
