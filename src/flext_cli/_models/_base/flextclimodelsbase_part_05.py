"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import m, t


class FlextCliModelsBasePart05:
    """Implementation part for FlextCliModelsBasePart05."""

    class SettingsSnapshot(m.Value):
        """Snapshot of current CLI settings information."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(frozen=True, extra="forbid")

        settings_dir: Annotated[str, m.Field(description="Settings directory path")] = (
            ""
        )

        settings_exists: Annotated[
            bool,
            m.Field(description="Whether settings directory exists"),
        ] = False

        settings_readable: Annotated[
            bool,
            m.Field(description="Whether settings directory is readable"),
        ] = False

        settings_writable: Annotated[
            bool,
            m.Field(description="Whether settings directory is writable"),
        ] = False

        timestamp: Annotated[str, m.Field(description="Timestamp of snapshot")] = ""

    class OfficeRenderRequest(m.FrozenModel):
        """Shared request shape of every office-document renderer."""

        template: (
            Annotated[
                bytes,
                m.Field(min_length=1, description="Formatting template bytes."),
            ]
            | None
        ) = m.Field(default=None, description="Optional source office document.")

    class OfficeRenderResult(m.FrozenModel):
        """Shared result shape of every office-document renderer."""

        content: Annotated[
            bytes,
            m.Field(min_length=1, description="Rendered office document bytes."),
        ]


__all__: list[str] = ["FlextCliModelsBasePart05"]
