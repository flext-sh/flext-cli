"""Caller-declared durability contract of the atomic file writers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from tests import c, m, tm, u


class TestsFlextCliAtomicFileDurability:
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
    @pytest.mark.parametrize(
        "durability",
        [c.Cli.WriteDurability.DURABLE, c.Cli.WriteDurability.SCRATCH],
    )
    def test_guarded_create_publishes_its_proof_for_each_durability(
        tmp_path: Path,
        durability: c.Cli.WriteDurability,
    ) -> None:
        """A guarded create keeps its proof and mode whichever durability it declares."""
        path = tmp_path / "created.bin"

        state = tm.ok(
            u.Cli.atomic_create_binary_file_guarded(
                path,
                b"created",
                permission_mode=0o600,
                durability=durability,
            ),
        )

        tm.that(path.read_bytes(), eq=b"created")
        tm.that(state.mode, eq=0o600)
        tm.ok(u.Cli.atomic_verify_binary_file_states((state,)))
        tm.fail(
            u.Cli.atomic_create_binary_file_guarded(
                path,
                b"again",
                permission_mode=0o600,
                durability=durability,
            ),
        )

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
        tm.ok(link.is_symlink())

    @staticmethod
    @pytest.mark.parametrize(
        "durability",
        [c.Cli.WriteDurability.DURABLE, c.Cli.WriteDurability.SCRATCH],
    )
    def test_json_write_publishes_payload_for_each_durability(
        tmp_path: Path,
        durability: c.Cli.WriteDurability,
    ) -> None:
        """Publish the same JSON document whichever durability the caller declares."""
        path = tmp_path / "nested" / "state.json"
        options = m.Cli.JsonWriteOptions(durability=durability)

        tm.ok(u.Cli.json_write(path, {"version": 1}, options))
        tm.ok(u.Cli.json_write(path, {"version": 2}, options))

        tm.that(u.Cli.json_read(path).unwrap(), eq={"version": 2})
        tm.that(sorted(item.name for item in path.parent.iterdir()), eq=["state.json"])

    @staticmethod
    def test_scratch_json_write_still_rejects_linked_destination(
        tmp_path: Path,
    ) -> None:
        """Skipping fsync never relaxes the JSON destination checks."""
        target = tmp_path / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = tmp_path / "link.json"
        link.symlink_to(target)

        tm.fail(
            u.Cli.json_write(
                link,
                {"replaced": True},
                m.Cli.JsonWriteOptions(durability=c.Cli.WriteDurability.SCRATCH),
            ),
        )

        tm.that(target.read_text(encoding="utf-8"), eq="{}")
