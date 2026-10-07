"""CLI command-service helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, m, p, r, t


class FlextCliUtilitiesCmd:
    """Utility helpers for FlextCliCmd service orchestration."""

    @staticmethod
    def cmd_status() -> m.Cli.RuntimeStatus:
        """Return the canonical public CLI runtime status model.

        Returns:
            The canonical public CLI runtime status model.

        """
        from flext_core import u
        return m.Cli.RuntimeStatus(
            status=c.Cli.ServiceStatus.OPERATIONAL,
            service=c.Cli.FLEXT_CLI,
            timestamp=u.generate("timestamp"),
            version=c.Cli.CLI_VERSION,
            components=m.Cli.RuntimeComponents(
                settings="available",
                formatters="available",
                prompts="available",
                rules="available",
            ),
        )

    @staticmethod
    def cmd_settings_snapshot() -> p.Result[m.Cli.SettingsSnapshot]:
        """Return the canonical settings snapshot without normalizing failures.

        Returns:
            The canonical settings snapshot without normalizing failures.

        """
        from flext_cli._utilities import FlextCliUtilitiesSettings
        return r[m.Cli.SettingsSnapshot].ok(
            FlextCliUtilitiesSettings.settings_snapshot_model(),
        )

    @staticmethod
    def cmd_show_settings(logger: p.Logger) -> p.Result[bool]:
        """Resolve and log current settings snapshot.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        info_result = FlextCliUtilitiesCmd.cmd_settings_snapshot()
        if info_result.failure:
            return r[bool].fail(
                c.Cli.ERR_SHOW_SETTINGS_FAILED.format(error=info_result.error),
            )
        logger.info(
            c.Cli.LOG_MSG_SETTINGS_DISPLAYED,
            settings=info_result.value.model_dump_json(),
        )
        return r[bool].ok(value=True)

    @staticmethod
    def cmd_validate_settings(logger: p.Logger) -> p.Result[bool]:
        """Validate canonical settings structure and log normalized results.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesSettings
        results = FlextCliUtilitiesSettings.validate_settings_structure()
        if results:
            logger.info(
                c.Cli.LOG_MSG_SETTINGS_VALIDATION_RESULTS.format(results=results),
            )
        return r[bool].ok(value=True)


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCmd"]
