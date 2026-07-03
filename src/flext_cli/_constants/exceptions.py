"""Re-export framework exceptions through canonical c.Cli.* namespace.

flext-cli is the SSOT owner of Click/Typer abstraction. Click and Typer
exceptions captured by consumer code MUST be referenced through these
canonical aliases instead of importing click/typer directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from click import Abort, ClickException
from typer import Exit
from yaml import YAMLError


class FlextCliConstantsExceptions:
    """Canonical CLI exception aliases for cross-project consumption.

    Usage:
        from flext_cli import c
        try:
            ...
        except c.Cli.CliAbortError:
            ...
    """

    CliAbortError: ClassVar[type[BaseException]] = Abort
    CliCommandError: ClassVar[type[BaseException]] = ClickException
    CliExit: ClassVar[type[BaseException]] = Exit
    YamlParseError: ClassVar[type[Exception]] = YAMLError


__all__: list[str] = ["FlextCliConstantsExceptions"]
