"""Command execution and configuration bridge for flext-.

Encapsulates the bridge between registered commands, file utilities, and configuration
helpers using `r` for predictable success/failure handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_cli import (
    FlextCliServiceBase,
    c,
    m,
    t,
    u,
)
from flext_core import r


class FlextCliCmd(FlextCliServiceBase):
    """Execute registered CLI commands and expose execution metadata.

    Extends FlextCliServiceBase for consistent logging and container access.
    Delegates config operations to u.Cli.ConfigOps.
    Railway-Oriented Programming via r for composable error handling.
    """

    @staticmethod
    def get_config_info() -> r[m.Cli.ConfigSnapshot]:
        """Get configuration information using u directly."""
        return u.try_(
            u.Cli.ConfigOps.get_config_info,
        ).map_error(
            lambda e: c.Cli.ErrorMessages.CONFIG_INFO_FAILED.format(
                error=e,
            ),
        )

    @override
    def execute(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Report operational status required by `FlextService`."""
        return r[Mapping[str, t.Cli.JsonValue]].ok({
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.CmdDefaults.SERVICE_NAME,
        })

    def show_config(self) -> r[bool]:
        """Show current configuration.

        Returns:
            r[bool]: True if displayed successfully, or error

        """
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return r[bool].fail(
                    c.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error,
                    ),
                )
            self.logger.info(
                c.Cli.LogMessages.CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return r[bool].ok(value=True)
        except c.Cli.CLI_SAFE_EXCEPTIONS as e:
            return r[bool].fail(
                c.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                    error=e,
                ),
            )

    def validate_config(self) -> r[bool]:
        """Validate configuration structure using u directly.

        Returns:
            r[bool]: True if validation passed, or error

        """
        try:
            results = u.Cli.ConfigOps.validate_config_structure()
            if results:
                self.logger.info(
                    c.Cli.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results,
                    ),
                )
            return r[bool].ok(value=True)
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_VALIDATION_FAILED.format(
                    error=e,
                ),
            )


__all__ = ["FlextCliCmd"]
