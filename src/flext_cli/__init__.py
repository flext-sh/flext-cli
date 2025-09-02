"""FLEXT CLI - CLI-specific functionality extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from .api import *
from .auth import *
from .client import *
from .cmd import *
from .config import *
from .constants import *
from .context import *
from .debug import *
from .decorators import *
from .models import *
from .services import *
from .typings import *
from .cli_utils import *
from .formatters import *
from .protocols import *
from .formatter_adapter import *
from .output_adapter import *
from .api_functions import FlextCliApiFunctions
from .helpers import (
    FlextCliDataProcessor,
    FlextCliFileManager,
    FlextCliHelper,
    FlextCliHelpers,
)
from flext_core.result import FlextResult
from typing import Any, TypeVar
from rich.console import Console
from rich.table import Table

T = TypeVar("T")


# Thin functional wrappers for the class-based API (new API underneath)
def flext_cli_format(data: object, format_type: str) -> FlextResult[str]:
    """Format data using the consolidated class-based API.

    Kept as a thin wrapper to maintain test compatibility while using
    the new class-based API under the hood.
    """
    return FlextCliApiFunctions.format(data, format_type)


def flext_cli_table(data: object, title: str | None = None) -> FlextResult[Table]:
    """Create a table representation for the given data (via new API)."""
    return FlextCliApiFunctions.table(data, title)


def flext_cli_export(
    data: object, file_path: str, format_type: str
) -> FlextResult[str]:
    """Export data to a file path using the selected format (via new API)."""
    return FlextCliApiFunctions.export(data, file_path, format_type)


def flext_cli_batch_export(
    datasets: dict[str, object], directory: str, format_type: str
) -> FlextResult[list[str]]:
    """Export multiple datasets into a directory (via new API)."""
    return FlextCliApiFunctions.batch_export(datasets, directory, format_type)


def flext_cli_unwrap_or_default[T](result: FlextResult[T], default: T) -> T:
    """Unwrap result value or return the provided default (via new API)."""
    return FlextCliApiFunctions.unwrap_or_default(result, default)


def flext_cli_unwrap_or_none[T](result: FlextResult[T]) -> T | None:
    """Unwrap result value or return None (via new API)."""
    return FlextCliApiFunctions.unwrap_or_none(result)


# Helper factories
def flext_cli_create_helper(
    *, console: Console | None = None, quiet: bool = False
) -> FlextCliHelper:
    """Create a Flext CLI helper using the new helper factories."""
    return FlextCliHelpers.create_helper(console=console, quiet=quiet)


def flext_cli_create_data_processor(
    *, helper: FlextCliHelper | None = None
) -> FlextCliDataProcessor:
    """Create a Flext CLI data processor (new API)."""
    return FlextCliHelpers.create_data_processor(helper=helper)


def flext_cli_create_file_manager(
    *, helper: FlextCliHelper | None = None
) -> FlextCliFileManager:
    """Create a Flext CLI file manager (new API)."""
    return FlextCliHelpers.create_file_manager(helper=helper)


__all__: list[str] = [
    # Class facades
    "FlextCliApiFunctions",
    "FlextCliHelpers",
    # Functional wrappers
    "flext_cli_format",
    "flext_cli_table",
    "flext_cli_export",
    "flext_cli_batch_export",
    "flext_cli_unwrap_or_default",
    "flext_cli_unwrap_or_none",
    "flext_cli_create_helper",
    "flext_cli_create_data_processor",
    "flext_cli_create_file_manager",
]
