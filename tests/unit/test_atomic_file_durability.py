"""Caller-declared durability contract of the atomic file writers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import stat
from pathlib import Path

import pytest
from flext_tests import tm

from tests import c, u


class TestsAtomicFileDurability:
    """SCRATCH keeps every publication check while durability stays default."""

    @staticmethod
    @pytest.mark.parametrize(
        "durability",
        [c.Cli.WriteDurability.DURABLE, c.Cli.WriteDurability.SCRATCH],
    )
    def test_text_write_publishes_content_for_each_durability(
        tmp_path: Path,
        durability: c.Cli.WriteDurability,
    ) -> None:
        """Publish identical bytes whichever durability the caller declares."""
        path = tmp_path / "nested" / "atomic.txt"

        tm.ok(u.Cli.atomic_write_text_file(path, "first", durability=durability))
        tm.ok(u.Cli.atomic_write_text_file(path, "second", durability=durability))

        tm.that(path.read_text(encoding="utf-8"), eq="second")
        tm.that(sorted(item.name for item in path.parent.iterdir()), eq=["atomic.txt"])

    @staticmethod
    def test_scratch_binary_write_preserves_host_permission_mode(
        tmp_path: Path,
    ) -> None:
        """Keep the permission-mode contract on the SCRATCH binary path."""
        path = tmp_path / "atomic.bin"
        path.write_bytes(b"before")
        path.chmod(0o640)
        expected_mode = stat.S_IMODE(path.stat().st_mode)

        tm.ok(
            u.Cli.files_write_binary(
                path,
                b"after",
                durability=c.Cli.WriteDurability.SCRATCH,
            ),
        )

        tm.that(path.read_bytes(), eq=b"after")
        tm.that(stat.S_IMODE(path.stat().st_mode), eq=expected_mode)

    @staticmethod
    def test_scratch_write_still_rejects_linked_destination(tmp_path: Path) -> None:
        """Skipping fsync never relaxes the physical destination checks."""
        target = tmp_path / "target.txt"
        target.write_text("kept", encoding="utf-8")
        link = tmp_path / "link.txt"
        link.symlink_to(target)

        tm.fail(
            u.Cli.atomic_write_text_file(
                link,
                "replaced",
                durability=c.Cli.WriteDurability.SCRATCH,
            ),
        )

        tm.that(target.read_text(encoding="utf-8"), eq="kept")
        tm.that(link.is_symlink(), eq=True)
