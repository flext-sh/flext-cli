"""DSL service for declarative local rule loading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._utilities.rules import FlextCliUtilitiesRules
from flext_cli.base import FlextCliServiceBase

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliRules(FlextCliServiceBase, FlextCliUtilitiesRules):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]
