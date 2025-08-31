"""FLEXT CLI Decorators - Single unique CLI decorators class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextDecorators

# =============================================================================
# CONSOLIDATED CLASS - Single unique class for the module
# =============================================================================


class FlextCliDecorators(FlextDecorators):
    """CLI-specific decorators extending flext-core FlextDecorators.

    Single unique class for the module following flext-core inheritance patterns.
    All functionality should be available through FlextDecorators base class.
    """

    # Reference to flext-core decorators for inheritance
    Core: ClassVar = FlextDecorators


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliDecorators",
]
