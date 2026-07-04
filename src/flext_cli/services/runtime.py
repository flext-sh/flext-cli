"""DSL service for external process runtime helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli.base import FlextCliServiceBase

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliRuntime(FlextCliServiceBase, FlextCliUtilitiesRuntime):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
