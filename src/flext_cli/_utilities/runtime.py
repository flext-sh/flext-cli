"""Generic external process runtime shared through ``u.Cli``."""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path

from flext_cli import c, m, p, r, t


class FlextCliUtilitiesRuntime:
    """Runtime helpers for external command execution."""

    @staticmethod
    def process_env(
        *,
        overrides: t.StrMapping | None = None,
        remove_keys: t.StrSequence = (),
    ) -> dict[str, str]:
        """Return one inherited process environment with optional overrides."""
        return m.Cli.ProcessEnvironmentSpec.model_validate(
            {
                "base_env": dict(os.environ),
                "overrides": overrides if overrides is not None else {},
                "remove_keys": tuple(remove_keys),
            },
        ).resolve()

    @staticmethod
    def _resolved_env(
        env: t.StrMapping | None,
        remove_env_keys: t.StrSequence = (),
    ) -> dict[str, str] | None:
        """Resolve the child environment with overrides and optional removals."""
        if env is None and not remove_env_keys:
            return None
        return FlextCliUtilitiesRuntime.process_env(
            overrides=env,
            remove_keys=remove_env_keys,
        )

    @staticmethod
    def run_raw(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: bytes | None = None,
    ) -> p.Result[m.Cli.CommandOutput]:
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
                env=FlextCliUtilitiesRuntime._resolved_env(env, remove_env_keys),
                input=input_data,
            )
        except subprocess.TimeoutExpired as exc:
            return r[m.Cli.CommandOutput].fail(
                f"timeout {exc.timeout}s: {shlex.join(list(cmd))}",
            )
        except c.EXC_OS_VALUE as exc:
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
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
    ) -> p.Result[m.Cli.CommandOutput]:
        """Run a command and fail on non-zero exit status."""

        def require_zero_exit(
            output: m.Cli.CommandOutput,
        ) -> p.Result[m.Cli.CommandOutput]:
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
            remove_env_keys=remove_env_keys,
        ).flat_map(
            require_zero_exit,
        )

    @staticmethod
    def run_checked(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
    ) -> p.Result[bool]:
        """Run a command and return a success flag."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
        ).map(lambda _: True)

    @staticmethod
    def capture(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
    ) -> p.Result[str]:
        """Run a command and return stripped stdout."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
        ).map(lambda output: output.stdout.strip())

    @staticmethod
    def run_to_file(
        cmd: t.StrSequence,
        output_file: t.Cli.TextPath,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
    ) -> p.Result[int]:
        """Run a command and write combined output to ``output_file``."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding=c.Cli.ENCODING_DEFAULT) as handle:
                result = subprocess.run(
                    list(cmd),
                    cwd=cwd,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    check=False,
                    timeout=timeout,
                    env=FlextCliUtilitiesRuntime._resolved_env(env, remove_env_keys),
                )
        except subprocess.TimeoutExpired as exc:
            return r[int].fail(f"timeout {exc.timeout}s: {shlex.join(list(cmd))}")
        except c.EXC_OS_VALUE as exc:
            return r[int].fail(f"execution error: {exc}")
        return r[int].ok(result.returncode)


__all__: list[str] = ["FlextCliUtilitiesRuntime"]
