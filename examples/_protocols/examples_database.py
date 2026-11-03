# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
examples/_protocols/examples_database
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli import FlextCliProtocols


class ExamplesFlextCliProtocolsExamplesDatabase:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AdvancedDatabaseConfig(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def host(self) -> str:
            """Database host."""
            ...

        @property
        def port(self) -> int:
            """Database port."""
            ...

        @property
        def name(self) -> str:
            """Database name."""
            ...

        @property
        def username(self) -> str:
            """Database username."""
            ...

        @property
        def password(self) -> str:
            """Database password."""
            ...

        @property
        def ssl_enabled(self) -> bool:
            """Enable SSL."""
            ...

        @property
        def connection_pool(self) -> int:
            """Connection pool size."""
            ...


__all__: list[str] = [
    "ExamplesFlextCliProtocolsExamplesDatabase",
]
