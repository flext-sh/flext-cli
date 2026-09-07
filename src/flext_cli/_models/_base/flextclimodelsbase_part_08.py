"""Typed atomic directory-chain plan model."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Self

from flext_cli._models import atomic_state
from flext_core import m, t, u


class FlextCliModelsBase:
    """Implementation part for FlextCliModelsBase."""

    class AtomicDirectoryChainPlan(m.BaseModel):
        """Exact existing anchor plus contiguous directories observed absent."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid", frozen=True, arbitrary_types_allowed=True
        )
        target: Annotated[Path, m.Field(description="Requested directory path")]
        anchor_path: Annotated[
            Path, m.Field(description="Deepest physical existing ancestor")
        ]
        anchor_device: Annotated[
            int, m.Field(ge=0, strict=True, description="Anchor device")
        ]
        anchor_inode: Annotated[
            int, m.Field(ge=0, strict=True, description="Anchor inode")
        ]
        anchor_ancestry: Annotated[
            tuple[tuple[int, int], ...],
            m.Field(min_length=1, description="Root-to-anchor physical identities"),
        ]
        directories: Annotated[
            tuple[Path, ...],
            m.Field(description="Ordered contiguous paths observed absent"),
        ] = ()

        @u.field_validator("target", "anchor_path")
        @classmethod
        def _validate_paths(cls, value: Path) -> Path:
            return atomic_state.validate_atomic_state_path(
                value, label="atomic directory-chain", allow_root=True
            )

        @u.field_validator("directories")
        @classmethod
        def _validate_directories(cls, value: tuple[Path, ...]) -> tuple[Path, ...]:
            return tuple(
                atomic_state.validate_atomic_state_path(
                    path, label="atomic directory-chain entry"
                )
                for path in value
            )

        @u.model_validator(mode="after")
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
            current = self.anchor_path
            for directory in self.directories:
                if directory.parent != current:
                    msg = "atomic directory-chain paths are not contiguous"
                    raise ValueError(msg)
                current = directory
            if current != self.target:
                msg = "atomic directory-chain does not terminate at its target"
                raise ValueError(msg)
            return self


__all__: list[str] = ["FlextCliModelsBase"]
