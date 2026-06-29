"""DSL service for external process runtime helpers."""

from __future__ import annotations

from flext_cli import t
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli.base import FlextCliServiceBase


class FlextCliRuntime(FlextCliServiceBase, FlextCliUtilitiesRuntime):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""

    pass


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
