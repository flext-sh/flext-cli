"""Public hard-wall contract under real live-output backpressure."""

from __future__ import annotations

import os
import sys
import time
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliRuntimeStreamedProcessHardWall:
    """Prove backpressure never blocks authoritative durable capture."""

    @pytest.mark.skipif(os.name == "nt", reason="POSIX pipe backpressure contract")
    def test_live_backpressure_preserves_durable_bytes_and_hard_wall(
        self, tmp_path: Path
    ) -> None:
        """Truncate only live output when its real sink stops consuming."""
        output_file = tmp_path / "backpressure.log"
        payload_bytes = 2 * 1024 * 1024
        child = (
            "import os;"
            f"payload=b'x'*{payload_bytes};"
            "\nwhile payload:"
            "\n written=os.write(1,payload)"
            "\n payload=payload[written:]"
        )
        harness = (
            "import os,sys,time;"
            "from flext_cli import m,u;"
            "read_fd,write_fd=os.pipe();saved=os.dup(1);"
            "os.dup2(write_fd,1);os.close(write_fd);"
            "deadline=m.Cli.ProcessDeadline("
            "expires_at_monotonic=time.monotonic()+3.0,"
            "termination_grace_seconds=1.0,timeout_exit_code=97);"
            f"result=u.Cli.run_to_file([sys.executable,'-c',{child!r}],"
            f"{str(output_file)!r},live=True,deadline=deadline);"
            "os.dup2(saved,1);os.close(saved);os.close(read_fd);"
            "raise SystemExit(result.value if result.success else 99)"
        )
        started = time.monotonic()

        completed = u.Cli().run_bytes(
            [sys.executable, "-c", harness], timeout=4
        )

        tm.ok(completed)
        tm.that(completed.value.exit_code, eq=0)
        tm.that(output_file.stat().st_size, eq=payload_bytes)
        tm.that(completed.value.stderr, has=b"live output truncated")
        tm.that(time.monotonic() - started, lt=3.5)


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcessHardWall"]
