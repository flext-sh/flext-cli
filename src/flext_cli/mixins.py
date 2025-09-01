"""FLEXT CLI Mixins - Thin alias to flext-core mixins.

Prefer importing FlextMixins from flext_core directly when possible.
This wrapper exists only to keep CLI’s public API stable when required.
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextMixins


class FlextCliMixins(FlextMixins):
    """CLI-specific mixins extending flext-core FlextMixins (no extra behavior)."""

    Core: ClassVar = FlextMixins


__all__ = ["FlextCliMixins"]
