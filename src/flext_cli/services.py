"""FLEXT CLI Services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextProcessing, FlextResult


class FlextCliServices:
    """CLI Services using flext-core directly - ZERO duplication.

    Uses FlextProcessing (aliased as FlextServices) directly for all service operations.
    NO custom implementations, NO wrappers, NO duplications.
    """

    # Use flext-core processing directly
    registry = FlextProcessing.HandlerRegistry()
    orchestrator = FlextProcessing.Pipeline()

    # Use flext-core management utilities
    metrics = FlextProcessing.Management.HandlerRegistry()

    @staticmethod
    def create_command_processor() -> FlextResult[str]:
        """Create command processor using flext-core processing directly."""
        try:
            # Use flext-core processing directly
            FlextProcessing.create_handler_registry()
            return FlextResult[str].ok("Command processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Command processor creation failed: {e}")

    @staticmethod
    def create_session_processor() -> FlextResult[str]:
        """Create session processor using flext-core processing directly."""
        try:
            # Use flext-core processing directly
            FlextProcessing.create_pipeline()
            return FlextResult[str].ok("Session processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Session processor creation failed: {e}")

    @staticmethod
    def create_config_processor() -> FlextResult[str]:
        """Create config processor using flext-core processing directly."""
        try:
            # Use flext-core processing directly
            FlextProcessing.create_handler_registry()
            return FlextResult[str].ok("Config processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Config processor creation failed: {e}")


__all__ = ["FlextCliServices"]
