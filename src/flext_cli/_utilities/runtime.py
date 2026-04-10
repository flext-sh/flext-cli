"""Generic external process runtime shared through ``u.Cli``."""

from __future__ import annotations

import shlex
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from flext_cli import c, m, r, t


class FlextCliUtilitiesRuntime:
    """Runtime helpers for external command execution."""

    @staticmethod
    def run_raw(
        cmd: t.StrSequence,
        cwd: t.Cli.PathLike | None = None,
        timeout: int | None = None,
        env: t.Cli.StrEnvMapping | None = None,
        input_data: bytes | None = None,
    ) -> r[m.Cli.CommandOutput]:
        """Run a command without enforcing a zero exit code."""
        start = time.monotonic()
        try:
            result = subprocess.run(
                list(cmd),
                cwd=cwd,
                capture_output=True,
                text=input_data is None,
                check=False,
                timeout=timeout,
                env=dict(env) if env is not None else None,
                input=input_data,
            )
        except subprocess.TimeoutExpired as exc:
            return r[m.Cli.CommandOutput].fail(
                f"timeout {exc.timeout}s: {shlex.join(list(cmd))}",
            )
        except (OSError, ValueError) as exc:
            return r[m.Cli.CommandOutput].fail(f"execution error: {exc}")
        stdout_raw = result.stdout or (b"" if input_data is not None else "")
        stderr_raw = result.stderr or (b"" if input_data is not None else "")
        duration = max(0.0, time.monotonic() - start)
        return r[m.Cli.CommandOutput].ok(
            m.Cli.CommandOutput(
                stdout=stdout_raw.decode()
                if isinstance(stdout_raw, bytes)
                else stdout_raw,
                stderr=stderr_raw.decode()
                if isinstance(stderr_raw, bytes)
                else stderr_raw,
                exit_code=result.returncode,
                duration=duration,
            ),
        )

    @staticmethod
    def run(
        cmd: t.StrSequence,
        cwd: t.Cli.PathLike | None = None,
        timeout: int | None = None,
        env: t.Cli.StrEnvMapping | None = None,
    ) -> r[m.Cli.CommandOutput]:
        """Run a command and fail on non-zero exit status."""

        def require_zero_exit(
            output: m.Cli.CommandOutput,
        ) -> r[m.Cli.CommandOutput]:
            if output.exit_code != 0:
                return r[m.Cli.CommandOutput].fail(
                    f"failed ({output.exit_code}): {shlex.join(list(cmd))}: {(output.stderr or output.stdout).strip()}",
                )
            return r[m.Cli.CommandOutput].ok(output)

        return FlextCliUtilitiesRuntime.run_raw(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
        ).flat_map(
            require_zero_exit,
        )

    @staticmethod
    def run_checked(
        cmd: t.StrSequence,
        cwd: t.Cli.PathLike | None = None,
        timeout: int | None = None,
        env: t.Cli.StrEnvMapping | None = None,
    ) -> r[bool]:
        """Run a command and return a success flag."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
        ).map(lambda _: True)

    @staticmethod
    def capture(
        cmd: t.StrSequence,
        cwd: t.Cli.PathLike | None = None,
        timeout: int | None = None,
        env: t.Cli.StrEnvMapping | None = None,
    ) -> r[str]:
        """Run a command and return stripped stdout."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
        ).map(lambda output: output.stdout.strip())

    @staticmethod
    def run_to_file(
        cmd: Sequence[str],
        output_file: t.Cli.PathLike,
        cwd: t.Cli.PathLike | None = None,
        timeout: int | None = None,
        env: t.Cli.StrEnvMapping | None = None,
    ) -> r[int]:
        """Run a command and write combined output to ``output_file``."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding=c.Cli.Encoding.DEFAULT) as handle:
                result = subprocess.run(
                    list(cmd),
                    cwd=cwd,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    check=False,
                    timeout=timeout,
                    env=dict(env) if env is not None else None,
                )
        except subprocess.TimeoutExpired as exc:
            return r[int].fail(f"timeout {exc.timeout}s: {shlex.join(list(cmd))}")
        except (OSError, ValueError) as exc:
            return r[int].fail(f"execution error: {exc}")
        return r[int].ok(result.returncode)


__all__ = ["FlextCliUtilitiesRuntime"]
