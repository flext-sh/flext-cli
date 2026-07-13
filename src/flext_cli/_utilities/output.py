"""CLI output helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import c, t
from flext_cli._utilities._output_parts.flextcliutilitiesoutput_part_01 import (
    FlextCliUtilitiesOutput as FlextCliUtilitiesOutputPart01,
)
from flext_cli._utilities._output_parts.flextcliutilitiesoutput_part_02 import (
    FlextCliUtilitiesOutput as FlextCliUtilitiesOutputPart02,
)


class FlextCliUtilitiesOutput(
    FlextCliUtilitiesOutputPart01, FlextCliUtilitiesOutputPart02
):
    """Public facade for FlextCliUtilitiesOutput."""

    @staticmethod
    def output_status_line(
        success: bool, label: str, detail: str, *, elapsed: float | None
    ) -> t.Pair[str, str]:
        """Build one canonical status line and style."""
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if success else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if success else c.Cli.MessageStyles.BOLD_RED
        )
        timing = f"  ({elapsed:.2f}s)" if elapsed is not None else ""
        line = f"  {symbol} {label:<8} {detail:<24}{timing}"
        return line, style

    @staticmethod
    def output_gate_line(name: str, passed: bool, *, message: str) -> t.Pair[str, str]:
        """Build one canonical gate line and style."""
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if passed else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if passed else c.Cli.MessageStyles.BOLD_RED
        )
        suffix = f"  {message}" if message else ""
        return f"    {symbol} {name:<10}{suffix}", style


__all__: list[str] = ["FlextCliUtilitiesOutput"]
