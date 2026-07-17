"""Public-shape protocols for the private XLSX byte boundary."""

from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING


from ._xlx.xlsx_archive import FlextCliProtocolsXlsxArchive
from ._xlx.xlsx_rules import FlextCliProtocolsXlsxRules
from ._xlx.xlsx_snapshot import FlextCliProtocolsXlsxSnapshot
from ._xlx.xlsx_workbook import FlextCliProtocolsXlsxWorkbook

if TYPE_CHECKING:
    from flext_core import p
    from flext_cli._typings.xlsx import FlextCliTypesXlsx as tx


class FlextCliProtocolsXlsx(
    FlextCliProtocolsXlsxArchive,
    FlextCliProtocolsXlsxSnapshot,
    FlextCliProtocolsXlsxWorkbook,
    FlextCliProtocolsXlsxRules,
):
    """Consumer protocols for plans, requests, results, and services."""

    # mro-wkii.17.26 (codex): all public XLSX relationships are expressed by
    # sibling p contracts; concrete m models never participate in p composition.
    # NOTE (multi-agent, mro-j2yt.1): protocol properties retain the exact
    # source model objects; no dump, mapping, or adapter DTO is introduced.
    @runtime_checkable
    class XlsxSheetPlan(Protocol):
        @property
        def name(self) -> str: ...

    @runtime_checkable
    class XlsxWorkbookPlan(Protocol):
        @property
        def sheets(self) -> tuple[FlextCliProtocolsXlsx.XlsxSheetPlan, ...]: ...

        @property
        def full_calculation_on_load(self) -> bool: ...

    @runtime_checkable
    class XlsxRenderRequest(Protocol):
        @property
        def template(self) -> bytes | None: ...

        @property
        def plan(self) -> FlextCliProtocolsXlsx.XlsxWorkbookPlan: ...

    @runtime_checkable
    class XlsxRenderResult(Protocol):
        @property
        def content(self) -> bytes: ...

        @property
        def plan(self) -> FlextCliProtocolsXlsx.XlsxWorkbookPlan: ...

    @runtime_checkable
    class XlsxParseRangeRequest(Protocol):
        @property
        def reference(self) -> str: ...

    @runtime_checkable
    class XlsxCellRange(Protocol):
        @property
        def first(self) -> FlextCliProtocolsXlsx.XlsxCellAddress: ...

        @property
        def last(self) -> FlextCliProtocolsXlsx.XlsxCellAddress: ...

    # mro-j2yt.1 (xlsx_reference_api): public structural formatting boundary.
    @runtime_checkable
    class XlsxFormatReferenceRequest(Protocol):
        @property
        def area(self) -> FlextCliProtocolsXlsx.XlsxCellRange: ...

        @property
        def sheet(self) -> str | None: ...

        @property
        def absolute(self) -> bool: ...

        @property
        def collapse_single_cell(self) -> bool: ...

    @runtime_checkable
    class XlsxReference(Protocol):
        @property
        def reference(self) -> str: ...

    @runtime_checkable
    class XlsxArchivePolicy(Protocol):
        @property
        def max_members(self) -> int: ...

        @property
        def max_member_uncompressed_bytes(self) -> int: ...

        @property
        def max_total_uncompressed_bytes(self) -> int: ...

        @property
        def forbidden_members(self) -> frozenset[str]: ...

        @property
        def forbidden_prefixes(self) -> tuple[str, ...]: ...

        @property
        def forbidden_worksheet_tags(self) -> frozenset[str]: ...

        @property
        def required_worksheet_count(self) -> int | None: ...

        @property
        def reject_defined_names(self) -> bool: ...

        @property
        def reject_style_protection(self) -> bool: ...

        @property
        def allowed_locked_tokens(self) -> frozenset[str | None]: ...

        @property
        def allowed_hidden_tokens(self) -> frozenset[str | None]: ...

    @runtime_checkable
    class XlsxArchiveViolation(Protocol):
        @property
        def kind(self) -> tx.XlsxArchiveViolationKind: ...

        @property
        def location(self) -> str: ...

        @property
        def detail(self) -> str: ...

    @runtime_checkable
    class XlsxArchiveInspection(Protocol):
        @property
        def member_count(self) -> int: ...

        @property
        def worksheet_count(self) -> int: ...

        @property
        def total_uncompressed_bytes(self) -> int: ...

        @property
        def violations(
            self,
        ) -> tuple[FlextCliProtocolsXlsx.XlsxArchiveViolation, ...]: ...

        @property
        def clean(self) -> bool: ...

    @runtime_checkable
    class XlsxArchiveInspectionRequest(Protocol):
        @property
        def source(self) -> bytes: ...

        @property
        def policy(self) -> FlextCliProtocolsXlsx.XlsxArchivePolicy: ...

    @runtime_checkable
    class XlsxStyleCatalogRequest(Protocol):
        @property
        def source(self) -> bytes: ...

        @property
        def style_name_prefix(self) -> str: ...

    @runtime_checkable
    class XlsxStyleTemplateRequest(XlsxStyleCatalogRequest, Protocol): ...

    @runtime_checkable
    class XlsxStyleMapEntry(Protocol):
        @property
        def source_style_id(self) -> int: ...

        @property
        def style_name(self) -> str: ...

    @runtime_checkable
    class XlsxNamedStyleSpec(Protocol):
        @property
        def name(self) -> str: ...

        @property
        def visual(self) -> p.BaseModel: ...

    @runtime_checkable
    class XlsxStyleCatalog(Protocol):
        @property
        def style_map(self) -> tuple[FlextCliProtocolsXlsx.XlsxStyleMapEntry, ...]: ...

        @property
        def styles(self) -> tuple[FlextCliProtocolsXlsx.XlsxNamedStyleSpec, ...]: ...

    @runtime_checkable
    class XlsxStyleTemplateResult(Protocol):
        @property
        def content(self) -> bytes: ...

        @property
        def style_map(self) -> tuple[FlextCliProtocolsXlsx.XlsxStyleMapEntry, ...]: ...

    @runtime_checkable
    class XlsxService(FlextCliProtocolsXlsxSnapshot.XlsxSnapshotService, Protocol):
        def xlsx_parse_range(
            self, request: FlextCliProtocolsXlsx.XlsxParseRangeRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxCellRange]: ...

        def xlsx_format_reference(
            self, request: FlextCliProtocolsXlsx.XlsxFormatReferenceRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxReference]: ...

        def xlsx_render(
            self, request: FlextCliProtocolsXlsx.XlsxRenderRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxRenderResult]: ...

        def xlsx_inspect(
            self, request: FlextCliProtocolsXlsx.XlsxArchiveInspectionRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxArchiveInspection]: ...

        def xlsx_style_catalog(
            self, request: FlextCliProtocolsXlsx.XlsxStyleCatalogRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxStyleCatalog]: ...

        def xlsx_style_template(
            self, request: FlextCliProtocolsXlsx.XlsxStyleTemplateRequest
        ) -> p.Result[FlextCliProtocolsXlsx.XlsxStyleTemplateResult]: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsx",)
