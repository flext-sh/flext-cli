"""Generic typed XLSX service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import s

if TYPE_CHECKING:
    from flext_cli import m, p


class FlextCliXlsx(s):
    """Expose byte-only XLSX operations for later public API composition."""

    if TYPE_CHECKING:

        @staticmethod
        def xlsx_recalc(
            request: m.Cli.XlsxRecalcRequest,
        ) -> p.Result[m.Cli.XlsxRecalcResult]: ...

        @staticmethod
        def xlsx_recalc_parity(
            request: m.Cli.XlsxRecalcParityRequest,
        ) -> p.Result[m.Cli.XlsxRecalcParityReport]: ...

    # NOTE (multi-agent, mro-j2yt.1): this service contains no document or
    # customer rules; consumers provide immutable plans and receive bytes/models.


__all__: tuple[str, ...] = ("FlextCliXlsx",)
