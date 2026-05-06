"""DSL service for external process runtime helpers."""

from __future__ import annotations

from flext_cli import FlextCliServiceBase, FlextCliUtilitiesRuntime, t


class FlextCliRuntime(FlextCliServiceBase, FlextCliUtilitiesRuntime):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""

    pass


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
