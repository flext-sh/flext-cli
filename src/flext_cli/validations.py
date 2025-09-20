"""FLEXT CLI Centralized Validations - Eliminate internal duplication.

Centralized validation logic for CLI operations to eliminate duplication
across multiple modules. Provides single source of truth for all CLI validations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.constants import FlextCliConstants
from flext_core import FlextResult


class FlextCliValidations:
    """Centralized CLI validation using direct validation - SOURCE OF TRUTH for all CLI validations."""

    @staticmethod
    def validate_output_format(format_type: str) -> FlextResult[str]:
        """Centralized output format validation - ELIMINATE ALL DUPLICATION.

        Validates format against canonical FlextCliConstants.VALID_OUTPUT_FORMATS.
        This is the single source of truth for output format validation.

        Args:
            format_type: The format type to validate

        Returns:
            FlextResult[str]: Success with normalized format or failure with error

        """
        if not format_type or not isinstance(format_type, str):
            return FlextResult[str].fail("Format type must be a non-empty string")

        normalized_format = format_type.strip().lower()

        # Use canonical constant as single source of truth
        if normalized_format not in FlextCliConstants.VALID_OUTPUT_FORMATS:
            valid_formats = ", ".join(FlextCliConstants.VALID_OUTPUT_FORMATS)
            return FlextResult[str].fail(
                f"Invalid output format '{format_type}'. Must be one of: {valid_formats}"
            )

        return FlextResult[str].ok(normalized_format)

    @staticmethod
    def validate_command_line(command_line: object) -> FlextResult[str]:
        """Centralized command line validation - ELIMINATE ALL DUPLICATION.

        Args:
            command_line: The command line to validate

        Returns:
            FlextResult[str]: Success with cleaned command or failure with error

        """
        if not isinstance(command_line, str) or not command_line.strip():
            return FlextResult[str].fail("Command line must be a non-empty string")

        return FlextResult[str].ok(command_line.strip())

    @staticmethod
    def validate_profile_name(profile: str) -> FlextResult[str]:
        """Centralized profile name validation - ELIMINATE ALL DUPLICATION.

        Args:
            profile: The profile name to validate

        Returns:
            FlextResult[str]: Success with normalized profile or failure with error

        """
        if not profile or not isinstance(profile, str):
            return FlextResult[str].fail("Profile name must be a non-empty string")

        normalized_profile = profile.strip()

        # Basic profile name validation (alphanumeric, dash, underscore)
        if not normalized_profile.replace("-", "").replace("_", "").isalnum():
            return FlextResult[str].fail(
                "Profile name must contain only alphanumeric characters, hyphens, and underscores"
            )

        return FlextResult[str].ok(normalized_profile)

    @staticmethod
    def validate_config_key(key: str) -> FlextResult[str]:
        """Centralized configuration key validation - ELIMINATE ALL DUPLICATION.

        Args:
            key: The configuration key to validate

        Returns:
            FlextResult[str]: Success with normalized key or failure with error

        """
        if not key or not isinstance(key, str):
            return FlextResult[str].fail("Configuration key must be a non-empty string")

        normalized_key = key.strip()

        # Basic key validation (alphanumeric, dot, dash, underscore)
        if not all(c.isalnum() or c in "._-" for c in normalized_key):
            return FlextResult[str].fail(
                "Configuration key must contain only alphanumeric characters, dots, hyphens, and underscores"
            )

        return FlextResult[str].ok(normalized_key)


__all__ = [
    "FlextCliValidations",
]
