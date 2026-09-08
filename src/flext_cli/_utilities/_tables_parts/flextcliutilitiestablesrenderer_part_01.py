"""Plain-text table rendering engine for the CLI tables facade."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from flext_cli import c, m, t

_EMPTY: Final[str] = ""
_GAP: Final[str] = "  "
_TSV_GAP: Final[str] = "\t"
_ROW_GLYPH: Final[str] = "-"
_ROW_EDGE: Final[str] = "+"
_COLUMN_EDGE: Final[str] = "|"
_INDEX_HEADER: Final[str] = ""
_PAD_METHODS: Final[dict[str, str]] = {
    "left": "ljust",
    "right": "rjust",
    "center": "center",
}
_DECIMAL_ALIASES: Final[frozenset[str]] = frozenset({"decimal", "right"})
_SHAPES: Final[dict[str, str]] = {
    c.Cli.TabularFormat.PLAIN: "plain",
    c.Cli.TabularFormat.TSV: "tsv",
    c.Cli.TabularFormat.GRID: "grid",
    c.Cli.TabularFormat.FANCY_GRID: "grid",
    c.Cli.TabularFormat.PIPE: "pipe",
    c.Cli.TabularFormat.RST: "rst",
}
_SHAPE_SIMPLE: Final[str] = "simple"
_RST_GLYPH: Final[str] = "="


class FlextCliUtilitiesTablesRenderer:
    """Render normalized table rows to deterministic plain-text tables."""

    @staticmethod
    def _format_cell(value: t.JsonPayload, floatfmt: str, missingval: str) -> str:
        if value is None:
            return missingval
        if isinstance(value, float):
            return format(value, floatfmt)
        return str(value)

    @staticmethod
    def _pad(cell: str, width: int, alignment: str) -> str:
        method = _PAD_METHODS.get(alignment, "ljust")
        return getattr(cell, method)(width)

    @staticmethod
    def _is_numeric(cell: str) -> bool:
        try:
            float(cell)
        except ValueError:
            return False
        return True

    @classmethod
    def _header_labels(
        cls, rows: Sequence[t.Cli.TableRow], headers: str | t.StrSequence
    ) -> list[str]:
        if headers == "firstrow" and rows:
            return [str(cell) for cell in rows[0]]
        if headers == "keys" and rows and isinstance(rows[0], Mapping):
            return [str(key) for key in rows[0]]
        if isinstance(headers, str):
            return []
        return list(headers)

    @classmethod
    def _column_alignments(
        cls,
        column_count: int,
        numeric_columns: set[int],
        *,
        colalign: t.SequenceOf[str],
        settings: m.Cli.TableConfig,
    ) -> list[str]:
        alignments: list[str] = []
        for index in range(column_count):
            override = colalign[index] if index < len(colalign) else _EMPTY
            if override:
                resolved = "right" if override in _DECIMAL_ALIASES else override
            elif index in numeric_columns:
                resolved = (
                    "right"
                    if settings.numalign in _DECIMAL_ALIASES
                    else settings.numalign
                )
            else:
                resolved = settings.stralign
            alignments.append(resolved if resolved in _PAD_METHODS else "left")
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
        cls, cells: list[list[str]], *, settings: m.Cli.TableConfig
    ) -> set[int]:
        if settings.disable_numparse is True or not cells:
            return set()
        skipped = (
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
        headers: str | t.StrSequence,
        *,
        colalign: t.SequenceOf[str],
        settings: m.Cli.TableConfig,
    ) -> str:
        """Render normalized rows with the configured tabular format shape."""
        header_labels = cls._header_labels(rows, headers)
        data_rows = rows[1:] if headers == "firstrow" and rows else rows
        indexed_labels, indexed_rows = cls._apply_index(data_rows, settings)
        if indexed_labels is not None:
            header_labels = [*indexed_labels, *header_labels]
            data_rows = indexed_rows
        column_count = max(
            [len(header_labels), *(len(row) for row in data_rows)], default=0
        )
        cells = cls._prepare_cells(data_rows, column_count, settings=settings)
        numeric_columns = cls._numeric_columns(cells, settings=settings)
        alignments = cls._column_alignments(
            column_count, numeric_columns, colalign=colalign, settings=settings
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
        data_rows: Sequence[t.Cli.TableRow], settings: m.Cli.TableConfig
    ) -> tuple[list[str] | None, list[list[t.JsonPayload]]]:
        if settings.showindex is True:
            return (
                [_INDEX_HEADER],
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
    def _compose(
        cls,
        cells: list[list[str]],
        header_labels: list[str],
        widths: list[int],
        alignments: list[str],
        *,
        settings: m.Cli.TableConfig,
    ) -> str:
        shape = _SHAPES.get(settings.table_format, _SHAPE_SIMPLE)
        lines: list[str] = []
        if shape == "pipe":
            if header_labels and settings.show_header:
                lines.extend([
                    _COLUMN_EDGE
                    + _COLUMN_EDGE.join(
                        f" {cls._pad(label, widths[index], alignments[index])} "
                        for index, label in enumerate(header_labels)
                    )
                    + _COLUMN_EDGE,
                    _COLUMN_EDGE
                    + _COLUMN_EDGE.join(f" {_ROW_GLYPH * width} " for width in widths)
                    + _COLUMN_EDGE,
                ])
            lines.extend(
                _COLUMN_EDGE
                + _COLUMN_EDGE.join(
                    f" {cls._pad(cell, widths[index], alignments[index])} "
                    for index, cell in enumerate(row)
                )
                + _COLUMN_EDGE
                for row in cells
            )
            return "\n".join(lines)
        if shape == "tsv":
            if header_labels and settings.show_header:
                lines.append(_TSV_GAP.join(header_labels))
            lines.extend(_TSV_GAP.join(row) for row in cells)
            return "\n".join(lines)
        border = (
            _ROW_EDGE
            + _ROW_EDGE.join(_ROW_GLYPH * (width + 2) for width in widths)
            + _ROW_EDGE
        )
        rst_rule = _RST_GLYPH * (sum(widths) + 2 * (len(widths) - 1))
        if shape == "grid":
            lines.append(border)
        if header_labels and settings.show_header:
            lines.append(
                _GAP.join(
                    cls._pad(label, widths[index], alignments[index])
                    for index, label in enumerate(header_labels)
                )
            )
            if shape == "simple":
                lines.append(_GAP.join(_ROW_GLYPH * width for width in widths))
            elif shape == "grid":
                lines.append(border)
            elif shape == "rst":
                lines.append(rst_rule)
        lines.extend(
            _GAP.join(
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
