"""FLEXT CLI Validator Service - Centralized validation logic.

Consolidates all validation functions from config.py, cli_params.py, models.py,
and cmd.py into a single focused validator service following SOLID principles.

Key validators consolidated:
- Field validators (output_format, profile, api_url, log_level, log_verbosity, environment)
- Model validators (configuration consistency, session consistency, debug consistency)
- Business rule validators (cross-field validation, domain logic)
- CLI parameter validators (enabled state, parameter enforcement)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.constants import FlextCliConstants


class FlextCliValidator:
    """Centralized validation service for all FLEXT CLI validation logic.

    Consolidates validators from config, cli_params, models, and cmd modules.
    Provides reusable, testable validation methods following SOLID principles.

    Methods are organized into categories:
    - Field validators: Single field value validation
    - Model validators: Cross-field validation
    - Business rule validators: Domain logic validation
    - CLI validators: CLI-specific parameter validation
    """

    # ===== Field Validators =====

    @staticmethod
    def validate_output_format(value: str) -> FlextResult[str]:
        """Validate output format is one of the allowed values."""
        if value not in FlextCliConstants.OUTPUT_FORMATS_LIST:
            valid_formats = ", ".join(FlextCliConstants.OUTPUT_FORMATS_LIST)
            return FlextResult[str].fail(
                FlextCliConstants.ValidationMessages.INVALID_OUTPUT_FORMAT_MUST_BE.format(
                    format=value, valid_formats=valid_formats
                )
            )
        return FlextResult[str].ok(value)

    @staticmethod
    def validate_profile(value: str) -> FlextResult[str]:
        """Validate profile name is not empty."""
        if not value or not value.strip():
            return FlextResult[str].fail(
                FlextCliConstants.ValidationMessages.PROFILE_NAME_CANNOT_BE_EMPTY
            )
        return FlextResult[str].ok(value.strip())

    @staticmethod
    def validate_api_url(value: str) -> FlextResult[str]:
        """Validate API URL format."""
        if not value.startswith(FlextCliConstants.ConfigValidation.URL_PROTOCOLS):
            return FlextResult[str].fail(
                FlextCliConstants.ValidationMessages.INVALID_API_URL_MUST_START.format(
                    url=value
                )
            )
        return FlextResult[str].ok(value)

    @staticmethod
    def validate_log_level(value: str) -> FlextResult[str]:
        """Validate log level is one of the allowed values."""
        valid_levels = set(FlextCliConstants.LOG_LEVELS_LIST)
        level_upper = value.upper()
        if level_upper not in valid_levels:
            return FlextResult[str].fail(
                FlextCliConstants.ValidationMessages.INVALID_LOG_LEVEL_MUST_BE.format(
                    level=value, valid_levels=", ".join(sorted(valid_levels))
                )
            )
        return FlextResult[str].ok(level_upper)

    @staticmethod
    def validate_log_verbosity(value: str) -> FlextResult[str]:
        """Validate log verbosity is one of the allowed values."""
        valid_verbosity = FlextCliConstants.ConfigValidation.LOG_VERBOSITY_VALUES
        verbosity_lower = value.lower()
        if verbosity_lower not in valid_verbosity:
            return FlextResult[str].fail(
                FlextCliConstants.ValidationMessages.INVALID_LOG_VERBOSITY_MUST_BE.format(
                    verbosity=value,
                    valid_verbosity=", ".join(sorted(valid_verbosity)),
                )
            )
        return FlextResult[str].ok(verbosity_lower)

    @staticmethod
    def validate_environment(value: str) -> FlextResult[str]:
        """Validate environment is one of the allowed values."""
        valid_environments = FlextCliConstants.ConfigValidation.ENVIRONMENT_VALUES
        env_lower = value.lower()
        if env_lower not in valid_environments:
            msg = f"Invalid environment '{value}'. Must be one of: {', '.join(sorted(valid_environments))}"
            return FlextResult[str].fail(msg)
        return FlextResult[str].ok(env_lower)

    # ===== CLI Parameter Validators =====

    @staticmethod
    def validate_log_level_for_cli(value: str) -> FlextResult[str]:
        """Validate log level from CLI parameters."""
        log_level_upper = value.upper()
        if log_level_upper not in FlextCliConstants.LOG_LEVELS_LIST:
            valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
            return FlextResult[str].fail(
                FlextCliConstants.CliParamsErrorMessages.INVALID_LOG_LEVEL.format(
                    log_level=value, valid=valid
                )
            )
        return FlextResult[str].ok(log_level_upper)

    @staticmethod
    def validate_output_format_for_cli(value: str) -> FlextResult[str]:
        """Validate output format from CLI parameters."""
        output_format_lower = value.lower()
        if (
            output_format_lower
            not in FlextCliConstants.CliParamsDefaults.VALID_OUTPUT_FORMATS
        ):
            valid = ", ".join(FlextCliConstants.CliParamsDefaults.VALID_OUTPUT_FORMATS)
            return FlextResult[str].fail(
                FlextCliConstants.CliParamsErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    output_format=value, valid=valid
                )
            )
        return FlextResult[str].ok(output_format_lower)


__all__ = [
    "FlextCliValidator",
]
