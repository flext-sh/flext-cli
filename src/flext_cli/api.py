"""Public API facade for flext-.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import (
    FlextCliApiRuntime,
    FlextCliAuth,
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliRules,
    FlextCliTables,
    t,
)
from flext_cli.services.pipeline import FlextCliPipeline
from flext_cli.services.runtime import FlextCliRuntime


class FlextCli(
    FlextCliAuth,
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPipeline,
    FlextCliPrompts,
    FlextCliRules,
    FlextCliRuntime,
    FlextCliTables,
    FlextCliApiRuntime,
):
    """Coordinate CLI operations and expose domain services.

    MRO facade over CLI services (cli, cmd, commands, params, file_tools,
    formatters, output, pipeline, prompts, rules, runtime, settings, tables).
    All operations return r[T].
    """

    pass


cli = FlextCli.fetch_global()
"""Process-wide ``FlextCli`` facade singleton exposing every CLI service via MRO."""


__all__: t.MutableSequenceOf[str] = ["FlextCli", "cli"]
