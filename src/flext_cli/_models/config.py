"""Flext-cli config models (m facade).

Typed, frozen shapes for the ``config/*.yaml`` business-rule SSOT. The models
are declared natively by the layer-zero owner ``flext_cli.config``; this
namespace re-publishes them for the ``m.Cli`` composition so model consumers
keep one stable surface (§2.0b).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliConfig


class FlextCliConfigModels:
    """Namespace of typed flext-cli config models (m facade)."""

    Cli = FlextCliConfig.CliModel
    ProcessIsolation = FlextCliConfig.ProcessIsolationModel
    Root = FlextCliConfig.Root


__all__: list[str] = ["FlextCliConfigModels"]
