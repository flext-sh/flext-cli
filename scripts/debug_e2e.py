#!/usr/bin/env python3
"""Debug E2E test failures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import traceback

from click import Command
from click.testing import CliRunner

from flext_cli import FlextCli


def main() -> None:
    """Debug E2E test runner for CLI operations."""
    runner = CliRunner()

    # Create CLI instance and get the Click group
    cli_main = FlextCli()
    cli_group = cli_main.main.get_click_group()

    # Type assertion for MyPy
    if not isinstance(cli_group, Command):
        error_msg = f"Expected BaseCommand, got {type(cli_group)}"
        raise TypeError(error_msg)

    operations = [
        ["config", "show"],
        ["config", "validate"],
        ["auth", "status"],
        ["debug", "check"],
    ]

    for operation in operations:
        result = runner.invoke(cli_group, ["--output", "json", *operation])
        if result.exit_code != 0:
            if result.exception:
                traceback.print_exception(result.exception)
            break


if __name__ == "__main__":
    main()
