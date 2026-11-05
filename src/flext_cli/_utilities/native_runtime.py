"""Single audited native spawn owner, loadable without the CLI/Core SDK.

Only standard-library dependencies belong here. The typed runtime delegates to
this original package asset; authenticated cold workers can load the same asset
before SDK admission and own waiting/reaping of the returned native child.
Options are structural resolved inputs, not a second policy/defaults model.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from typing import BinaryIO, Literal, Protocol

TimeoutExpired = subprocess.TimeoutExpired


class RuntimeSpawnCommand(Protocol):
    """Resolved native argv, working directory, and environment of one child."""

    @property
    def cmd(self) -> Sequence[str]:
        """Executable and ordered child arguments."""
        ...

    @property
    def cwd(self) -> str | os.PathLike[str] | None:
        """Working directory, or the parent directory when absent."""
        ...

    @property
    def env(self) -> Mapping[str, str] | None:
        """Resolved environment, or the inherited parent environment."""
        ...


class RuntimeSpawnOptions(Protocol):
    """Resolved spawn capabilities shared with the typed frontend, without defaults."""

    @property
    def capture_output(self) -> bool:
        """Whether stdout and separate stderr use pipes."""
        ...

    @property
    def combine_output(self) -> bool:
        """Whether stderr is redirected to stdout."""
        ...

    @property
    def creation_flags(self) -> int:
        """Native platform process creation flags."""
        ...

    @property
    def pass_fds(self) -> tuple[int, ...]:
        """Descriptors forwarded to the native child."""
        ...

    @property
    def start_new_session(self) -> bool | None:
        """Explicit session ownership, or the native platform default."""
        ...

    @property
    def stdin_mode(self) -> Literal["devnull", "inherit", "pipe"]:
        """Stdin policy when no explicit handle is supplied."""
        ...


def spawn_streamed_process(
    command: RuntimeSpawnCommand,
    stdin_handle: BinaryIO | None,
    *,
    options: RuntimeSpawnOptions,
) -> subprocess.Popen[bytes]:
    """Create the single native binary child without waiting or adapting its result.

    Returns:
        The actual native process handle; its caller owns communication and reaping.

    """
    return subprocess.Popen(
        list(command.cmd),
        cwd=command.cwd,
        stdin=_stdin_target(stdin_handle, options),
        stdout=subprocess.PIPE if options.capture_output else None,
        stderr=_stderr_target(options),
        text=False,
        bufsize=0,
        env=command.env,
        start_new_session=(
            os.name != "nt"
            if options.start_new_session is None
            else options.start_new_session
        ),
        creationflags=options.creation_flags,
        pass_fds=options.pass_fds,
    )


def _stdin_target(
    stdin_handle: BinaryIO | None,
    options: RuntimeSpawnOptions,
) -> BinaryIO | int | None:
    """Resolve the child stdin from an explicit handle or the stdin policy.

    Returns:
        The explicit handle, a native pipe or null-device marker, or ``None``
        to inherit the parent stdin.

    """
    if stdin_handle is not None:
        return stdin_handle
    return {"pipe": subprocess.PIPE, "devnull": subprocess.DEVNULL}.get(
        options.stdin_mode
    )


def _stderr_target(options: RuntimeSpawnOptions) -> int | None:
    """Resolve the child stderr from the combine and capture policy.

    Returns:
        A native redirect or pipe marker, or ``None`` to inherit stderr.

    """
    if options.combine_output:
        return subprocess.STDOUT
    return subprocess.PIPE if options.capture_output else None


def streamed_creation_flags() -> int:
    """Return platform creation flags for pre-execution containment.

    Returns:
        The existing native Windows group/suspension flags, or zero on POSIX.

    """
    if os.name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)) | int(
        getattr(subprocess, "CREATE_SUSPENDED", 0x00000004),
    )


__all__ = [
    "TimeoutExpired",
    "spawn_streamed_process",
    "streamed_creation_flags",
]
