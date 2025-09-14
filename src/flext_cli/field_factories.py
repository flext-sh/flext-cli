"""FLEXT CLI Field Factories - Pydantic field factory functions.

Provides reusable field factory functions for Pydantic models in the CLI package.
Extracted to avoid circular imports between constants.py and utils.py.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field


def positive_int_field(
    default: int, min_val: int | None = None, max_val: int | None = None
):
    """Factory for positive integer fields with validation."""
    if max_val is not None:
        return Field(default=default, ge=min_val or 1, le=max_val)
    return Field(default=default, ge=min_val or 1)


def size_field(default: int, max_size: int | None = None):
    """Factory for size fields with validation."""
    if max_size is not None:
        return Field(default=default, ge=1, le=max_size)
    return Field(default=default, ge=1)


def timeout_field(default: int, max_timeout: int | None = None):
    """Factory for timeout fields with validation."""
    if max_timeout is not None:
        return Field(default=default, ge=1, le=max_timeout)
    return Field(default=default, ge=1)


def bounded_str_field(
    default: str,
    min_len: int | None = None,
    max_len: int | None = None,
    pattern: str | None = None,
):
    """Factory for bounded string fields with validation."""
    kwargs: dict[str, int | str | bool] = {}
    if min_len is not None:
        kwargs["min_length"] = min_len
    if max_len is not None:
        kwargs["max_length"] = max_len
    if pattern is not None:
        kwargs["pattern"] = pattern
    return Field(default=default, **kwargs)


def frozen_str_field(default: str):
    """Factory for frozen string fields."""
    return Field(default=default, frozen=True)


def port_field(default: int):
    """Factory for port fields with validation."""
    return Field(default=default, ge=1, le=65535)