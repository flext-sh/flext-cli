"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

from flext_core import (
    FlextContainer as container,
    FlextLogger as logger_core,
    r,
)

from flext_cli import (
    FlextCliCmd,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliSettings,
    c,
    t,
    u,
)


class FlextCli:
    """Coordinate CLI operations and expose domain services.

    Composition facade over CLI services (cmd, output, prompts, tables, formatters).
    All operations return r[T].
    """

    logger: logger_core
    config: FlextCliSettings
    formatters: FlextCliFormatters
    file_tools: FlextCliFileTools
    output: FlextCliOutput
    cmd: FlextCliCmd
    prompts: FlextCliPrompts
    _name: str
    _version: str
    _description: str
    _container: container

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        super().__init__()
        self._name = c.Cli.CliDefaults.DEFAULT_APP_NAME
        self._version = c.Cli.CLI_VERSION
        self._description = f"{self._name}{c.Cli.APIDefaults.APP_DESCRIPTION_SUFFIX}"
        self.logger = logger_core(__name__)
        self._container = container()
        key = c.Cli.APIDefaults.CONTAINER_REGISTRATION_KEY
        if not self._container.has_service(key):
            self._container.register(key, key)
        self.formatters, self.file_tools = (FlextCliFormatters(), FlextCliFileTools())
        self.output, self.cmd, self.prompts = (
            FlextCliOutput(),
            FlextCliCmd(),
            FlextCliPrompts(),
        )
        self.config = FlextCliSettings.get_global()

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

    def print(self, message: str, style: str | None = None) -> None:
        """Print a message with optional style."""
        FlextCliFormatters().print(message, style=style or "")


__all__ = ["FlextCli"]
