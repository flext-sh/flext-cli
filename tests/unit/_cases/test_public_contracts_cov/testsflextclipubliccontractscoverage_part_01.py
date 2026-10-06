"""Public contract coverage tests for the flext-cli facade and models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import FlextCliSettings, cli, settings
from tests import c, p, u


class TestsFlextCliPublicContractsCoveragePart01:
    """Implementation part for TestsFlextCliPublicContractsCoveragePart01."""

    @staticmethod
    def test_public_facade_and_settings_contract() -> None:
        # NOTE (multi-agent): flat cli_* settings (§2.6) — fresh instances come
        # from ``settings.clone()`` and test-runtime detection lives in
        # ``u.Cli.cli_test_env`` (behavior moved off the settings model).
        """Verify that public facade and settings contract."""
        FlextCliSettings.reset_for_testing()

        fresh_settings = settings.clone()
        tm.that(fresh_settings, is_=p.Cli.Settings)
        tm.that(u.Cli.cli_test_env(fresh_settings), eq=False)

        shell_settings = settings.clone(cli_shell_command="pytest -k smoke")
        tm.that(u.Cli.cli_test_env(shell_settings), eq=True)

        pytest_settings = settings.clone(
            cli_pytest_current_test=(
                "tests/unit/test_public_contracts_cov.py::test_public_facade"
            ),
        )
        tm.that(u.Cli.cli_test_env(pytest_settings), eq=True)

        ci_settings = settings.clone(cli_ci=True)
        tm.that(u.Cli.cli_test_env(ci_settings), eq=True)

        FlextCliSettings.reset_for_testing()

        facade_result = cli.execute()

        tm.ok(facade_result)
        tm.that(facade_result.value.status, eq=(c.Cli.ServiceStatus.OPERATIONAL))
        tm.that(facade_result.value.service, eq=c.Cli.FLEXT_CLI)
