"""Command execution and settings bridge for flext-.

Encapsulates the bridge between registered commands, file utilities, and settings
helpers using `r` for predictable success/failure handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import override

from flext_cli import (
    c,
    m,
    r,
    s,
    t,
    u,
)


class FlextCliCmd(s):
    """Execute registered CLI commands and expose execution metadata.

    Extends s for consistent logging and container access.
    Delegates settings operations to direct ``u.Cli`` helpers.
    Railway-Oriented Programming via r for composable error handling.
    """

    @staticmethod
    def settings_snapshot() -> r[m.Cli.SettingsSnapshot]:
        """Return the current settings snapshot using ``u.Cli``."""
        return u.Cli.cmd_settings_snapshot()

    @override
    def execute(self) -> r[t.Cli.JsonMapping]:
        """Report operational status required by `s`."""
        status: t.Cli.JsonMapping = {
            c.Cli.DICT_KEY_STATUS: c.Cli.ServiceStatus.OPERATIONAL,
            c.Cli.DICT_KEY_SERVICE: c.Cli.CMD_SERVICE_NAME,
        }
        return r[t.Cli.JsonMapping].ok(status)

    def show_settings(self) -> r[bool]:
        """Show current settings.

        Returns:
            r[bool]: True if displayed successfully, or error

        """
        return u.Cli.cmd_show_settings(self.logger)

    def validate_settings(self) -> r[bool]:
        """Validate settings structure using u directly.

        Returns:
            r[bool]: True if validation passed, or error

        """
        return u.Cli.cmd_validate_settings(self.logger)


__all__ = ["FlextCliCmd"]
