"""Native and package owners adapted to typed results for ``u.Cli`` helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import r

from flext_cli import p


class FlextCliUtilitiesFilesNativeResults:
    """Own the single owner-exception-to-result adaptation of helpers."""

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

    @staticmethod
    def coded_result[**P, T](
        operation: Callable[P, T],
        code: str,
        exceptions: tuple[type[Exception], ...],
    ) -> Callable[P, p.Result[T]]:
        """Adapt one owner raising ``exceptions`` to a coded typed result.

        Returns:
            The owner as a callable whose failure is ``code`` followed by the
            exception text, or its class name when the text is empty.

        """

        def run(*args: P.args, **kwargs: P.kwargs) -> p.Result[T]:
            try:
                value = operation(*args, **kwargs)
            except exceptions as exc:
                detail = str(exc).strip() or exc.__class__.__name__
                return r[T].fail(f"{code}: {detail}")
            return r[T].ok(value)

        return run


__all__: list[str] = ["FlextCliUtilitiesFilesNativeResults"]
