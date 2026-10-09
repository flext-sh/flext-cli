"""Real child completion ends monitoring before the execution deadline.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_tests import tm

from tests import u


class TestsRuntimeProcessCompletion:
    """A completed child must not wait for its execution deadline."""

    @staticmethod
    def test_completion_before_wake_clear_ends_monitoring(tmp_path: Path) -> None:
        """A child that completes is reported complete, never timed out.

        A monitor that lost the completion notification would sleep until its
        deadline and report ``timed_out``; the public outcome, not the host
        clock or private scheduling state, proves that it did not.
        """
        result = u.Cli().run_to_file(
            [sys.executable, "-I", "-S", "-c", "print('complete')"],
            tmp_path / "completion.log",
            timeout=4,
        )

        outcome = tm.ok(result)
        tm.that(outcome.raw_return_code, eq=0)
        tm.that(outcome.timed_out, eq=False)
        tm.that((tmp_path / "completion.log").read_text(), eq="complete\n")
