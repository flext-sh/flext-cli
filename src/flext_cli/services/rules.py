"""DSL service for declarative local rule loading."""

from __future__ import annotations

from flext_cli import s, t


class FlextCliRules(s):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]
