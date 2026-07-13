"""Console Output - Format report tables through the public CLI facade.

WHEN TO USE THIS:
- Need ASCII/tabular output for logs, files, or terminal reports
- Want one public helper that stays aligned with the CLI facade

FLEXT-CLI PROVIDES:
- cli.format_table() - Format typed rows as strings with the requested style

HOW TO USE IN YOUR CLI:
Pass typed rows to export_report() and reuse the returned table string wherever you
need human-readable output.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import c, cli, p, t


def export_report(
    data: t.SequenceOf[t.Cli.TableMappingRow],
    format_type: c.Cli.TabularFormat = c.Cli.TabularFormat.TABLE,
) -> p.Result[str]:
    """Create ASCII tables for logs/reports in your app."""
    return cli.format_table(list(data) if data else [], table_format=format_type)
