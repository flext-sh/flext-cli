"""FLEXT CLI custom parameter types for Click framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Click parameter types for command-line interfaces using flext-core patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

import click

if TYPE_CHECKING:
    from click import Context, Parameter


class PositiveIntType(click.ParamType):
    """Click parameter type for positive integers."""

    name = "positive_int"

    def convert(
        self,
        value: object,
        param: Parameter | None,
        ctx: Context | None,
    ) -> int:
        """Convert value to positive integer."""
        if isinstance(value, int):
            if value <= 0:
                self.fail(f"{value} is not a positive integer", param, ctx)
            return value

        try:
            # Type narrowing for int conversion
            if isinstance(value, (str, int, float)):
                int_value = int(value)
                if int_value <= 0:
                    self.fail(f"{value} is not a positive integer", param, ctx)
                return int_value
            self.fail(f"{value!r} is not a valid integer type", param, ctx)
        except (ValueError, TypeError):
            self.fail(f"{value!r} is not a valid integer", param, ctx)


class URLType(click.ParamType):
    """Click parameter type for URLs."""

    name = "url"

    def convert(
        self,
        value: object,
        param: Parameter | None,
        ctx: Context | None,
    ) -> str:
        """Convert value to validated URL."""
        if not isinstance(value, str):
            self.fail(f"{value!r} is not a string", param, ctx)

        try:
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                self.fail(f"{value!r} is not a valid URL", param, ctx)
            return value
        except (ValueError, TypeError):
            self.fail(f"{value!r} is not a valid URL", param, ctx)


class ClickPath(click.Path):
    """Enhanced Click Path type with flext-core integration."""

    def __init__(
        self,
        *,
        exists: bool = False,
        file_okay: bool = True,
        dir_okay: bool = True,
        writable: bool = False,
        readable: bool = True,
    ) -> None:
        """Initialize enhanced Click Path."""
        super().__init__(
            exists=exists,
            file_okay=file_okay,
            dir_okay=dir_okay,
            writable=writable,
            readable=readable,
            resolve_path=True,
            allow_dash=False,
            path_type=str,
        )


# Convenience instances
PositiveInt = PositiveIntType()
URL = URLType()
ExistingFile = ClickPath(exists=True, file_okay=True, dir_okay=False)
ExistingDir = ClickPath(exists=True, file_okay=False, dir_okay=True)
NewFile = ClickPath(exists=False, file_okay=True, dir_okay=False)
