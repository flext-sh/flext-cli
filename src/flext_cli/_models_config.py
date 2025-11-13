"""Config-related models - Separate module to avoid circular imports.

This module contains models used by config.py but defined separately
to break the circular dependency: config.py → models.py → config.py

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from pydantic import BaseModel, ConfigDict, Field


class ConfigServiceExecutionResult(BaseModel):
    """Config service execution result - replaces dict in execute_as_service().

    Pydantic 2 Features:
        - Type-safe model instead of dict[str, JsonValue]
        - Validates service operational status
        - Embeds complete config as nested dict

    Railway Pattern:
        Used internally as type-safe model, serialized to dict for API compatibility

    """

    model_config = ConfigDict(frozen=False, validate_assignment=True)

    status: str = Field(description="Service status")
    service: str = Field(description="Service name")
    timestamp: str = Field(default="", description="Execution timestamp (ISO)")
    version: str = Field(description="Service version")
    config: dict[str, object] = Field(
        default_factory=dict, description="Complete configuration dump"
    )


__all__ = ["ConfigServiceExecutionResult"]
