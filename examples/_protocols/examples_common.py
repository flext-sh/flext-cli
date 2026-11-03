# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
examples/_protocols/examples_common
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from examples import t
from flext_cli import FlextCliProtocols


class ExamplesFlextCliProtocolsExamplesCommon:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class MyAppSettings(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def app_name(self) -> str:
            """Application name."""
            ...

        @property
        def api_key(self) -> str:
            """API key."""
            ...

        @property
        def max_workers(self) -> int:
            """Max workers."""
            ...

        @property
        def timeout(self) -> int:
            """Timeout in seconds."""
            ...

        def display(self, cli: t.CliApi) -> None:
            """Display app settings; uses the canonical CLI settings singleton."""
            ...


__all__: list[str] = [
    "ExamplesFlextCliProtocolsExamplesCommon",
]
