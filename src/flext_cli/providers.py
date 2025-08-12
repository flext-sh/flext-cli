"""FLEXT CLI Configuration Providers - Provider implementations for hierarchical config.

This module implements configuration providers that integrate with the hierarchical
configuration system following docs/patterns/config-cli.md patterns.

Provider Types:
    - FlextCliArgsProvider: CLI arguments (highest precedence)
    - FlextConstantsProvider: Default constants (lowest precedence)

Integration:
    - Used by flext_cli.config_hierarchical.FlextCLIConfigHierarchical
    - Supports the 5-level configuration hierarchy
    - Type-safe with FlextResult patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.constants import FlextConfigSemanticConstants


class FlextCliArgsProvider:
    """CLI arguments configuration provider (highest precedence)."""

    def __init__(self, args: dict[str, object]) -> None:
        """Initialize provider with CLI args dict."""
        self.args = args

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration from CLI arguments."""
        value = self.args.get(key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority."""
        return FlextConfigSemanticConstants.Hierarchy.CLI_ARGS

    def get_all(self) -> dict[str, object]:
        """Get all CLI arguments."""
        return self.args.copy()


class FlextConstantsProvider:
    """Constants configuration provider (lowest precedence)."""

    def __init__(self, constants: dict[str, object]) -> None:
        """Initialize provider with constants dict."""
        self.constants = constants

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration from constants."""
        value = self.constants.get(key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority."""
        return FlextConfigSemanticConstants.Hierarchy.CONSTANTS

    def get_all(self) -> dict[str, object]:
        """Get all constants."""
        return self.constants.copy()


__all__ = [
    "FlextCliArgsProvider",
    "FlextConstantsProvider",
]
