"""Causal failure preservation for authenticated parent descriptors."""

from __future__ import annotations

import errno
from collections.abc import Callable
from pathlib import Path


def preserve_recheck_failure(
    path: Path, operation_error: BaseException, recheck: Callable[[], None]
) -> None:
    """Attach a failed parent recheck to the active operation failure."""
    try:
        recheck()
    except OSError as recheck_error:
        message = (
            f"atomic operation failed ({operation_error}); "
            f"parent recheck failed ({recheck_error})"
        )
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(
                "atomic operation and parent recheck failed",
                [operation_error, recheck_error],
            )
            raise OSError(errno.ESTALE, message, path) from causes
        group_message = "atomic operation and parent recheck failed"
        raise BaseExceptionGroup(
            group_message, [operation_error, recheck_error]
        ) from recheck_error


__all__: list[str] = ["preserve_recheck_failure"]
