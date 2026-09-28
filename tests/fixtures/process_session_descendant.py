"""Fork one descendant and exit, for managed-process session-group tests."""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path


def _descendant(sentinel: Path, mode: str) -> None:
    """Run as the forked descendant until the session group is signaled."""
    devnull = os.open(os.devnull, os.O_RDWR)
    for stream in (0, 1, 2):
        os.dup2(devnull, stream)
    if mode == "terminate":

        def record(*_: object) -> None:
            sentinel.write_bytes(b"terminated")
            os._exit(0)

        signal.signal(signal.SIGTERM, record)
    time.sleep(30)
    os._exit(0)


def main() -> None:
    """Fork the descendant, print its pid, and exit while it keeps running."""
    sentinel = Path(sys.argv[1])
    mode = sys.argv[2]
    pid = os.fork()
    if pid == 0:
        _descendant(sentinel, mode)
    print(pid, flush=True)


if __name__ == "__main__":
    main()
