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

from flext_core._exceptions.types import FlextExceptionsTypes


class CliDefinitionError(FlextExceptionsTypes.ValidationError):
    """Located CLI definition-time failure (route/model/field).

    Raised while building/registering the automatic CLI so that consumers
    surface ``[CLI_DEFINITION_ERROR] command '<name>' field '<field>': ...``
    instead of a raw stacktrace. Inherits ``[code] message`` rendering and
    correlation metadata from ``flext_core`` ``e.ValidationError``.
    """

    _default_error_code: ClassVar[str] = "CLI_DEFINITION_ERROR"


class CliValidationError(FlextExceptionsTypes.ValidationError):
    """Located CLI runtime input failure (command/field).

    Raised when ``model_validate`` rejects user input so that consumers
    surface ``[VALIDATION_ERROR] command '<name>' field '<field>': ...``
    instead of pydantic's multi-line dump.
    """

    _default_error_code: ClassVar[str] = "VALIDATION_ERROR"


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
    CliDefinitionError: ClassVar[type[BaseException]] = CliDefinitionError
    CliValidationError: ClassVar[type[BaseException]] = CliValidationError


__all__: list[str] = [
    "CliDefinitionError",
    "CliValidationError",
    "FlextCliConstantsExceptions",
]
