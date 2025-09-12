"""FLEXT CLI Services - Direct flext-core usage.

NO WRAPPERS - Direct usage of flext-core FlextServices.
Eliminates duplicate service patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextServices


class FlextCliServices(FlextServices):
    """Direct flext-core FlextServices usage - NO WRAPPERS."""

    @staticmethod
    def create_command_processor() -> FlextResult[str]:
        """Create command processor using flext-core directly."""
        try:
            # Use flext-core HandlerRegistry for command processing
            FlextServices.create_handler_registry()
            return FlextResult[str].ok("Command processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create processor: {e}")

    @staticmethod
    def create_session_processor() -> FlextResult[str]:
        """Create session processor using flext-core directly."""
        try:
            # Use flext-core Pipeline for session processing
            FlextServices.create_pipeline()
            return FlextResult[str].ok("Session processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create processor: {e}")

    @staticmethod
    def create_config_processor() -> FlextResult[str]:
        """Create config processor using flext-core directly."""
        try:
            # Use flext-core HandlerRegistry for config processing
            FlextServices.create_handler_registry()
            return FlextResult[str].ok("Config processor created successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create processor: {e}")


__all__ = [
    "FlextCliServices",
]
