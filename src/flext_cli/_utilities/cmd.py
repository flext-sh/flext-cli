"""CLI command-service helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import u

from flext_cli import c, m, p, t


class FlextCliUtilitiesCmd:
    """Utility helpers for the CLI runtime status shared by every service."""

    @staticmethod
    def cmd_status() -> p.Cli.RuntimeStatus:
        """Return the canonical public CLI runtime status model.

        Returns:
            The canonical public CLI runtime status model.

        """
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


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCmd"]
