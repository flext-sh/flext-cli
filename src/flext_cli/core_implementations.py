"""Core implementations for CLI functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from flext_core import FlextResult


class ValidationError(TypedDict):
    """Type definition for validation errors."""

    type: str
    loc: tuple[str, ...]
    msg: NotRequired[str]  # Explicitly make msg optional
    input: object  # Flexible type for error input data


def handle_service_result(result: object) -> object:
    """Handle service result and return appropriate response.

    Args:
        result: The service result to handle

    Returns:
        The processed result

    """
    if isinstance(result, FlextResult):
        return result.data if result.success else result.error
    return result


__all__ = [
    "ValidationError",
    "handle_service_result",
]
