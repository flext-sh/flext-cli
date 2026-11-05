"""Argv contract for runtime command execution.

The child receives every argument exactly as the caller passed it: the
launcher hands argv to the operating system and never normalizes it, so
leading, trailing, and embedded whitespace reach the child untouched.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from tests import tm, u

_ECHO_ARGV = "import sys; sys.stdout.write(repr(sys.argv[1:]))"


class TestsFlextCliRuntimeArgvVerbatim:
    """u.Cli children see the caller's argv byte for byte."""

    @staticmethod
    def test_child_receives_whitespace_in_arguments_verbatim() -> None:
        """Surrounding and embedded whitespace survive the launch."""
        arguments = (" padded ", "\ttabbed\n", "inner  gap", "")
        output = tm.ok(
            u.Cli.run_raw([sys.executable, "-c", _ECHO_ARGV, *arguments]),
        )
        tm.ok(u.Cli.process_succeeded(output.outcome))
        tm.that(output.stdout, eq=repr(list(arguments)))


__all__: list[str] = ["TestsFlextCliRuntimeArgvVerbatim"]
