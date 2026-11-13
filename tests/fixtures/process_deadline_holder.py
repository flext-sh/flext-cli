"""Hold one supervised child under a process deadline, for deadline-scope tests.

Run as ``python process_deadline_holder.py <root> <mode> <deadline_seconds>``.
``deadline`` lets the deadline expire; ``expire`` expires it on demand from a
worker thread once the child recorded its pid; ``child`` is the supervised
child itself, which records its pid in ``<root>/child.pid`` and waits.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import ClassVar

from flext_cli import m, u


class TestsFlextCliProcessDeadlineHolder:
    """Run one deadline-scope role and leave with its status."""

    GRACE_SECONDS: ClassVar[float] = 0.5

    @staticmethod
    def _expire_once_child_runs(pid_file: Path) -> None:
        while not pid_file.is_file():
            time.sleep(0.05)
        u.Cli.process_deadline_expire()

    @classmethod
    def main(cls, root: Path, mode: str, deadline_seconds: float) -> int:
        """Run the requested role.

        Returns:
            Zero; an expired deadline ends the process with the timeout status.

        """
        pid_file = root / "child.pid"
        if mode == "child":
            pid_file.write_text(str(os.getpid()), encoding="utf-8")
            threading.Event().wait()
            return 0
        if mode == "expire":
            threading.Thread(
                target=cls._expire_once_child_runs, args=(pid_file,), daemon=True
            ).start()
        deadline = (
            m.Cli.ProcessDeadline(
                expires_at_monotonic=time.monotonic() + deadline_seconds,
                termination_grace_seconds=cls.GRACE_SECONDS,
            )
            if deadline_seconds
            else None
        )
        with u.Cli.process_deadline_scope(deadline):
            u.Cli.run([sys.executable, __file__, str(root), "child", "0"])
        return 0


if __name__ == "__main__":
    sys.exit(
        TestsFlextCliProcessDeadlineHolder.main(
            Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
        )
    )

__all__ = ["TestsFlextCliProcessDeadlineHolder"]
