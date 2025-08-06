"""Project-specific commands for flext-cli.

Consolidated project commands from across the FLEXT workspace.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Import project modules when they are available
try:
    from . import client-a, client-b, meltano
except ImportError:
    # Modules may not be available in all configurations
    pass

__all__: list[str] = ["client-a", "client-b", "meltano"]
