"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_core import r
from pydantic_settings import SettingsConfigDict

from flext_cli import (
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliSettings,
    FlextCliTables,
    c,
    t,
    u,
)


class FlextCli(
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliSettings,
    FlextCliTables,
):
    """Coordinate CLI operations and expose domain services.

    MRO facade over CLI services (cli, cmd, commands, params, file_tools,
    formatters, output, prompts, settings, tables).
    All operations return r[T].
    """

    model_config = SettingsConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        validate_assignment=True,
    )

    @override
    def execute(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Execute CLI service with railway pattern."""
        result_dict: Mapping[str, t.Cli.JsonValue] = {
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": c.Cli.CLI_VERSION,
            "components": {
                "config": "available",
                "formatters": "available",
                "prompts": "available",
            },
        }
        return r[Mapping[str, t.Cli.JsonValue]].ok(result_dict)


__all__ = ["FlextCli"]
