"""Behavioral tests for public CLI option annotation resolution."""

from __future__ import annotations

from pathlib import Path

from flext_cli import u
from flext_tests import tm


class TestsFlextCliOptions:
    """Observable contracts for Typer-compatible public annotations."""

    def test_tuple_field_becomes_repeated_typer_input(self) -> None:
        """Canonical tuple fields accept repeated CLI values through a list."""
        resolved = u.Cli.resolve_typer_annotation(tuple[Path, ...])

        tm.that(resolved, eq=list[Path])


__all__: list[str] = ["TestsFlextCliOptions"]
