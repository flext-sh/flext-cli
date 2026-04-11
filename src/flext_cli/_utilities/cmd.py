"""CLI command-service helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import c, m, r
from flext_cli._utilities.configuration import FlextCliUtilitiesConfiguration
from flext_core import p


class FlextCliUtilitiesCmd:
    """Utility helpers for FlextCliCmd service orchestration."""

    @staticmethod
    def cmd_config_snapshot() -> r[m.Cli.ConfigSnapshot]:
        """Return settings snapshot with canonical error mapping."""
        try:
            return r[m.Cli.ConfigSnapshot].ok(
                FlextCliUtilitiesConfiguration.config_snapshot(),
            )
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[m.Cli.ConfigSnapshot].fail(
                c.Cli.ERR_CONFIG_INFO_FAILED.format(error=exc),
            )

    @staticmethod
    def cmd_show_config(logger: p.Logger) -> r[bool]:
        """Resolve and log current settings snapshot."""
        info_result = FlextCliUtilitiesCmd.cmd_config_snapshot()
        if info_result.failure:
            return r[bool].fail(
                c.Cli.ERR_SHOW_CONFIG_FAILED.format(error=info_result.error),
            )
        logger.info(
            c.Cli.LOG_MSG_CONFIG_DISPLAYED,
            settings=info_result.value,
        )
        return r[bool].ok(True)

    @staticmethod
    def cmd_validate_config(logger: p.Logger) -> r[bool]:
        """Validate canonical settings structure and log normalized results."""
        try:
            results = FlextCliUtilitiesConfiguration.validate_config_structure()
            if results:
                logger.info(
                    c.Cli.LOG_MSG_CONFIG_VALIDATION_RESULTS.format(results=results),
                )
            return r[bool].ok(True)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[bool].fail(
                c.Cli.ERR_CONFIG_VALIDATION_FAILED.format(error=exc),
            )


__all__ = ["FlextCliUtilitiesCmd"]
