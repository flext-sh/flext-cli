"""Planning and guarded materialization for missing directory chains.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from pathlib import Path

from flext_cli import m, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryCreate,
    FlextCliUtilitiesAtomicDirectoryDelete,
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
    def create_guarded_directory_chain(
        plan: m.Cli.AtomicDirectoryChainPlan,
        *,
        permission_mode: int,
    ) -> t.SequenceOf[m.Cli.AtomicDirectoryState]:
        """Create every planned level, rolling back successful levels on failure.

        Returns:
            The resulting ``t.SequenceOf[m.Cli.AtomicDirectoryState]``.

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
        FlextCliUtilitiesAtomicDirectoryChain._require_anchor(plan)
        created: list[m.Cli.AtomicDirectoryState] = []
        expected_parent = (plan.anchor_device, plan.anchor_inode)
        try:
            created = FlextCliUtilitiesAtomicDirectoryChain._create_chained_directories(
                plan,
                mode,
                created,
                expected_parent,
            )
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicDirectoryChain._rollback_created(
                created,
                operation_error,
            )
            raise
        return tuple(created)

    @staticmethod
    def _create_chained_directories(
        plan: m.Cli.AtomicDirectoryChainPlan,
        mode: int | None,
        created: list[m.Cli.AtomicDirectoryState],
        expected_parent: tuple[int, int],
    ) -> list[m.Cli.AtomicDirectoryState]:
        """Create each planned directory, advancing the expected identity.

        Returns:
            The resulting ``list[m.Cli.AtomicDirectoryState]``.
        """
        for directory in plan.directories:
            snapshot = FlextCliUtilitiesAtomicDirectorySnapshot
            before = snapshot.read_authenticated_empty_directory(
                directory,
                required=False,
            )
            FlextCliUtilitiesAtomicDirectoryChain._require_planned_parent(
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
                FlextCliUtilitiesAtomicDirectoryChain._require_created_identity(
                    state,
                )
            )
        return created

    @staticmethod
    def _require_anchor(plan: m.Cli.AtomicDirectoryChainPlan) -> None:
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
    def _require_planned_parent(
        path: Path,
        state: m.Cli.AtomicDirectoryState,
        expected: t.Pair[int, int],
    ) -> None:
        if (state.parent_device, state.parent_inode) != expected:
            message = f"atomic directory-chain parent changed: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def _require_created_identity(
        state: m.Cli.AtomicDirectoryState,
    ) -> t.Pair[int, int]:
        if state.device is None or state.inode is None:
            message = f"created directory has no physical identity: {state.path}"
            raise OSError(errno.EINVAL, message, state.path)
        return state.device, state.inode

    @staticmethod
    def _rollback_created(
        created: list[m.Cli.AtomicDirectoryState],
        operation_error: BaseException,
    ) -> None:
        for state in reversed(created):
            try:
                FlextCliUtilitiesAtomicDirectoryDelete.remove_guarded_empty_directory(
                    state,
                )
            except OSError as cleanup_error:
                message = (
                    f"directory-chain creation failed ({operation_error}); "
                    f"rollback failed ({cleanup_error})"
                )
                if isinstance(operation_error, Exception):
                    causes = ExceptionGroup(
                        "directory-chain creation and rollback failed",
                        [operation_error, cleanup_error],
                    )
                    raise OSError(errno.EIO, message, state.path) from causes
                group_message = "directory-chain creation and rollback failed"
                raise BaseExceptionGroup(
                    group_message,
                    [operation_error, cleanup_error],
                ) from cleanup_error


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryChain"]
