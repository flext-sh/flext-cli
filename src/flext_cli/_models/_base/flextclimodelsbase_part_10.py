"""Typed descriptor-authenticated atomic publication models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar, Self

from flext_cli._models import FlextCliModelsBasePart02
from flext_core import m, u


class FlextCliModelsBasePart10:
    """Implementation part for FlextCliModelsBasePart10."""

    class AtomicFilePublication(m.BaseModel):
        """One guarded live state and its caller-owned staged replacement."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            extra="forbid",
            frozen=True,
            arbitrary_types_allowed=True,
        )
        before: Annotated[
            FlextCliModelsBasePart02.AtomicFileState,
            m.Field(description="Exact destination state observed during preflight"),
        ]
        replacement: Annotated[
            FlextCliModelsBasePart02.AtomicFileState,
            m.Field(description="Exact caller-owned staged replacement state"),
        ]

        @u.model_validator(mode="after")
        def _validate_replacement_state(self) -> Self:
            """Require one complete staged file state or one absent tombstone.

            Returns:
                The resulting ``Self``.

            Raises:
                ValueError: If atomic publication replacement state is incomplete.

            """
            if (self.replacement.content is None) is not (
                self.replacement.mode is None
            ):
                msg = "atomic publication replacement state is incomplete"
                raise ValueError(msg)
            return self


__all__: list[str] = ["FlextCliModelsBasePart10"]
