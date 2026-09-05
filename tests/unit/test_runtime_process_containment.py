"""Signal, deadline, and descendant containment contracts."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from collections import UserList
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, override

import pytest

from flext_tests import tm
from tests import m, p, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(
    *, seconds: float, grace: float, exit_code: int = 124
) -> m.Cli.ProcessDeadline:
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
        timeout_exit_code=exit_code,
    )


def _survivor_acknowledged(probe: Path, acknowledgement: Path) -> bool:
    """Ask an owned descendant to prove it is still able to execute."""
    probe.touch()
    acknowledgement_deadline = time.monotonic() + 0.5
    while not acknowledgement.exists() and time.monotonic() < acknowledgement_deadline:
        time.sleep(0.01)
    return acknowledgement.exists()


def _assert_owned_descendant_stopped(
    process_info: Path, probe: Path, acknowledgement: Path
) -> None:
    """Prove no owned descendant can execute and clean an observed failure."""
    child_survived = _survivor_acknowledged(probe, acknowledgement)
    if child_survived:
        os.kill(int(process_info.read_text(encoding="utf-8")), signal.SIGTERM)
    tm.that(child_survived, eq=False)


def _assert_timeout_empties_descendants[
    Output: (p.Cli.CommandOutput | p.Cli.CommandBytesOutput)
](tmp_path: Path, execute: Callable[[tuple[str, ...]], p.Result[Output]]) -> None:
    process_info = tmp_path / "captured-process-info"
    survivor_probe = tmp_path / "captured-survivor-probe"
    survivor_ack = tmp_path / "captured-survivor-ack"
    child = (
        "import os,pathlib,sys,time;"
        "info=pathlib.Path(sys.argv[1]);probe=pathlib.Path(sys.argv[2]);"
        "ack=pathlib.Path(sys.argv[3]);info.write_text(str(os.getpid()));"
        "\nwhile True:\n"
        " if probe.exists(): ack.touch()\n"
        " time.sleep(.01)"
    )
    parent = (
        "import pathlib,subprocess,sys,time;"
        f"subprocess.Popen([sys.executable,'-c',{child!r},"
        "sys.argv[1],sys.argv[2],sys.argv[3]],stdout=subprocess.DEVNULL,"
        "stderr=subprocess.DEVNULL);"
        "info=pathlib.Path(sys.argv[1]);"
        "\nwhile not info.exists():\n time.sleep(.01)\n"
        "time.sleep(30)"
    )

    result = execute((
        sys.executable,
        "-c",
        parent,
        str(process_info),
        str(survivor_probe),
        str(survivor_ack),
    ))

    tm.fail(result, has="timeout")
    _assert_owned_descendant_stopped(process_info, survivor_probe, survivor_ack)


class _InterruptingCommand(UserList[str]):
    @override
    def __iter__(self) -> Iterator[str]:
        signal.raise_signal(signal.SIGTERM)
        return super().__iter__()


class TestsFlextCliRuntimeProcessContainment:
    """Prove pre-spawn signals, deadline escalation, and empty boundaries."""

    def test_run_raw_timeout_leaves_no_descendant(self, tmp_path: Path) -> None:
        """Return only after the captured text runner empties its owned boundary."""
        _assert_timeout_empties_descendants(
            tmp_path, lambda command: u.Cli().run_raw(command, timeout=1)
        )

    def test_run_timeout_leaves_no_descendant(self, tmp_path: Path) -> None:
        """Return only after the checked text runner empties its owned boundary."""
        _assert_timeout_empties_descendants(
            tmp_path, lambda command: u.Cli().run(command, timeout=1)
        )

    def test_run_bytes_timeout_leaves_no_descendant(self, tmp_path: Path) -> None:
        """Return only after the byte runner empties its owned boundary."""
        _assert_timeout_empties_descendants(
            tmp_path, lambda command: u.Cli().run_bytes(command, timeout=1)
        )

    def test_return_proves_owned_process_boundary_empty(self, tmp_path: Path) -> None:
        process_info = tmp_path / "boundary-process-info"
        survivor_probe = tmp_path / "boundary-survivor-probe"
        survivor_ack = tmp_path / "boundary-survivor-ack"
        nested = (
            "import os,pathlib,sys,time;"
            "info=pathlib.Path(sys.argv[1]);probe=pathlib.Path(sys.argv[2]);"
            "ack=pathlib.Path(sys.argv[3]);info.write_text(str(os.getpid()));"
            "\nwhile True:\n"
            " if probe.exists(): ack.touch()\n"
            " time.sleep(.01)"
        )
        root = (
            "import pathlib,subprocess,sys,time;"
            f"subprocess.Popen([sys.executable,'-c',{nested!r},"
            "sys.argv[1],sys.argv[2],sys.argv[3]],"
            "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
            "info=pathlib.Path(sys.argv[1]);"
            "\nwhile not info.exists():\n time.sleep(.01)"
        )

        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                root,
                str(process_info),
                str(survivor_probe),
                str(survivor_ack),
            ],
            tmp_path / "boundary.log",
            deadline=_deadline(seconds=2.0, grace=0.8, exit_code=94),
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        _assert_owned_descendant_stopped(process_info, survivor_probe, survivor_ack)

    @pytest.mark.parametrize("signal_number", [signal.SIGINT, signal.SIGTERM])
    def test_manual_signal_is_forwarded_without_exit_normalization(
        self, tmp_path: Path, signal_number: signal.Signals
    ) -> None:
        ready = tmp_path / f"child-ready-{signal_number}"
        output_file = tmp_path / f"manual-{signal_number}.log"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
            "pathlib.Path(sys.argv[1]).touch();time.sleep(30)"
        )
        signaler_errors: list[str] = []

        def signal_when_ready() -> None:
            ready_deadline = time.monotonic() + 1.0
            while not ready.exists() and time.monotonic() < ready_deadline:
                time.sleep(0.005)
            if ready.exists():
                signal.raise_signal(signal_number)
            else:
                signaler_errors.append("child did not become ready")

        signaler = threading.Thread(target=signal_when_ready, daemon=False)
        signaler.start()
        signal_started = time.monotonic()
        result = u.Cli().run_to_file(
            [sys.executable, "-c", child, str(ready)],
            output_file,
            deadline=_deadline(seconds=3.0, grace=1.0, exit_code=95),
        )
        signaler.join(timeout=1.0)

        tm.ok(result)
        tm.that(result.value, eq=-signal_number)
        tm.that(signaler_errors, eq=[])
        tm.that(signaler.is_alive(), eq=False)
        tm.that(time.monotonic() - signal_started, lt=6.0)

    def test_pre_spawn_signal_is_captured_before_command_materialization(
        self, tmp_path: Path
    ) -> None:
        marker = tmp_path / "must-not-spawn"
        result = u.Cli().run_to_file(
            _InterruptingCommand([
                sys.executable,
                "-c",
                "import pathlib,sys;pathlib.Path(sys.argv[1]).touch()",
                str(marker),
            ]),
            tmp_path / "pre-spawn.log",
        )

        tm.ok(result)
        tm.that(result.value, eq=-signal.SIGTERM)
        tm.that(marker.exists(), eq=False)

    def test_deadline_forwards_interrupt_before_forced_cleanup(
        self, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "interrupt.log"
        script = (
            "import os,signal,time;"
            "handler=lambda *_: (os.write(1,b'interrupted\\n'),raise_exit())[0];"
            "raise_exit=lambda: (_ for _ in ()).throw(SystemExit(0));"
            "signal.signal(signal.SIGINT,handler);"
            "signal.signal(getattr(signal,'SIGBREAK',signal.SIGINT),handler);"
            "time.sleep(30)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", script],
            output_file,
            deadline=_deadline(seconds=1.2, grace=0.6, exit_code=91),
        )

        tm.ok(result)
        tm.that(result.value, eq=91)
        tm.that(output_file.read_bytes(), has=b"interrupted")
        tm.that(time.monotonic() - started, lt=1.2)

    def test_deadline_kills_recursive_process_tree(self, tmp_path: Path) -> None:
        output_file = tmp_path / "tree.log"
        process_info = tmp_path / "process-info"
        survivor_probe = tmp_path / "survivor-probe"
        survivor_ack = tmp_path / "survivor-ack"
        child = (
            "import os,pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "info=pathlib.Path(sys.argv[1]);probe=pathlib.Path(sys.argv[2]);"
            "ack=pathlib.Path(sys.argv[3]);info.write_text(str(os.getpid()));"
            "\nwhile True:\n"
            " if probe.exists(): ack.touch()\n"
            " time.sleep(.01)"
        )
        parent = (
            "import signal,subprocess,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            f"subprocess.Popen([sys.executable,'-c',{child!r},"
            "sys.argv[1],sys.argv[2],sys.argv[3]]);"
            "time.sleep(30)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                parent,
                str(process_info),
                str(survivor_probe),
                str(survivor_ack),
            ],
            output_file,
            deadline=_deadline(seconds=1.5, grace=0.7, exit_code=92),
        )

        tm.ok(result)
        tm.that(result.value, eq=92)
        tm.that(process_info.exists(), eq=True)
        _assert_owned_descendant_stopped(process_info, survivor_probe, survivor_ack)
        tm.that(time.monotonic() - started, lt=2.0)


__all__: list[str] = ["TestsFlextCliRuntimeProcessContainment"]
