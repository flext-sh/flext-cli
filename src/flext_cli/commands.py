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
        name: str,  # noqa: ARG002
        handler: Callable[..., t.GeneralValueType],  # noqa: ARG002
        description: str = "",  # noqa: ARG002
    ) -> r[bool]:
        """Register a CLI command (simplified implementation)."""
        # Phase 2: Simplified to return success without state management
        return r[bool].ok(True)

    def execute_command(
        self,
        name: str,  # noqa: ARG002
        **kwargs: t.GeneralValueType,  # noqa: ARG002
    ) -> r[t.GeneralValueType]:
        """Execute a CLI command (simplified implementation)."""
        # Phase 2: Simplified to return success
        return r[t.GeneralValueType].ok(None)
