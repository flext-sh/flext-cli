"""Service settings contract for services built on the flext-cli service base.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import cli, settings
from tests import p


class TestsFlextCliServiceSettingsContract:
    """A flext-cli service resolves the canonical CLI settings."""

    @staticmethod
    def test_service_settings_satisfy_cli_settings() -> None:
        """The facade settings satisfy the CLI settings protocol and SSOT."""
        resolved: p.Cli.Settings = cli.settings
        tm.that(resolved, is_=p.Cli.Settings)
        tm.that(resolved.cli_app_name, eq=settings.cli_app_name)
        tm.that(resolved.cli_log_level, eq=settings.cli_log_level)
