# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_archive
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsXlsxXlsxArchive:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxArchivePolicy(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def max_members(self) -> int:
            """Maximum archive member count."""
            ...

        @property
        def max_member_uncompressed_bytes(self) -> int:
            """Maximum uncompressed member bytes."""
            ...

        @property
        def max_total_uncompressed_bytes(self) -> int:
            """Maximum total uncompressed bytes."""
            ...

        @property
        def forbidden_members(self) -> frozenset[str]:
            """Exact archive members that are forbidden."""
            ...

        @property
        def forbidden_prefixes(self) -> tuple[str, ...]:
            """Forbidden member prefixes."""
            ...

        @property
        def forbidden_worksheet_tags(self) -> frozenset[str]:
            """Forbidden local worksheet XML tags."""
            ...

        @property
        def required_worksheet_count(self) -> int | None:
            """Required worksheet count."""
            ...

        @property
        def reject_defined_names(self) -> bool:
            """Reject workbook defined names."""
            ...

        @property
        def reject_style_protection(self) -> bool:
            """Reject non-default style protection."""
            ...

        @property
        def allowed_locked_tokens(self) -> frozenset[str | None]:
            """Accepted OOXML locked tokens."""
            ...

        @property
        def allowed_hidden_tokens(self) -> frozenset[str | None]:
            """Accepted OOXML hidden tokens."""
            ...

    @runtime_checkable
    class XlsxArchiveViolation(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> t.Cli.XlsxArchiveViolationKind:
            """Violation kind."""
            ...

        @property
        def location(self) -> str:
            """Archive violation location."""
            ...

        @property
        def detail(self) -> str:
            """Violation evidence."""
            ...

    @runtime_checkable
    class XlsxArchiveInventory(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def members(self) -> tuple[str, ...]:
            """Ordered archive members."""
            ...

        @property
        def blocked_members(self) -> frozenset[str]:
            """Members skipped because a safety limit was exceeded."""
            ...

        @property
        def total_uncompressed_bytes(self) -> int:
            """Declared total uncompressed bytes."""
            ...

        @property
        def violations(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxArchive.XlsxArchiveViolation, ...]:
            """Inventory violations."""
            ...

    @runtime_checkable
    class XlsxArchiveInspection(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def member_count(self) -> int:
            """Discovered archive member count."""
            ...

        @property
        def worksheet_count(self) -> int:
            """Discovered worksheet count."""
            ...

        @property
        def total_uncompressed_bytes(self) -> int:
            """Declared total uncompressed bytes."""
            ...

        @property
        def violations(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxArchive.XlsxArchiveViolation, ...]:
            """Policy violations."""
            ...

        @property
        def clean(self) -> bool:
            """Whether no violation was found."""
            ...

    @runtime_checkable
    class XlsxArchiveInspectionRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Workbook archive bytes."""
            ...

        @property
        def policy(self) -> FlextCliProtocolsXlsxXlsxArchive.XlsxArchivePolicy:
            """Inspection policy."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxArchive",
]
