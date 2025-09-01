"""FLEXT CLI Utilities - Thin alias to flext-core utilities.

Prefer importing FlextUtilities from flext_core directly when possible.
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextUtilities


class FlextCliUtilities(FlextUtilities):
    """CLI-specific utilities extending flext-core FlextUtilities (no extra behavior)."""

    Core: ClassVar = FlextUtilities


__all__ = ["FlextCliUtilities"]
