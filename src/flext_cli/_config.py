"""FlextCliConfig — frozen config singleton for flext-cli (ADR-005 §7).

Model-backed: business rules live in ``config/*.yaml`` and are validated into
typed namespaces at singleton construction. Access is
``config.Cli.<key>`` / ``config.ProcessIsolation.<key>`` — never a model-less
dict subscript (§2.2/§2.4).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_core import FlextConfig, m

from flext_cli._models.config import FlextCliModelsConfig


class FlextCliConfig(FlextConfig):
    """Cli config auto-loaded from ``config/*.yaml`` and validated via models."""

    Cli: Annotated[
        FlextCliModelsConfig.Cli,
        m.Field(description="CLI identity metadata from ``config/cli.yaml``."),
    ]

    ProcessIsolation: Annotated[
        FlextCliModelsConfig.ProcessIsolation,
        m.Field(description="Native read-only reference import policy."),
    ]


config: FlextCliConfig = FlextCliConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_cli import config``."""

__all__: list[str] = ["FlextCliConfig", "config"]
