"""Portable publication, permission-mode, link, and failure contracts."""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

import pytest

from flext_tests import tm
from tests import u


class TestsAtomicFileContract:
    """Observable atomic-write behavior shared by text and binary APIs."""

    def test_text_write_persists_content(self, tmp_path: Path) -> None:
        """Keep the unconditional text facade on the strict atomic owner."""
        path = tmp_path / "atomic.txt"

        tm.ok(u.Cli.atomic_write_text_file(path, "hello atomic"))

        tm.that(path.read_text(encoding="utf-8"), eq="hello atomic")

    def test_new_file_matches_host_secure_temporary_mode(self, tmp_path: Path) -> None:
        """Use the host's canonical secure temporary-file permission mode."""
        descriptor, reference_name = tempfile.mkstemp(dir=tmp_path)
        os.close(descriptor)
        reference = tmp_path / Path(reference_name).name
        expected_mode = stat.S_IMODE(reference.stat().st_mode)
        reference.unlink()
        path = tmp_path / "atomic.txt"

        tm.ok(u.Cli.atomic_write_text_file(path, "created"))

        tm.that(stat.S_IMODE(path.stat().st_mode), eq=expected_mode)

    @pytest.mark.parametrize("requested_mode", [0o640, 0o750])
    def test_text_write_preserves_host_permission_mode(
        self, tmp_path: Path, requested_mode: int
    ) -> None:
        """Retain the mode the host applied to a uniquely owned regular file."""
        path = tmp_path / "atomic.txt"
        path.write_text("before", encoding="utf-8")
        path.chmod(requested_mode)
        expected_mode = stat.S_IMODE(path.stat().st_mode)

        tm.ok(u.Cli.atomic_write_text_file(path, "after"))

        tm.that(path.read_text(encoding="utf-8"), eq="after")
        tm.that(stat.S_IMODE(path.stat().st_mode), eq=expected_mode)

    def test_binary_write_preserves_host_permission_mode(self, tmp_path: Path) -> None:
        """Apply the same permission-mode contract through the binary API."""
        path = tmp_path / "atomic.bin"
        path.write_bytes(b"before")
        path.chmod(0o640)
        expected_mode = stat.S_IMODE(path.stat().st_mode)

        tm.ok(u.Cli.files_write_binary(path, b"after"))

        tm.that(path.read_bytes(), eq=b"after")
        tm.that(stat.S_IMODE(path.stat().st_mode), eq=expected_mode)

    @pytest.mark.parametrize("link_kind", ["symbolic", "hard"])
    def test_unconditional_write_rejects_linked_destination(
        self, tmp_path: Path, link_kind: str
    ) -> None:
        """Reject linked names through every public atomic-write facade."""
        owner, destination = self._linked_destination(tmp_path, link_kind)
        owner_inode = owner.lstat().st_ino
        destination_inode = destination.lstat().st_ino

        result = u.Cli.atomic_write_text_file(destination, "replacement")

        tm.fail(result)
        tm.that(owner.read_text(encoding="utf-8"), eq="owner")
        tm.that(destination.read_text(encoding="utf-8"), eq="owner")
        tm.that(owner.lstat().st_ino, eq=owner_inode)
        tm.that(destination.lstat().st_ino, eq=destination_inode)

    @pytest.mark.parametrize(
        ("link_kind", "error_fragment"),
        [("symbolic", "not a regular file"), ("hard", "hard links")],
    )
    def test_snapshot_rejects_linked_destination(
        self, tmp_path: Path, link_kind: str, error_fragment: str
    ) -> None:
        """Reject a pathname that cannot form a uniquely owned state."""
        owner, destination = self._linked_destination(tmp_path, link_kind)

        result = u.Cli.atomic_read_binary_file_state(destination, required=True)

        tm.fail(result)
        tm.that(result.error or "", has=error_fragment)
        tm.that(owner.read_text(encoding="utf-8"), eq="owner")

    def test_write_failure_after_staging_leaves_no_partial_file(
        self, tmp_path: Path
    ) -> None:
        """Expose a real host write failure without publishing partial state."""
        path = tmp_path / "atomic.txt"
        if os.name == "nt":
            path.write_text("before", encoding="utf-8")
            before = u.Cli.atomic_read_binary_file_state(path, required=True)
            tm.ok(before)
            with path.open("rb"):
                result = u.Cli.atomic_write_text_file_guarded(
                    before.value, "replacement"
                )
            tm.fail(result)
            tm.that(path.read_text(encoding="utf-8"), eq="before")
            return
        script = """
import resource
import signal
import sys
from pathlib import Path
from flext_cli import u

resource.setrlimit(resource.RLIMIT_FSIZE, (1, 1))
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
before = u.Cli.atomic_read_binary_file_state(Path(sys.argv[1]))
if before.failure:
    raise SystemExit(3)
result = u.Cli.atomic_write_text_file_guarded(before.value, "replacement")
raise SystemExit(0 if result.failure else 2)
"""
        completed = u.Cli.run_raw((sys.executable, "-c", script, str(path)), timeout=30)
        tm.ok(completed)
        tm.that(
            completed.value.outcome.raw_return_code,
            eq=0,
            msg=completed.value.stderr,
        )
        tm.that(path.exists(), eq=False)
        tm.that(tuple(tmp_path.iterdir()), eq=())

    def test_unwritable_parent_fails(self) -> None:
        """Expose an invalid destination through the public result contract."""
        result = u.Cli.atomic_write_text_file(
            "/nonexistent_root_dir/x/y/z/file.txt", "x"
        )

        tm.fail(result)

    @staticmethod
    def _linked_destination(tmp_path: Path, link_kind: str) -> tuple[Path, Path]:
        """Create one real linked pathname for public behavior tests."""
        owner = tmp_path / "owner.txt"
        owner.write_text("owner", encoding="utf-8")
        destination = tmp_path / "atomic.txt"
        if link_kind == "symbolic":
            destination.symlink_to(owner)
        else:
            os.link(owner, destination)
        return owner, destination
