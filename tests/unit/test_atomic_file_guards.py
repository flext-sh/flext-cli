"""Owner-uid and size guards of the authenticated atomic read and create.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import sys
from pathlib import Path
from types import FrameType

import pytest

from tests import t, tm, u


class TestsFlextCliAtomicFileGuards:
    """Guards reject foreign owners and oversized content before effects."""

    @staticmethod
    def test_whole_file_read_does_not_inherit_duplicate_offset(tmp_path: Path) -> None:
        """An EOF cursor shared by dup must not authenticate an empty payload."""
        path = tmp_path / "offset.bin"
        payload = b"authenticated payload"
        path.write_bytes(payload)
        observed: list[int] = []

        def observe_open(
            frame: FrameType, event: str, returned: t.Scalar | bytes | None
        ) -> None:
            if (
                event == "return"
                and frame.f_code.co_name == "open_entry"
                and frame.f_locals.get("path") == path
                and isinstance(returned, int)
            ):
                descriptor = os.dup(returned)
                try:
                    observed.append(os.lseek(descriptor, 0, os.SEEK_END))
                finally:
                    os.close(descriptor)

        previous = sys.getprofile()
        sys.setprofile(observe_open)
        try:
            states = [
                tm.ok(u.Cli.atomic_read_binary_file_state(path, required=True))
                for _ in range(2)
            ]
        finally:
            sys.setprofile(previous)
        tm.that(observed, eq=[len(payload), len(payload)])
        for state in states:
            tm.that(state.content, eq=payload)

    @staticmethod
    def test_whole_file_read_rejects_short_payload_with_unchanged_stat(
        tmp_path: Path,
    ) -> None:
        """A cursor moved by another holder cannot authenticate a short read."""
        path = tmp_path / "short.bin"
        path.write_bytes(b"x" * (1024 * 1024 + 1))
        descriptors: list[int] = []

        def observe_chunks(
            frame: FrameType, event: str, _returned: t.Scalar | bytes | None
        ) -> None:
            if (
                event == "return"
                and frame.f_code.co_name == "descriptor_chunks"
                and frame.f_locals.get("path") == path
            ):
                descriptor = frame.f_locals.get("descriptor")
                if isinstance(descriptor, int):
                    descriptors.append(descriptor)

        chunks = iter(u.Cli.atomic_iter_binary_file(path))
        previous = sys.getprofile()
        sys.setprofile(observe_chunks)
        try:
            first = next(chunks)
        finally:
            sys.setprofile(previous)
        tm.that(len(first), eq=1024 * 1024)
        descriptor = descriptors[-1]
        expected = os.fstat(descriptor)
        os.lseek(descriptor, 0, os.SEEK_END)
        with pytest.raises(
            OSError, match="atomic destination changed during authenticated read"
        ) as rejected:
            next(chunks)
        tm.that(rejected.value.errno, eq=errno.ESTALE)
        observed = path.stat()
        tm.that(observed, eq=expected)
        tm.that(observed.st_mtime_ns, eq=expected.st_mtime_ns)
        tm.that(observed.st_ctime_ns, eq=expected.st_ctime_ns)

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

        tm.fail(path.exists())

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

        tm.fail(path.exists())

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
