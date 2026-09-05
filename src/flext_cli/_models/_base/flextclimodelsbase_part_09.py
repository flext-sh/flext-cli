"""Typed descriptor-authenticated physical tree manifest models."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from flext_cli._models import atomic_state
from flext_core import m, u


class FlextCliModelsBase:
    """Implementation part for FlextCliModelsBase."""

    class AtomicPhysicalTreeEntry(m.BaseModel):
        """One exact regular file, symlink leaf, or physical directory."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            extra="forbid", frozen=True, arbitrary_types_allowed=True
        )
        path: Annotated[Path, m.Field(description="Absolute entry path")]
        kind: Annotated[
            Literal["directory", "file", "symlink"],
            m.Field(description="Physical entry kind"),
        ]
        parent_device: Annotated[
            int, m.Field(ge=0, strict=True, description="Physical parent device")
        ]
        parent_inode: Annotated[
            int, m.Field(ge=0, strict=True, description="Physical parent inode")
        ]
        parent_mount_id: Annotated[
            int, m.Field(ge=1, strict=True, description="Physical parent mount ID")
        ]
        mode: Annotated[
            int, m.Field(ge=0, le=0o7777, strict=True, description="Permission bits")
        ]
        device: Annotated[
            int, m.Field(ge=0, strict=True, description="Physical device")
        ]
        inode: Annotated[int, m.Field(ge=0, strict=True, description="Physical inode")]
        mount_id: Annotated[
            int, m.Field(ge=1, strict=True, description="Physical mount ID")
        ]
        link_count: Annotated[
            int, m.Field(ge=1, strict=True, description="Exact link count")
        ]
        uid: Annotated[int, m.Field(ge=0, strict=True, description="Owner user ID")]
        gid: Annotated[int, m.Field(ge=0, strict=True, description="Owner group ID")]
        mtime_ns: Annotated[
            int, m.Field(strict=True, description="Modification timestamp in ns")
        ]
        ctime_ns: Annotated[
            int, m.Field(strict=True, description="Metadata-change timestamp in ns")
        ]
        file_attributes: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Host attributes")
        ] = None
        link_target: Annotated[
            str | None, m.Field(min_length=1, description="Exact symlink target text")
        ] = None
        reparse_tag: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Host reparse tag")
        ] = None
        size: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Regular-file size")
        ] = None
        sha256: Annotated[
            str | None,
            m.Field(
                pattern=r"^[0-9a-f]{64}$", description="Regular-file SHA-256 digest"
            ),
        ] = None

        @u.field_validator("path")
        @classmethod
        def _validate_path(cls, value: Path) -> Path:
            return atomic_state.validate_atomic_state_path(
                value, label="atomic physical-tree entry"
            )

        @u.model_validator(mode="after")
        def _validate_kind_state(self) -> Self:
            atomic_state.validate_non_reparse_state(
                self.file_attributes,
                self.reparse_tag,
                label="atomic physical-tree entry",
            )
            if self.device != self.parent_device:
                msg = "atomic physical-tree entry crosses its parent device"
                raise ValueError(msg)
            if self.mount_id != self.parent_mount_id:
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

    class AtomicPhysicalTreeManifest(m.BaseModel):
        """Exact root identity plus its ordered descriptor-authenticated entries."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            extra="forbid", frozen=True, arbitrary_types_allowed=True
        )
        root: Annotated[
            FlextCliModelsBase.AtomicPhysicalTreeEntry,
            m.Field(description="Physical tree root"),
        ]
        entries: Annotated[
            tuple[FlextCliModelsBase.AtomicPhysicalTreeEntry, ...],
            m.Field(description="Lexically ordered descendants"),
        ] = ()

        @u.model_validator(mode="after")
        def _validate_topology(self) -> Self:
            if self.root.kind != "directory":
                msg = "atomic physical-tree root must be a directory"
                raise ValueError(msg)
            directories = {self.root.path: self.root}
            directory_identities = {(self.root.device, self.root.inode)}
            seen = {self.root.path}
            ordered_paths = tuple(entry.path.as_posix() for entry in self.entries)
            if ordered_paths != tuple(sorted(ordered_paths)):
                msg = "atomic physical-tree entries must be lexically ordered"
                raise ValueError(msg)
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


__all__: list[str] = ["FlextCliModelsBase"]
