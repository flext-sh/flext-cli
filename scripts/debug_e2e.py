#!/usr/bin/env python3
"""Debug E2E test failures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
import traceback

from flext_cli import FlextCli


def main() -> None:
    """Debug E2E test runner for CLI operations."""
    # Configure logging for this debug script
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Use flext-cli testing abstraction instead of direct Click
    # This maintains zero tolerance for direct Click imports

    operations = [
        ["config", "show"],
        ["config", "validate"],
        ["auth", "status"],
        ["debug", "check"],
    ]

    for operation in operations:
        try:
            # Use flext-cli API for testing instead of direct Click
            # This maintains abstraction and zero tolerance policy
            logger.info("Testing operation: %s", operation)
            # Note: This script needs updating - FlextCli does not have .main.run_command()
            # For now, just log what would be tested
            FlextCli().run_cli_operation(operation)
        except Exception:
            logger.exception("Command %s raised exception", operation)
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
