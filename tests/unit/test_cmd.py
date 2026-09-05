"""Behavioral tests for the public CLI command surface (FlextCliCmd via ``cli``).

Exercises the observable public contract of the process-wide ``cli`` facade:
``execute``, ``settings_snapshot``, ``show_settings``, and ``validate_settings``.
Every assertion targets a return value (``r[T]`` outcome / public model state)
reachable through the public API — never logging format, private attributes, or
internal collaborators.

Module tested: flext_cli.services.cmd.FlextCliCmd (surfaced on flext_cli.cli)
Data I/O: reads isolated child ``$HOME/.flext`` states through the public
process facade and exercises the current process state without rewriting it.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from flext_cli import cli, m
from flext_tests import tm
from tests import c, p, t, u


class TestsFlextCliCmd:
    """Public behavioral contract of the CLI command service facade."""

    def test_cli_satisfies_cmd_service_contract(self) -> None:
        """The public facade must satisfy the CmdService protocol."""
        tm.that(cli, none=False, is_=p.Cli.CmdService)

    def test_execute_reports_operational_runtime_payload(self) -> None:
        """execute() must succeed and expose the canonical status payload."""
        data = m.Cli.RuntimeStatus.model_validate(tm.ok(cli.execute()))

        tm.that(data.status, eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(data.service, eq=c.Cli.FLEXT_CLI)
        tm.that(data.version, eq=c.Cli.CLI_VERSION)
        tm.that(data.timestamp, is_=str)
        tm.that(data.components, is_=m.Cli.RuntimeComponents)

    def test_execute_is_deterministic_across_calls(self) -> None:
        """Repeated execute() calls must report identical stable identity fields."""
        first: m.Cli.RuntimeStatus = tm.ok(cli.execute())
        second: m.Cli.RuntimeStatus = tm.ok(cli.execute())

        tm.that(first.status, eq=second.status)
        tm.that(first.service, eq=second.service)
        tm.that(first.version, eq=second.version)

    def test_settings_snapshot_reports_absent_home_state(self, tmp_path: Path) -> None:
        """A missing settings dir must yield a fully-negative snapshot."""
        info = self._settings_snapshot(tmp_path)

        expected: t.JsonMapping = {
            "settings_dir": str(tmp_path / c.Cli.PATH_FLEXT_DIR_NAME),
            "settings_exists": False,
            "settings_readable": False,
            "settings_writable": False,
        }
        tm.that(info, attr_eq=expected)

    def test_settings_snapshot_reports_present_home_state(self, tmp_path: Path) -> None:
        """An existing, accessible settings dir must yield a positive snapshot."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        info = self._settings_snapshot(tmp_path)

        expected: t.JsonMapping = {
            "settings_dir": str(settings_dir),
            "settings_exists": True,
            "settings_readable": True,
            "settings_writable": True,
        }
        tm.that(info, attr_eq=expected)

    def test_settings_snapshot_timestamp_is_iso8601(self) -> None:
        """The snapshot timestamp must be a parseable ISO-8601 instant."""
        info: m.Cli.SettingsSnapshot = tm.ok(cli.settings_snapshot())
        parsed = datetime.fromisoformat(info.timestamp)

        tm.that(parsed, is_=datetime)

    def test_settings_snapshot_is_a_settings_snapshot_model(self) -> None:
        """The snapshot value must be the public SettingsSnapshot model."""
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

    def test_show_settings_succeeds_for_current_home_state(self) -> None:
        """show_settings() must expose the current settings-dir state."""
        tm.that(tm.ok(cli.show_settings()), eq=True)

    def test_validate_settings_succeeds_for_current_home_state(self) -> None:
        """validate_settings() must report the real current structure."""
        tm.that(tm.ok(cli.validate_settings()), eq=True)

    @staticmethod
    def _settings_snapshot(home: Path) -> m.Cli.SettingsSnapshot:
        output = tm.ok(
            u.Cli.capture(
                [
                    sys.executable,
                    "-c",
                    "from flext_cli import cli;"
                    "print(cli.settings_snapshot().unwrap().model_dump_json())",
                ],
                env={c.Cli.ENV_VAR_HOME: str(home)},
            )
        )
        return m.Cli.SettingsSnapshot.model_validate_json(output)
