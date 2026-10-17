"""Descriptor-authenticated inventory for one physical filesystem tree.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, Never

from flext_cli import m, t
from flext_cli._utilities.atomic_directory_chain import (
    FlextCliUtilitiesAtomicDirectoryChain,
)
from flext_cli._utilities.atomic_directory_descriptor import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
)
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState
from flext_cli._utilities.atomic_models import FlextCliUtilitiesAtomicModels
from flext_cli._utilities.atomic_parent_descriptor import (
    FlextCliUtilitiesAtomicParentDescriptor,
)
from flext_cli._utilities.atomic_parent_failure import (
    FlextCliUtilitiesAtomicParentFailure,
)
from flext_cli._utilities.atomic_tree_descriptor import (
    FlextCliUtilitiesAtomicTreeDescriptor,
)


class FlextCliUtilitiesAtomicTreeInventory:
    """Canonical namespace owner."""

    _DIRECTORY_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    @staticmethod
    def directory_query_value(
        inventory: m.Cli.AtomicDirectoryInventory,
        name: str,
        predicate: Literal["exists", "isfile", "isdir"],
    ) -> bool:
        """Evaluate one native predicate from its physical directory receipt.

        Returns:
            Whether the captured child satisfies the native predicate.

        Raises:
            OSError: If the queried child is a physical alias.

        """
        entry = next((item for item in inventory.entries if item.name == name), None)
        if entry is not None and entry.kind == "symlink":
            raise OSError(
                errno.ELOOP,
                "atomic directory query encountered a physical alias",
                inventory.root.path / name,
            )
        return entry is not None and (
            predicate == "exists"
            or entry.kind == ("file" if predicate == "isfile" else "directory")
        )

    @classmethod
    def merge_directory_query_receipts(
        cls,
        inventories: t.VariadicTuple[m.Cli.AtomicDirectoryInventory],
        topology: t.VariadicTuple[m.Cli.AtomicDirectoryChainPlan],
    ) -> t.Pair[
        t.VariadicTuple[m.Cli.AtomicDirectoryInventory],
        t.VariadicTuple[m.Cli.AtomicDirectoryChainPlan],
    ]:
        """Union selectors only when every original native observation agrees.

        Returns:
            The directory inventories and ancestry plans with united selectors.

        Raises:
            ValueError: If original identity, query, or membership epochs disagree.

        """
        directories: t.MutableMappingKV[Path, m.Cli.AtomicDirectoryInventory] = {}
        chains: t.MutableMappingKV[Path, m.Cli.AtomicDirectoryChainPlan] = {}
        for incoming in inventories:
            path = incoming.root.path
            previous = directories.get(path)
            if previous is None:
                directories[path] = incoming
                continue
            cls._require_directory_identity(
                previous.root,
                incoming.root,
                f"source directory query epochs disagree: {path}",
            )
            if any(
                cls.directory_query_value(previous, name, predicate)
                != cls.directory_query_value(incoming, name, predicate)
                for name, predicate in (*previous.queries, *incoming.queries)
            ):
                msg = f"source directory query epochs disagree: {path}"
                raise ValueError(msg)
            if (previous.membership_queried or incoming.membership_queried) and tuple(
                (item.name, item.kind) for item in previous.entries
            ) != tuple((item.name, item.kind) for item in incoming.entries):
                msg = f"source directory membership epochs disagree: {path}"
                raise ValueError(msg)
            directories[path] = previous.model_copy(
                update={
                    "queries": tuple(sorted({*previous.queries, *incoming.queries})),
                    "membership_queried": (
                        previous.membership_queried or incoming.membership_queried
                    ),
                }
            )
        for incoming in topology:
            previous = chains.get(incoming.target)
            if previous is None:
                chains[incoming.target] = incoming
                continue
            if previous.model_dump(
                exclude={"queries", "membership_queried"}
            ) != incoming.model_dump(exclude={"queries", "membership_queried"}):
                msg = f"source directory ancestry epochs disagree: {incoming.target}"
                raise ValueError(msg)
            chains[incoming.target] = previous.model_copy(
                update={
                    "queries": tuple(sorted({*previous.queries, *incoming.queries})),
                    "membership_queried": (
                        previous.membership_queried or incoming.membership_queried
                    ),
                }
            )
        return tuple(directories.values()), tuple(chains.values())

    @staticmethod
    def _require_directory_identity(
        expected: m.Cli.AtomicPhysicalTreeEntry,
        observed: m.Cli.AtomicPhysicalTreeEntry,
        diagnostic: str,
    ) -> None:
        """Reject changed physical identity without freezing child membership.

        Raises:
            ValueError: If any original field except membership timestamps and
                link count differs.

        """
        mutable_membership = {"mtime_ns", "ctime_ns", "link_count"}
        if expected.model_dump(exclude=mutable_membership) != observed.model_dump(
            exclude=mutable_membership
        ):
            raise ValueError(diagnostic)

    @classmethod
    def verify_directory_queries(
        cls,
        inventories: t.VariadicTuple[m.Cli.AtomicDirectoryInventory],
        topology: t.VariadicTuple[m.Cli.AtomicDirectoryChainPlan],
        publications: t.VariadicTuple[
            t.Pair[m.Cli.AtomicFileState, m.Cli.AtomicFileState]
        ] = (),
        directory_publications: t.VariadicTuple[m.Cli.AtomicDirectoryState] = (),
    ) -> bool:
        """Reprove consumed elections, allowing only supplied physical own effects.

        Returns:
            True when every consumed query and physical identity still agrees.

        Raises:
            ValueError: If receipts disagree or an unaccounted change is observed.

        """
        published = {before.path: (before, after) for before, after in publications}
        created = {item.path: item for item in directory_publications}
        if len(published) != len(publications) or any(
            before.path != after.path for before, after in publications
        ):
            msg = "directory query publication identities disagree"
            raise ValueError(msg)
        ancestors = dict.fromkeys(
            path
            for _before, after in publications
            if after.content is not None
            for path in (after.path, *after.path.parents)
        )
        cls._verify_query_topology(
            topology, publications, published, created, ancestors
        )
        for expected in inventories:
            observed = cls.inventory_physical_directory(expected.root.path)
            cls._require_directory_identity(
                expected.root,
                observed.root,
                f"source directory physical identity changed: {expected.root.path}",
            )
            for name, predicate in expected.queries:
                value = cls.directory_query_value(expected, name, predicate)
                effect = published.get(expected.root.path / name)
                if effect is not None:
                    before, after = effect
                    before_value = before.content is not None and predicate != "isdir"
                    if value != before_value:
                        msg = f"source query preimage changed: {before.path}"
                        raise ValueError(msg)
                    value = after.content is not None and predicate != "isdir"
                elif predicate != "isfile" and (
                    expected.root.path / name in created
                    or expected.root.path / name in ancestors
                ):
                    # A directory the preimage already held needs no creation
                    # receipt for publications beneath it; only an own creation
                    # or a directory the preimage lacked must bind to one.
                    if expected.root.path / name in created or not (
                        cls.directory_query_value(expected, name, "isdir")
                    ):
                        cls._published_directory_current(
                            expected.root.path / name, created
                        )
                    value = True
                if value != cls.directory_query_value(observed, name, predicate):
                    msg = (
                        f"source directory query changed: "
                        f"{expected.root.path / name}; predicate={predicate}"
                    )
                    raise ValueError(msg)
            if expected.membership_queried:
                cls._verify_query_membership(
                    observed,
                    {item.name: item.kind for item in expected.entries},
                    publications,
                    created,
                )
        return True

    @classmethod
    def _verify_query_topology(
        cls,
        topology: t.VariadicTuple[m.Cli.AtomicDirectoryChainPlan],
        publications: t.VariadicTuple[
            t.Pair[m.Cli.AtomicFileState, m.Cli.AtomicFileState]
        ],
        published: t.MappingKV[
            Path, t.Pair[m.Cli.AtomicFileState, m.Cli.AtomicFileState]
        ],
        created: t.MappingKV[Path, m.Cli.AtomicDirectoryState],
        ancestors: t.MappingKV[Path, None],
    ) -> None:
        """Reprove absent-parent elections against the original native ancestry.

        Raises:
            ValueError: If ancestry or an absent candidate changed unexpectedly.

        """
        for witness in topology:
            observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(
                witness.target
            )
            gained = witness.directories[
                : max(0, len(witness.directories) - len(observed.directories))
            ]
            ancestry = dict(
                zip(
                    reversed((observed.anchor_path, *observed.anchor_path.parents)),
                    observed.anchor_ancestry,
                    strict=True,
                )
            )
            if observed.model_dump(
                exclude={"queries", "membership_queried"}
            ) != witness.model_dump(exclude={"queries", "membership_queried"}) and not (
                gained
                and observed.anchor_path == gained[-1]
                and observed.directories == witness.directories[len(gained) :]
                and observed.anchor_ancestry[: len(witness.anchor_ancestry)]
                == witness.anchor_ancestry
                and all(
                    path in created
                    and created[path].exists
                    and ancestry.get(path)
                    == (created[path].device, created[path].inode)
                    and ancestry.get(path.parent)
                    == (created[path].parent_device, created[path].parent_inode)
                    for path in gained
                )
            ):
                msg = f"source directory ancestry changed: {witness.target}"
                raise ValueError(msg)
            if (
                witness.queries or witness.membership_queried
            ) and not observed.directories:
                inventory = cls.inventory_physical_directory(witness.target)
                for name, predicate in witness.queries:
                    path = witness.target / name
                    effect = published.get(path)
                    value = (
                        effect[1].content is not None and predicate != "isdir"
                        if effect is not None
                        else predicate != "isfile" and path in ancestors
                    )
                    if predicate != "isfile" and path in created:
                        cls._published_directory_current(path, created)
                        value = True
                    if value and effect is None:
                        cls._published_directory_current(path, created)
                    if value != cls.directory_query_value(inventory, name, predicate):
                        msg = f"absent source candidate changed: {path}"
                        raise ValueError(msg)
                if witness.membership_queried:
                    cls._verify_query_membership(inventory, {}, publications, created)

    @classmethod
    def _verify_query_membership(
        cls,
        observed: m.Cli.AtomicDirectoryInventory,
        members: t.MutableMappingKV[
            str, Literal["directory", "file", "symlink", "other"]
        ],
        publications: t.VariadicTuple[
            t.Pair[m.Cli.AtomicFileState, m.Cli.AtomicFileState]
        ],
        created: t.MappingKV[Path, m.Cli.AtomicDirectoryState],
    ) -> None:
        """Reprove direct membership with only original native publication effects.

        Raises:
            ValueError: If direct membership or a published directory kind changed.

        """
        root = observed.root.path
        for path in created:
            if path.parent == root:
                cls._published_directory_current(path, created)
                if members.get(path.name) not in {None, "directory"}:
                    msg = f"source directory kind changed: {path}"
                    raise ValueError(msg)
                members[path.name] = "directory"
        for _before, after in publications:
            if after.path.parent == root:
                if after.content is None:
                    members.pop(after.path.name, None)
                else:
                    members[after.path.name] = "file"
            elif after.content is not None and after.path.is_relative_to(root):
                child = root / after.path.relative_to(root).parts[0]
                if child in created or members.get(child.name) != "directory":
                    cls._published_directory_current(child, created)
                members[child.name] = "directory"
        if members != {item.name: item.kind for item in observed.entries}:
            msg = f"source directory membership changed: {root}"
            raise ValueError(msg)

    @staticmethod
    def _published_directory_current(
        path: Path,
        created: t.MappingKV[Path, m.Cli.AtomicDirectoryState],
    ) -> None:
        """Bind an elected own directory to the publisher's original inode.

        Raises:
            ValueError: If the original directory or parent inode no longer agrees.

        """
        receipt = created.get(path)
        observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(path)
        if (
            receipt is None
            or not receipt.exists
            or observed.directories
            or (observed.anchor_device, observed.anchor_inode)
            != (receipt.device, receipt.inode)
            or observed.anchor_ancestry[-2]
            != (receipt.parent_device, receipt.parent_inode)
        ):
            msg = f"source directory lacks its original publication: {path}"
            raise ValueError(msg)

    @staticmethod
    def inventory_physical_directory(root_path: Path) -> m.Cli.AtomicDirectoryInventory:
        """Capture immediate elections without descending or hashing child payloads.

        Returns:
            The inventory of the immediate child names with their
            authenticated kinds and version keys.

        """
        with FlextCliUtilitiesAtomicTreeInventory._opened_root(root_path) as (
            root,
            parent,
        ):
            names = FlextCliUtilitiesAtomicTreeInventory._directory_names(
                parent.descriptor
            )
            entries: list[m.Cli.AtomicDirectoryName] = []
            for name in names:
                path = root.path / name
                child = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
                kind: Literal["directory", "file", "symlink", "other"]
                if stat.S_ISDIR(child.st_mode):
                    kind = "directory"
                elif stat.S_ISREG(child.st_mode):
                    kind = "file"
                elif stat.S_ISLNK(child.st_mode):
                    kind = "symlink"
                else:
                    kind = "other"
                entries.append(
                    m.Cli.AtomicDirectoryName(
                        name=name,
                        kind=kind,
                        version_key=FlextCliUtilitiesAtomicFileRead.state_key(child),
                        link_target=os.readlink(name, dir_fd=parent.descriptor)
                        if kind == "symlink"
                        else None,
                    )
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent, path, child
                )
            if names != FlextCliUtilitiesAtomicTreeInventory._directory_names(
                parent.descriptor
            ):
                FlextCliUtilitiesAtomicTreeInventory._raise_changed(root.path)
        return m.Cli.AtomicDirectoryInventory(root=root, entries=tuple(entries))

    @staticmethod
    def inventory_physical_tree(root_path: Path) -> m.Cli.AtomicPhysicalTreeManifest:
        """Inventory one exact tree through non-aliased directory descriptors.

        The shared root acquisition rejects a missing physical-tree root with
        ``FileNotFoundError`` before any descendant is read.

        Returns:
            The resulting ``m.Cli.AtomicPhysicalTreeManifest``.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(root_path)
        entries: list[m.Cli.AtomicPhysicalTreeEntry] = []
        with FlextCliUtilitiesAtomicTreeInventory._opened_root(root_path) as (
            root,
            parent,
        ):
            FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                root.path, os.fstat(parent.lineage[-1]), parent.state
            )
            FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                root.path, root.parent_mount_id, root.mount_id
            )
            FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                parent, root.mount_id, entries, {(root.device, root.inode)}
            )
        return m.Cli.AtomicPhysicalTreeManifest(
            root=root,
            entries=tuple(
                sorted(
                    entries, key=FlextCliUtilitiesAtomicTreeInventory._entry_path_key
                )
            ),
        )

    @staticmethod
    @contextmanager
    def _opened_root(
        root_path: Path,
    ) -> Generator[
        t.Pair[
            m.Cli.AtomicPhysicalTreeEntry,
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        ]
    ]:
        """Retain one shared root acquisition for shallow and recursive inventories.

        Yields:
            The authenticated root entry and its retained parent descriptor
            for the duration of the inventory.

        Raises:
            FileNotFoundError: If the required physical-tree root is missing.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_directory_path(root_path)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(root_path)
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            root_path,
        ) as opened:
            parent_descriptor = (
                opened.lineage[-1] if opened.lineage else opened.descriptor
            )
            parent_state = os.fstat(parent_descriptor)
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                parent_descriptor,
                root_path.parent,
            )
            root_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                opened.descriptor,
                root_path,
            )
            root = FlextCliUtilitiesAtomicTreeInventory._entry(
                root_path,
                parent_state,
                opened.state,
                FlextCliUtilitiesAtomicModels.TreeEntryDetails(
                    kind="directory",
                    parent_mount_id=parent_mount_id,
                    mount_id=root_mount_id,
                ),
            )
            root_parent = FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                root_path,
                opened.descriptor,
                opened.state,
                opened.ancestry,
                opened.lineage,
            )

            def recheck() -> None:
                FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                    opened.descriptor,
                    root_path,
                    opened.state,
                )
                FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
                    root_parent
                )

            try:
                yield root, root_parent
            except BaseException as exc:
                FlextCliUtilitiesAtomicParentFailure.preserve_recheck_failure(
                    root_path, exc, recheck
                )
                raise
            recheck()

    @staticmethod
    def _inventory_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        parent_mount_id: int,
        entries: list[m.Cli.AtomicPhysicalTreeEntry],
        directory_identities: set[t.Pair[int, int]],
    ) -> None:
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )
        names = FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
        for name in names:
            path = parent.path / name
            observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
            if stat.S_ISDIR(observed.st_mode):
                FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, observed)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                identity = FlextCliUtilitiesAtomicFilePath.identity(observed)
                if identity in directory_identities:
                    message = f"atomic physical-tree directory identity repeats: {path}"
                    raise OSError(errno.ELOOP, message, path)
                with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                    parent,
                    path,
                    FlextCliUtilitiesAtomicTreeInventory._DIRECTORY_FLAGS,
                ) as descriptor:
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                    mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                        descriptor,
                        path,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                        path,
                        parent_mount_id,
                        mount_id,
                    )
                    directory_identities.add(identity)
                    entries.append(
                        FlextCliUtilitiesAtomicTreeInventory._entry(
                            path,
                            parent.state,
                            observed,
                            FlextCliUtilitiesAtomicModels.TreeEntryDetails(
                                kind="directory",
                                parent_mount_id=parent_mount_id,
                                mount_id=mount_id,
                            ),
                        ),
                    )
                    child_parent = (
                        FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                            path,
                            descriptor,
                            observed,
                            (
                                *parent.ancestry,
                                FlextCliUtilitiesAtomicFilePath.identity(observed),
                            ),
                            (*parent.lineage, parent.descriptor),
                        )
                    )
                    FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                        child_parent,
                        mount_id,
                        entries,
                        directory_identities,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
            elif stat.S_ISREG(observed.st_mode):
                authenticated = FlextCliUtilitiesAtomicFileState.destination_state(
                    path,
                    parent=parent,
                )
                if authenticated is None:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    authenticated,
                )
                size, digest = (
                    FlextCliUtilitiesAtomicTreeDescriptor.measure_authenticated_file(
                        parent,
                        path,
                        authenticated,
                        required_mount_id=parent_mount_id,
                    )
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        parent.state,
                        authenticated,
                        FlextCliUtilitiesAtomicModels.TreeEntryDetails(
                            kind="file",
                            parent_mount_id=parent_mount_id,
                            size=size,
                            digest=digest,
                            mount_id=parent_mount_id,
                        ),
                    ),
                )
            elif stat.S_ISLNK(observed.st_mode):
                target = os.readlink(name, dir_fd=parent.descriptor)
                if not target:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        parent.state,
                        observed,
                        FlextCliUtilitiesAtomicModels.TreeEntryDetails(
                            kind="symlink",
                            parent_mount_id=parent_mount_id,
                            mount_id=parent_mount_id,
                            link_target=target,
                        ),
                    ),
                )
            else:
                message = (
                    f"atomic physical-tree entry is not regular or a directory: {path}"
                )
                raise OSError(errno.EINVAL, message, path)
        if (
            FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
            != names
        ):
            FlextCliUtilitiesAtomicTreeInventory._raise_changed(parent.path)
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )

    @staticmethod
    def _entry(
        path: Path,
        parent: os.stat_result,
        observed: os.stat_result,
        details: FlextCliUtilitiesAtomicModels.TreeEntryDetails,
    ) -> m.Cli.AtomicPhysicalTreeEntry:
        if details.kind == "file" and observed.st_nlink > 1:
            # Cleanup authority is per pathname; a second physical name sharing
            # the inode means pruning this tree must not silently claim the
            # sibling's content. Read/replace paths stay permissive — this
            # refusal owns the cleanup verb only.
            message = (
                f"cleanup authority refused: {path} has {observed.st_nlink} hard"
                " links (another physical name owns the same inode)"
            )
            raise OSError(errno.EMLINK, message, path)
        return m.Cli.AtomicPhysicalTreeEntry(
            path=path,
            kind=details.kind,
            parent_device=parent.st_dev,
            parent_inode=parent.st_ino,
            parent_mount_id=details.parent_mount_id,
            mode=stat.S_IMODE(observed.st_mode),
            device=observed.st_dev,
            inode=observed.st_ino,
            mount_id=details.mount_id,
            link_count=observed.st_nlink,
            uid=observed.st_uid,
            gid=observed.st_gid,
            mtime_ns=observed.st_mtime_ns,
            ctime_ns=observed.st_ctime_ns,
            file_attributes=getattr(observed, "st_file_attributes", None),
            reparse_tag=getattr(observed, "st_reparse_tag", None),
            size=details.size,
            sha256=details.digest,
            link_target=details.link_target,
        )

    @staticmethod
    def _directory_names(descriptor: int) -> t.VariadicTuple[str]:
        """Enumerate names through the authenticated directory descriptor.

        Returns:
            The resulting ``t.VariadicTuple[str]``.

        """
        with os.scandir(descriptor) as entries:
            return tuple(sorted(entry.name for entry in entries))

    @staticmethod
    def _entry_path_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> str:
        """Return the deterministic lexical manifest key.

        Returns:
            The deterministic lexical manifest key.

        """
        return entry.path.as_posix()

    @staticmethod
    def _raise_changed(path: Path) -> Never:
        message = f"atomic physical-tree entry changed during inventory: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeInventory"]
