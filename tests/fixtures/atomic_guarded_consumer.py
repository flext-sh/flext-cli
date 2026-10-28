"""Isolated consumer for guarded-publication audit scenarios.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
import errno
import sys
from pathlib import Path

from flext_tests import tm

from flext_cli import t, u


class TestsFlextCliAtomicGuardedConsumer:
    """Exercise native audit boundaries without changing the parent interpreter."""

    @staticmethod
    def run(root: Path, scenario: str) -> None:
        """Verify publication and cleanup for one isolated audit scenario."""
        destination = root / "atomic.txt"
        before = tm.ok(u.Cli.atomic_read_binary_file_state(destination))
        armed = True

        def audit(event: str, args: tuple[t.Scalar, ...],) -> None:
            nonlocal armed
            if not armed:
                return
            if scenario == "unlink-failure":
                if event == "os.remove" and destination.exists():
                    armed = False
                    raise OSError(errno.EIO, "staged unlink failed")
            elif event in {"os.link", "os.rename"} and args[1] == destination.name:
                armed = False
                destination.write_bytes(b"concurrent")

        sys.addaudithook(audit)
        result = u.Cli.atomic_write_binary_file_guarded(
            before,
            b"published" if scenario == "unlink-failure" else b"replacement",
            permission_mode=0o600,
        )
        tm.that(armed, eq=False)
        tm.fail(result)
        if scenario == "unlink-failure":
            tm.fail(result, has="staged unlink failed")
            tm.that(destination.read_bytes(), eq=b"published")
            tm.that(destination.stat().st_nlink, eq=1)
        else:
            tm.that(destination.read_bytes(), eq=b"concurrent")
        tm.that(
            {path.name for path in root.iterdir()}, eq={"consumer.py", "atomic.txt"}
        )


if __name__ == "__main__":
    TestsFlextCliAtomicGuardedConsumer.run(Path(sys.argv[1]), sys.argv[2])
