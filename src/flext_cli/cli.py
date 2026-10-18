"""CLI entrypoint for flext-cli — executes the project API handlers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import api

if TYPE_CHECKING:
    from flext_cli import t


def main(args: t.StrSequence | None = None) -> int:
    """Execute the API-declared handlers through the adapter framework.

    Declared routes register through the API service; with none declared the
    framework owns help and argument errors, so this entry never reports an
    empty success.

    Args:
        args: Optional command-line tokens passed to the application.

    Returns:
        The resulting exit code.

    """
    application = api.cli.framework_create_app(
        name="flext-cli",
        help_text="FLEXT developer CLI and SSOT for CLI-adjacent domains.",
    )
    executed = api.cli.execute_app(
        application,
        prog_name="flext-cli",
        args=args,
    )
    return api.cli.finalize_result(executed)


__all__: list[str] = ["main"]
