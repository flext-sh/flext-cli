"""Generic data-report helpers shared through ``u.Cli``.

One owner for every CLI domain that needs to present homogeneous tabular data:
the caller builds a typed ``m.Cli.DataReportRequest`` and this facade renders it
with the canonical table engine. No domain re-implements column building or
formatting.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, m, p
from flext_cli._utilities.tables import FlextCliUtilitiesTables


class FlextCliUtilitiesReport:
    """Canonical generic data report exposed through ``u.Cli.report_*``."""

    @staticmethod
    def report_render(request: m.Cli.DataReportRequest) -> p.Result[str]:
        """Render one data report as a deterministic plain-text table.

        Returns:
            The resulting ``p.Result[str]``.

        """
        config = m.Cli.TableConfig(
            headers=tuple(request.columns),
            title=request.title or None,
            show_header=request.show_header,
            table_format=c.Cli.TabularFormat(request.table_format),
        )
        return FlextCliUtilitiesTables.tables_render(tuple(request.rows), config)


__all__: list[str] = ["FlextCliUtilitiesReport"]
