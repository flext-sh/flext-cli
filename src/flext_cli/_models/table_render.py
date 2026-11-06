"""Parameter objects owned by the plain-text table renderer.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m


class FlextCliModelsTableRender:
    """Table rendering parameter objects exposed through ``m.Cli``."""

    class TableColumnPolicy(m.FrozenModel):
        """Header selection and column alignment overrides of one render."""

        headers: str | tuple[str, ...] = m.Field(
            description="Header mode (``firstrow``/``keys``) or explicit labels.",
        )
        colalign: tuple[str, ...] = m.Field(
            default=(),
            description="Per-column alignment overrides, in column order.",
        )

    class TableLayout(m.FrozenModel):
        """Formatted cells, header labels, widths, and alignments to compose."""

        cells: tuple[tuple[str, ...], ...] = m.Field(
            description="Formatted body cells, one tuple per row.",
        )
        header_labels: tuple[str, ...] = m.Field(
            description="Header labels in column order.",
        )
        widths: tuple[int, ...] = m.Field(
            description="Display width of every column.",
        )
        alignments: tuple[str, ...] = m.Field(
            description="Resolved padding alignment of every column.",
        )


__all__: list[str] = ["FlextCliModelsTableRender"]
