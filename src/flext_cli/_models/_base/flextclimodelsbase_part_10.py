"""Typed descriptor-authenticated atomic publication models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar, Self

from flext_core import m

from flext_cli import t
from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02


class FlextCliModelsBasePart10:
    """Implementation part for FlextCliModelsBasePart10."""

    class AtomicDirectoryQueryEffects(m.BaseModel):
        """Caller-elected query authority and authenticated publication effects."""

        files: t.VariadicTuple[
            t.Pair[
                FlextCliModelsBasePart02.AtomicFileState,
                FlextCliModelsBasePart02.AtomicFileState,
            ]
        ] = m.Field(
            default=(), description="Authenticated file effects in this boundary"
        )
        membership_policy: t.StrTuple = m.Field(
            description="Canonical membership policy elected independently of receipts"
        )

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

        @m.model_validator(mode="after")
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
