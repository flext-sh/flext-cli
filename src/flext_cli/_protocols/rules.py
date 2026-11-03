# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/rules
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._typings import FlextCliTypesDomain


class FlextCliProtocolsRules:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class LocalDefinitionsOptions[TRuleKind, TFileRuleKind](
        FlextProtocols.Model, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def package_rules_dir(self) -> Path:
            """Directory containing packaged default rule YAMLs."""
            ...

        @property
        def rule_filters(self) -> Sequence[str]:
            """Glob/substring filters limiting loaded rules."""
            ...

        @property
        def rule_catalog(self) -> FlextCliTypesDomain.RuleCatalog[TRuleKind]:
            """Catalog mapping rule kinds to their matchers."""
            ...

        @property
        def file_rule_catalog(
            self,
        ) -> FlextCliTypesDomain.RuleCatalog[TFileRuleKind] | None:
            """Optional catalog of file-rule kinds and matchers."""
            ...

        @property
        def registry_filename(self) -> str:
            """Name of the YAML registry file inside the rules dir."""
            ...

        @property
        def rules_key(self) -> str:
            """Top-level key under which rules are nested in YAMLs."""
            ...

        @property
        def rule_id_key(self) -> str:
            """Per-rule key holding the unique rule identifier."""
            ...

        @property
        def enabled_key(self) -> str:
            """Per-rule key controlling whether the rule is active."""
            ...

        @property
        def action_key(self) -> str:
            """Per-rule key naming the fix action to dispatch."""
            ...

        @property
        def check_key(self) -> str:
            """Per-rule key naming the check predicate to dispatch."""
            ...

        @property
        def rules_dir_name(self) -> str:
            """Name of the rules subdirectory inside config_path."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsRules",
]
