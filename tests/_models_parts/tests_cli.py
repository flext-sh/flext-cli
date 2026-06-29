"""Split test model namespace."""

from __future__ import annotations

from typing import Annotated

from flext_cli import m
from tests import c


class TestsFlextCliModelsCli:
    """Split test model namespace."""

    class SampleInput(m.BaseModel):
        """Small request model for exercising model-driven CLI generation."""

        name: Annotated[str, m.Field(description="Target name")]
        count: Annotated[int, m.Field(description="How many times")] = 1
        dry_run: Annotated[bool, m.Field(description="Dry-run mode")] = False
        output_format: Annotated[
            c.Cli.OutputFormats, m.Field(description="Output format")
        ] = c.Cli.OutputFormats.TABLE

    class SampleOutput(m.BaseModel):
        """Concrete output model for result-route tests."""

        message: Annotated[str, m.Field(description="User-facing success message")]

    class RepeatableInput(m.BaseModel):
        """Exercise repeatable CLI options derived from list-typed fields."""

        make_arg: Annotated[
            list[str],
            m.Field(default_factory=list, description="Repeatable make-style arg"),
        ] = m.Field(default_factory=list)


__all__: list[str] = ["TestsFlextCliModelsCli"]
