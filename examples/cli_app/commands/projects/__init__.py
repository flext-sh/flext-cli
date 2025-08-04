"""Project-specific commands for flext-cli.

Consolidated project commands from across the FLEXT workspace.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.commands.projects import client-a, client-b, meltano

__all__: list[str] = ["client-a", "client-b", "meltano"]
