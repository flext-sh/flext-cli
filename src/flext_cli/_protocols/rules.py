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

from flext_core import p

if TYPE_CHECKING:
    from flext_cli._typings import FlextCliTypesDomain


class FlextCliProtocolsRules:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class LocalDefinitionsOptions[TRuleKind, TFileRuleKind](p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        package_rules_dir: Path
        rule_filters: Sequence[str]

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

        registry_filename: str
        rules_key: str
        rule_id_key: str
        enabled_key: str
        action_key: str
        check_key: str
        rules_dir_name: str


__all__: list[str] = [
    "FlextCliProtocolsRules",
]
