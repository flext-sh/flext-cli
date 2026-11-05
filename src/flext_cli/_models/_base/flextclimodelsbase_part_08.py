"""Typed atomic directory-chain plan model.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from flext_core import m

from flext_cli import t
from flext_cli._models import FlextCliModelsAtomicState


class FlextCliModelsBasePart08:
    """Implementation part for FlextCliModelsBasePart08."""

    class AtomicNativeSelections(m.ContractModel):
        """Native candidate predicates and membership selections of one plan."""

        atomic_queries_message: ClassVar[str] = (
            "atomic native queries require ordered lexical child names"
        )

        queries: tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...] = m.Field(
            default=(),
            description="Consumed native candidate predicates",
        )
        membership_queried: bool = m.Field(
            default=False,
            strict=True,
            description="Whether native planning consumed direct membership",
        )
        membership_queries: tuple[t.StrTuple, ...] = m.Field(
            default=(),
            description="Consumed membership selections, each excluding named children",
        )

        @m.model_validator(mode="after")
        def _validate_native_selections(self) -> Self:
            """Require ordered, unique, lexical child names in every selection.

            Inherited by every plan, so no subclass can skip the contract.

            Returns:
                The validated model instance.

            Raises:
                ValueError: If a membership selection or candidate query is
                    unordered, repeated, or names something other than one child.

            """

            def lexical(name: str) -> bool:
                return name not in {"", ".", ".."} and Path(name).name == name

            if self.membership_queries != tuple(
                sorted(set(self.membership_queries))
            ) or any(
                selection != tuple(sorted(set(selection)))
                or not all(lexical(name) for name in selection)
                for selection in self.membership_queries
            ):
                msg = "atomic membership selections require ordered lexical exclusions"
                raise ValueError(msg)
            if self.queries != tuple(sorted(set(self.queries))) or not all(
                lexical(name) for name, _predicate in self.queries
            ):
                raise ValueError(self.atomic_queries_message)
            return self

    class AtomicDirectoryChainPlan(AtomicNativeSelections):
        """Exact existing anchor plus contiguous directories observed absent.

        Its native selections are consumed beneath the absent parent.
        """

        atomic_queries_message: ClassVar[str] = (
            "atomic directory-chain queries require lexical unique children"
        )

        target: Annotated[Path, m.Field(description="Requested directory path")]
        anchor_path: Annotated[
            Path,
            m.Field(description="Deepest physical existing ancestor"),
        ]
        anchor_device: Annotated[
            int,
            m.Field(ge=0, strict=True, description="Anchor device"),
        ]
        anchor_inode: Annotated[
            int,
            m.Field(ge=0, strict=True, description="Anchor inode"),
        ]
        anchor_ancestry: Annotated[
            tuple[tuple[int, int], ...],
            m.Field(min_length=1, description="Root-to-anchor physical identities"),
        ]
        directories: Annotated[
            tuple[Path, ...],
            m.Field(description="Ordered contiguous paths observed absent"),
        ] = ()

        @m.field_validator("target", "anchor_path")
        @classmethod
        def _validate_paths(cls, value: Path) -> Path:
            return FlextCliModelsAtomicState.validate_atomic_state_path(
                value,
                label="atomic directory-chain",
                allow_root=True,
            )

        @m.field_validator("directories")
        @classmethod
        def _validate_directories(
            cls,
            value: tuple[Path, ...],
        ) -> tuple[Path, ...]:
            return tuple(
                FlextCliModelsAtomicState.validate_atomic_state_path(
                    path,
                    label="atomic directory-chain entry",
                )
                for path in value
            )

        @m.model_validator(mode="after")
        def _validate_topology(self) -> Self:
            if self.anchor_ancestry[-1] != (
                self.anchor_device,
                self.anchor_inode,
            ) or any(
                isinstance(item, bool) or item < 0
                for identity in self.anchor_ancestry
                for item in identity
            ):
                msg = "atomic directory-chain ancestry is inconsistent"
                raise ValueError(msg)
            chain = (self.anchor_path, *self.directories)
            if any(child.parent != parent for parent, child in pairwise(chain)):
                msg = "atomic directory-chain paths are not contiguous"
                raise ValueError(msg)
            if chain[-1] != self.target:
                msg = "atomic directory-chain does not terminate at its target"
                raise ValueError(msg)
            return self


__all__: list[str] = ["FlextCliModelsBasePart08"]
