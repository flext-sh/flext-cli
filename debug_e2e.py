#!/usr/bin/env python3
"""Debug E2E test failures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import traceback

from click.testing import CliRunner
from flext_cli.cli import cli


def main() -> None:
    runner = CliRunner()
    operations = [
        ["config", "show"],
        ["config", "validate"],
        ["auth", "status"],
        ["debug", "check"],
    ]

    for operation in operations:
        result = runner.invoke(cli, ["--output", "json", *operation])
        if result.exit_code != 0:
            if result.exception:
                traceback.print_exception(
                    type(result.exception),
                    result.exception,
                    result.exception.__traceback__,
                )
            break


if __name__ == "__main__":
    main()
