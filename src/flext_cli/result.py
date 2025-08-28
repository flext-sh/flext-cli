"""FlextResult pattern re-export for CLI operations.

Re-exports FlextResult from flext-core following FLEXT architectural patterns.
This module follows the Foundation Layer pattern from flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Re-export FlextResult from flext-core (don't reimplement)
from flext_core import FlextResult

__all__ = ["FlextResult"]
