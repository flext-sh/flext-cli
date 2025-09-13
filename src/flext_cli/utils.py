"""FLEXT CLI Utilities - Shared factory functions and utilities.

Consolidates duplicate factory functions and common utilities to reduce code bloat.
Single source of truth for UUID generation, datetime factories, and collection factories.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from flext_core import FlextContainer, FlextLogger
from pydantic import ConfigDict, Field
from pydantic.fields import FieldInfo
from pydantic_settings import SettingsConfigDict

# Removed FlextCliConstants import to prevent circular dependency
# Use local imports in functions that need constants


# Consolidated factory functions for better performance and reduced bloat
def generate_uuid() -> str:
    """Generate UUID string for entity IDs."""
    return str(uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def empty_dict() -> dict[str, object]:
    """Factory for empty dictionary - optimized for Pydantic default_factory."""
    return {}


def empty_list() -> list[object]:
    """Factory for empty list - optimized for Pydantic default_factory."""
    return []


def empty_str_dict() -> dict[str, str]:
    """Factory for empty string dictionary."""
    return {}


def empty_str_list() -> list[str]:
    """Factory for empty string list."""
    return []


# Consolidated ConfigDict patterns for consistent Pydantic configuration
STRICT_CONFIG_DICT = ConfigDict(
    str_strip_whitespace=True,
    validate_default=True,
    use_enum_values=True,
    extra="forbid",
)

BASE_CONFIG_DICT = ConfigDict(
    str_strip_whitespace=True,
    validate_default=True,
    extra="forbid",
)

SETTINGS_CONFIG_DICT = SettingsConfigDict(
    str_strip_whitespace=True,
    validate_default=True,
    extra="ignore",
    use_enum_values=True,
    env_prefix="FLEXT_CLI_",
)


# Path factory functions for CLI configuration
def home_path() -> Path:
    """Factory for user home directory path."""
    return Path.home()


def token_file_path() -> Path:
    """Factory for CLI authentication token file path."""
    from flext_cli.constants import (
        FlextCliConstants,  # Local import to avoid circular dependency
    )

    return (
        Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.AUTH_DIR_NAME
        / FlextCliConstants.TOKEN_FILE_NAME
    )


def refresh_token_file_path() -> Path:
    """Factory for CLI refresh token file path."""
    from flext_cli.constants import (
        FlextCliConstants,  # Local import to avoid circular dependency
    )

    return (
        Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.AUTH_DIR_NAME
        / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
    )


# Field factory functions to eliminate repetitive Field definitions
def positive_int_field(
    default: int, min_val: int = 1, max_val: int | None = None, **kwargs: dict[str, Any]
) -> FieldInfo:
    """Factory for positive integer fields with bounds validation."""
    field_kwargs: dict[str, Any] = {"default": default, "ge": min_val}
    if max_val is not None:
        field_kwargs["le"] = max_val
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def bounded_str_field(
    default: str,
    min_len: int | None = None,
    max_len: int | None = None,
    pattern: str | None = None,
    **kwargs: dict[str, Any],
) -> FieldInfo:
    """Factory for string fields with length and pattern validation."""
    field_kwargs: dict[str, Any] = {"default": default}
    if min_len is not None:
        field_kwargs["min_length"] = min_len
    if max_len is not None:
        field_kwargs["max_length"] = max_len
    if pattern is not None:
        field_kwargs["pattern"] = pattern
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def frozen_str_field(default: str, **kwargs: dict[str, Any]) -> FieldInfo:
    """Factory for immutable string fields."""
    return Field(default=default, frozen=True, **kwargs)


def size_field(
    default: int,
    min_size: int = 1024,
    max_size: int = 10_485_760,
    **kwargs: dict[str, Any],
) -> FieldInfo:
    """Factory for size/capacity fields with reasonable bounds."""
    return Field(default=default, ge=min_size, le=max_size, **kwargs)


def timeout_field(
    default: int,
    min_timeout: int = 1,
    max_timeout: int = 3600,
    **kwargs: dict[str, Any],
) -> FieldInfo:
    """Factory for timeout fields with sensible defaults."""
    return Field(default=default, ge=min_timeout, le=max_timeout, **kwargs)


def port_field(default: int, **kwargs: dict[str, Any]) -> FieldInfo:
    """Factory for network port fields."""
    return Field(default=default, ge=1, le=65535, **kwargs)


def optional_str_field(
    default: str | None = None, **kwargs: dict[str, Any]
) -> FieldInfo:
    """Factory for optional string fields."""
    return Field(default=default, **kwargs)


def version_field(default: str = "0.9.0", **kwargs: dict[str, Any]) -> FieldInfo:
    """Factory for version string fields."""
    return Field(default=default, pattern=r"^\d+\.\d+\.\d+", **kwargs)


def bool_field(*, default: bool, **kwargs: dict[str, Any]) -> FieldInfo:
    """Factory for boolean fields with common defaults."""
    return Field(default=default, **kwargs)


def description_field(
    default: str, description: str = "", **kwargs: dict[str, Any]
) -> FieldInfo:
    """Factory for description/documentation fields."""
    field_kwargs: dict[str, Any] = {"default": default}
    if description:
        field_kwargs["description"] = description
    elif "doc" in kwargs:
        field_kwargs["description"] = kwargs.pop("doc")
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def optional_field(
    default: str | None = None,
    description: str = "",
    **kwargs: dict[str, str | int | bool],
) -> FieldInfo:
    """Factory for optional fields with description."""
    field_kwargs: dict[str, Any] = {"default": default}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def path_field(
    default_factory: Callable[[], Path],
    description: str = "",
    **kwargs: dict[str, str | int | bool],
) -> FieldInfo:
    """Factory for Path fields with default_factory."""
    field_kwargs: dict[str, Any] = {"default_factory": default_factory}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def uuid_field(
    description: str = "", **kwargs: dict[str, str | int | bool]
) -> FieldInfo:
    """Factory for UUID fields using generate_uuid."""
    field_kwargs: dict[str, Any] = {"default_factory": generate_uuid}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def datetime_field(
    description: str = "", **kwargs: dict[str, str | int | bool]
) -> FieldInfo:
    """Factory for datetime fields using utc_now."""
    field_kwargs: dict[str, Any] = {"default_factory": utc_now}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


# Command-specific field factories for eliminating command bloat
def command_type_field(
    default: str, **kwargs: dict[str, str | int | bool]
) -> FieldInfo:
    """Factory for command type identifier fields."""
    return description_field(default, description="Command type identifier", **kwargs)


def profile_field(
    description: str = "Configuration profile", **kwargs: dict[str, str | int | bool]
) -> FieldInfo:
    """Factory for profile fields with consistent default."""
    return description_field("default", description=description, **kwargs)


def output_format_field(
    default: str = "table",
    description: str = "Output format",
    **kwargs: dict[str, str | int | bool],
) -> FieldInfo:
    """Factory for output format fields with validation."""
    return bounded_str_field(
        default,
        description=f"{description} (table, json, yaml, csv)",
        pattern=r"^(table|json|yaml|csv)$",
        **kwargs,
    )


def api_url_field(
    description: str = "API URL override", **kwargs: dict[str, str | int | bool]
) -> FieldInfo:
    """Factory for API URL override fields."""
    return optional_field(default="", description=description, **kwargs)


# Flext-core integration optimization mixins
class FlextServiceMixin:
    """Mixin for consistent flext-core service initialization.

    Eliminates repetitive FlextContainer and FlextLogger setup patterns.
    """

    def __init__(self) -> None:
        """Initialize flext-core services with optimized patterns."""
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(self.__class__.__module__)

    @property
    def logger(self) -> FlextLogger:
        """Access logger instance."""
        return self._logger

    @property
    def container(self) -> FlextContainer:
        """Access container instance."""
        return self._container


# Advanced field factories for constants-based patterns
def enum_field(enum_value: str, **kwargs: dict[str, Any]) -> FieldInfo:
    """Factory for enum constant fields."""
    return Field(default=enum_value, **kwargs)


def constant_field(
    constant_value: str | float, description: str = "", **kwargs: dict[str, Any]
) -> FieldInfo:
    """Factory for constant-based fields from FlextCliConstants."""
    field_kwargs: dict[str, Any] = {"default": constant_value}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)


def validation_field(
    default: str,
    validator_pattern: str,
    description: str = "",
    **kwargs: dict[str, Any],
) -> FieldInfo:
    """Factory for fields requiring custom validation patterns."""
    field_kwargs: dict[str, Any] = {"default": default, "pattern": validator_pattern}
    if description:
        field_kwargs["description"] = description
    field_kwargs.update(kwargs)
    return Field(**field_kwargs)
