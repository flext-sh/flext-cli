"""Reproof of consumed direct-membership selections through own effects.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Literal, Never

from flext_cli import m, p, t
from flext_cli._utilities import FlextCliUtilitiesAtomicDirectoryChain
from flext_cli._utilities.atomic_tree_physical import (
    FlextCliUtilitiesAtomicTreePhysical,
)
from flext_cli._utilities.atomic_tree_query_receipts import (
    FlextCliUtilitiesAtomicTreeQueryReceipts,
)


class FlextCliUtilitiesAtomicTreeQueryMembership(
    FlextCliUtilitiesAtomicTreeQueryReceipts,
    FlextCliUtilitiesAtomicTreePhysical,
):
    """Reprove direct membership allowing only the boundary's own effects."""

    @classmethod
    def _verify_query_membership(
        cls,
        observed: p.Cli.AtomicDirectoryInventory,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
        excluded_names: t.StrTuple = (),
    ) -> None:
        """Reprove direct membership with only original native publication effects.

        Raises:
            ValueError: If direct membership changed.

        """
        root = observed.root.path
        cls._apply_created_members(root, members, boundary.created)
        cls._apply_published_members(root, members, boundary)
        expected = {
            name: kind for name, kind in members.items() if name not in excluded_names
        }
        actual = cls.directory_membership_value(observed, excluded_names)
        if expected != actual:
            added = sorted(actual.keys() - expected.keys())
            removed = sorted(expected.keys() - actual.keys())
            changed = [
                (name, expected[name], actual[name])
                for name in sorted(expected.keys() & actual.keys())
                if expected[name] != actual[name]
            ]
            msg = (
                f"source directory membership changed: {root}; "
                f"added={added!r}; removed={removed!r}; kind_changed={changed!r}"
            )
            raise ValueError(msg)

    @classmethod
    def _apply_created_members(
        cls,
        root: Path,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> None:
        """Add every own direct child directory creation to the membership.

        Raises:
            ValueError: If an own creation replaced a child of another kind.

        """
        for path in created:
            if path.parent != root:
                continue
            cls._published_directory_current(path, created)
            if members.get(path.name) not in {None, "directory"}:
                msg = f"source directory kind changed: {path}"
                raise ValueError(msg)
            members[path.name] = "directory"

    @classmethod
    def _apply_published_members(
        cls,
        root: Path,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Apply every own file effect at or beneath the root to the membership."""
        for _before, after in boundary.published.values():
            if after.path.parent == root:
                if after.content is None:
                    members.pop(after.path.name, None)
                else:
                    members[after.path.name] = "file"
            elif after.content is not None and after.path.is_relative_to(root):
                child = root / after.path.relative_to(root).parts[0]
                if child in boundary.created or members.get(child.name) != "directory":
                    cls._published_directory_current(child, boundary.created)
                members[child.name] = "directory"

    @classmethod
    def _published_directory_current(
        cls,
        path: Path,
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> None:
        """Bind an elected own directory to the publisher's original inode."""
        receipt = created.get(path)
        observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(path)
        if receipt is None or not receipt.exists or observed.directories:
            cls._raise_unpublished_directory(path)
        if (observed.anchor_device, observed.anchor_inode) != (
            receipt.device,
            receipt.inode,
        ) or observed.anchor_ancestry[-2] != (
            receipt.parent_device,
            receipt.parent_inode,
        ):
            cls._raise_unpublished_directory(path)

    @staticmethod
    def _raise_unpublished_directory(path: Path) -> Never:
        """Reject an elected directory lacking its original own publication.

        Raises:
            ValueError: Always.

        """
        msg = f"source directory lacks its original publication: {path}"
        raise ValueError(msg)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeQueryMembership"]
