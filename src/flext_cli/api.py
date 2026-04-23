"""Public API facade for flext-.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import (
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
    c,
    p,
    r,
    t,
    u,
)


class FlextCli(
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
):
    """Coordinate CLI operations and expose domain services.

    MRO facade over CLI services (cli, cmd, commands, params, file_tools,
    formatters, output, prompts, rules, settings, tables).
    All operations return r[T].
    """

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Execute CLI service with railway pattern."""
        result_dict: t.JsonMapping = {
            c.Cli.DICT_KEY_STATUS: c.Cli.ServiceStatus.OPERATIONAL,
            c.Cli.DICT_KEY_SERVICE: c.Cli.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": c.Cli.CLI_VERSION,
            "components": {
                "settings": "available",
                "formatters": "available",
                "prompts": "available",
                "rules": "available",
            },
        }
        return r[t.JsonMapping].ok(result_dict)


cli = FlextCli()


__all__: list[str] = ["FlextCli", "cli"]
