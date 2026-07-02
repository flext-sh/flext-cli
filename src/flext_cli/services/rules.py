"""DSL service for declarative local rule loading."""

from __future__ import annotations

from flext_cli import t
from flext_cli._utilities.rules import FlextCliUtilitiesRules
from flext_cli.base import FlextCliServiceBase


class FlextCliRules(FlextCliServiceBase, FlextCliUtilitiesRules):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]
