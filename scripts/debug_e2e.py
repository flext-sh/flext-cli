#!/usr/bin/env python3
"""Debug E2E test failures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import traceback

from flext_cli import FlextCli


def main() -> None:
    """Debug E2E test runner for CLI operations."""
    # Create CLI instance
    cli_main = FlextCli()

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
            result = cli_main.main.run_command(operation)
            if result.is_failure:
                print(f"Command {operation} failed: {result.error}")
                break
        except Exception as e:
            print(f"Command {operation} raised exception: {e}")
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
