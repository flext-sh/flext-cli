"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_core import FlextTypes


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
        Usage: Other projects can reference `FlextCliTypes.Cli.*` via short alias `FlextTypes.Cli.*`.
        This enables consistent namespace patterns for cross-project type access.
        """

        type JsonValue = FlextTypes.NormalizedValue
        type TableRow = Mapping[str, JsonValue]
        TabularData = Sequence[TableRow]
        type CliValue = (
            FlextTypes.Scalar
            | FlextTypes.StrSequence
            | Mapping[str, FlextTypes.Scalar | FlextTypes.StrSequence]
            | None
        )


t = FlextCliTypes
__all__ = ["FlextCliTypes", "t"]
