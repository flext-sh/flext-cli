"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from flext_core import FlextTypes, r

# ═══════════════════════════════════════════════════════════════════════════
# TYPEVARS: Only object allowed outside the class
# ═══════════════════════════════════════════════════════════════════════════
# Reuse from FlextTypes when available
# Centralize all TypeVars here for massive reuse
# Use centralized TypeVars from flext-core
# Import them for local use if needed


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

        # ────────────────────────────────────────────────────────────────────
        # CORE TYPE ALIASES
        # ────────────────────────────────────────────────────────────────────

        # Formattable result types for output operations
        type FormatableResult = (
            dict[str, FlextTypes.JsonValue]
            | list[FlextTypes.JsonValue]
            | tuple[FlextTypes.JsonValue, ...]
            | FlextTypes.JsonValue
            | r[FlextTypes.GeneralValueType]
        )

        # Formatter function signature for result formatting
        type ResultFormatter = Callable[
            [
                dict[str, FlextTypes.JsonValue]
                | list[FlextTypes.JsonValue]
                | tuple[FlextTypes.JsonValue, ...]
                | FlextTypes.JsonValue
                | r[FlextTypes.GeneralValueType],
                str,
            ],
            None,
        ]

        # ────────────────────────────────────────────────────────────────────
        # DATA STRUCTURE TYPES (flattened from nested namespaces)
        # ────────────────────────────────────────────────────────────────────

        # Basic data dict types
        type CliDataDict = dict[str, object]
        type CliFormatData = dict[str, object]
        type CliConfigData = dict[str, object]
        type CliConfigMapping = dict[str, FlextTypes.GeneralValueType]
        type CliJsonDict = dict[str, object]
        type JsonDict = dict[str, object]

        # Auth data types
        type CliAuthData = dict[str, object]
        type CliTokenData = dict[str, object]

        # ────────────────────────────────────────────────────────────────────
        # TABLE AND SEQUENCE TYPES
        # ────────────────────────────────────────────────────────────────────

        # Tabular data types - for table output formatting
        type TabularData = Sequence[FlextTypes.JsonDict] | FlextTypes.JsonDict

        # Table data with multiple format support
        type TableData = (
            Sequence[FlextTypes.JsonDict]
            | FlextTypes.JsonDict
            | Sequence[Sequence[FlextTypes.GeneralValueType]]
            | Mapping[str, FlextTypes.GeneralValueType]
        )

        # Table rows as sequence of dicts
        type TableRows = Sequence[FlextTypes.JsonDict]


t = FlextCliTypes

__all__ = [
    "FlextCliTypes",
    "t",
]
