"""Scoped read contract for authenticated binary artifact ranges.

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

from typing import Protocol, runtime_checkable


class FlextCliProtocolsAtomicFile:
    """Binary artifact contracts independent of descriptor implementation."""

    @runtime_checkable
    class AtomicFileReader(Protocol):
        """Reader usable only inside its authenticated descriptor context."""

        def read_range(self, offset: int, length: int) -> bytes: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsAtomicFile",)
