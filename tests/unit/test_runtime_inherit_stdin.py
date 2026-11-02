"""Stdin inheritance contract for runtime command execution.

A caller that re-runs an interactive invocation (a changed loader environment,
for example) hands its own stdin to the child with ``inherit_stdin``; the
default keeps the child on the null device. The parent here is a real outer
process whose stdin is a pipe fed through ``input_data``; the inner child is
launched by that parent through the same public ``u.Cli`` facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

import pytest

from tests import c, m, tm, u

_READER = "import sys; sys.stdout.write(sys.stdin.read())"
_PARENT = (
    "import sys\n"
    "from flext_cli import m, p, u\n"
    "out = u.Cli.run_raw(\n"
    "    [sys.executable, '-c', sys.argv[1]],\n"
    "    options=m.Cli.ProcessOptions(inherit_stdin=sys.argv[2] == 'inherit'),\n"
    ").unwrap()\n"
    "sys.stdout.write(out.stdout)\n"
    "raise SystemExit(out.exit_code)\n"
)
_PAYLOAD = "operator-typed line\n"


class TestsFlextCliRuntimeInheritStdin:
    """u.Cli children read the caller's stdin only when asked to."""

    @staticmethod
    def _child_view(mode: str) -> str:
        """Return what the inner child read from its stdin.

        Returns:
            The inner child's stdin contents as relayed by the outer parent.

        """
        return tm.ok(
            u.Cli.capture(
                [sys.executable, "-c", _PARENT, _READER, mode],
                options=m.Cli.ProcessOptions(input_data=_PAYLOAD),
            ),
        )

    @staticmethod
    def test_inherited_stdin_reaches_the_child() -> None:
        """The child reads exactly what the caller's stdin carries."""
        tm.that(
            TestsFlextCliRuntimeInheritStdin._child_view("inherit"),
            eq=_PAYLOAD.strip(),
        )

    @staticmethod
    def test_default_child_stdin_is_the_null_device() -> None:
        """Without the option the caller's stdin never reaches the child."""
        tm.that(TestsFlextCliRuntimeInheritStdin._child_view("devnull"), eq="")

    @staticmethod
    def test_child_exit_code_is_preserved_with_inherited_stdin() -> None:
        """The raw outcome keeps the child's exit code for the caller."""
        output = tm.ok(
            u.Cli.run_raw(
                [sys.executable, "-c", "raise SystemExit(7)"],
                options=m.Cli.ProcessOptions(inherit_stdin=True),
                capture=False,
            ),
        )

        tm.that(output.exit_code, eq=7)

    @staticmethod
    def test_run_failure_carries_the_typed_outcome() -> None:
        """A failed ``u.Cli.run`` carries the child's exit as data, not text."""
        failed = u.Cli.run(
            [sys.executable, "-c", "raise SystemExit(7)"],
            options=m.Cli.ProcessOptions(inherit_stdin=True),
            capture=False,
        )
        tm.fail(failed, has="failed (7)")
        data = tm.not_none(failed.error_data)
        tm.that(data[c.Cli.PROCESS_EXIT_CODE_KEY], eq=7)
        tm.that(data[c.Cli.PROCESS_TIMED_OUT_KEY], eq=False)
        tm.that(data[c.Cli.PROCESS_FORWARDED_SIGNAL_KEY], eq=None)

    @staticmethod
    def test_inherit_stdin_and_input_data_are_one_source() -> None:
        """Declaring both stdin sources is rejected before any effect."""
        with pytest.raises(m.ValidationError):
            m.Cli.ProcessOptions(inherit_stdin=True, input_data=_PAYLOAD)
