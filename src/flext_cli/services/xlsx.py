"""Generic typed XLSX service."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from flext_cli import m, s

if TYPE_CHECKING:
    from flext_cli import p, t


class FlextCliXlsx(s[m.Cli.RuntimeStatus]):
    """Expose byte-only XLSX operations for later public API composition."""

    if TYPE_CHECKING:

        @staticmethod
        @override
        def xlsx_recalc(
            request: m.Cli.XlsxRecalcRequest,
        ) -> p.Result[m.Cli.XlsxRecalcResult]:
            """Recalculate workbook bytes through the inherited XLSX owner."""
            ...

        @staticmethod
        @override
        def xlsx_recalc_parity(
            request: m.Cli.XlsxRecalcParityRequest,
        ) -> p.Result[m.Cli.XlsxRecalcParityReport]:
            """Validate recalculation parity through the inherited XLSX owner."""
            ...

    # NOTE (multi-agent, mro-j2yt.1): this service contains no document or
    # customer rules; consumers provide immutable plans and receive bytes/models.


__all__: t.VariadicTuple[str] = ("FlextCliXlsx",)
