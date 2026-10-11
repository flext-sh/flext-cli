"""Owner-uid and size guards of the authenticated atomic read and create.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_tests import tm

from tests import u


class TestsAtomicFileGuards:
    """Guards reject foreign owners and oversized content before effects."""

    @staticmethod
    def test_read_accepts_current_owner_within_bound(tmp_path: Path) -> None:
        """Return the exact bytes when owner and size satisfy the guards."""
        path = tmp_path / "owned.bin"
        path.write_bytes(b"12345")

        state = tm.ok(
            u.Cli.atomic_read_binary_file_state(
                path,
                required=True,
                owner_uid=os.getuid(),
                max_bytes=5,
            ),
        )

        tm.that(state.content, eq=b"12345")

    @staticmethod
    def test_read_rejects_foreign_owner(tmp_path: Path) -> None:
        """Fail a read whose parent and leaf belong to another uid."""
        path = tmp_path / "owned.bin"
        path.write_bytes(b"data")

        tm.fail(
            u.Cli.atomic_read_binary_file_state(
                path,
                required=True,
                owner_uid=os.getuid() + 1,
            ),
        )

    @staticmethod
    def test_read_rejects_oversized_leaf(tmp_path: Path) -> None:
        """Fail a read whose leaf exceeds the declared bound."""
        path = tmp_path / "large.bin"
        path.write_bytes(b"123456")

        tm.fail(
            u.Cli.atomic_read_binary_file_state(path, required=True, max_bytes=5),
        )

    @staticmethod
    def test_create_rejects_oversized_content_before_effect(tmp_path: Path) -> None:
        """Leave the destination absent when the content exceeds the bound."""
        path = tmp_path / "created.bin"

        tm.fail(
            u.Cli.atomic_create_binary_file_guarded(
                path,
                b"123456",
                permission_mode=0o600,
                max_bytes=5,
            ),
        )

        tm.that(path.exists(), eq=False)

    @staticmethod
    def test_create_rejects_foreign_parent_owner_before_effect(
        tmp_path: Path,
    ) -> None:
        """Leave the destination absent when its parent belongs to another uid."""
        path = tmp_path / "created.bin"

        tm.fail(
            u.Cli.atomic_create_binary_file_guarded(
                path,
                b"data",
                permission_mode=0o600,
                owner_uid=os.getuid() + 1,
            ),
        )

        tm.that(path.exists(), eq=False)

    @staticmethod
    def test_create_publishes_under_satisfied_guards(tmp_path: Path) -> None:
        """Publish and re-read the leaf when owner and size satisfy the guards."""
        path = tmp_path / "created.bin"

        state = tm.ok(
            u.Cli.atomic_create_binary_file_guarded(
                path,
                b"data",
                permission_mode=0o600,
                owner_uid=os.getuid(),
                max_bytes=4,
            ),
        )

        tm.that(state.content, eq=b"data")
        tm.that(path.read_bytes(), eq=b"data")
