"""Behavioral tests for public CLI option annotation resolution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from pathlib import Path
from typing import cast

from tests import t, tm, u


class TestsFlextCliOptions:
    """Observable contracts for Typer-compatible public annotations."""

    @staticmethod
    def test_tuple_field_becomes_repeated_typer_input() -> None:
        """Canonical tuple fields accept repeated CLI values through a list."""
        resolved = u.Cli.resolve_typer_annotation(
            cast("t.Cli.RuntimeAnnotation", tuple[Path, ...]),
        )

        tm.that(resolved, eq=list[Path])
