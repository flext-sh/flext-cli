"""Managed process primitives shared through ``u.Cli``.

The managed family owns no native spawn path: every child comes from the
single audited spawn engine on the runtime owner, composed through MRO.
Handles receive only the communication capability they need; the public
``p.Cli.ManagedProcess`` contract is adapted at this boundary alone.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import select
import shlex
import signal
import time
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from flext_cli import c, m, p, r, t
from flext_cli._utilities import FlextCliUtilitiesRuntime
from flext_cli._utilities._runtime_process_group import (
    FlextCliUtilitiesRuntimeProcessGroupMixin,
)


class FlextCliUtilitiesProcesses(FlextCliUtilitiesRuntime):
    """Runtime helpers for managed external processes."""

    class ManagedProcess(FlextCliUtilitiesRuntimeProcessGroupMixin):
        """Typed handle for a long-running child process.

        Session leaders own their POSIX process group: ``terminate`` and ``kill``
        signal the whole group, including descendants that outlive the leader.
        """

        def __init__(
            self,
            process: p.Cli.ProcessHandle,
            *,
            cwd: t.Cli.TextPath | None,
            env: t.StrMapping | None,
            session_leader: bool = False,
        ) -> None:
            self._process = process
            self._cwd = Path(cwd) if cwd is not None else None
            self._env = dict(env) if env is not None else None
            self._session_leader = session_leader and os.name == "posix"
            self._stdout = ""
            self._stderr = ""
            self._stdout_buffer = bytearray()
            self._communicated = False

        @property
        def pid(self) -> int:
            return self._process.pid

        @property
        def returncode(self) -> int | None:
            return self._process.poll()

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
            """Signal the owned session group, or the child, to finish.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            return self._signal_owned(signal.SIGTERM, force=False)

        def kill(self) -> p.Result[bool]:
            """Force the owned session group, or the child, to stop.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            return self._signal_owned(signal.SIGTERM, force=True)

        def _signal_owned(self, signal_number: int, *, force: bool) -> p.Result[bool]:
            """Tear down the process group this handle owns, or the single child.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            if self._session_leader:
                return self._signal_process_tree(
                    self._process,
                    signal_number,
                    0,
                    force=force,
                )
            if self.poll() is not None:
                return r[bool].ok(value=True)
            try:
                self._process.send_signal(signal.SIGKILL if force else signal_number)
            except c.EXC_OS_VALUE as exc:
                return r[bool].fail(
                    f"process {'kill' if force else 'terminate'} error: {exc}",
                    exception=exc,
                )
            return r[bool].ok(value=True)

        def wait(self, timeout: float | None = None) -> p.Result[int]:
            if self._communicated:
                return r[int].ok(self._process.poll() or 0)
            communicated = FlextCliUtilitiesRuntime.child_communicate(
                self._process,
                timeout=timeout,
            )
            if communicated.failure:
                return r[int].from_failure(communicated)
            stdout, stderr = communicated.unwrap()
            try:
                self._stdout = (bytes(self._stdout_buffer) + stdout).decode(
                    c.DEFAULT_ENCODING,
                    errors="strict",
                )
                self._stderr = stderr.decode(
                    c.DEFAULT_ENCODING,
                    errors="strict",
                )
            except UnicodeDecodeError as exc:
                return r[int].fail(
                    f"process output is not valid UTF-8: {exc}",
                    exception=exc,
                )
            self._stdout_buffer.clear()
            self._communicated = True
            return r[int].ok(self._process.poll() or 0)

        def stdin_write(self, content: bytes) -> p.Result[bool]:
            """Write and flush exact bytes to the managed child stdin.

            Returns:
                The resulting ``p.Result[bool]``.

            """
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
            return r[bool].ok(value=True)

        def stdout_read_until(
            self,
            delimiter: bytes,
            *,
            timeout: float,
        ) -> p.Result[bytes]:
            """Read through one exact delimiter within the supplied deadline.

            Returns:
                The resulting ``p.Result[bytes]``.

            """
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
            """Read exactly ``size`` bytes within the supplied deadline.

            Returns:
                The resulting ``p.Result[bytes]``.

            """
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
            """Append one available binary stdout chunk before ``deadline``.

            Returns:
                The resulting ``p.Result[bool]``.

            """
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
            return r[bool].ok(value=True)

    @classmethod
    def process_start(
        cls,
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
        capture: bool = True,
        start_new_session: bool = False,
    ) -> p.Result[p.Cli.ManagedProcess]:
        """Start a managed child with captured or inherited standard streams.

        Capture preserves interactive pipes by default. Disabling it inherits
        stdin, stdout, and stderr without accumulating output in the handle.
        A new POSIX session gives the returned handle ownership of the child's
        process group: ``terminate`` and ``kill`` signal every descendant,
        including ones that outlive the leader; the caller stays responsible
        for reaping. The child is always spawned by the single audited engine
        owner composed through MRO; the handle receives its communication
        capability through the public protocol.

        Returns:
            The existing managed child through its public ``p.Cli`` contract.

        """
        launch = options if options is not None else m.Cli.ProcessOptions()
        forwarded_fds = tuple(launch.pass_fds)
        if any(
            isinstance(file_descriptor, bool) or file_descriptor < 0
            for file_descriptor in forwarded_fds
        ):
            return r[p.Cli.ManagedProcess].fail(
                "process pass_fds must contain non-negative file descriptors",
            )
        if os.name == "nt" and forwarded_fds:
            return r[p.Cli.ManagedProcess].fail(
                "process pass_fds is unsupported on Windows",
            )
        resolved_env = cls._resolved_env(
            launch.env,
            launch.remove_env_keys,
            inherit_environment=launch.inherit_environment,
        )
        try:
            process = cls._spawn_streamed_process(
                list(cmd),
                cwd,
                resolved_env,
                None,
                options=m.Cli.RuntimeSpawnOptions(
                    capture_output=capture,
                    combine_output=False,
                    stdin_mode="pipe" if capture else "inherit",
                    start_new_session=start_new_session,
                    pass_fds=forwarded_fds,
                ),
            )
        except c.EXC_OS_VALUE as exc:
            return r[p.Cli.ManagedProcess].fail(
                f"execution error: {shlex.join(list(cmd))}: {exc}",
                exception=exc,
            )
        return r[p.Cli.ManagedProcess].ok(
            cls.ManagedProcess(
                process,
                cwd=cwd,
                env=resolved_env,
                session_leader=start_new_session,
            ),
        )


__all__: list[str] = ["FlextCliUtilitiesProcesses"]
