"""Behavioral tests for the public CLI runtime status surface (``cli.execute``).

Every assertion targets a return value (``r[T]`` outcome / public model state)
reachable through the public API — never logging format, private attributes, or
internal collaborators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli
from tests import c, p, tm


class TestsFlextCliCmd:
    """Public behavioral contract of the CLI runtime status facade."""

    @staticmethod
    def test_execute_reports_operational_runtime_payload() -> None:
        """execute() must succeed and expose the canonical status payload."""
        data = tm.ok(cli.execute())

        tm.that(data, is_=p.Cli.RuntimeStatus)
        tm.that(data.status, eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(data.service, eq=c.Cli.FLEXT_CLI)
        tm.that(data.version, eq=c.Cli.CLI_VERSION)
        tm.that(data.timestamp, is_=str)
        tm.that(data.components, is_=p.Cli.RuntimeComponents)

    @staticmethod
    def test_execute_is_deterministic_across_calls() -> None:
        """Repeated execute() calls must report identical stable identity fields."""
        first: p.Cli.RuntimeStatus = tm.ok(cli.execute())
        second: p.Cli.RuntimeStatus = tm.ok(cli.execute())

        tm.that(first.status, eq=second.status)
        tm.that(first.service, eq=second.service)
        tm.that(first.version, eq=second.version)
