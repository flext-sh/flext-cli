"""FLEXT CLI Utilities - Unified class following FLEXT architecture patterns.

Single FlextCliUtilities class consolidating all utility functions and validation helpers.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_core import FlextContainer, FlextResult


class FlextCliUtilities(BaseModel):
    """Unified utility service for CLI operations using modern Pydantic v2.

    Provides centralized utilities without duplicating Pydantic v2 functionality.
    Uses FlextModels and FlextConfig for all validation needs.
    """

    def __init__(self) -> None:
        """Initialize FlextCliUtilities service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = logging.getLogger(__name__)

    def execute(self) -> FlextResult[None]:
        """Execute the main domain service operation."""
        return FlextResult[None].ok(None)

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance."""
        return self._logger

    @property
    def container(self) -> FlextContainer:
        """Get container instance."""
        return self._container

    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID string."""
        return str(uuid4())

    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime."""
        return datetime.now(UTC)

    @staticmethod
    def empty_dict() -> dict[str, object]:
        """Get empty dict."""
        return {}

    @staticmethod
    def empty_list() -> list[object]:
        """Get empty list."""
        return []

    @staticmethod
    def empty_str_dict() -> dict[str, str]:
        """Get empty string dict."""
        return {}

    @staticmethod
    def get_base_config_dict() -> ConfigDict:
        """Get base Pydantic configuration for CLI models."""
        return ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
        )

    @staticmethod
    def get_strict_config_dict() -> ConfigDict:
        """Get strict Pydantic configuration for CLI models."""
        return ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=False,
            str_strip_whitespace=True,
        )

    @staticmethod
    def empty_str_list() -> list[str]:
        """Get empty string list."""
        return []

    @staticmethod
    def home_path() -> Path:
        """Get home directory path."""
        return Path.home()

    @staticmethod
    def token_file_path() -> Path:
        """Get authentication token file path."""
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.TOKEN_FILE_NAME
        )

    @staticmethod
    def refresh_token_file_path() -> Path:
        """Get refresh token file path."""
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
        )

    @staticmethod
    def get_settings_config_dict() -> SettingsConfigDict:
        """Get Pydantic configuration for CLI settings models."""
        return SettingsConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            env_prefix="FLEXT_CLI_",
            case_sensitive=False,
        )

    @staticmethod
    def validate_with_pydantic_model(
        data: dict[str, object] | object, model_class: type[BaseModel]
    ) -> FlextResult[BaseModel]:
        """Validate data using Pydantic v2 model directly.

        Args:
            data: Data to validate (dict or object convertible to dict)
            model_class: Pydantic v2 model class to validate against

        Returns:
            FlextResult containing validated model instance or error

        """
        try:
            # Convert data to dict if needed
            if isinstance(data, dict):
                validated_data = data
            elif hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                validated_data = getattr(data, "model_dump")()
            elif hasattr(data, "__dict__"):
                validated_data = data.__dict__
            else:
                # Try to convert other types to dict format
                validated_data = {"value": data}

            validated_model = model_class.model_validate(validated_data)
            return FlextResult[BaseModel].ok(validated_model)
        except ValidationError as e:
            error_details = "; ".join(
                [
                    f"{err['loc'][0] if err['loc'] else 'field'}: {err['msg']}"
                    for err in e.errors()
                ]
            )
            return FlextResult[BaseModel].fail(f"Validation failed: {error_details}")
        except Exception as e:
            return FlextResult[BaseModel].fail(f"Unexpected validation error: {e}")

    @staticmethod
    def validate_data(data: object, validator: object) -> FlextResult[bool]:
        """Validate data using provided validator function or dict.

        Backward compatibility method for legacy validation patterns.
        """
        try:
            if data is None or validator is None:
                return FlextResult[bool].fail("Data and validator cannot be None")

            if callable(validator):
                result = validator(data)
                return FlextResult[bool].ok(bool(result))
            if isinstance(validator, dict):
                # Simple dict-based validation
                if isinstance(data, dict):
                    for key, expected_type in validator.items():
                        if key not in data:
                            return FlextResult[bool].fail(
                                f"Missing required field: {key}"
                            )
                        if not isinstance(data[key], expected_type):
                            return FlextResult[bool].fail(
                                f"Invalid type for {key}: expected {expected_type.__name__}"
                            )
                    return FlextResult[bool].ok(data=True)
                return FlextResult[bool].fail(
                    "Data must be dict for dict-based validation"
                )
            return FlextResult[bool].fail("Validator must be callable or dict")
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    @staticmethod
    def batch_process_items(
        items: Sequence[object], processor: Callable[[object], object]
    ) -> FlextResult[list[object]]:
        """Process items in batch with error handling."""
        try:
            if not isinstance(items, (list, tuple)):
                return FlextResult[list[object]].fail(
                    "Invalid items format: must be list or tuple"
                )

            results = []
            for item in items:
                try:
                    result = processor(item)
                    # Handle both FlextResult and raw value returns
                    if hasattr(result, "is_failure") and hasattr(result, "unwrap"):
                        if getattr(result, "is_failure"):
                            error_msg = getattr(result, "error", "Unknown error")
                            return FlextResult[list[object]].fail(
                                f"Item processing failed: {error_msg}"
                            )
                        results.append(getattr(result, "unwrap")())
                    else:
                        results.append(result)
                except Exception as e:
                    return FlextResult[list[object]].fail(
                        f"Item processing failed: {e}"
                    )
            return FlextResult[list[object]].ok(results)
        except Exception as e:
            return FlextResult[list[object]].fail(f"Batch processing failed: {e}")

    @staticmethod
    def safe_json_stringify(data: object) -> str:
        """Safely stringify data to JSON."""
        try:
            return json.dumps(data, default=str, indent=2)
        except Exception:
            return str(data)

    @staticmethod
    def json_stringify_with_result(data: object) -> FlextResult[str]:
        """Stringify data to JSON with result handling."""
        try:
            return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            return FlextResult[str].fail(f"JSON serialization failed: {e}")

    @staticmethod
    def safe_json_stringify_flext_result(result: FlextResult[object]) -> str:
        """Safely stringify FlextResult to JSON."""
        return FlextCliUtilities.safe_json_stringify(
            result.unwrap() if result.is_success else {"error": result.error}
        )


__all__ = ["FlextCliUtilities"]
