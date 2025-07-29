"""FLEXT CLI Commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Command modules for the FLEXT CLI.
"""

from __future__ import annotations

from flext_cli.commands import auth, config, debug, pipeline, plugin
from flext_cli.commands.projects import algar, gruponos, meltano

__all__ = [
    "algar",
    "auth",
    "config",
    "debug",
    "gruponos",
    "meltano",
    "pipeline",
    "plugin",
]
