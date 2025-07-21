"""Version information for flext_cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Import from centralized version management system
from flext_core.version import get_version, get_version_info

__version__ = get_version("flext-cli")
__version_info__ = get_version_info("flext-cli")

# FLEXT Enterprise - Unified Versioning System
# Version is managed centrally in flext_core.version
# This maintains backward compatibility while eliminating duplication.
