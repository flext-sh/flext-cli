"""FLEXT CLI Commands.

Command modules for the FLEXT CLI.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.commands import auth, config, debug  # pipeline and plugin don't exist yet
from flext_cli.commands.projects import algar, gruponos, meltano

__all__: list[str] = [
    "algar",
    "auth",
    "config",
    "debug",
    "gruponos",
    "meltano",
    # "pipeline",  # Not implemented yet
    # "plugin",    # Not implemented yet
]
