#!/usr/bin/env python3
"""Debug E2E test failures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
import traceback

from flext_core import FlextCore

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

            cli = FlextCli()

            # Route operations to appropriate methods
            if operation == ["config", "show"]:
                result = cli.cmd.show_config_paths()
            elif operation == ["config", "validate"]:
                result = cli.cmd.validate_config()
            elif operation == ["auth", "status"]:
                # Test authentication status
                is_authenticated = cli.is_authenticated()
                result = FlextCore.Result[None].ok(None) if is_authenticated else FlextCore.Result[None].fail("Not authenticated")
            elif operation == ["debug", "check"]:
                # Test debug functionality - check if services are operational
                result = cli.execute()
            else:
                result = FlextCore.Result[None].fail(f"Unknown operation: {operation}")

            if result.is_success:
                logger.info("Operation %s completed successfully", operation)
            else:
                logger.error("Operation %s failed: %s", operation, result.error)

        except Exception:
            logger.exception("Command %s raised exception", operation)
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
