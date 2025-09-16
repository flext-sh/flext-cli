"""FLEXT CLI Utilities - Unified class following FLEXT architecture patterns.

Single FlextCliUtilities class consolidating all utility functions and validation helpers.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from flext_core import FlextContainer, FlextLogger, FlextResult, FlextUtilities
from pydantic import ConfigDict
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants


class FlextCliUtilities(FlextUtilities):
    """CLI utilities extending flext-core FlextUtilities.

    Single unified class consolidating all utility functions and validation helpers.
    Follows FLEXT unified class pattern - one class per module extending flext-core.
    """

    def __init__(self) -> None:
        """Initialize with flext-core services."""
        super().__init__()
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

    # Factory Functions (consolidated from loose functions)
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID string for entity IDs."""
        return str(uuid4())

    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime."""
        return datetime.now(UTC)

    @staticmethod
    def empty_dict() -> dict[str, object]:
        """Factory for empty dictionary - optimized for Pydantic default_factory."""
        return {}

    @staticmethod
    def empty_list() -> list[object]:
        """Factory for empty list - optimized for Pydantic default_factory."""
        return []

    @staticmethod
    def empty_str_dict() -> dict[str, str]:
        """Factory for empty string dictionary."""
        return {}

    @staticmethod
    def empty_str_list() -> list[str]:
        """Factory for empty string list."""
        return []

    # Path Factory Functions
    @staticmethod
    def home_path() -> Path:
        """Factory for user home directory path."""
        return Path.home()

    @staticmethod
    def token_file_path() -> Path:
        """Factory for CLI authentication token file path."""
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.TOKEN_FILE_NAME
        )

    @staticmethod
    def refresh_token_file_path() -> Path:
        """Factory for CLI refresh token file path."""
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
        )

    # Configuration Dictionaries
    @staticmethod
    def get_strict_config_dict() -> ConfigDict:
        """Get strict ConfigDict for Pydantic configuration."""
        return ConfigDict(
            str_strip_whitespace=True,
            validate_default=True,
            use_enum_values=True,
            extra="forbid",
        )

    @staticmethod
    def get_base_config_dict() -> ConfigDict:
        """Get base ConfigDict for Pydantic configuration."""
        return ConfigDict(
            str_strip_whitespace=True,
            validate_default=True,
            extra="forbid",
        )

    @staticmethod
    def get_settings_config_dict() -> SettingsConfigDict:
        """Get settings ConfigDict for Pydantic Settings."""
        return SettingsConfigDict(
            str_strip_whitespace=True,
            validate_default=True,
            extra="ignore",
            use_enum_values=True,
            env_prefix="FLEXT_CLI_",
        )

    # Data Processing (consolidated from FlextCliDataProcessing)
    @staticmethod
    def validate_data(data: object, validator_func: object) -> FlextResult[object]:
        """Validate data using flext-core utilities directly."""
        try:
            # Handle dict of validators
            if isinstance(validator_func, dict) and isinstance(data, dict):
                for key, validator_type in validator_func.items():
                    if key not in data:
                        return FlextResult[object].fail(
                            f"Missing required field: {key}"
                        )
                    if not isinstance(data[key], validator_type):
                        return FlextResult[object].fail(
                            f"Field '{key}' has wrong type, expected {validator_type.__name__}"
                        )
                return FlextResult[object].ok(data)

            # Handle callable validator function
            if not callable(validator_func):
                return FlextResult[object].fail("Validator function must be callable")

            # Use flext-core validation directly
            if isinstance(data, dict):
                # Validate dictionary data
                validation_result = validator_func(data)
                if validation_result:
                    return FlextResult[object].ok(data)
                return FlextResult[object].fail("Data validation failed")

            if isinstance(data, list):
                # Validate list data
                validation_result = validator_func(data)
                if validation_result:
                    return FlextResult[object].ok(data)
                return FlextResult[object].fail("Data validation failed")

            # For other types, try validation
            validation_result = validator_func(data)
            if validation_result:
                return FlextResult[object].ok(data)
            return FlextResult[object].fail("Data validation failed")

        except Exception as e:
            return FlextResult[object].fail(f"Validation failed: {e}")

    @staticmethod
    def batch_process_items(
        items: object, processor_func: object
    ) -> FlextResult[object]:
        """Process items in batch using flext-core utilities directly."""
        try:
            if not isinstance(items, list):
                return FlextResult[object].fail("Invalid items format - must be a list")

            if not callable(processor_func):
                return FlextResult[object].fail("Processor function must be callable")

            # Use flext-core processing directly
            processed_items = []
            for item in items:
                try:
                    processed_item = processor_func(item)
                    processed_items.append(processed_item)
                except Exception as e:
                    return FlextResult[object].fail(f"Item processing failed: {e}")

            return FlextResult[object].ok(processed_items)

        except Exception as e:
            return FlextResult[object].fail(f"Batch processing failed: {e}")

    @staticmethod
    def safe_json_stringify_flext_result(data: object) -> FlextResult[str]:
        """Convert data to JSON string with FlextResult wrapper - avoid override conflict."""
        try:
            # Use flext-core utilities directly
            json_string = FlextUtilities.safe_json_stringify(data)
            return FlextResult[str].ok(json_string)
        except Exception as e:
            return FlextResult[str].fail(f"JSON stringify failed: {e}")

    # NOTE: safe_json_stringify removed to avoid override conflict with flext-core
    # Use safe_json_stringify_flext_result() directly for FlextResult wrapper



    # Validation Utilities (consolidated from Validation class)
    class _ValidationHelper:
        """Internal validation helper class."""

        @staticmethod
        def is_valid_uuid(uuid_string: str | None) -> bool:
            """Validate if a string is a valid UUID."""
            if uuid_string is None:
                return False
            try:
                UUID(uuid_string)
                return True
            except (ValueError, TypeError):
                return False

        @staticmethod
        def is_valid_email(email: str) -> bool:
            """Validate if a string is a valid email address."""
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return bool(re.match(pattern, email))

        @staticmethod
        def is_valid_url(url: str) -> bool:
            """Validate if a string is a valid URL."""
            pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            return bool(re.match(pattern, url))

    # Public validation interface
    @property
    def validation(self) -> _ValidationHelper:
        """Access validation utilities."""
        return self._ValidationHelper()

    # Backwards compatibility aliases for validation
    @staticmethod
    def is_valid_uuid(uuid_string: str | None) -> bool:
        """Validate if a string is a valid UUID."""
        return FlextCliUtilities._ValidationHelper.is_valid_uuid(uuid_string)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate if a string is a valid email address."""
        return FlextCliUtilities._ValidationHelper.is_valid_email(email)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate if a string is a valid URL."""
        return FlextCliUtilities._ValidationHelper.is_valid_url(url)


# Maintain backwards compatibility with global constants
STRICT_CONFIG_DICT = FlextCliUtilities.get_strict_config_dict()
BASE_CONFIG_DICT = FlextCliUtilities.get_base_config_dict()
SETTINGS_CONFIG_DICT = FlextCliUtilities.get_settings_config_dict()

# Maintain backwards compatibility with loose functions
generate_uuid = FlextCliUtilities.generate_uuid
utc_now = FlextCliUtilities.utc_now
empty_dict = FlextCliUtilities.empty_dict
empty_list = FlextCliUtilities.empty_list
empty_str_dict = FlextCliUtilities.empty_str_dict
empty_str_list = FlextCliUtilities.empty_str_list
home_path = FlextCliUtilities.home_path
token_file_path = FlextCliUtilities.token_file_path
refresh_token_file_path = FlextCliUtilities.refresh_token_file_path

# Maintain backwards compatibility with previous classes
Validation = FlextCliUtilities._ValidationHelper
FlextServiceMixin = FlextCliUtilities

__all__ = [
    "BASE_CONFIG_DICT",
    "SETTINGS_CONFIG_DICT",
    "STRICT_CONFIG_DICT",
    "FlextCliUtilities",
    "FlextServiceMixin",
    "Validation",
    "empty_dict",
    "empty_list",
    "empty_str_dict",
    "empty_str_list",
    "generate_uuid",
    "home_path",
    "refresh_token_file_path",
    "token_file_path",
    "utc_now",
]
