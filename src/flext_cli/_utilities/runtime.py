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
        *, overrides: t.StrMapping | None = None, remove_keys: t.StrSequence = ()
    ) -> dict[str, str]:
        """Return one inherited process environment with optional overrides."""
        return m.Cli.ProcessEnvironmentSpec.model_validate({
            "base_env": dict(os.environ),
            "overrides": overrides if overrides is not None else {},
            "remove_keys": tuple(remove_keys),
        }).resolve()

    @staticmethod
    def _resolved_env(
        env: t.StrMapping | None, remove_env_keys: t.StrSequence = ()
    ) -> dict[str, str] | None:
        """Resolve the child environment with overrides and optional removals."""
        if env is None and not remove_env_keys:
            return None
        return FlextCliUtilitiesRuntime.process_env(
            overrides=env, remove_keys=remove_env_keys
        )

    @staticmethod
    def run_raw(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
        *,
        capture: bool = True,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Run a command without enforcing a zero exit code.

        Accepts text or binary stdin (text is UTF-8 encoded). When ``capture``
        is True (default) stdout/stderr are captured and returned as text
        (UTF-8); non-UTF-8 output fails closed with a typed error instead of
        crashing or surfacing a generic error. When ``capture`` is False the
        child inherits the parent's stdout/stderr so its output streams live
        (for long-running makes/rollouts); the returned stdout/stderr are then
        empty and only the exit code is meaningful.
        """
        start = time.monotonic()
        stdin = (
            input_data.encode("utf-8") if isinstance(input_data, str) else input_data
        )
        try:
            result = subprocess.run(
                list(cmd),
                cwd=cwd,
                capture_output=capture,
                text=False,
                check=False,
                timeout=timeout,
                env=FlextCliUtilitiesRuntime._resolved_env(env, remove_env_keys),
                input=stdin,
            )
        except subprocess.TimeoutExpired as exc:
            return r[p.Cli.CommandOutput].fail(
                f"timeout {exc.timeout}s: {shlex.join(list(cmd))}"
            )
        except c.EXC_OS_VALUE as exc:
            return r[p.Cli.CommandOutput].fail(f"execution error: {exc}")
        try:
            stdout = (result.stdout or b"").decode("utf-8")
            stderr = (result.stderr or b"").decode("utf-8")
        except UnicodeDecodeError as exc:
            return r[p.Cli.CommandOutput].fail(
                f"non-UTF-8 output from {shlex.join(list(cmd))}: {exc}"
            )
        duration = max(0.0, time.monotonic() - start)
        return r[p.Cli.CommandOutput].ok(
            m.Cli.CommandOutput(
                stdout=stdout,
                stderr=stderr,
                exit_code=result.returncode,
                duration=duration,
            )
        )

    @staticmethod
    def run_bytes(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Run a command capturing byte-exact stdout/stderr (no text decoding)."""
        start = time.monotonic()
        stdin = (
            input_data.encode("utf-8") if isinstance(input_data, str) else input_data
        )
        try:
            result = subprocess.run(
                list(cmd),
                cwd=cwd,
                capture_output=True,
                text=False,
                check=False,
                timeout=timeout,
                env=FlextCliUtilitiesRuntime._resolved_env(env, remove_env_keys),
                input=stdin,
            )
        except subprocess.TimeoutExpired as exc:
            return r[p.Cli.CommandBytesOutput].fail(
                f"timeout {exc.timeout}s: {shlex.join(list(cmd))}"
            )
        except c.EXC_OS_VALUE as exc:
            return r[p.Cli.CommandBytesOutput].fail(f"execution error: {exc}")
        duration = max(0.0, time.monotonic() - start)
        return r[p.Cli.CommandBytesOutput].ok(
            m.Cli.CommandBytesOutput(
                stdout=result.stdout or b"",
                stderr=result.stderr or b"",
                exit_code=result.returncode,
                duration=duration,
            )
        )

    @staticmethod
    def run(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
        *,
        capture: bool = True,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Run a command and fail on non-zero exit status."""

        def require_zero_exit(
            output: p.Cli.CommandOutput,
        ) -> p.Result[p.Cli.CommandOutput]:
            if output.exit_code != 0:
                return r[p.Cli.CommandOutput].fail(
                    f"failed ({output.exit_code}): {shlex.join(list(cmd))}: {(output.stderr or output.stdout).strip()}"
                )
            return r[p.Cli.CommandOutput].ok(output)

        return FlextCliUtilitiesRuntime.run_raw(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=capture,
        ).flat_map(require_zero_exit)

    @staticmethod
    def run_checked(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
        *,
        capture: bool = True,
    ) -> p.Result[bool]:
        """Run a command and return a success flag."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=capture,
        ).map(lambda _: True)

    @staticmethod
    def run_live(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Run a command streaming stdout/stderr live (inherited stdio).

        Ergonomic alias for ``run(..., capture=False)``: the child's output
        flows straight to the parent terminal (long makes, rollouts) and the
        non-zero exit still fails closed. Captured stdout/stderr are empty.
        """
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
            capture=False,
        )

    @staticmethod
    def capture(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[str]:
        """Run a command and return stripped stdout."""
        return FlextCliUtilitiesRuntime.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            env=env,
            remove_env_keys=remove_env_keys,
            input_data=input_data,
        ).map(lambda output: output.stdout.strip())

    @staticmethod
    def run_to_file(
        cmd: t.StrSequence,
        output_file: t.Cli.TextPath,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        input_data: str | bytes | None = None,
    ) -> p.Result[int]:
        """Run a command and write combined output to ``output_file``."""
        stdin = (
            input_data.encode("utf-8") if isinstance(input_data, str) else input_data
        )
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
                    input=stdin,
                )
        except subprocess.TimeoutExpired as exc:
            return r[int].fail(f"timeout {exc.timeout}s: {shlex.join(list(cmd))}")
        except c.EXC_OS_VALUE as exc:
            return r[int].fail(f"execution error: {exc}")
        return r[int].ok(result.returncode)


__all__: list[str] = ["FlextCliUtilitiesRuntime"]
