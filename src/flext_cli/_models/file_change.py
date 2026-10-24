"""One planned file change shared by every publishing engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Self

from flext_core import m

from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02


class FlextCliModelsFileChange:
    """File change contract, flat in ``m.Cli.*``."""

    class FileChange(m.ArbitraryTypesModel):
        """Observed state plus desired bytes and mode for one file.

        ``desired_content`` of ``None`` deletes the file; publication fails
        when the destination no longer matches ``before``.
        """

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

        path: Annotated[Path, m.Field(description="Absolute destination path")]
        before: Annotated[
            FlextCliModelsBasePart02.AtomicFileState,
            m.Field(description="Destination state observed while planning"),
        ]
        desired_content: Annotated[
            bytes | None,
            m.Field(strict=True, description="Desired bytes, or None to delete"),
        ]
        desired_mode: Annotated[
            int | None,
            m.Field(
                ge=0,
                le=0o7777,
                strict=True,
                description="Desired mode, or None with deletion",
            ),
        ]

        @m.model_validator(mode="after")
        def _validate_change(self) -> Self:
            if not self.path.is_absolute() or self.before.path != self.path:
                msg = f"file change requires its absolute observed path: {self.path}"
                raise ValueError(msg)
            if (self.desired_content is None) != (self.desired_mode is None):
                msg = f"file change bytes and mode must agree: {self.path}"
                raise ValueError(msg)
            return self


__all__: list[str] = ["FlextCliModelsFileChange"]
