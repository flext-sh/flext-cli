"""FLEXT CLI Main Entry Point.

CLI application entry point that initializes and runs the FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib
import sys
import traceback

# FlextCliMain is imported inside main() to avoid circular import


def main() -> int:
    """Main CLI entry point."""
    try:
        # Import here to avoid circular import (using importlib to satisfy ruff)
        flext_cli_main = importlib.import_module("flext_cli.main")
        flext_cli_main_class = flext_cli_main.FlextCliMain

        # Create main CLI instance
        cli_main = flext_cli_main_class(
            name="flext",
            version="0.9.9",
            description="FLEXT - Enterprise Data Integration Platform",
        )

        # Execute CLI
        result = cli_main.execute_cli()

        if result.is_success:
            return 0
        return 1

    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
