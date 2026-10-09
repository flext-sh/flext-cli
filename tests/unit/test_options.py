"""Behavioral tests for public CLI option annotation resolution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from flext_tests import tm

from flext_cli import t, u


class TestsFlextCliOptions:
    """Observable contracts for Typer-compatible public annotations."""

    @staticmethod
    def test_tuple_field_becomes_repeated_typer_input() -> None:
        """Canonical tuple fields accept repeated CLI values through a list."""
        resolved = u.Cli.resolve_typer_annotation(
            cast("t.Cli.RuntimeAnnotation", t.VariadicTuple[Path]),
        )

        tm.that(resolved, eq=list[Path])
