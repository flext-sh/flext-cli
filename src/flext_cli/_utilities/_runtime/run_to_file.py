"""Canonical streamed process runner exposed through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import m, p, settings, t
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessExecution


class FlextCliUtilitiesRuntimeRunToFile(
    FlextCliUtilitiesRuntimeProcessExecution,
):
    """Validate and dispatch one portable streamed process lifecycle."""

    if TYPE_CHECKING:

        @staticmethod
        def _resolved_env(
            env: Mapping[str, str] | None,
            remove_env_keys: Sequence[str] = (),
            *,
            inherit_environment: bool = True,
        ) -> dict[str, str] | None: ...

    @classmethod
    def _runtime_request_fields(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None,
        timeout: int | None,
        launch: m.Cli.ProcessOptions,
    ) -> dict[str, object]:
        """Resolve one launch declaration into the shared lifecycle request fields.

        Returns:
            The request fields with the resolved child environment and every
            launch input; callers add their capture and durable output fields
            and validate the complete request once through
            ``m.Cli.RuntimeProcessRequest.model_validate``.

        """
        return {
            "cmd": cmd,
            "cwd": cwd,
            "env": cls._resolved_env(
                launch.env,
                launch.remove_env_keys,
                inherit_environment=launch.inherit_environment,
            ),
            "input_data": launch.input_data,
            "inherit_stdin": launch.inherit_stdin,
            "timeout": timeout,
            "deadline": launch.deadline,
            "live": launch.live,
            "heartbeat_seconds": launch.heartbeat_seconds,
            "isolation": launch.isolation,
            "pass_fds": tuple(launch.pass_fds),
            "signal_wave": launch.signal_wave,
        }

    @classmethod
    def run_to_file(
        cls,
        cmd: Sequence[str],
        output_file: t.Cli.TextPath,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
    ) -> p.Result[p.Cli.ProcessOutcome]:
        """Stream exact bytes to combined or separate durable destinations.

        Containment owns the inherited POSIX process group or Windows Job
        Object. Trusted project tools remain inside that boundary; deliberate
        POSIX ``setsid()`` escape is outside this contract. The deadline covers
        child execution, termination, reaping, stream drain, and durable flush.
        An outer caller wall remains responsible for an OS syscall that becomes
        uninterruptible. Separate stderr durability rides on ``options``.

        Returns:
            The resulting ``p.Result[p.Cli.ProcessOutcome]``.

        """
        launch = (
            m.Cli.ProcessOptions.model_validate(options, from_attributes=True)
            if options is not None
            else m.Cli.ProcessOptions()
        )
        return cls._execute_streamed_process(
            m.Cli.RuntimeProcessRequest.model_validate({
                **cls._runtime_request_fields(cmd, cwd, timeout, launch),
                "output_path": Path(output_file),
                "stderr_path": (
                    Path(launch.stderr_file) if launch.stderr_file is not None else None
                ),
                "capture_output": False,
                "heartbeat_seconds": (
                    settings.cli_process_heartbeat_seconds
                    if launch.live and launch.heartbeat_seconds is None
                    else launch.heartbeat_seconds
                ),
            }),
        ).map(lambda output: output.outcome)


__all__: list[str] = ["FlextCliUtilitiesRuntimeRunToFile"]
