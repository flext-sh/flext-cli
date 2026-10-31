"""Public command-result composition for ``u.Cli`` runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shlex
from collections.abc import Sequence
from typing import TYPE_CHECKING

from flext_cli import c, p, r, t
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessOutcome


class FlextCliUtilitiesRuntimeCommands(
    FlextCliUtilitiesRuntimeProcessOutcome,
):
    """Compose captured command primitives without owning subprocess creation."""

    if TYPE_CHECKING:

        @classmethod
        def run_raw(
            cls,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: p.Cli.ProcessOptions | None = None,
            capture: bool = True,
        ) -> p.Result[p.Cli.CommandOutput]: ...

    @classmethod
    def run(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
        capture: bool = True,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Require a zero exit without timeout or forwarded interruption.

        A non-zero, timed-out or interrupted child fails with its typed
        outcome in ``error_data`` (``c.Cli.PROCESS_EXIT_CODE_KEY``,
        ``PROCESS_TIMED_OUT_KEY``, ``PROCESS_FORWARDED_SIGNAL_KEY``), so the
        caller propagates the child's exit without parsing the message.

        Returns:
            The resulting ``p.Result[p.Cli.CommandOutput]``.

        """

        def require_zero_exit(
            output: p.Cli.CommandOutput,
        ) -> p.Result[p.Cli.CommandOutput]:
            if not cls.process_succeeded(output.outcome):
                detail = (output.stderr or output.stdout).strip()
                return r[p.Cli.CommandOutput].fail(
                    f"failed ({output.outcome.raw_return_code}): "
                    f"{shlex.join(list(cmd))}: "
                    f"timed_out={output.outcome.timed_out}, "
                    f"forwarded_signal={output.outcome.forwarded_signal}: {detail}",
                    error_data={
                        c.Cli.PROCESS_EXIT_CODE_KEY: output.outcome.raw_return_code,
                        c.Cli.PROCESS_TIMED_OUT_KEY: output.outcome.timed_out,
                        c.Cli.PROCESS_FORWARDED_SIGNAL_KEY: (
                            output.outcome.forwarded_signal
                        ),
                    },
                )
            return r[p.Cli.CommandOutput].ok(output)

        return cls.run_raw(
            cmd,
            cwd=cwd,
            timeout=timeout,
            options=options,
            capture=capture,
        ).flat_map(require_zero_exit)

    @classmethod
    def run_checked(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
        capture: bool = True,
    ) -> p.Result[bool]:
        """Run a command and return a success flag.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return cls.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            options=options,
            capture=capture,
        ).map(lambda _: True)

    @classmethod
    def run_live(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Run a command with inherited live stdout and stderr.

        Returns:
            The resulting ``p.Result[p.Cli.CommandOutput]``.

        """
        return cls.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            options=options,
            capture=False,
        )

    @classmethod
    def capture(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
    ) -> p.Result[str]:
        """Run a command and return stripped stdout.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return cls.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            options=options,
        ).map(lambda output: output.stdout.strip())


__all__: list[str] = ["FlextCliUtilitiesRuntimeCommands"]
