"""Entry point for FLEXT CLI when run as module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cli import FlextCli


def main() -> None:
    """Main entry point for FLEXT CLI."""
    cli = FlextCli()
    cli.run_cli()


if __name__ == "__main__":
    main()
