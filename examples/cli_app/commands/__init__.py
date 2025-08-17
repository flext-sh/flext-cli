"""FLEXT CLI Commands.

Command modules for the FLEXT CLI.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import (  # pipeline and plugin don't exist yet
    auth,
    config,
    debug,
)
from flext_cli import algar, gruponos, meltano

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
