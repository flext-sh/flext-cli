"""FLEXT CLI Mixins - Single unique CLI mixins class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextMixins


class FlextCliMixins(FlextMixins):
    """CLI-specific mixins extending flext-core FlextMixins.

    Single unique class for the module following flext-core inheritance patterns.
    All functionality should be available through FlextMixins base class.
    """

    # Reference to flext-core mixins for inheritance
    Core: ClassVar = FlextMixins


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliMixins",
]
