"""FlextCliConfig — frozen config singleton for flext-cli (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``Cli:`` key and
are exposed through the open ``config.Cli`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.Cli.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from flext_core import FlextConfig


class _CliNamespace(BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = ConfigDict(extra="allow", frozen=True)


class FlextCliConfig(FlextConfig):
    """Cli config auto-loaded model-less from ``config/*.yaml``."""

    Cli: _CliNamespace = _CliNamespace()


config: FlextCliConfig = FlextCliConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_cli import config``."""

__all__: list[str] = ["FlextCliConfig", "config"]
