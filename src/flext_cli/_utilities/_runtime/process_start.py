"""Portable suspended-start and containment handoff.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING, BinaryIO

from flext_core import r

from flext_cli import m, p


class FlextCliUtilitiesRuntimeProcessStart:
    """Start one root process and contain it before child code can run."""

    if TYPE_CHECKING:

        @staticmethod
        def _spawn_streamed_process(
            command: m.Cli.RuntimeSpawnCommand,
            stdin_handle: BinaryIO | None,
            *,
            options: p.Cli.RuntimeSpawnOptions,
        ) -> p.Cli.ProcessHandle: ...

        @staticmethod
        def _streamed_creation_flags() -> int: ...

        @classmethod
        def _signal_process_tree(
            cls,
            process: p.Cli.ProcessHandle,
            job_handle: int,
            tree_signal: m.Cli.ProcessTreeSignal,
        ) -> p.Result[bool]: ...

        @classmethod
        def _windows_job_close(cls, job_handle: int) -> str | None: ...

        @classmethod
        def _windows_job_create(cls, process_id: int) -> p.Result[int]: ...

        @classmethod
        def _windows_process_resume(cls, process_id: int) -> str | None: ...

    @classmethod
    def _start_contained_process(
        cls,
        command: m.Cli.RuntimeSpawnCommand,
        stdin_handle: BinaryIO | None,
        *,
        options: p.Cli.RuntimeSpawnOptions,
    ) -> p.Result[tuple[p.Cli.ProcessHandle, int]]:
        contained = options.model_copy(
            update={"creation_flags": cls._streamed_creation_flags()},
        )
        process = cls._spawn_streamed_process(command, stdin_handle, options=contained)
        job_result = cls._windows_job_create(process.pid)
        if job_result.failure:
            cls._discard_uncontained_process(process, 0)
            return r[tuple[p.Cli.ProcessHandle, int]].from_failure(job_result)
        job_handle = job_result.value
        resume_error = cls._windows_process_resume(process.pid)
        if resume_error is not None:
            cls._discard_uncontained_process(process, job_handle)
            return r[tuple[p.Cli.ProcessHandle, int]].fail(resume_error)
        return r[tuple[p.Cli.ProcessHandle, int]].ok((process, job_handle))

    @classmethod
    def _discard_uncontained_process(
        cls,
        process: p.Cli.ProcessHandle,
        job_handle: int,
    ) -> None:
        _ = cls._signal_process_tree(
            process,
            job_handle,
            m.Cli.ProcessTreeSignal(signal_number=signal.SIGKILL, force=True),
        )
        process.wait()
        _ = cls._windows_job_close(job_handle)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessStart"]
