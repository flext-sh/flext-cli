"""FLEXT CLI Protocols - Centralized interface contracts for CLI library.

This module centralizes protocol interfaces for the `flext-cli` library to avoid
duplication and to provide a single source of truth, following SOLID and PEP8
standards. These protocols are designed to be used by concrete implementations
across the CLI library and related ecosystem projects.

Quality standards:
- Python 3.13 typing and runtime-checkable protocols
- flext-core FlextResult for all operations that can fail
- No duplication of contracts across modules

Copyright (c) 2025 FLEXT Team
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextResult


@runtime_checkable
class FlextConfigProvider(Protocol):
    """Protocol for configuration providers in hierarchical configuration.

    Implementations provide access to configuration values with an explicit
    numeric priority used to determine precedence in a configuration hierarchy.
    """

    def get_config(self, key: str, default: object | None = None) -> FlextResult[object]:
        """Get configuration value by dot-notated key."""
        ...

    def get_priority(self) -> int:
        """Return provider priority (lower value = higher precedence)."""
        ...

    def get_all(self) -> dict[str, object]:
        """Return all available configuration values for this provider."""
        ...


__all__ = [
    "FlextConfigProvider",
]
