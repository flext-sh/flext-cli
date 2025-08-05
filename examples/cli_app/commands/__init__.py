"""FLEXT CLI Commands.

Command modules for the FLEXT CLI.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.commands import (  # pipeline and plugin don't exist yet
    auth,
    config,
    debug,
)
from flext_cli.commands.projects import client-a, client-b, meltano

__all__: list[str] = [
    "client-a",
    "auth",
    "config",
    "debug",
    "client-b",
    "meltano",
    # "pipeline",  # Not implemented yet
    # "plugin",    # Not implemented yet
]
