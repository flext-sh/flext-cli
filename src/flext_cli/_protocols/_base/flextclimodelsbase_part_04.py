# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_04
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import c, t


class FlextCliProtocolsBaseFlextclimodelsbasePart04:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class TableConfig(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def headers(self) -> t.Cli.TableHeaders:
            """Structural member projected from the owning model.

            Table headers (string like 'keys', 'firstrow' or sequence of header
            names).
            """
            ...

        @property
        def title(self) -> str | None:
            """Optional title printed before the rendered table."""
            ...

        @property
        def show_header(self) -> bool:
            """Whether to show table header."""
            ...

        @property
        def table_format(self) -> c.Cli.TabularFormat:
            """Table format enum-derived literal authority."""
            ...

        @property
        def table_backend_format(self) -> c.Cli.TabularFormat:
            """Canonical backend format used by table rendering."""
            ...

        @property
        def floatfmt(self) -> str:
            """Float format string."""
            ...

        @property
        def numalign(self) -> str:
            """Number alignment (right, center, left, decimal)."""
            ...

        @property
        def stralign(self) -> str:
            """String alignment (left, center, right)."""
            ...

        @property
        def align(self) -> str:
            """General alignment (left, center, right, decimal)."""
            ...

        @property
        def missingval(self) -> str:
            """String to use for missing values."""
            ...

        @property
        def showindex(self) -> t.Cli.TableShowIndex:
            """Whether to show row indices."""
            ...

        @property
        def colalign(self) -> t.Cli.TableColAlign:
            """Per-column alignment (left, center, right, decimal)."""
            ...

        @property
        def disable_numparse(self) -> t.Cli.TableDisableNumparse:
            """Disable number parsing (bool or list of column indices)."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart04",
]
