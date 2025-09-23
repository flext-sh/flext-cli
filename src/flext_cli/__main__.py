"""Entry point for FLEXT CLI when run as module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.flext_cli_main import create_main_cli

if __name__ == "__main__":
    cli = create_main_cli()
    cli.run_cli()
