"""Centralized typings facade for flext-cli.

- Extends flext-core types
- Add CLI-specific type aliases and Protocols here
"""

from __future__ import annotations

from flext_core.typings import E, F, FlextTypes as CoreFlextTypes, P, R, T, U, V


class FlextTypes(CoreFlextTypes):
    """CLI domain-specific types can extend here."""


__all__ = [
    "E",
    "F",
    "FlextTypes",
    "P",
    "R",
    "T",
    "U",
    "V",
]
