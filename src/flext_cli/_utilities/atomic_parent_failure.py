"""Causal failure preservation for authenticated parent descriptors.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Never


class FlextCliUtilitiesAtomicParentFailure:
    """Canonical namespace owner."""

    @staticmethod
    def preserve_recheck_failure(
        path: Path,
        operation_error: BaseException,
        recheck: Callable[[], None],
    ) -> None:
        """Attach a failed parent recheck to the active operation failure."""
        try:
            recheck()
        except OSError as recheck_error:
            FlextCliUtilitiesAtomicParentFailure.raise_combined_failure(
                path,
                operation_error,
                (recheck_error,),
                ("atomic operation", "parent recheck"),
                errno.ESTALE,
            )

    @staticmethod
    def raise_combined_failure(
        path: Path,
        operation_error: BaseException,
        secondary_errors: Sequence[OSError],
        labels: tuple[str, str],
        errno_code: int = errno.EIO,
    ) -> Never:
        """Raise one operation failure together with every follow-up failure.

        ``labels`` names the failed operation and its follow-up step.

        An ordinary operation failure becomes one native ``OSError`` caused by
        the group of every original error; an interruption stays a
        ``BaseExceptionGroup`` so it is never converted into an ordinary error.

        Raises:
            OSError: When the operation failed with an ordinary exception.
            BaseExceptionGroup: When the operation was interrupted.

        """
        operation, secondary = labels
        summary = "; ".join(str(error) for error in secondary_errors)
        message = (
            f"{operation} failed ({operation_error}); {secondary} failed ({summary})"
        )
        group_message = f"{operation} and {secondary} failed"
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(group_message, [operation_error, *secondary_errors])
            raise OSError(errno_code, message, path) from causes
        raise BaseExceptionGroup(
            group_message,
            [operation_error, *secondary_errors],
        ) from secondary_errors[-1]


__all__: list[str] = ["FlextCliUtilitiesAtomicParentFailure"]
