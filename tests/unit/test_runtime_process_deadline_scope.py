"""Process deadline scope through the native one-shot timer and the supervisor.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import ClassVar

from tests import c, tm, u


class TestsFlextCliRuntimeProcessDeadlineScope:
    """An expired deadline stops the owned child and exits with the timeout status."""

    HOLDER: ClassVar[Path] = (
        Path(__file__).parents[1] / "fixtures" / "process_deadline_holder.py"
    )

    @staticmethod
    def _alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True

    @classmethod
    def _expire(cls, tmp_path: Path, mode: str, deadline_seconds: str) -> None:
        result = u.Cli.run([
            sys.executable,
            str(cls.HOLDER),
            str(tmp_path),
            mode,
            deadline_seconds,
        ])
        tm.fail(result)
        data = tm.not_none(result.error_data)
        tm.that(data[c.Cli.PROCESS_EXIT_CODE_KEY], eq=c.Cli.PROCESS_TIMEOUT_EXIT_CODE)
        child = int((tmp_path / "child.pid").read_text(encoding="utf-8"))
        tm.that(cls._alive(child), eq=False)

    @classmethod
    def test_expired_deadline_stops_the_owned_child(cls, tmp_path: Path) -> None:
        """The kernel timer fires; the supervised child is reaped before exit."""
        cls._expire(tmp_path, "deadline", "15")

    @classmethod
    def test_expire_on_demand_uses_the_same_stop(cls, tmp_path: Path) -> None:
        """Expiring from another thread stops the child the same way."""
        cls._expire(tmp_path, "expire", "600")

    @classmethod
    def test_scope_without_deadline_expires_only_on_demand(cls, tmp_path: Path) -> None:
        """No timer is armed; the on-demand expiry still stops the child."""
        cls._expire(tmp_path, "expire", "0")
