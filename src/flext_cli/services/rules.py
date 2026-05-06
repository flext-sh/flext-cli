"""DSL service for declarative local rule loading."""

from __future__ import annotations

from flext_cli import FlextCliServiceBase, FlextCliUtilitiesRules, t


class FlextCliRules(FlextCliServiceBase, FlextCliUtilitiesRules):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""

    pass


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]
