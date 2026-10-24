"""Frozen descriptor-authenticated snapshots, separate from working selectors.

Physical tree records use the upstream arbitrary-types preset with frozen fields;
mutable query selection belongs to the invocation's utilities, not these models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from flext_core import m

from flext_cli import t
from flext_cli._models import FlextCliModelsAtomicState


class FlextCliModelsBasePart09:
    """Implementation part for FlextCliModelsBasePart09."""

    class AtomicPhysicalTreeEntry(m.ArbitraryTypesModel):
        """One exact regular file, symlink leaf, or physical directory."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

        path: Annotated[Path, m.Field(description="Absolute entry path")]
        kind: Annotated[
            Literal["directory", "file", "symlink"],
            m.Field(description="Physical entry kind"),
        ]
        parent_device: Annotated[
            int,
            m.Field(ge=0, strict=True, description="Physical parent device"),
        ]
        parent_inode: Annotated[
            int,
            m.Field(ge=0, strict=True, description="Physical parent inode"),
        ]
        parent_mount_id: Annotated[
            int,
            m.Field(ge=1, strict=True, description="Physical parent mount ID"),
        ]
        mode: Annotated[
            int,
            m.Field(ge=0, le=0o7777, strict=True, description="Permission bits"),
        ]
        device: Annotated[
            int,
            m.Field(ge=0, strict=True, description="Physical device"),
        ]
        inode: Annotated[int, m.Field(ge=0, strict=True, description="Physical inode")]
        mount_id: Annotated[
            int,
            m.Field(ge=1, strict=True, description="Physical mount ID"),
        ]
        link_count: Annotated[
            int,
            m.Field(ge=1, strict=True, description="Exact link count"),
        ]
        uid: Annotated[int, m.Field(ge=0, strict=True, description="Owner user ID")]
        gid: Annotated[int, m.Field(ge=0, strict=True, description="Owner group ID")]
        mtime_ns: Annotated[
            int,
            m.Field(strict=True, description="Modification timestamp in ns"),
        ]
        ctime_ns: Annotated[
            int,
            m.Field(strict=True, description="Metadata-change timestamp in ns"),
        ]
        file_attributes: Annotated[
            int | None,
            m.Field(ge=0, strict=True, description="Host attributes"),
        ] = None
        link_target: Annotated[
            str | None,
            m.Field(min_length=1, description="Exact symlink target text"),
        ] = None
        reparse_tag: Annotated[
            int | None,
            m.Field(ge=0, strict=True, description="Host reparse tag"),
        ] = None
        size: Annotated[
            int | None,
            m.Field(ge=0, strict=True, description="Regular-file size"),
        ] = None
        sha256: Annotated[
            str | None,
            m.Field(
                pattern=r"^[0-9a-f]{64}$",
                description="Regular-file SHA-256 digest",
            ),
        ] = None

        @m.model_validator(mode="after")
        def _validate_kind_state(self) -> Self:
            FlextCliModelsAtomicState.validate_atomic_state_path(
                self.path,
                label="atomic physical-tree entry",
                allow_root=self.kind == "directory",
            )
            FlextCliModelsAtomicState.validate_non_reparse_state(
                self.file_attributes,
                self.reparse_tag,
                label="atomic physical-tree entry",
            )
            if self.kind != "directory" and self.device != self.parent_device:
                msg = "atomic physical-tree entry crosses its parent device"
                raise ValueError(msg)
            if self.kind != "directory" and self.mount_id != self.parent_mount_id:
                msg = "atomic physical-tree entry crosses its parent mount"
                raise ValueError(msg)
            if self.kind == "file":
                if (
                    self.link_count != 1
                    or self.size is None
                    or self.sha256 is None
                    or self.link_target is not None
                ):
                    msg = (
                        "atomic physical-tree file requires one link, size, and digest"
                    )
                    raise ValueError(msg)
            elif self.kind == "symlink":
                if (
                    self.link_count != 1
                    or self.link_target is None
                    or self.size is not None
                    or self.sha256 is not None
                ):
                    msg = "atomic physical-tree symlink requires one link and target"
                    raise ValueError(msg)
            elif (
                self.size is not None
                or self.sha256 is not None
                or self.link_target is not None
            ):
                msg = "atomic physical-tree directory cannot contain file content state"
                raise ValueError(msg)
            return self

    class AtomicDirectoryName(m.ContractModel):
        """One captured directory election without reading any child payload."""

        name: Annotated[
            str, m.Field(min_length=1, strict=True, description="Lexical child name")
        ]
        kind: Literal["directory", "file", "symlink", "other"] = m.Field(
            description="Native physical entry kind"
        )
        version_key: t.VariadicTuple[int] = m.Field(
            description="Descriptor-authenticated native entry version"
        )
        link_target: str | None = m.Field(
            default=None, description="Literal target of a physical symlink"
        )

        @m.model_validator(mode="after")
        def _validate_leaf(self) -> Self:
            if self.name in {".", ".."} or Path(self.name).name != self.name:
                msg = "atomic directory child must be one lexical name"
                raise ValueError(msg)
            if (self.kind == "symlink") != (self.link_target is not None):
                msg = "atomic directory symlink must carry its literal target"
                raise ValueError(msg)
            return self

    class AtomicDirectoryInventory(m.ContractModel):
        """One physical directory and its complete immediate child elections."""

        root: FlextCliModelsBasePart09.AtomicPhysicalTreeEntry = m.Field(
            description="Descriptor-authenticated physical directory identity"
        )
        entries: t.VariadicTuple[FlextCliModelsBasePart09.AtomicDirectoryName] = (
            m.Field(
                default=(), description="Complete ordered immediate physical children"
            )
        )
        queries: t.VariadicTuple[t.Pair[str, Literal["exists", "isfile", "isdir"]]] = (
            m.Field(default=(), description="Consumed native candidate predicates")
        )
        membership_queried: bool = m.Field(
            default=False,
            description="Whether native planning consumed direct membership",
        )
        membership_queries: t.VariadicTuple[t.StrTuple] = m.Field(
            default=(),
            description="Consumed membership selections, each excluding named children",
        )

        @m.model_validator(mode="after")
        def _validate_names(self) -> Self:
            if self.membership_queries != tuple(
                sorted(set(self.membership_queries))
            ) or any(
                selection != tuple(sorted(set(selection)))
                or any(
                    name in {"", ".", ".."} or Path(name).name != name
                    for name in selection
                )
                for selection in self.membership_queries
            ):
                msg = "atomic membership selections require ordered lexical exclusions"
                raise ValueError(msg)
            names = tuple(entry.name for entry in self.entries)
            if self.root.kind != "directory" or names != tuple(sorted(set(names))):
                msg = "atomic directory inventory requires ordered unique children"
                raise ValueError(msg)
            if self.queries != tuple(sorted(set(self.queries))) or any(
                name in {"", ".", ".."} or Path(name).name != name
                for name, _predicate in self.queries
            ):
                msg = "atomic directory queries require ordered lexical child names"
                raise ValueError(msg)
            return self

    class AtomicPhysicalTreeManifest(m.ArbitraryTypesModel):
        """Exact root identity plus its ordered descriptor-authenticated entries."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

        root: Annotated[
            FlextCliModelsBasePart09.AtomicPhysicalTreeEntry,
            m.Field(description="Physical tree root"),
        ]
        entries: Annotated[
            t.VariadicTuple[FlextCliModelsBasePart09.AtomicPhysicalTreeEntry],
            m.Field(description="Lexically ordered descendants"),
        ] = ()

        @m.model_validator(mode="after")
        def _validate_root_and_order(self) -> Self:
            FlextCliModelsAtomicState.validate_atomic_state_path(
                self.root.path,
                label="atomic physical-tree manifest root",
            )
            for entry in (self.root, *self.entries):
                if entry.device != entry.parent_device:
                    msg = "atomic physical-tree entry must share its parent device"
                    raise ValueError(msg)
                if entry.mount_id != entry.parent_mount_id:
                    msg = "atomic physical-tree entry must share its parent mount"
                    raise ValueError(msg)
            if self.root.kind != "directory":
                msg = "atomic physical-tree root must be a directory"
                raise ValueError(msg)
            ordered_paths = tuple(entry.path.as_posix() for entry in self.entries)
            if ordered_paths != tuple(sorted(ordered_paths)):
                msg = "atomic physical-tree entries must be lexically ordered"
                raise ValueError(msg)
            return self

        @m.model_validator(mode="after")
        def _validate_topology(self) -> Self:
            directories = {self.root.path: self.root}
            directory_identities = {(self.root.device, self.root.inode)}
            seen = {self.root.path}
            for entry in self.entries:
                if entry.path in seen:
                    msg = "atomic physical-tree entries must have unique paths"
                    raise ValueError(msg)
                if not entry.path.is_relative_to(self.root.path):
                    msg = "atomic physical-tree entry is outside its root"
                    raise ValueError(msg)
                parent = directories.get(entry.path.parent)
                parent_binding = (
                    entry.parent_device,
                    entry.parent_inode,
                    entry.parent_mount_id,
                )
                if parent is None or parent_binding != (
                    parent.device,
                    parent.inode,
                    parent.mount_id,
                ):
                    msg = "atomic physical-tree parent binding is inconsistent"
                    raise ValueError(msg)
                if entry.device != self.root.device:
                    msg = "atomic physical-tree entries must share the root device"
                    raise ValueError(msg)
                if entry.mount_id != self.root.mount_id:
                    msg = "atomic physical-tree entries must share the root mount"
                    raise ValueError(msg)
                seen.add(entry.path)
                if entry.kind == "directory":
                    identity = (entry.device, entry.inode)
                    if identity in directory_identities:
                        msg = "atomic physical-tree directory identity is repeated"
                        raise ValueError(msg)
                    directory_identities.add(identity)
                    directories[entry.path] = entry
            return self


__all__: list[str] = ["FlextCliModelsBasePart09"]
