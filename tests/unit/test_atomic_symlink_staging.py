"""Observe real staged-link ownership when its physical parent moves.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from flext_tests import tm

from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsAtomicSymlinkStaging:
    """An unverified staged inode must stay discoverable through its failure."""

    def test_snapshot_failure_retains_original_cause_and_unverified_stage(
        self,
        tmp_path: Path,
    ) -> None:
        """Test snapshot failure retains original cause and unverified stage."""
        script = tmp_path / "consumer.py"
        script.write_text(
            "import errno\n"
            "import sys\n"
            "from pathlib import Path\n"
            "from flext_cli import u\n"
            "root = Path(sys.argv[1])\n"
            "parent = root / 'parent'\n"
            "parent.mkdir()\n"
            "moved = root / 'moved'\n"
            "path = parent / 'link'\n"
            "before = u.Cli.atomic_read_symlink_state(path).unwrap()\n"
            "armed = True\n"
            "def move_parent(event, args):\n"
            "    global armed\n"
            "    if event == 'os.symlink' and armed:\n"
            "        armed = False\n"
            "        parent.rename(moved)\n"
            "        parent.mkdir()\n"
            "sys.addaudithook(move_parent)\n"
            "result = u.Cli.atomic_write_symlink_guarded(before, 'unresolved')\n"
            "assert result.failure\n"
            "error = result.exception\n"
            "assert isinstance(error, OSError)\n"
            "assert error.errno == errno.ESTALE\n"
            "assert isinstance(error.__cause__, BaseExceptionGroup)\n"
            "original = error\n"
            "while isinstance(original.__cause__, BaseExceptionGroup):\n"
            "    original = original.__cause__.exceptions[0]\n"
            "assert isinstance(original, OSError)\n"
            "assert original.errno == errno.ESTALE\n"
            "assert original.__traceback__ is not None\n"
            "assert not getattr(original, '__notes__', ())\n"
            "retained = tuple(moved.iterdir())\n"
            "assert len(retained) == 1\n"
            "stage = retained[0]\n"
            "assert stage.is_symlink()\n"
            "assert str(stage.readlink()) == 'unresolved'\n"
            "physical = moved.stat()\n"
            "assert physical.st_dev == before.parent_device\n"
            "assert physical.st_ino == before.parent_inode\n"
            "assert not (moved / 'link').exists()\n"
            "assert not (moved / 'link').is_symlink()\n"
            "assert tuple(parent.iterdir()) == ()\n",
            encoding="utf-8",
        )
        outcome = tm.ok(
            u.Cli.run_raw((sys.executable, "-I", str(script), str(tmp_path))),
        )
        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True, msg=outcome.stderr)
        tm.that(outcome.stderr, eq="")
