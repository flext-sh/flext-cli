"""Public command-result composition for ``u.Cli`` runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shlex
from typing import TYPE_CHECKING

from flext_cli import p, r, t
from flext_cli._utilities import FlextCliUtilitiesRuntimeProcessOutcomeMixin


class FlextCliUtilitiesRuntimeCommandsMixin(
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
):
    """Compose captured command primitives without owning subprocess creation."""

    if TYPE_CHECKING:

        @classmethod
        def run_raw(
            cls,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
            input_data: str | bytes | None = None,
            *,
            capture: bool = True,
        ) -> p.Result[p.Cli.CommandOutput]: ...

    @classmethod
    def run(
        cls,
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
        *,
        capture: bool = True,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Require a zero exit without timeout or forwarded interruption.

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
                )
            return r[p.Cli.CommandOutput].ok(output)

        return cls.run_raw(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=capture,
        ).flat_map(require_zero_exit)

    @classmethod
    def run_checked(
        cls,
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
        *,
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
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=capture,
        ).map(lambda _: True)

    @classmethod
    def run_live(
        cls,
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Run a command with inherited live stdout and stderr.

        Returns:
            The resulting ``p.Result[p.Cli.CommandOutput]``.

        """
        return cls.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=False,
        )

    @classmethod
    def capture(
        cls,
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[str]:
        """Run a command and return stripped stdout.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return cls.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
        ).map(lambda output: output.stdout.strip())


__all__: list[str] = ["FlextCliUtilitiesRuntimeCommandsMixin"]
