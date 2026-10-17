"""Scoped read contract for authenticated binary artifact ranges.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import t


class FlextCliProtocolsAtomicFile:
    """Binary artifact contracts independent of descriptor implementation."""

    @runtime_checkable
    class AtomicFileReader(Protocol):
        """Reader usable only inside its authenticated descriptor context."""

        def read_range(self, offset: int, length: int) -> bytes: ...


__all__: t.VariadicTuple[str] = ("FlextCliProtocolsAtomicFile",)
