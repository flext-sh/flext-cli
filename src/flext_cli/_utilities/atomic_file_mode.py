"""Public permission-mode contracts for atomic file publication.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path


class FlextCliNoModePrecondition:
    """Marker for callers that do not guard the destination mode."""


NO_MODE_PRECONDITION = FlextCliNoModePrecondition()


def validate_mode(mode: int | None, *, label: str) -> int | None:
    """Return one portable permission mode or fail before any file effect.

    Returns:
        One portable permission mode or fail before any file effect.

    Raises:
        OSError: If ``isinstance(mode, bool)``; or if ``mode < 0 or mode !=
            stat.S_IMODE(mode)``.

    """
    if mode is None:
        return None
    if isinstance(mode, bool):
        msg = f"{label} must be an integer permission mode"
        raise OSError(errno.EINVAL, msg)
    if mode < 0 or mode != stat.S_IMODE(mode):
        msg = f"{label} contains non-permission bits: {mode!r}"
        raise OSError(errno.EINVAL, msg)
    return mode


def validate_mode_precondition(
    path: Path,
    state: os.stat_result | None,
    expected_mode: int | FlextCliNoModePrecondition | None,
) -> None:
    """Require the observed mode to match one explicit planned version.

    Raises:
        OSError: If ``expected_mode`` is ``FlextCliNoModePrecondition``; or if
            ``observed != planned``.

    """
    if expected_mode is NO_MODE_PRECONDITION:
        return
    if isinstance(expected_mode, FlextCliNoModePrecondition):
        msg = "expected_mode sentinel must be the canonical singleton"
        raise OSError(errno.EINVAL, msg, path)
    planned = validate_mode(expected_mode, label="expected_mode")
    observed = None if state is None else stat.S_IMODE(state.st_mode)
    if observed != planned:
        msg = f"atomic destination permission mode changed before operation: {path}"
        raise OSError(errno.ESTALE, msg, path)


def validate_guarded_mode_tuple(
    path: Path,
    expected_bytes: bytes | None,
    expected_mode: int | FlextCliNoModePrecondition | None,
) -> None:
    """Require absence or one complete existing byte-and-mode version.

    Raises:
        OSError: If ``isinstance(expected_mode, FlextCliNoModePrecondition)``; or if
            ``expected_bytes is None``; or if ``expected_mode is None``.

    """
    if expected_mode is NO_MODE_PRECONDITION:
        return
    if isinstance(expected_mode, FlextCliNoModePrecondition):
        msg = "expected_mode sentinel must be the canonical singleton"
        raise OSError(errno.EINVAL, msg, path)
    if expected_bytes is None:
        if expected_mode is None:
            return
        msg = "expected_mode must be None when expected_bytes requires absence"
        raise OSError(errno.EINVAL, msg, path)
    if expected_mode is None:
        msg = "expected_mode is required when expected_bytes identifies a file"
        raise OSError(errno.EINVAL, msg, path)
    validate_mode(expected_mode, label="expected_mode")


def assert_observed_mode(path: Path, state: os.stat_result, expected: int) -> None:
    """Require a filesystem to represent the requested permission mode exactly.

    Raises:
        OSError: If ``observed != expected``.

    """
    observed = stat.S_IMODE(state.st_mode)
    if observed != expected:
        msg = (
            "filesystem did not materialize the requested permission mode "
            f"for {path}: requested={expected:#o}, observed={observed:#o}"
        )
        raise OSError(errno.ENOTSUP, msg, path)


def publication_mode(
    state: os.stat_result | None,
    permission_mode: int | None,
) -> int | None:
    """Resolve the mode applied to the temporary before publication.

    Returns:
        The resulting ``int | None``.

    """
    requested = validate_mode(permission_mode, label="permission_mode")
    if requested is not None:
        return requested
    return None if state is None else stat.S_IMODE(state.st_mode)


__all__: list[str] = [
    "NO_MODE_PRECONDITION",
    "assert_observed_mode",
    "publication_mode",
    "validate_guarded_mode_tuple",
    "validate_mode",
    "validate_mode_precondition",
]
