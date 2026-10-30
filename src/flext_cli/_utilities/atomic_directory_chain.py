"""Planning and guarded materialization for missing directory chains.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from collections.abc import MutableSequence, Sequence
from pathlib import Path

from flext_cli import m, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryCreate,
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectorySnapshot,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicParentDescriptor,
)


class FlextCliUtilitiesAtomicDirectoryChain:
    """Canonical namespace owner."""

    @staticmethod
    def plan_directory_chain(target: t.Cli.TextPath) -> m.Cli.AtomicDirectoryChainPlan:
        """Snapshot one physical anchor and every descendant observed absent.

        Returns:
            The resulting ``m.Cli.AtomicDirectoryChainPlan``.

        """
        path = Path(target)
        anchor, state, ancestry, missing = (
            FlextCliUtilitiesAtomicParentDescriptor.inspect_directory_chain(
                path,
            )
        )
        return m.Cli.AtomicDirectoryChainPlan(
            target=path,
            anchor_path=anchor,
            anchor_device=state.st_dev,
            anchor_inode=state.st_ino,
            anchor_ancestry=ancestry,
            directories=missing,
        )

    @staticmethod
    def verify_guarded_directory_chain(
        plan: m.Cli.AtomicDirectoryChainPlan,
        created: Sequence[m.Cli.AtomicDirectoryState],
    ) -> None:
        """Verify original ancestry and the exact ordered creation receipts.

        Raises:
            OSError: If receipts differ from the plan or physical ancestry changed.

        """
        # Consumers retain the original plan; a fresh snapshot grants no authority.
        owner = FlextCliUtilitiesAtomicDirectoryChain
        if tuple(state.path for state in created) != plan.directories:
            message = "directory-chain receipts differ from the original plan"
            raise OSError(errno.EINVAL, message, plan.target)
        owner.require_anchor(plan)
        parent = (plan.anchor_device, plan.anchor_inode)
        identities: list[tuple[int, int]] = []
        for state in created:
            owner.require_planned_parent(state.path, state, parent)
            parent = owner.require_created_identity(state)
            identities.append(parent)
        observed = owner.plan_directory_chain(plan.target)
        if (
            observed.anchor_path != plan.target
            or observed.directories
            or observed.anchor_ancestry != (*plan.anchor_ancestry, *identities)
        ):
            message = "provisioned directory-chain ancestry changed"
            raise OSError(errno.ESTALE, message, plan.target)

    @staticmethod
    def create_guarded_directory_chain(
        plan: m.Cli.AtomicDirectoryChainPlan,
        *,
        permission_mode: int,
        created: MutableSequence[m.Cli.AtomicDirectoryState] | None = None,
    ) -> Sequence[m.Cli.AtomicDirectoryState]:
        """Create planned levels while retaining every completed effect.

        The optional caller-owned collection records progress before the next
        native operation. A failure never removes a successfully created level.

        Returns:
            The resulting ``Sequence[m.Cli.AtomicDirectoryState]``.

        Raises:
            OSError: If ``mode is None``.

        """
        mode = FlextCliUtilitiesAtomicFileMode.validate_mode(
            permission_mode,
            label="permission_mode",
        )
        if mode is None:
            message = "permission_mode is required for directory-chain creation"
            raise OSError(errno.EINVAL, message, plan.target)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_create_capabilities(
            plan.target,
        )
        FlextCliUtilitiesAtomicDirectoryChain.require_anchor(plan)
        progress: MutableSequence[m.Cli.AtomicDirectoryState] = (
            [] if created is None else created
        )
        initial_count = len(progress)
        expected_parent = (plan.anchor_device, plan.anchor_inode)
        try:
            FlextCliUtilitiesAtomicDirectoryChain._create_chained_directories(
                plan,
                mode,
                progress,
                expected_parent,
            )
        except BaseException as operation_error:
            for state in progress[initial_count:]:
                operation_error.add_note(
                    f"created directory receipt: {state.model_dump_json()}",
                )
            raise
        return tuple(progress[initial_count:])

    @staticmethod
    def _create_chained_directories(
        plan: m.Cli.AtomicDirectoryChainPlan,
        mode: int,
        created: MutableSequence[m.Cli.AtomicDirectoryState],
        expected_parent: tuple[int, int],
    ) -> MutableSequence[m.Cli.AtomicDirectoryState]:
        """Create each planned directory, advancing the expected identity.

        Returns:
            The created directory states in plan order.

        """
        for directory in plan.directories:
            snapshot = FlextCliUtilitiesAtomicDirectorySnapshot
            before = snapshot.read_authenticated_empty_directory(
                directory,
                required=False,
            )
            FlextCliUtilitiesAtomicDirectoryChain.require_planned_parent(
                directory,
                before,
                expected_parent,
            )
            create = FlextCliUtilitiesAtomicDirectoryCreate
            state = create.create_guarded_empty_directory(
                before,
                permission_mode=mode,
            )
            created.append(state)
            expected_parent = (
                FlextCliUtilitiesAtomicDirectoryChain.require_created_identity(
                    state,
                )
            )
        return created

    @staticmethod
    def require_anchor(plan: m.Cli.AtomicDirectoryChainPlan) -> None:
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            plan.anchor_path,
        ) as current:
            if (current.state.st_dev, current.state.st_ino) != (
                plan.anchor_device,
                plan.anchor_inode,
            ) or current.ancestry != plan.anchor_ancestry:
                message = f"atomic directory-chain anchor changed: {plan.anchor_path}"
                raise OSError(errno.ESTALE, message, plan.anchor_path)

    @staticmethod
    def require_planned_parent(
        path: Path, state: m.Cli.AtomicDirectoryState, expected: tuple[int, int]
    ) -> None:
        if (state.parent_device, state.parent_inode) != expected:
            message = f"atomic directory-chain parent changed: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def require_created_identity(
        state: m.Cli.AtomicDirectoryState,
    ) -> tuple[int, int]:
        if state.device is None or state.inode is None:
            message = f"created directory has no physical identity: {state.path}"
            raise OSError(errno.EINVAL, message, state.path)
        return state.device, state.inode


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryChain"]
