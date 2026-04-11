"""Command execution and configuration bridge for flext-.

Encapsulates the bridge between registered commands, file utilities, and configuration
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
    Delegates config operations to direct ``u.Cli`` helpers.
    Railway-Oriented Programming via r for composable error handling.
    """

    @staticmethod
    def config_snapshot() -> r[m.Cli.ConfigSnapshot]:
        """Return the current configuration snapshot using ``u.Cli``."""
        return u.try_(
            u.Cli.config_snapshot,
        ).map_error(
            lambda e: c.Cli.ERR_CONFIG_INFO_FAILED.format(
                error=e,
            ),
        )

    @override
    def execute(self) -> r[t.Cli.JsonMapping]:
        """Report operational status required by `s`."""
        status: t.Cli.JsonMapping = {
            c.Cli.DICT_KEY_STATUS: c.Cli.SERVICE_STATUS_OPERATIONAL.value,
            c.Cli.DICT_KEY_SERVICE: c.Cli.CMD_SERVICE_NAME,
        }
        return r[t.Cli.JsonMapping].ok(status)

    def show_config(self) -> r[bool]:
        """Show current configuration.

        Returns:
            r[bool]: True if displayed successfully, or error

        """
        try:
            info_result = self.config_snapshot()
            if info_result.failure:
                return r[bool].fail(
                    c.Cli.ERR_SHOW_CONFIG_FAILED.format(
                        error=info_result.error,
                    ),
                )
            self.logger.info(
                c.Cli.LOG_MSG_CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return r[bool].ok(True)
        except c.Cli.CLI_SAFE_EXCEPTIONS as e:
            return r[bool].fail(
                c.Cli.ERR_SHOW_CONFIG_FAILED.format(
                    error=e,
                ),
            )

    def validate_config(self) -> r[bool]:
        """Validate configuration structure using u directly.

        Returns:
            r[bool]: True if validation passed, or error

        """
        try:
            results = u.Cli.validate_config_structure()
            if results:
                self.logger.info(
                    c.Cli.LOG_MSG_CONFIG_VALIDATION_RESULTS.format(
                        results=results,
                    ),
                )
            return r[bool].ok(True)
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            return r[bool].fail(
                c.Cli.ERR_CONFIG_VALIDATION_FAILED.format(
                    error=e,
                ),
            )


__all__ = ["FlextCliCmd"]
