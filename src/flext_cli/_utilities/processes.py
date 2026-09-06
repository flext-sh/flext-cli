"""Managed process primitives shared through ``u.Cli``."""

from __future__ import annotations

import os
import select
import shlex
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from flext_cli import c, p, r, t
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime


class FlextCliUtilitiesProcesses:
    """Runtime helpers for managed external processes."""

    class ManagedProcess:
        """Typed handle for a long-running child process."""

        def __init__(
            self,
            process: subprocess.Popen[bytes],
            *,
            cwd: t.Cli.TextPath | None,
            env: t.StrMapping | None,
        ) -> None:
            self._process = process
            self._cwd = Path(cwd) if cwd is not None else None
            self._env = dict(env) if env is not None else None
            self._stdout = ""
            self._stderr = ""
            self._stdout_buffer = bytearray()
            self._communicated = False

        @property
        def pid(self) -> int:
            return self._process.pid

        @property
        def returncode(self) -> int | None:
            return self._process.returncode

        @property
        def cwd(self) -> Path | None:
            return self._cwd

        @property
        def env(self) -> Mapping[str, str] | None:
            if self._env is None:
                return None
            return MappingProxyType(self._env)

        @property
        def stdout(self) -> str:
            return self._stdout

        @property
        def stderr(self) -> str:
            return self._stderr

        def poll(self) -> int | None:
            return self._process.poll()

        def terminate(self) -> p.Result[bool]:
            if self.poll() is not None:
                return r[bool].ok(True)
            try:
                self._process.terminate()
            except c.EXC_OS_VALUE as exc:
                return r[bool].fail(f"process terminate error: {exc}", exception=exc)
            return r[bool].ok(True)

        def kill(self) -> p.Result[bool]:
            if self.poll() is not None:
                return r[bool].ok(True)
            try:
                self._process.kill()
            except c.EXC_OS_VALUE as exc:
                return r[bool].fail(f"process kill error: {exc}", exception=exc)
            return r[bool].ok(True)

        def wait(self, timeout: float | None = None) -> p.Result[int]:
            if self._communicated:
                return r[int].ok(self._process.returncode or 0)
            try:
                stdout, stderr = self._process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                return r[int].fail(f"timeout {exc.timeout}s: pid {self.pid}")
            except c.EXC_OS_VALUE as exc:
                return r[int].fail(f"process wait error: {exc}", exception=exc)
            try:
                self._stdout = (bytes(self._stdout_buffer) + (stdout or b"")).decode(
                    c.Cli.ENCODING_DEFAULT, errors="strict"
                )
                self._stderr = (stderr or b"").decode(
                    c.Cli.ENCODING_DEFAULT, errors="strict"
                )
            except UnicodeDecodeError as exc:
                return r[int].fail(
                    f"process output is not valid UTF-8: {exc}", exception=exc
                )
            self._stdout_buffer.clear()
            self._communicated = True
            return r[int].ok(self._process.returncode or 0)

        def stdin_write(self, content: bytes) -> p.Result[bool]:
            """Write and flush exact bytes to the managed child stdin."""
            if self.poll() is not None:
                return r[bool].fail(f"process already exited: pid {self.pid}")
            stream = self._process.stdin
            if stream is None:
                return r[bool].fail(f"process stdin is unavailable: pid {self.pid}")
            try:
                stream.write(content)
                stream.flush()
            except c.EXC_OS_VALUE as exc:
                return r[bool].fail(f"process stdin write error: {exc}", exception=exc)
            return r[bool].ok(True)

        def stdout_read_until(
            self, delimiter: bytes, *, timeout: float
        ) -> p.Result[bytes]:
            """Read through one exact delimiter within the supplied deadline."""
            if not delimiter:
                return r[bytes].fail("stdout delimiter must not be empty")
            deadline = time.monotonic() + timeout
            while True:
                position = self._stdout_buffer.find(delimiter)
                if position >= 0:
                    end = position + len(delimiter)
                    content = bytes(self._stdout_buffer[:end])
                    del self._stdout_buffer[:end]
                    return r[bytes].ok(content)
                read = self._read_stdout(deadline)
                if read.failure:
                    return r[bytes].from_failure(read)

        def stdout_read_exact(self, size: int, *, timeout: float) -> p.Result[bytes]:
            """Read exactly ``size`` bytes within the supplied deadline."""
            if size < 0:
                return r[bytes].fail("stdout byte count must be non-negative")
            deadline = time.monotonic() + timeout
            while len(self._stdout_buffer) < size:
                read = self._read_stdout(deadline)
                if read.failure:
                    return r[bytes].from_failure(read)
            content = bytes(self._stdout_buffer[:size])
            del self._stdout_buffer[:size]
            return r[bytes].ok(content)

        def _read_stdout(self, deadline: float) -> p.Result[bool]:
            """Append one available binary stdout chunk before ``deadline``."""
            stream = self._process.stdout
            if stream is None:
                return r[bool].fail(f"process stdout is unavailable: pid {self.pid}")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return r[bool].fail(f"process stdout timeout: pid {self.pid}")
            try:
                ready, _, _ = select.select((stream.fileno(),), (), (), remaining)
                if not ready:
                    return r[bool].fail(f"process stdout timeout: pid {self.pid}")
                content = os.read(stream.fileno(), 65536)
            except c.EXC_OS_VALUE as exc:
                return r[bool].fail(f"process stdout read error: {exc}", exception=exc)
            if not content:
                return r[bool].fail(f"process stdout closed: pid {self.pid}")
            self._stdout_buffer.extend(content)
            return r[bool].ok(True)

    @staticmethod
    def process_start(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence = (),
        pass_fds: t.SequenceOf[int] = (),
    ) -> p.Result[FlextCliUtilitiesProcesses.ManagedProcess]:
        """Start long-running commands; use instead of direct ``subprocess.Popen``."""
        forwarded_fds = tuple(pass_fds)
        if any(
            isinstance(file_descriptor, bool) or file_descriptor < 0
            for file_descriptor in forwarded_fds
        ):
            return r[FlextCliUtilitiesProcesses.ManagedProcess].fail(
                "process pass_fds must contain non-negative file descriptors"
            )
        if os.name == "nt" and forwarded_fds:
            return r[FlextCliUtilitiesProcesses.ManagedProcess].fail(
                "process pass_fds is unsupported on Windows"
            )
        resolved_env = None
        if env is not None or remove_env_keys:
            resolved_env = FlextCliUtilitiesRuntime.process_env(
                overrides=env, remove_keys=remove_env_keys
            )
        try:
            process = subprocess.Popen(
                list(cmd),
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                bufsize=0,
                env=resolved_env,
                pass_fds=forwarded_fds,
            )
        except c.EXC_OS_VALUE as exc:
            return r[FlextCliUtilitiesProcesses.ManagedProcess].fail(
                f"execution error: {shlex.join(list(cmd))}: {exc}", exception=exc
            )
        return r[FlextCliUtilitiesProcesses.ManagedProcess].ok(
            FlextCliUtilitiesProcesses.ManagedProcess(
                process, cwd=cwd, env=resolved_env
            )
        )


__all__: list[str] = ["FlextCliUtilitiesProcesses"]
