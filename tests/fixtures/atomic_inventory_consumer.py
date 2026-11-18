"""Isolated consumer for physical-inventory failure scenarios.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import sys
from pathlib import Path

from flext_tests import tm

from tests import t, u


class TestsFlextCliAtomicInventoryConsumer:
    """Move the inventoried parent mid-scan without changing the parent interpreter."""

    @staticmethod
    def run(root: Path, failure: str) -> None:
        """Verify that an operation error or a cancellation keeps its own cause."""
        parent = root / "parent"
        parent.mkdir()
        directory = parent / "inventory"
        directory.mkdir()
        expected = directory.stat()
        armed = True

        def fail_inventory(event: str, args: tuple[t.Scalar, ...]) -> None:
            nonlocal armed
            if event != "os.scandir" or not armed or not isinstance(args[0], int):
                return
            observed = os.fstat(args[0])
            if (observed.st_dev, observed.st_ino) != (expected.st_dev, expected.st_ino):
                return
            armed = False
            parent.rename(root / "moved")
            if failure == "interrupt":
                raise KeyboardInterrupt("inventory cancelled")
            raise OSError(errno.EIO, "inventory failed")

        sys.addaudithook(fail_inventory)
        if failure == "interrupt":
            try:
                u.Cli.atomic_inventory_physical_directory(directory)
            except BaseExceptionGroup as error:
                tm.that(isinstance(error.exceptions[0], KeyboardInterrupt), eq=True)
                tm.that(isinstance(error.exceptions[1], OSError), eq=True)
            else:
                tm.reject("cancellation was normalized")
            return
        result = u.Cli.atomic_inventory_physical_directory(directory)
        tm.fail(result)
        error = result.exception
        assert isinstance(error, OSError)
        tm.that(error.errno, eq=errno.ESTALE)
        cause = error.__cause__
        assert isinstance(cause, ExceptionGroup)
        first = cause.exceptions[0]
        assert isinstance(first, OSError)
        tm.that(first.errno, eq=errno.EIO)
        tm.that(isinstance(cause.exceptions[1], OSError), eq=True)


if __name__ == "__main__":
    TestsFlextCliAtomicInventoryConsumer.run(Path(sys.argv[1]), sys.argv[2])
