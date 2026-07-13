"""Private MRO composition for the generic XLSX byte boundary."""

from __future__ import annotations

from .xlsx_archive import FlextCliUtilitiesXlsxArchive
from .xlsx_recalc import FlextCliUtilitiesXlsxRecalc
from .xlsx_renderer import FlextCliUtilitiesXlsxRenderer
from .xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
from .xlsx_style_catalog import FlextCliUtilitiesXlsxStyleCatalog


class FlextCliUtilitiesXlsx(
    FlextCliUtilitiesXlsxRecalc,
    FlextCliUtilitiesXlsxSnapshot,
    FlextCliUtilitiesXlsxRenderer,
    FlextCliUtilitiesXlsxStyleCatalog,
    FlextCliUtilitiesXlsxArchive,
):
    """Compose rendering, snapshot, style-template, and inspection operations."""

    # NOTE (multi-agent, mro-j2yt.1): one MRO path exposes every generic XLSX
    # byte operation; snapshotting does not create a parallel service.


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsx",)
