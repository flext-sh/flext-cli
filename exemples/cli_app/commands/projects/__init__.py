"""Project-specific commands for flext-cli.

Consolidated project commands from across the FLEXT workspace.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Import project modules when they are available
import contextlib

with contextlib.suppress(ImportError):
    from . import algar, gruponos, meltano

__all__: list[str] = ["algar", "gruponos", "meltano"]
