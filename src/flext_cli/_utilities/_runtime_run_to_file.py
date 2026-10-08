"""Canonical streamed process runner exposed through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import p, settings, t
from flext_cli._utilities import FlextCliUtilitiesRuntimeProcessExecutionMixin
from flext_cli._utilities._runtime_models import (
    RuntimeProcessOptions,
    RuntimeProcessRequest,
)


class FlextCliUtilitiesRuntimeRunToFileMixin(
    FlextCliUtilitiesRuntimeProcessExecutionMixin,
):
    """Validate and dispatch one portable streamed process lifecycle."""

    if TYPE_CHECKING:

        @staticmethod
        def _resolved_env(
            env: t.StrMapping | None,
            remove_env_keys: t.StrSequence = (),
        ) -> dict[str, str] | None: ...

    @classmethod
    def run_to_file(
        cls,
        cmd: t.StrSequence,
        output_file: t.Cli.TextPath,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: RuntimeProcessOptions | None = None,
    ) -> p.Result[p.Cli.ProcessOutcome]:
        """Stream combined bytes live and durably under one absolute deadline.

        Containment owns the inherited POSIX process group or Windows Job
        Object. Trusted project tools remain inside that boundary; deliberate
        POSIX ``setsid()`` escape is outside this contract. The deadline covers
        child execution, termination, reaping, stream drain, and durable flush.
        An outer caller wall remains responsible for an OS syscall that becomes
        uninterruptible.

        Returns:
            The resulting ``p.Result[p.Cli.ProcessOutcome]``.

        """
        launch = options if options is not None else RuntimeProcessOptions()
        return cls._execute_streamed_process(
            RuntimeProcessRequest(
                cmd=cmd,
                output_path=Path(output_file),
                cwd=cwd,
                env=cls._resolved_env(launch.env, launch.remove_env_keys),
                input_data=launch.input_data,
                capture_output=False,
                live=launch.live,
                heartbeat_seconds=(
                    settings.cli_process_heartbeat_seconds
                    if launch.live and launch.heartbeat_seconds is None
                    else launch.heartbeat_seconds
                ),
                timeout=timeout,
                deadline=launch.deadline,
            ),
        ).map(lambda output: output.outcome)


__all__: list[str] = ["FlextCliUtilitiesRuntimeRunToFileMixin"]
