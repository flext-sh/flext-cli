"""Re-export framework exceptions through canonical c.Cli.* namespace.

flext-cli is the SSOT owner of Click/Typer abstraction. Click and Typer
exceptions captured by consumer code MUST be referenced through these
canonical aliases instead of importing click/typer directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from click import Abort as _ClickAbort, ClickException as _ClickException
from typer import Exit as _TyperExit
from yaml import YAMLError as _YamlError


class FlextCliConstantsExceptions:
    """Canonical CLI exception aliases for cross-project consumption.

    Usage:
        from flext_cli import c
        try:
            ...
        except c.Cli.CliAbortError:
            ...
    """

    CliAbortError: ClassVar[type[BaseException]] = _ClickAbort
    CliCommandError: ClassVar[type[BaseException]] = _ClickException
    CliExit: ClassVar[type[BaseException]] = _TyperExit
    YamlParseError: ClassVar[type[Exception]] = _YamlError


__all__: list[str] = ["FlextCliConstantsExceptions"]
