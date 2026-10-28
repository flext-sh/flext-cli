"""Plain-text table rendering engine for the CLI tables facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Callable, Mapping, Sequence
from typing import ClassVar

from flext_cli import c, m, t


class FlextCliUtilitiesTablesRenderer:
    """Render normalized table rows to deterministic plain-text tables."""

    _EMPTY: ClassVar[str] = ""
    _GAP: ClassVar[str] = "  "
    _TSV_GAP: ClassVar[str] = "\t"
    _ROW_GLYPH: ClassVar[str] = "-"
    _ROW_EDGE: ClassVar[str] = "+"
    _COLUMN_EDGE: ClassVar[str] = "|"
    _INDEX_HEADER: ClassVar[str] = ""
    _PAD_METHODS: ClassVar[Mapping[str, Callable[[str, int], str]]] = {
        "left": str.ljust,
        "right": str.rjust,
        "center": str.center,
    }
    _DECIMAL_ALIASES: ClassVar[frozenset[str]] = frozenset({"decimal", "right"})
    _SHAPES: ClassVar[Mapping[str, str]] = {
        c.Cli.TabularFormat.PLAIN: "plain",
        c.Cli.TabularFormat.TSV: "tsv",
        c.Cli.TabularFormat.GRID: "grid",
        c.Cli.TabularFormat.FANCY_GRID: "grid",
        c.Cli.TabularFormat.PIPE: "pipe",
        c.Cli.TabularFormat.RST: "rst",
    }
    _SHAPE_SIMPLE: ClassVar[str] = "simple"
    _RST_GLYPH: ClassVar[str] = "="

    @staticmethod
    def _format_cell(value: t.JsonPayload, floatfmt: str, missingval: str) -> str:
        if value is None:
            return missingval
        if isinstance(value, float):
            return format(value, floatfmt)
        return str(value)

    @staticmethod
    def _pad(cell: str, width: int, alignment: str) -> str:
        return FlextCliUtilitiesTablesRenderer._PAD_METHODS.get(alignment, str.ljust)(
            cell, width
        )

    @staticmethod
    def _is_numeric(cell: str) -> bool:
        try:
            float(cell)
        except ValueError:
            is_numeric_cell = False
        else:
            is_numeric_cell = True
        return is_numeric_cell

    @classmethod
    def _header_labels(
        cls,
        rows: Sequence[t.Cli.TableRow],
        headers: str | Sequence[str],
    ) -> list[str]:
        if headers == "firstrow" and rows:
            return [str(cell) for cell in rows[0]]
        if headers == "keys" and rows and isinstance(rows[0], Mapping):
            return list(rows[0])
        if isinstance(headers, str):
            return []
        return list(headers)

    @classmethod
    def _column_alignments(
        cls,
        column_count: int,
        numeric_columns: set[int],
        *,
        colalign: Sequence[str],
        settings: m.Cli.TableConfig,
    ) -> list[str]:
        alignments: list[str] = []
        for index in range(column_count):
            override = (
                colalign[index]
                if index < len(colalign)
                else FlextCliUtilitiesTablesRenderer._EMPTY
            )
            if override:
                resolved = (
                    "right"
                    if override in FlextCliUtilitiesTablesRenderer._DECIMAL_ALIASES
                    else override
                )
            elif index in numeric_columns:
                resolved = (
                    "right"
                    if settings.numalign
                    in FlextCliUtilitiesTablesRenderer._DECIMAL_ALIASES
                    else settings.numalign
                )
            else:
                resolved = settings.stralign
            alignments.append(
                resolved
                if resolved in FlextCliUtilitiesTablesRenderer._PAD_METHODS
                else "left"
            )
        return alignments

    @classmethod
    def _row_values(cls, row: t.Cli.TableRow) -> list[t.JsonPayload]:
        if isinstance(row, Mapping):
            return list(row.values())
        return list(row)

    @classmethod
    def _prepare_cells(
        cls,
        data_rows: Sequence[t.Cli.TableRow],
        column_count: int,
        *,
        settings: m.Cli.TableConfig,
    ) -> list[list[str]]:
        return [
            [
                cls._format_cell(value, settings.floatfmt, settings.missingval)
                for value in (
                    cls._row_values(row)
                    + [None] * (column_count - len(cls._row_values(row)))
                )[:column_count]
            ]
            for row in data_rows
        ]

    @classmethod
    def _numeric_columns(
        cls,
        cells: Sequence[Sequence[str]],
        *,
        settings: m.Cli.TableConfig,
    ) -> set[int]:
        if settings.disable_numparse is True or not cells:
            return set()
        skipped: set[int] = (
            set(settings.disable_numparse)
            if isinstance(settings.disable_numparse, list)
            else set()
        )
        return {
            index
            for index in range(len(cells[0]))
            if index not in skipped
            and all(
                (row[index] == settings.missingval) or cls._is_numeric(row[index])
                for row in cells
            )
        }

    @classmethod
    def render(
        cls,
        rows: Sequence[t.Cli.TableRow],
        headers: str | Sequence[str],
        *,
        colalign: Sequence[str],
        settings: m.Cli.TableConfig,
    ) -> str:
        """Render normalized rows with the configured tabular format shape.

        Returns:
            The resulting ``str``.

        """
        header_labels = cls._header_labels(rows, headers)
        data_rows = rows[1:] if headers == "firstrow" and rows else rows
        indexed_labels, indexed_rows = cls._apply_index(data_rows, settings)
        if indexed_labels is not None:
            header_labels = [*indexed_labels, *header_labels]
            data_rows = indexed_rows
        column_count = max(
            [len(header_labels), *(len(row) for row in data_rows)],
            default=0,
        )
        cells = cls._prepare_cells(data_rows, column_count, settings=settings)
        numeric_columns = cls._numeric_columns(cells, settings=settings)
        alignments = cls._column_alignments(
            column_count,
            numeric_columns,
            colalign=colalign,
            settings=settings,
        )
        widths = [
            max([
                len(header_labels[index]) if index < len(header_labels) else 0,
                *(len(row[index]) for row in cells),
            ])
            for index in range(column_count)
        ]
        return cls._compose(cells, header_labels, widths, alignments, settings=settings)

    @staticmethod
    def _apply_index(
        data_rows: Sequence[t.Cli.TableRow],
        settings: m.Cli.TableConfig,
    ) -> tuple[list[str] | None, Sequence[t.Cli.TableRow]]:
        if settings.showindex is True:
            return (
                [FlextCliUtilitiesTablesRenderer._INDEX_HEADER],
                [[str(number + 1), *row] for number, row in enumerate(data_rows)],
            )
        if isinstance(settings.showindex, list):
            return (
                [str(value) for value in settings.showindex],
                [
                    [str(settings.showindex[number]), *row]
                    for number, row in enumerate(data_rows)
                ],
            )
        return None, data_rows

    @classmethod
    def _compose_pipe(
        cls,
        cells: Sequence[Sequence[str]],
        header_labels: Sequence[str],
        widths: Sequence[int],
        alignments: list[str],
        *,
        settings: m.Cli.TableConfig,
    ) -> str:
        """Compose the header, separator, and rows of a pipe table.

        Returns:
            The rendered pipe table.

        """
        lines: list[str] = []
        if header_labels and settings.show_header:
            lines.extend([
                FlextCliUtilitiesTablesRenderer._COLUMN_EDGE
                + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE.join(
                    f" {cls._pad(label, widths[index], alignments[index])} "
                    for index, label in enumerate(header_labels)
                )
                + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE,
                FlextCliUtilitiesTablesRenderer._COLUMN_EDGE
                + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE.join(
                    f" {FlextCliUtilitiesTablesRenderer._ROW_GLYPH * width} "
                    for width in widths
                )
                + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE,
            ])
        lines.extend(
            FlextCliUtilitiesTablesRenderer._COLUMN_EDGE
            + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE.join(
                f" {cls._pad(cell, widths[index], alignments[index])} "
                for index, cell in enumerate(row)
            )
            + FlextCliUtilitiesTablesRenderer._COLUMN_EDGE
            for row in cells
        )
        return "\n".join(lines)

    @staticmethod
    def _compose_tsv(
        cells: Sequence[Sequence[str]],
        header_labels: Sequence[str],
        *,
        settings: m.Cli.TableConfig,
    ) -> str:
        """Compose an unpadded tab-separated header and rows.

        Returns:
            The rendered tab-separated table.

        """
        lines: list[str] = []
        if header_labels and settings.show_header:
            lines.append(FlextCliUtilitiesTablesRenderer._TSV_GAP.join(header_labels))
        lines.extend(
            FlextCliUtilitiesTablesRenderer._TSV_GAP.join(row) for row in cells
        )
        return "\n".join(lines)

    @classmethod
    def _compose(
        cls,
        cells: Sequence[Sequence[str]],
        header_labels: Sequence[str],
        widths: Sequence[int],
        alignments: list[str],
        *,
        settings: m.Cli.TableConfig,
    ) -> str:
        shape = FlextCliUtilitiesTablesRenderer._SHAPES.get(
            settings.table_format, FlextCliUtilitiesTablesRenderer._SHAPE_SIMPLE
        )
        lines: list[str] = []
        if shape == "pipe":
            return cls._compose_pipe(
                cells,
                header_labels,
                widths,
                alignments,
                settings=settings,
            )
        if shape == "tsv":
            return cls._compose_tsv(cells, header_labels, settings=settings)
        border = (
            FlextCliUtilitiesTablesRenderer._ROW_EDGE
            + FlextCliUtilitiesTablesRenderer._ROW_EDGE.join(
                FlextCliUtilitiesTablesRenderer._ROW_GLYPH * (width + 2)
                for width in widths
            )
            + FlextCliUtilitiesTablesRenderer._ROW_EDGE
        )
        rst_rule = FlextCliUtilitiesTablesRenderer._RST_GLYPH * (
            sum(widths) + 2 * (len(widths) - 1)
        )
        if shape == "grid":
            lines.append(border)
        if header_labels and settings.show_header:
            lines.append(
                FlextCliUtilitiesTablesRenderer._GAP.join(
                    cls._pad(label, widths[index], alignments[index])
                    for index, label in enumerate(header_labels)
                ),
            )
            if shape == "simple":
                lines.append(
                    FlextCliUtilitiesTablesRenderer._GAP.join(
                        FlextCliUtilitiesTablesRenderer._ROW_GLYPH * width
                        for width in widths
                    )
                )
            elif shape == "grid":
                lines.append(border)
            elif shape == "rst":
                lines.append(rst_rule)
        lines.extend(
            FlextCliUtilitiesTablesRenderer._GAP.join(
                cls._pad(cell, widths[index], alignments[index])
                for index, cell in enumerate(row)
            )
            for row in cells
        )
        if shape == "grid":
            lines.append(border)
        elif shape == "rst":
            lines.append(rst_rule)
        return "\n".join(lines)


__all__: list[str] = ["FlextCliUtilitiesTablesRenderer"]
