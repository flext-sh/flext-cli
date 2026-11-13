"""Single Result Command - One Model-Backed Command as the Whole CLI.

Shows ``cli.run_result_command``: one request model and one handler become a
complete CLI whose options follow the program name with no subcommand token.

WHEN TO USE:
- A module or console script exposes exactly one operation
- The operation already returns ``p.Result[...]``

FLEXT-CLI PROVIDES:
- Options generated from the request model's fields
- Help taken from the model's docstring
- Exit codes 0 (success), 1 (domain failure) and 2 (usage error)

HOW TO USE IN YOUR CLI:
``python -m examples.ex_13_single_result_command --name Ada``

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from examples import c, m, p, r, t, u
from flext_cli import cli


class ExamplesFlextCliSingleResultCommand:
    """Single-command CLI example built on ``cli.run_result_command``."""

    @staticmethod
    def greet(request: p.Examples.GreetingRequest) -> p.Result[str]:
        """Build the greeting, refusing a blank name as a domain failure.

        Returns:
            The greeting, or a failure for a blank name.

        """
        if not request.name.strip():
            return r[str].fail(c.EXAMPLE_ERR_BLANK_NAME)
        greeting = c.EXAMPLE_GREETING_FMT.format(name=request.name)
        return r[str].ok(greeting.upper() if request.shout else greeting)

    @staticmethod
    def main(argv: t.StrSequence | None = None) -> int:
        """Run the greeting command and return its exit code.

        Returns:
            The process exit code.

        """
        return cli.run_result_command(
            m.Examples.GreetingRequest,
            ExamplesFlextCliSingleResultCommand.greet,
            m.Cli.CommandMetadata(name=c.EXAMPLE_GREET_PROG_NAME),
            args=argv,
            success_formatter=str,
        )

    @staticmethod
    def run() -> None:
        """Run the greeting command as the whole process."""
        u.Cli.process_main(ExamplesFlextCliSingleResultCommand.main)


if __name__ == "__main__":
    ExamplesFlextCliSingleResultCommand.run()

__all__: list[str] = ["ExamplesFlextCliSingleResultCommand"]
