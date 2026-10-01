"""Portable publication, permission-mode, link, and failure contracts."""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

import pytest
from flext_tests import tm

from tests import t, u


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

    @pytest.mark.parametrize("link_kind", ["symbolic"])
    def test_unconditional_write_rejects_linked_destination(
        self, tmp_path: Path, link_kind: str
    ) -> None:
        """Reject non-regular linked names through the atomic-write facade."""
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
        ("link_kind", "error_fragment"), [("symbolic", "not a regular file")]
    )
    def test_snapshot_rejects_linked_destination(
        self, tmp_path: Path, link_kind: str, error_fragment: str
    ) -> None:
        """Reject non-regular pathnames; hard destinations read fine."""
        owner, destination = self._linked_destination(tmp_path, link_kind)

        result = u.Cli.atomic_read_binary_file_state(destination, required=True)

        tm.fail(result)
        tm.that(result.error or "", has=error_fragment)
        tm.that(owner.read_text(encoding="utf-8"), eq="owner")

    def test_snapshot_reads_hardlinked_destination(self, tmp_path: Path) -> None:
        """A hard destination is safe to read under the d75f50d5 law.

        The state captures the observed link count instead of refusing, so
        package-manager-hardlinked content (uv link-mode) splices cleanly.
        """
        owner, destination = self._linked_destination(tmp_path, "hard")

        result = u.Cli.atomic_read_binary_file_state(destination, required=True)

        tm.ok(result)
        tm.that(result.value.content, eq=b"owner")
        tm.that(result.value.link_count, eq=2)
        tm.that(owner.read_text(encoding="utf-8"), eq="owner")

    def test_unconditional_write_replaces_hardlinked_destination(
        self, tmp_path: Path
    ) -> None:
        """Writing over a hard destination replaces that pathname only.

        The owner keeps its inode and bytes; the destination gets fresh
        content on a new inode, ending the hardlink share.
        """
        owner, destination = self._linked_destination(tmp_path, "hard")
        owner_inode = owner.lstat().st_ino

        result = u.Cli.atomic_write_text_file(destination, "replacement")

        tm.ok(result)
        tm.that(owner.read_text(encoding="utf-8"), eq="owner")
        tm.that(destination.read_text(encoding="utf-8"), eq="replacement")
        tm.that(owner.lstat().st_ino, eq=owner_inode)
        tm.that(destination.lstat().st_ino != owner_inode)

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
            u.Cli.process_succeeded(completed.value.outcome),
            eq=True,
            msg=completed.value.stderr,
        )
        tm.that(path.exists(), eq=False)
        tm.that(tuple(tmp_path.iterdir()), eq=())

    def test_timer_interrupt_preserves_cause_and_removes_authenticated_stage(
        self, tmp_path: Path
    ) -> None:
        """Preserve timer failure and never delete unauthenticated staging."""
        script = """
import signal
import sys
from pathlib import Path
from flext_cli import u

class AtomicDeadline(BaseException):
    pass

root = Path(sys.argv[1])
destination = root / "published.txt"
interrupted = {}
deadline = AtomicDeadline("atomic deadline")

def expire(_signum, _frame):
    # Disarm before any check: the glob below is slow enough (tens of
    # microseconds against a 0.1ms period) that a still-armed repeating
    # timer can re-enter this handler before it returns, recursing without
    # bound. Re-arming only on the negative branch keeps the polling alive
    # without ever letting two invocations overlap.
    signal.setitimer(signal.ITIMER_REAL, 0)
    stages = tuple(root.glob(".flext-atomic-*.tmp"))
    if stages:
        for path in stages:
            state = path.lstat()
            interrupted[path] = (state.st_dev, state.st_ino, state.st_size)
        raise deadline
    signal.setitimer(signal.ITIMER_REAL, 0.0001, 0.0001)

signal.signal(signal.SIGALRM, expire)
signal.setitimer(signal.ITIMER_REAL, 0.0001, 0.0001)
try:
    u.Cli.atomic_write_text_file(destination, "x" * (64 * 1024 * 1024))
except AtomicDeadline as error:
    signal.setitimer(signal.ITIMER_REAL, 0)
    if error is not deadline or error.__cause__ is not None:
        raise SystemExit(3)
    if destination.exists():
        raise SystemExit(4)
    for path in root.iterdir():
        state = path.lstat()
        if interrupted.get(path) != (state.st_dev, state.st_ino, state.st_size):
            raise SystemExit(5)
    print(len(tuple(root.iterdir())))
    raise SystemExit(0)
raise SystemExit(2)
"""

        completed = u.Cli.run_raw((sys.executable, "-c", script, str(tmp_path)))

        tm.ok(completed)
        tm.that(
            u.Cli.process_succeeded(completed.value.outcome),
            eq=True,
            msg=completed.value.stderr,
        )
        tm.that(len(tuple(tmp_path.iterdir())), eq=int(completed.value.stdout.strip()))

    @pytest.mark.parametrize("phase", ["before-registration", "authenticated"])
    def test_interrupt_cleanup_requires_captured_inode_identity(
        self, tmp_path: Path, phase: str
    ) -> None:
        """Keep an unowned entry and remove an owned inode on the same failure."""
        script = """
import os
import sys
from pathlib import Path
from flext_cli import u

class Interrupted(BaseException):
    pass

root = Path(sys.argv[1])
phase = sys.argv[2]
destination = root / 'published.txt'
failure = Interrupted('interrupted')
observed = {}
fired = False

def interrupt(event, args):
    global fired
    if fired:
        return
    if phase == 'before-registration' and event == 'open':
        name = args[0]
        if not isinstance(name, str) or not name.startswith('.flext-atomic-'):
            return
        fired = True
        path = root / name
        path.write_bytes(b'independent owner')
        state = path.lstat()
        observed[path] = (state.st_dev, state.st_ino, path.read_bytes())
        raise failure
    if phase == 'authenticated' and event == 'os.chmod':
        if not isinstance(args[0], int):
            return
        fired = True
        state = os.fstat(args[0])
        for path in root.glob('.flext-atomic-*.tmp'):
            current = path.lstat()
            if (current.st_dev, current.st_ino) == (state.st_dev, state.st_ino):
                observed[path] = (current.st_dev, current.st_ino, path.read_bytes())
        raise failure

before = u.Cli.atomic_read_binary_file_state(destination).unwrap()
sys.addaudithook(interrupt)
try:
    u.Cli.atomic_write_binary_file_guarded(before, b'written', permission_mode=0o600)
except Interrupted as error:
    if error is not failure or error.__cause__ is not None or not fired:
        raise SystemExit(2)
    if destination.exists() or len(observed) != 1:
        raise SystemExit(3)
    if phase == 'authenticated':
        if tuple(root.iterdir()):
            raise SystemExit(4)
    else:
        for path, before in observed.items():
            after = path.lstat()
            if (after.st_dev, after.st_ino, path.read_bytes()) != before:
                raise SystemExit(5)
    raise SystemExit(0)
raise SystemExit(6)
"""
        completed = tm.ok(
            u.Cli.run_raw((sys.executable, "-c", script, str(tmp_path), phase))
        )
        tm.that(
            u.Cli.process_succeeded(completed.outcome), eq=True, msg=completed.stderr
        )

    def test_unwritable_parent_fails(self) -> None:
        """Expose an invalid destination through the public result contract."""
        result = u.Cli.atomic_write_text_file(
            "/nonexistent_root_dir/x/y/z/file.txt", "x"
        )

        tm.fail(result)

    @staticmethod
    def _linked_destination(tmp_path: Path, link_kind: str) -> t.Pair[Path, Path]:
        """Create one real linked pathname for public behavior tests."""
        owner = tmp_path / "owner.txt"
        owner.write_text("owner", encoding="utf-8")
        destination = tmp_path / "atomic.txt"
        if link_kind == "symbolic":
            destination.symlink_to(owner)
        else:
            os.link(owner, destination)
        return owner, destination
