"""Flext-cli config models (pure Pydantic; no project/flext imports).

Typed, frozen shapes for the ``config/*.yaml`` business-rule SSOT. This module
imports **nothing** but ``pydantic`` — the ``_config.py`` facade validates the
model-less YAML slices into these classes and exposes the ready objects under
``config.Cli``. Adding a new config domain = add a nested model here and a
validated field on ``Root`` (§2.0b reference: cosmos-main ``_models/config.py``).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class FlextCliConfigModels:
    """Namespace of typed flext-cli config models (pure Pydantic)."""

    class FileIteration(BaseModel):
        """Git-aware file-selection policy from ``config/cli.yaml``."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        executable: Annotated[str, Field(min_length=1)]
        timeout_seconds: Annotated[int, Field(gt=0)]
        scope_files_args: Annotated[tuple[str, ...], Field(min_length=1)]
        output_separator: Annotated[str, Field(min_length=1, max_length=1)]
        fallback_excluded_segment_prefixes: Annotated[
            tuple[Annotated[str, Field(min_length=1)], ...], Field(min_length=1)
        ]

    class Cli(BaseModel):
        """CLI identity metadata and generic runtime policy."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        name: str
        version: str
        file_iteration: FlextCliConfigModels.FileIteration

    class Root(BaseModel):
        """Root flext-cli runtime config validated from ``config/*.yaml``."""

        model_config = ConfigDict(frozen=True, extra="ignore")

        Cli: FlextCliConfigModels.Cli


__all__: list[str] = ["FlextCliConfigModels"]
