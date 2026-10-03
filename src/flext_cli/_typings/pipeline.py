"""Pipeline type aliases for DAG engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_cli._constants.enums import FlextCliConstantsEnums as ce


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        ce.PipelineStageStatus.OK,
        ce.PipelineStageStatus.SKIPPED,
        ce.PipelineStageStatus.FAILED,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
