"""FLEXT CLI Commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Command modules for the FLEXT CLI.
"""

from __future__ import annotations

from flext_cli.commands import auth, config, debug, pipeline, plugin
from flext_cli.commands.projects import client-a, client-b, meltano

__all__ = [
    "client-a",
    "auth",
    "config",
    "debug",
    "client-b",
    "meltano",
    "pipeline",
    "plugin",
]
