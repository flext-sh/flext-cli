"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import p, r, t, u
from flext_cli.services import (
    FlextCliAuth,
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommonParams,
    FlextCliDocx,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPipeline,
    FlextCliPptx,
    FlextCliPrompts,
    FlextCliRules,
    FlextCliRuntime,
    FlextCliTables,
    FlextCliXlsx,
    FlextCliYamlModel,
)


class FlextCli(
    FlextCliAuth,
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommonParams,
    FlextCliDocx,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPipeline,
    FlextCliPrompts,
    FlextCliPptx,
    FlextCliRules,
    FlextCliRuntime,
    FlextCliTables,
    FlextCliXlsx,
    FlextCliYamlModel,
):
    """Coordinate CLI operations through one explicit service composition root."""

    @override
    def execute(self) -> p.Result[p.Cli.RuntimeStatus]:
        """Report the public CLI runtime surface state.

        Returns:
            The resulting ``p.Result[p.Cli.RuntimeStatus]``.

        """
        return r[p.Cli.RuntimeStatus].ok(u.Cli.cmd_status())


cli = FlextCli.fetch_global()
"""Process-wide ``FlextCli`` facade singleton exposing every CLI service via MRO."""


__all__: t.MutableSequenceOf[str] = ["FlextCli", "cli"]
