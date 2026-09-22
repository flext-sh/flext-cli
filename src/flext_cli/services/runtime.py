"""DSL service for external process runtime helpers."""

from __future__ import annotations

from flext_cli import m, s, t


class FlextCliRuntime(s[m.Cli.RuntimeStatus]):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
