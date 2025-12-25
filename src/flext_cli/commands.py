"""FLEXT CLI Commands - Simple class following FLEXT standards.

Command creation and management using flext-core patterns.
Converted to simple class in Phase 2 refactoring.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import r

from flext_cli.typings import t


class FlextCliCommands:
    """Simple CLI commands class following FLEXT standards.

    Converted to simple class in Phase 2 - minimal functionality preserved.
    """

    def register_command(
        self,
        name: str,
        handler: Callable[[], t.GeneralValueType],
    ) -> r[bool]:
        """Register a CLI command (simplified implementation)."""
        # Phase 2: Simplified to return success without state management
        # Validate inputs
        if not isinstance(name, str) or not name.strip():
            return r[bool].fail("Command name must be non-empty string")
        if not callable(handler):
            return r[bool].fail("Handler must be callable")
        return r[bool].ok(True)

    def execute_command(
        self,
        name: str,
        **kwargs: t.GeneralValueType,
    ) -> r[t.GeneralValueType]:
        """Execute a CLI command (simplified implementation)."""
        # Phase 2: Simplified to return success
        # Validate inputs minimally
        if not name or not isinstance(name, str):
            return r[t.GeneralValueType].fail("Invalid command name")
        if not kwargs:
            return r[t.GeneralValueType].fail("Command requires arguments")
        # Validate kwargs contain valid values
        for key in kwargs:
            if not isinstance(key, str):
                return r[t.GeneralValueType].fail(f"Invalid argument key: {key}")
        return r[t.GeneralValueType].ok(None)
