"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import m, p, r, t, u

from .services.auth import FlextCliAuth
from .services.cli import FlextCliCli
from .services.cli_params import FlextCliCommonParams
from .services.cmd import FlextCliCmd
from .services.docx import FlextCliDocx
from .services.file_tools import FlextCliFileTools
from .services.formatters import FlextCliFormatters
from .services.output import FlextCliOutput
from .services.pipeline import FlextCliPipeline
from .services.pptx import FlextCliPptx
from .services.prompts import FlextCliPrompts
from .services.rules import FlextCliRules
from .services.runtime import FlextCliRuntime
from .services.tables import FlextCliTables
from .services.xlsx import FlextCliXlsx
from .services.yaml_model import FlextCliYamlModel


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
    def execute(self) -> p.Result[m.Cli.RuntimeStatus]:
        """Report the public CLI runtime surface state.

        Returns:
            The resulting ``p.Result[m.Cli.RuntimeStatus]``.

        """
        return r[m.Cli.RuntimeStatus].ok(u.Cli.cmd_status())


cli: FlextCli = FlextCli.fetch_global()
"""Process-wide ``FlextCli`` facade singleton exposing every CLI service via MRO."""


__all__: t.MutableSequenceOf[str] = ["FlextCli", "cli"]
