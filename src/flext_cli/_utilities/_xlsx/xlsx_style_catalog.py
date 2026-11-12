"""Generic style catalog extraction and format-template emission.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterator
from hashlib import sha256

from flext_core import r
from openpyxl import Workbook
from openpyxl.cell.cell import Cell, MergedCell

from flext_cli import m, p
from flext_cli._utilities._xlsx.xlsx_style_codec import FlextCliUtilitiesXlsxStyleCodec
from flext_cli._utilities._xlsx.xlsx_workbook_io import FlextCliUtilitiesXlsxWorkbookIo


class FlextCliUtilitiesXlsxStyleCatalog(
    FlextCliUtilitiesXlsxStyleCodec,
    FlextCliUtilitiesXlsxWorkbookIo,
):
    """Own visual deduplication, deterministic names, and blank templates."""

    # NOTE (multi-agent, mro-j2yt.1): cells identify source style IDs through
    # public openpyxl properties; protection never enters the visual signature.
    @staticmethod
    def _style_name(prefix: str, visual: p.Cli.XlsxVisualStyleSpec) -> str:
        digest = sha256(repr(visual).encode("utf-8")).hexdigest()[:16]
        return f"{prefix}_{digest}"

    @staticmethod
    def _source_style_id(item: p.Cli.XlsxSourceVisualStyle) -> int:
        """Return the deterministic source-style sort key.

        Returns:
            The deterministic source-style sort key.

        """
        return item.source_style_id

    @classmethod
    def _source_visuals(
        cls,
        source: bytes,
    ) -> p.Result[tuple[p.Cli.XlsxSourceVisualStyle, ...]]:
        workbook_result = cls._load_workbook(source)
        if workbook_result.failure:
            return r[tuple[p.Cli.XlsxSourceVisualStyle, ...]].from_failure(
                workbook_result,
            )
        source_styles: list[p.Cli.XlsxSourceVisualStyle] = []
        for cell in cls._distinct_style_cells(workbook_result.value):
            visual_result = cls._visual_from_styleable(cell)
            if visual_result.failure:
                return r[tuple[p.Cli.XlsxSourceVisualStyle, ...]].from_failure(
                    visual_result,
                )
            source_styles.append(
                m.Cli.XlsxSourceVisualStyle.model_validate({
                    "source_style_id": cell.style_id,
                    "visual": visual_result.value,
                }),
            )
        ordered = tuple(sorted(source_styles, key=cls._source_style_id))
        return r[tuple[p.Cli.XlsxSourceVisualStyle, ...]].ok(ordered)

    @staticmethod
    def _distinct_style_cells(workbook: Workbook) -> Iterator[Cell | MergedCell]:
        """Yield the first used cell of every distinct source style, in order.

        Yields:
            Each cell carrying content, style, a comment, or a hyperlink whose
            style identifier was not yielded before.

        """
        seen: set[int] = set()
        for worksheet in workbook.worksheets:
            for row in worksheet.iter_rows():
                for cell in row:
                    if cell.style_id in seen or not (
                        FlextCliUtilitiesXlsxStyleCatalog._cell_in_use(cell)
                    ):
                        continue
                    seen.add(cell.style_id)
                    yield cell

    @staticmethod
    def _cell_in_use(cell: Cell | MergedCell) -> bool:
        """Report whether one cell carries a value, style, comment, or link.

        Returns:
            Whether the cell contributes a source visual style.

        """
        if cell.value is not None or cell.has_style:
            return True
        return cell.comment is not None or cell.hyperlink is not None

    @classmethod
    def extract_style_catalog(
        cls,
        request: p.Cli.XlsxStyleCatalogRequest,
    ) -> p.Result[p.Cli.XlsxStyleCatalog]:
        """Extract all cell-used visual styles and deduplicate them.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxStyleCatalog]``.

        """
        return cls._style_catalog(request)

    @classmethod
    def _style_catalog(
        cls,
        request: p.Cli.XlsxStyleCatalogRequest,
    ) -> p.Result[p.Cli.XlsxStyleCatalog]:
        source_result = cls._source_visuals(request.source)
        if source_result.failure:
            return r[p.Cli.XlsxStyleCatalog].from_failure(source_result)
        styles: tuple[p.Cli.XlsxNamedStyleSpec, ...] = ()
        style_map: tuple[p.Cli.XlsxStyleMapEntry, ...] = ()
        for source in source_result.value:
            existing = next(
                (style for style in styles if style.visual == source.visual),
                None,
            )
            if existing is None:
                existing = m.Cli.XlsxNamedStyleSpec(
                    name=cls._style_name(request.style_name_prefix, source.visual),
                    visual=m.Cli.XlsxVisualStyleSpec.model_validate(source.visual),
                )
                if any(style.name == existing.name for style in styles):
                    return r[p.Cli.XlsxStyleCatalog].fail(
                        f"Deterministic style-name collision: {existing.name}",
                    )
                styles = (*styles, existing)
            style_map = (
                *style_map,
                m.Cli.XlsxStyleMapEntry(
                    source_style_id=source.source_style_id,
                    style_name=existing.name,
                ),
            )
        return r[p.Cli.XlsxStyleCatalog].ok(
            m.Cli.XlsxStyleCatalog(style_map=style_map, styles=styles),
        )

    @classmethod
    def build_style_template(
        cls,
        request: p.Cli.XlsxStyleTemplateRequest,
    ) -> p.Result[p.Cli.XlsxStyleTemplateResult]:
        """Emit a blank workbook containing only deduplicated visual styles.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxStyleTemplateResult]``.

        """
        catalog_result = cls._style_catalog(
            m.Cli.XlsxStyleCatalogRequest(
                source=request.source,
                style_name_prefix=request.style_name_prefix,
            ),
        )
        if catalog_result.failure:
            return r[p.Cli.XlsxStyleTemplateResult].from_failure(catalog_result)
        catalog = catalog_result.value
        workbook = cls._new_workbook()
        for spec in catalog.styles:
            workbook.add_named_style(cls._named_style(spec))
        content_result = cls._serialize_workbook(workbook)
        if content_result.failure:
            return r[p.Cli.XlsxStyleTemplateResult].from_failure(content_result)
        return r[p.Cli.XlsxStyleTemplateResult].ok(
            m.Cli.XlsxStyleTemplateResult(
                content=content_result.value,
                style_map=catalog.style_map,
            ),
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxStyleCatalog",)
