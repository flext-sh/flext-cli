"""DSL service for external process runtime helpers."""

from __future__ import annotations

from flext_cli import s, t


class FlextCliRuntime(s):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
