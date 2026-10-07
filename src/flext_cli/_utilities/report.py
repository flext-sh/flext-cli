"""Generic data-report helpers shared through ``u.Cli``.

One owner for every CLI domain that needs to present homogeneous tabular data:
the caller builds a typed ``m.Cli.DataReportRequest`` and this facade renders it
with the canonical table engine or emits it as JSON. No domain re-implements
column building, formatting or emission.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, m, p, r


class FlextCliUtilitiesReport:
    """Canonical generic data report exposed through ``u.Cli.report_*``."""

    @staticmethod
    def report_render(request: m.Cli.DataReportRequest) -> p.Result[str]:
        """Render one data report as a deterministic plain-text table.

        Returns:
            The resulting ``p.Result[str]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesTables
        config = m.Cli.TableConfig(
            headers=tuple(request.columns),
            title=request.title or None,
            show_header=request.show_header,
            table_format=c.Cli.TabularFormat(request.table_format),
        )
        return FlextCliUtilitiesTables.tables_render(tuple(request.rows), config)

    @staticmethod
    def report_emit(
        request: m.Cli.DataReportRequest,
        *,
        json_output: bool,
    ) -> p.Result[bool]:
        """Emit one data report as canonical JSON or as a rendered table.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesOutput
        if json_output:
            FlextCliUtilitiesOutput.emit_raw(request.model_dump_json(indent=2) + "\n")
            return r[bool].ok(value=True)
        rendered = FlextCliUtilitiesReport.report_render(request)
        if rendered.failure:
            return r[bool].from_failure(rendered)
        FlextCliUtilitiesOutput.emit_raw(f"{rendered.value}\n")
        if request.message:
            FlextCliUtilitiesOutput.emit_raw(f"{request.message}\n")
        return r[bool].ok(value=True)


__all__: list[str] = ["FlextCliUtilitiesReport"]
