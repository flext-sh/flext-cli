"""Extracted facade class for runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import shlex
from collections.abc import Mapping, Sequence
from typing import BinaryIO, ClassVar, override

from flext_core import r, u

from flext_cli import c, m, p, t
from flext_cli._utilities._runtime import (
    FlextCliUtilitiesRuntimeCommands,
    FlextCliUtilitiesRuntimeRunToFile,
)
from flext_cli._utilities.native_runtime import (
    TimeoutExpired,
    spawn_streamed_process,
    streamed_creation_flags,
)


class FlextCliUtilitiesRuntime(
    FlextCliUtilitiesRuntimeCommands,
    FlextCliUtilitiesRuntimeRunToFile,
):
    """Connect typed process components to the native subprocess owner."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def process_env(
        *,
        overrides: Mapping[str, str] | None = None,
        remove_keys: Sequence[str] = (),
    ) -> dict[str, str]:
        """Resolve inherited process inputs through the environment model.

        Returns:
            The resulting ``dict[str, str]``.

        """
        return m.Cli.ProcessEnvironmentSpec.model_validate({
            "base_env": dict(os.environ),
            "overrides": overrides if overrides is not None else {},
            "remove_keys": tuple(remove_keys),
        }).resolve()

    @staticmethod
    @override
    def _resolved_env(
        env: Mapping[str, str] | None,
        remove_env_keys: Sequence[str] = (),
        *,
        inherit_environment: bool = True,
    ) -> dict[str, str] | None:
        """Apply overlays and explicit removals without borrowing environments.

        Returns:
            The resulting ``dict[str, str] | None``.

        """
        if not inherit_environment:
            return {
                key: value
                for key, value in (() if env is None else env.items())
                if key not in remove_env_keys
            }
        if env is None and not remove_env_keys:
            return None
        return FlextCliUtilitiesRuntime.process_env(
            overrides=env, remove_keys=remove_env_keys
        )

    @staticmethod
    @override
    def _spawn_streamed_process(
        command: m.Cli.RuntimeSpawnCommand,
        stdin_handle: BinaryIO | None,
        *,
        options: p.Cli.RuntimeSpawnOptions,
    ) -> p.Cli.ProcessHandle:
        """Delegate child creation to the single native process engine.

        Returns:
            The resulting ``p.Cli.ProcessHandle``.

        """
        return spawn_streamed_process(command, stdin_handle, options=options)

    @staticmethod
    def child_communicate(
        process: p.Cli.ProcessHandle,
        *,
        timeout: float | None,
    ) -> p.Result[tuple[bytes, bytes]]:
        """Drain process pipes through the declared timeout result boundary.

        Returns:
            The resulting ``p.Result[tuple[bytes, bytes]]``.

        """
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except TimeoutExpired as exc:
            return r[tuple[bytes, bytes]].fail(
                f"timeout {exc.timeout}s: pid {process.pid}",
            )
        except c.EXC_OS_VALUE as exc:
            return r[tuple[bytes, bytes]].fail(
                f"process wait error: {exc}", exception=exc
            )
        return r[tuple[bytes, bytes]].ok((stdout or b"", stderr or b""))

    @staticmethod
    @override
    def _streamed_creation_flags() -> int:
        """Read native platform containment flags.

        Returns:
            The resulting ``int``.

        """
        return streamed_creation_flags()

    @classmethod
    @override
    def run_raw(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
        capture: bool = True,
        env: Mapping[str, str] | None = None,
        remove_env_keys: Sequence[str] | None = None,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Execute a command and preserve its actual exit outcome.

        Returns:
            The resulting ``p.Result[p.Cli.CommandOutput]``.

        """

        def decode_output(
            output: p.Cli.CommandBytesOutput,
        ) -> p.Result[p.Cli.CommandOutput]:
            try:
                stdout = output.stdout.decode("utf-8")
                stderr = output.stderr.decode("utf-8")
            except UnicodeDecodeError as exc:
                return r[p.Cli.CommandOutput].fail(
                    f"non-UTF-8 output from {shlex.join(list(cmd))}: {exc}",
                    exception=exc,
                )
            return r[p.Cli.CommandOutput].ok(
                m.Cli.CommandOutput(
                    stdout=stdout,
                    stderr=stderr,
                    outcome=output.outcome,
                    duration=output.duration,
                ),
            )

        launch = (
            m.Cli.ProcessOptions.model_validate(options, from_attributes=True)
            if options is not None
            else m.Cli.ProcessOptions()
        )
        if env is not None or remove_env_keys is not None:
            launch = m.Cli.ProcessOptions(
                env=env if env is not None else launch.env,
                remove_env_keys=(
                    remove_env_keys
                    if remove_env_keys is not None
                    else launch.remove_env_keys
                ),
                inherit_environment=launch.inherit_environment,
                input_data=launch.input_data,
                inherit_stdin=launch.inherit_stdin,
                live=launch.live,
                heartbeat_seconds=launch.heartbeat_seconds,
                deadline=launch.deadline,
                pass_fds=launch.pass_fds,
                stderr_file=launch.stderr_file,
                isolation=launch.isolation,
                signal_wave=launch.signal_wave,
            )
        return cls._execute_streamed_process(
            cls._runtime_request(cmd, cwd, timeout, launch).model_copy(
                update={"capture_output": capture},
            ),
        ).flat_map(decode_output)

    @classmethod
    @override
    def run_bytes(
        cls,
        cmd: Sequence[str],
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Execute a command while preserving byte-exact output.

        Returns:
            The resulting ``p.Result[p.Cli.CommandBytesOutput]``.

        """
        launch = (
            m.Cli.ProcessOptions.model_validate(options, from_attributes=True)
            if options is not None
            else m.Cli.ProcessOptions()
        )
        return cls._execute_streamed_process(
            cls._runtime_request(cmd, cwd, timeout, launch),
        )


__all__: list[str] = ["FlextCliUtilitiesRuntime"]
