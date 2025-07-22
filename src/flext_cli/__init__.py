"""FLEXT CLI - Pure Generic Command Line Interface Framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Generic CLI framework that discovers commands from FLEXT projects via DI.
No knowledge of specific projects - purely architectural.
"""

from __future__ import annotations

from flext_cli.cli import cli, main

__version__ = "0.7.0"

__all__ = [
    "__version__",
    "cli",
    "main",
]
