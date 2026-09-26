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
    def windows_job_active_count(cls, job_handle: int) -> p.Result[int]:
        result: p.Result[int] = super().windows_job_active_count(job_handle)
        if result.success:
            cls.active_counts.append(result.value)
        return result


def _process_exists(process_id: int) -> bool:
    exists = True
    try:
        os.kill(process_id, 0)
    except OSError:
        exists = False
    return exists


class TestsFlextCliRuntimeProcessDescendants:
    """Prove root completion is not mistaken for boundary completion."""

    def test_normal_root_exit_leaves_no_descendant(self, tmp_path: Path) -> None:
        """A descendant alive when the root exits is gone when the run returns.

        The descendant announces its identity over a pipe and then blocks
        forever; the root reads that line (a blocking read, no polling),
        records it, and exits. Only containment can end the descendant, so
        its absence from the process table after ``run_to_file`` returns is
        the observable proof.
        """
        output_file = tmp_path / "normal-exit.log"
        process_info = tmp_path / "normal-process-info"
        child = (
            "import os,threading;"
            "print(os.getpid(),getattr(os,'getpgrp',lambda:0)(),flush=True);"
            "threading.Event().wait()"
        )
        parent = (
            "import pathlib,subprocess,sys;"
            f"child=subprocess.Popen([sys.executable,'-I','-S','-c',{child!r}],"
            "stdout=subprocess.PIPE);"
            "pathlib.Path(sys.argv[1]).write_bytes(child.stdout.readline())"
        )

        result = u.Cli().run_to_file(
            [sys.executable, "-I", "-S", "-c", parent, str(process_info)],
            output_file,
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=0)
        child_pid, process_group = (
            int(value) for value in process_info.read_text().split()
        )
        tm.that(_process_exists(child_pid), eq=False)
        if os.name != "nt":
            with pytest.raises(ProcessLookupError):
                os.killpg(process_group, 0)

    def test_windows_job_reports_zero_active_processes(self, tmp_path: Path) -> None:
        _ObservedWindowsCli.active_counts.clear()
        result = _ObservedWindowsCli.run_to_file(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            tmp_path / "windows-job.log",
            deadline=m.Cli.ProcessDeadline(
                expires_at_monotonic=time.monotonic() + 1.2,
                termination_grace_seconds=0.6,
            ),
        )

        tm.ok(result)
        tm.that(result.value.timed_out, eq=True)
        tm.that(result.value.raw_return_code, lt=0)
        if os.name == "nt":
            tm.that(_ObservedWindowsCli.active_counts, empty=False)
            tm.that(_ObservedWindowsCli.active_counts[-1], eq=0)
            return
        active_count = u.Cli.windows_job_active_count(0)
        tm.that(active_count.success, eq=True)
        tm.that(active_count.value, eq=0)
        tm.that(_ObservedWindowsCli.active_counts, empty=True)


__all__: list[str] = ["TestsFlextCliRuntimeProcessDescendants"]
