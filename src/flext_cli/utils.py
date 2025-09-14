"""FLEXT CLI Utilities - Shared factory functions and utilities.

Consolidates duplicate factory functions and common utilities to reduce code bloat.
Single source of truth for UUID generation, datetime factories, and collection factories.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from flext_core import FlextContainer, FlextLogger
from pydantic import ConfigDict
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants


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
    return (
        Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.AUTH_DIR_NAME
        / FlextCliConstants.TOKEN_FILE_NAME
    )


def refresh_token_file_path() -> Path:
    """Factory for CLI refresh token file path."""
    return (
        Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.AUTH_DIR_NAME
        / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
    )


# Field factory functions moved to field_factories.py to avoid circular imports
# Use direct Field() calls instead of factory functions to avoid type issues


# description_field removed - use direct Field() calls instead


# All factory functions removed - use direct Field() calls instead
# This eliminates type inference issues with MyPy strict mode


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


# All factory functions removed - use direct Field() calls instead
# This eliminates type inference issues with MyPy strict mode
