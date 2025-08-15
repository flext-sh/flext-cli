"""Core types."""

from __future__ import annotations

import click as _click

from flext_cli.cli_types import PositiveIntType


class ClickPath(_click.Path):
    """Enhanced Click Path with convenience options."""

    def __init__(
        self,
        *,
        exists: bool | None = None,
        file_okay: bool | None = None,
        dir_okay: bool | None = None,
        readable: bool | None = None,
        writable: bool | None = None,
        allow_dash: bool | None = None,
        resolve_path: bool | None = None,
        path_type: type[str] | None = None,
    ) -> None:
        """Init the ClickPath."""
        super().__init__(
            exists=bool(exists),
            file_okay=True if file_okay is None else bool(file_okay),
            dir_okay=True if dir_okay is None else bool(dir_okay),
            readable=False if readable is None else bool(readable),
            writable=False if writable is None else bool(writable),
            allow_dash=False if allow_dash is None else bool(allow_dash),
            resolve_path=False if resolve_path is None else bool(resolve_path),
            path_type=path_type or str,
        )


# Convenience instances used directly by tests
ExistingFile = ClickPath(exists=True, file_okay=True, dir_okay=False)
ExistingDir = ClickPath(exists=True, file_okay=False, dir_okay=True)
NewFile = ClickPath(exists=False, file_okay=True, dir_okay=False)

# PositiveInt instance expected by tests
PositiveInt = PositiveIntType()
