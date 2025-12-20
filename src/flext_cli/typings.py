"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypedDict

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
        FormatableResult = (
            dict[str, FlextTypes.JsonValue]
            | list[FlextTypes.JsonValue]
            | tuple[FlextTypes.JsonValue, ...]
            | FlextTypes.JsonValue
            | r[FlextTypes.GeneralValueType]
        )

        # Formatter function signature for result formatting
        ResultFormatter = Callable[
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
        CliDataDict = dict[str, object]
        CliFormatData = dict[str, object]
        CliConfigData = dict[str, object]
        CliConfigMapping = dict[str, FlextTypes.GeneralValueType]
        CliJsonDict = dict[str, object]
        JsonDict = dict[str, object]

        # Auth data types
        CliAuthData = dict[str, object]
        CliTokenData = dict[str, object]

        # ────────────────────────────────────────────────────────────────────
        # TABLE AND SEQUENCE TYPES
        # ────────────────────────────────────────────────────────────────────

        # Tabular data types - for table output formatting
        TabularData = Sequence[FlextTypes.JsonDict] | FlextTypes.JsonDict

        # Table data with multiple format support
        TableData = (
            Sequence[FlextTypes.JsonDict]
            | FlextTypes.JsonDict
            | Sequence[Sequence[FlextTypes.GeneralValueType]]
            | Mapping[str, FlextTypes.GeneralValueType]
        )

        # Table rows as sequence of dicts
        TableRows = Sequence[FlextTypes.JsonDict]


# ═══════════════════════════════════════════════════════════════════════════
# PYTHON 3.13 PEP 705: ReadOnly TypedDict
# ═══════════════════════════════════════════════════════════════════════════


class CliExecutionMetadata(TypedDict, total=False):
    """ReadOnly TypedDict for CLI execution metadata (PEP 705)."""

    command_name: str
    session_id: str
    start_time: float
    pid: int
    environment: str


class CliValidationResult(TypedDict, total=False):
    """ReadOnly TypedDict for CLI validation results (PEP 705)."""

    field_name: str
    rule_name: str
    is_valid: bool
    error_message: str | None


t = FlextCliTypes

__all__ = [
    "CliExecutionMetadata",
    "CliValidationResult",
    "FlextCliTypes",
    "t",
]
