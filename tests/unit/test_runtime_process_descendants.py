"""Normal-exit descendant containment contract."""

from __future__ import annotations

import os
import sys
import time
from typing import TYPE_CHECKING, ClassVar, override

import pytest

from flext_tests import tm
from tests import m, p, u

if TYPE_CHECKING:
    from pathlib import Path


class _ObservedWindowsCli(u.Cli):
    active_counts: ClassVar[list[int]] = []

    @classmethod
    @override
    def _windows_job_active_count(cls, job_handle: int) -> p.Result[int]:
        result: p.Result[int] = super()._windows_job_active_count(job_handle)
        if result.success:
            cls.active_counts.append(result.value)
        return result


def _process_exists(process_id: int) -> bool:
    try:
        os.kill(process_id, 0)
    except OSError:
        return False
    return True


class TestsFlextCliRuntimeProcessDescendants:
    """Prove root completion is not mistaken for boundary completion."""

    def test_normal_root_exit_leaves_no_descendant(self, tmp_path: Path) -> None:
        output_file = tmp_path / "normal-exit.log"
        heartbeat = tmp_path / "normal-heartbeat"
        process_info = tmp_path / "normal-process-info"
        child = (
            "import os,pathlib,sys,time;"
            "path=pathlib.Path(sys.argv[1]);"
            "group=getattr(os,'getpgrp',lambda:0)();"
            "pathlib.Path(sys.argv[2]).write_text(f'{os.getpid()} {group}');"
            "\nwhile True:\n path.write_text(str(time.monotonic()));time.sleep(.02)"
        )
        parent = (
            "import pathlib,subprocess,sys,time;"
            f"subprocess.Popen([sys.executable,'-c',{child!r},"
            "sys.argv[1],sys.argv[2]]);"
            "heartbeat=pathlib.Path(sys.argv[1]);"
            "info=pathlib.Path(sys.argv[2]);"
            "\nwhile not heartbeat.exists() or not info.exists():\n time.sleep(.01)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat), str(process_info)],
            output_file,
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        child_pid, process_group = (
            int(value) for value in process_info.read_text().split()
        )
        stopped_value = heartbeat.stat().st_mtime_ns
        time.sleep(0.15)
        tm.that(heartbeat.stat().st_mtime_ns, eq=stopped_value)
        tm.that(_process_exists(child_pid), eq=False)
        if os.name != "nt":
            with pytest.raises(ProcessLookupError):
                os.killpg(process_group, 0)
        tm.that(time.monotonic() - started, lt=5.0)

    @pytest.mark.skipif(os.name != "nt", reason="Windows Job Object contract")
    def test_windows_job_reports_zero_active_processes(self, tmp_path: Path) -> None:
        _ObservedWindowsCli.active_counts.clear()
        result = _ObservedWindowsCli.run_to_file(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            tmp_path / "windows-job.log",
            deadline=m.Cli.ProcessDeadline(
                expires_at_monotonic=time.monotonic() + 1.2,
                termination_grace_seconds=0.6,
                timeout_exit_code=96,
            ),
        )

        tm.ok(result)
        tm.that(result.value, eq=96)
        tm.that(_ObservedWindowsCli.active_counts, empty=False)
        tm.that(_ObservedWindowsCli.active_counts[-1], eq=0)


__all__: list[str] = ["TestsFlextCliRuntimeProcessDescendants"]
