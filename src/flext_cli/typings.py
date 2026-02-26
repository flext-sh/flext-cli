"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeAlias

from flext_core import FlextTypes


# ═══════════════════════════════════════════════════════════════════════════
# SINGLE CLASS WITH NESTED CLASSES
# ═══════════════════════════════════════════════════════════════════════════
class FlextCliTypes(FlextTypes):
    """FlextCli type definitions extending FlextTypes via inheritance.

    RULES:
    ───────
    1. TypeVars outside the class (only case allowed)
    2. PEP 695 type aliases inside nested classes
    3. Complex types composed with Protocols
    4. ZERO simple aliases - use direct types
    5. Inheritance from FlextTypes, no duplication
    """

    class Cli:
        """CLI types namespace for cross-project access.

        Provides organized access to all CLI types for other FLEXT projects.
        Usage: Other projects can reference `FlextCliTypes.Cli.*` via short alias `t.Cli.*`.
        This enables consistent namespace patterns for cross-project type access.

        RULES (Architecture Layer Compliance):
        ─────────────────────────────────────
        1. Single class pattern - NO nested sub-namespaces (Data, Auth, etFlextCliConstants.Cli.)
        2. Direct access via t.Cli.* - simple and clear
        3. Reuse from FlextTypes parent class (inheritance, no duplication)
        4. Complex types only - no simple wrappers
        5. Type composition with Protocols for better type safety
        """

        # Runtime namespace only
        ResultFormatter = Callable[[FlextTypes.JsonValue], str]
        FormatableResult: TypeAlias = str
        TabularData = Sequence[Mapping[str, FlextTypes.JsonValue]]
        TableRows: TypeAlias = Sequence[Mapping[str, FlextTypes.JsonValue]]
        JsonDict: TypeAlias = Mapping[str, FlextTypes.JsonValue]


t = FlextCliTypes

__all__ = [
    "FlextCliTypes",
    "t",
]
