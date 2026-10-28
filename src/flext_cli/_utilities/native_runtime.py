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
from subprocess import TimeoutExpired
from typing import BinaryIO, Literal, Protocol


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
    cmd: Sequence[str],
    cwd: str | os.PathLike[str] | None,
    env: Mapping[str, str] | None,
    stdin_handle: BinaryIO | None,
    *,
    options: RuntimeSpawnOptions,
) -> subprocess.Popen[bytes]:
    """Create the single native binary child without waiting or adapting its result.

    Returns:
        The actual native process handle; its caller owns communication and reaping.

    """
    return subprocess.Popen(
        list(cmd),
        cwd=cwd,
        stdin=(
            stdin_handle
            if stdin_handle is not None
            else subprocess.PIPE
            if options.stdin_mode == "pipe"
            else subprocess.DEVNULL
            if options.stdin_mode == "devnull"
            else None
        ),
        stdout=subprocess.PIPE if options.capture_output else None,
        stderr=(
            subprocess.STDOUT
            if options.combine_output
            else subprocess.PIPE
            if options.capture_output
            else None
        ),
        text=False,
        bufsize=0,
        env=env,
        start_new_session=(
            os.name != "nt"
            if options.start_new_session is None
            else options.start_new_session
        ),
        creationflags=options.creation_flags,
        pass_fds=options.pass_fds,
    )


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
    "RuntimeSpawnOptions",
    "TimeoutExpired",
    "spawn_streamed_process",
    "streamed_creation_flags",
]
