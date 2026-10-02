"""Public symbolic-link state and guarded mutation facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli import m, p, r, t
from flext_cli._utilities import atomic_file_descriptor as descriptor
from flext_cli._utilities.atomic_symlink_publish import (
    delete_guarded_symlink,
    write_guarded_symlink,
)
from flext_cli._utilities.atomic_symlink_state import read_symlink_state


class FlextCliUtilitiesSymlink:
    """Expose exact symbolic-link operations through the shared CLI domain."""

    @staticmethod
    def atomic_read_symlink_state(
        path: t.Cli.TextPath,
        *,
        required: bool = False,
    ) -> p.Result[m.Cli.AtomicSymlinkState]:
        """Read link text and identity without following even a dangling target.

        The immediate parent must already exist as a physical directory.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicSymlinkState]``.

        """
        try:
            location = Path(path)
            with descriptor.parent_descriptor(location) as parent:
                state = read_symlink_state(location, parent, required=required)
        except OSError as exc:
            return r[m.Cli.AtomicSymlinkState].fail(str(exc), exception=exc)
        return r[m.Cli.AtomicSymlinkState].ok(state)

    @staticmethod
    def atomic_write_symlink_guarded(
        before: m.Cli.AtomicSymlinkState,
        target: str,
    ) -> p.Result[bool]:
        """Publish exact link text under the caller's shared exclusive lease.

        This operation is not CAS against actors that ignore the lease.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        try:
            write_guarded_symlink(before, target)
        except (OSError, ValueError) as exc:
            return r[bool].fail(str(exc), exception=exc)
        return r[bool].ok(value=True)

    @staticmethod
    def atomic_delete_symlink_guarded(
        before: m.Cli.AtomicSymlinkState,
    ) -> p.Result[bool]:
        """Delete only the snapshotted link under the caller's exclusive lease.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        try:
            delete_guarded_symlink(before)
        except OSError as exc:
            return r[bool].fail(str(exc), exception=exc)
        return r[bool].ok(value=True)


__all__: list[str] = ["FlextCliUtilitiesSymlink"]
