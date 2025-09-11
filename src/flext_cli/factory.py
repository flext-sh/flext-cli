"""FLEXT CLI Factory - Direct flext-core usage.

NO WRAPPERS - Direct usage of flext-core FlextContainer for dependency injection.
Eliminates duplicate factory patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.client import FlextApiClient


class FlextCliFactory:
    """Simple factory using flext-core FlextContainer directly - NO WRAPPERS."""

    @staticmethod
    def create_auth_service() -> FlextResult[FlextCliAuth]:
        """Create auth service using flext-core container."""
        try:
            auth_service = FlextCliAuth()
            return FlextResult[FlextCliAuth].ok(auth_service)
        except Exception as e:
            return FlextResult[FlextCliAuth].fail(f"Failed to create auth service: {e}")

    @staticmethod
    def create_api_client() -> FlextResult[FlextApiClient]:
        """Create API client using flext-core container."""
        try:
            client = FlextApiClient()
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            return FlextResult[FlextApiClient].fail(f"Failed to create API client: {e}")

    @staticmethod
    def create_default_auth_service() -> FlextResult[FlextCliAuth]:
        """Create default auth service - simplified."""
        return FlextCliFactory.create_auth_service()
