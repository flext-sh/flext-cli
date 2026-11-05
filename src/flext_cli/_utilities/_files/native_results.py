"""Native ``OSError`` owners adapted to typed results for ``u.Cli`` files.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import r

from flext_cli import p


class FlextCliUtilitiesFilesNativeResults:
    """Own the single native-failure-to-result adaptation of file helpers."""

    @staticmethod
    def native_result[**P, T](
        operation: Callable[P, T],
        template: str,
    ) -> Callable[P, p.Result[T]]:
        """Adapt one native owner raising ``OSError`` to a typed result.

        Returns:
            The owner as a callable whose native failure is ``template``
            formatted with the original error, which stays attached.

        """

        def run(*args: P.args, **kwargs: P.kwargs) -> p.Result[T]:
            return r.safe(operation, exceptions=(OSError,))(*args, **kwargs).map_error(
                lambda error: template.format(error=error)
            )

        return run


__all__: list[str] = ["FlextCliUtilitiesFilesNativeResults"]
