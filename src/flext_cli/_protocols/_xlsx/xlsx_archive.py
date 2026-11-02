# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_archive
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxArchive:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxArchivePolicy(Protocol):
        """Structural data contract projected from the owning model."""

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
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> t.Cli.XlsxArchiveViolationKind: ...
        @property
        def location(self) -> str: ...
        @property
        def detail(self) -> str: ...

    @runtime_checkable
    class XlsxArchiveInventory(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def members(self) -> tuple[str, ...]: ...
        @property
        def blocked_members(self) -> frozenset[str]: ...
        @property
        def total_uncompressed_bytes(self) -> int: ...
        @property
        def violations(self) -> tuple[p.Cli.XlsxArchiveViolation, ...]: ...

    @runtime_checkable
    class XlsxArchiveInspection(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def member_count(self) -> int: ...
        @property
        def worksheet_count(self) -> int: ...
        @property
        def total_uncompressed_bytes(self) -> int: ...
        @property
        def violations(self) -> tuple[p.Cli.XlsxArchiveViolation, ...]: ...
        @property
        def clean(self) -> bool: ...

    @runtime_checkable
    class XlsxArchiveInspectionRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def policy(self) -> p.Cli.XlsxArchivePolicy: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxArchive",
]
