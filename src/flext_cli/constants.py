"""FLEXT CLI Constants - Zero Boilerplate Configuration Values.

Modern constants following foundation-refactored.md patterns.
Eliminates duplication across configuration modules.

Foundation Pattern Applied:
    # NEW: Self-documenting constants with type safety
    DEFAULT_API_URL: str = "http://localhost:8000"
    DEFAULT_TIMEOUT: int = 30

Architecture:
    - Type-safe constant definitions
    - Single source of truth for defaults
    - Integration with environment variables
    - Zero boilerplate constant management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# API defaults
DEFAULT_API_URL: str = "http://localhost:8000"
DEFAULT_TIMEOUT: int = 30
DEFAULT_RETRIES: int = 3

# Output defaults
DEFAULT_OUTPUT_FORMAT: str = "table"
DEFAULT_LOG_LEVEL: str = "INFO"

# CLI behavior
DEFAULT_PROFILE: str = "default"
DEFAULT_DEBUG: bool = False

# Environment configuration
ENV_PREFIX: str = "FLEXT_CLI_"
ENV_FILE: str = ".env"

# Validation limits
MAX_TIMEOUT: int = 300
MIN_TIMEOUT: int = 1
MAX_RETRIES: int = 10

# Entity limits
MAX_ENTITY_NAME_LENGTH: int = 255
MAX_ERROR_MESSAGE_LENGTH: int = 1000


class _CLIConstants:
    """CLI constants namespace for backward compatibility."""

    MAX_ENTITY_NAME_LENGTH: int = MAX_ENTITY_NAME_LENGTH
    MAX_ERROR_MESSAGE_LENGTH: int = MAX_ERROR_MESSAGE_LENGTH
    DEFAULT_TIMEOUT: int = DEFAULT_TIMEOUT


# Export constants for backward compatibility
CLI_CONSTANTS = _CLIConstants()
