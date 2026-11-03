# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
examples/_protocols/examples_advanced
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from examples import c, t
from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_cli import p


class ExamplesFlextCliProtocolsExamplesAdvanced:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AppSettingsAdvanced(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def database_url(self) -> str:
            """Database URL."""
            ...

        @property
        def redis_url(self) -> str:
            """Redis URL."""
            ...

        @property
        def api_key(self) -> str:
            """API key."""
            ...

        @property
        def environment(self) -> c.DeploymentEnvironment:
            """Deployment environment."""
            ...

        @property
        def max_workers(self) -> int:
            """Max workers."""
            ...

        @property
        def enable_metrics(self) -> bool:
            """Enable metrics."""
            ...

        @property
        def log_level(self) -> str:
            """Log level."""
            ...

        @property
        def temp_dir(self) -> Path:
            """Temp directory."""
            ...

        def validate_to_mapping(self) -> p.Result[Mapping[str, t.JsonValue]]:
            """Validate configuration and return as mapping or failure."""
            ...


__all__: list[str] = [
    "ExamplesFlextCliProtocolsExamplesAdvanced",
]
