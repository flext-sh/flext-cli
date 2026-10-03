"""Physical symbolic-link state for guarded namespace operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Self

from flext_cli._models.atomic_state import FlextCliModelsAtomicState
from flext_core import m, t, u


class FlextCliModelsAtomicSymlink:
    """Declarations for a symbolic link and its authenticated parent."""

    class AtomicSymlinkIdentity(m.StrictModel):
        """Complete lstat identity, without following the symbolic link."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)
        mode: Annotated[int, m.Field(ge=0, description="Exact link permission bits.")]
        device: Annotated[int, m.Field(ge=0, description="Link filesystem device.")]
        inode: Annotated[int, m.Field(ge=0, description="Link inode number.")]
        link_count: Annotated[
            int,
            m.Field(ge=1, description="Link inode reference count."),
        ]
        uid: Annotated[int, m.Field(ge=0, description="Link owner user identifier.")]
        gid: Annotated[int, m.Field(ge=0, description="Link owner group identifier.")]
        mtime_ns: Annotated[int, m.Field(description="Link modification timestamp.")]
        ctime_ns: Annotated[int, m.Field(description="Link change timestamp.")]
        file_attributes: Annotated[
            int | None,
            m.Field(description="Platform file attributes."),
        ]
        reparse_tag: Annotated[int | None, m.Field(description="Platform reparse tag.")]

    class AtomicSymlinkState(m.StrictModel):
        """Exact link text and physical identities, or authenticated absence."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)
        path: Annotated[
            Path,
            m.Field(description="Absolute lexical symbolic-link path."),
        ]
        parent_device: Annotated[
            int,
            m.Field(ge=0, description="Physical parent device."),
        ]
        parent_inode: Annotated[
            int,
            m.Field(ge=0, description="Physical parent inode."),
        ]
        target: Annotated[
            Annotated[str, t.StringConstraints(strip_whitespace=False)] | None,
            m.Field(description="Exact readlink text, or None when absent."),
        ]
        identity: Annotated[
            FlextCliModelsAtomicSymlink.AtomicSymlinkIdentity | None,
            m.Field(
                description="Complete physical link identity, or None when absent.",
            ),
        ]

        @u.field_validator("path")
        @classmethod
        def _absolute_path(cls, value: Path) -> Path:
            """Reject relative or traversing identities at the boundary.

            Returns:
                The resulting ``Path``.

            """
            return FlextCliModelsAtomicState.validate_atomic_state_path(
                value,
                label="atomic symlink state",
            )

        @u.model_validator(mode="after")
        def _complete_presence(self) -> Self:
            """Require target text and identity together, including broken links.

            Returns:
                The resulting ``Self``.

            Raises:
                ValueError: If atomic symlink state requires both target and identity or
                    neither; or if atomic symlink target must be nonempty and contain no
                    NUL.

            """
            if (self.target is None) != (self.identity is None):
                msg = (
                    "atomic symlink state requires both target and identity or neither"
                )
                raise ValueError(msg)
            if self.target is not None and (not self.target or "\0" in self.target):
                msg = "atomic symlink target must be nonempty and contain no NUL"
                raise ValueError(msg)
            if self.target is not None:
                self.target.encode("utf-8", errors="strict")
            return self


__all__: list[str] = ["FlextCliModelsAtomicSymlink"]
