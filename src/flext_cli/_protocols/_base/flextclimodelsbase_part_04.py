# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_04
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli import c, t


class FlextCliProtocolsBaseFlextclimodelsbasePart04:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class TableConfig(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def headers(self) -> t.Cli.TableHeaders: ...
        @property
        def title(self) -> str | None: ...
        @property
        def show_header(self) -> bool: ...
        @property
        def table_format(self) -> c.Cli.TabularFormat: ...
        @property
        def table_backend_format(self) -> c.Cli.TabularFormat: ...
        @property
        def floatfmt(self) -> str: ...
        @property
        def numalign(self) -> str: ...
        @property
        def stralign(self) -> str: ...
        @property
        def align(self) -> str: ...
        @property
        def missingval(self) -> str: ...
        @property
        def showindex(self) -> t.Cli.TableShowIndex: ...
        @property
        def colalign(self) -> t.Cli.TableColAlign: ...
        @property
        def disable_numparse(self) -> t.Cli.TableDisableNumparse: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart04",
]
