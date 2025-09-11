"""FLEXT CLI Factory - Dependency injection factory for CLI components.

Provides factory methods to create CLI components with proper dependency injection,
eliminating circular dependencies and enforcing SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig
from flext_cli.protocols import AuthenticationClient


class FlextCliFactory:
    """Factory for creating CLI components with proper dependency injection."""

    @staticmethod
    def create_auth_service(
        *, 
        config: FlextCliConfig | None = None,
        auth_client: AuthenticationClient | None = None
    ) -> FlextResult[FlextCliAuth]:
        """Create authentication service with injected dependencies."""
        try:
            # Create auth client if not provided
            if auth_client is None:
                auth_client = FlextApiClient()
            
            # Create auth service with injected client
            auth_service = FlextCliAuth(
                config=config,
                auth_client=auth_client
            )
            
            return FlextResult[FlextCliAuth].ok(auth_service)
        except Exception as e:
            return FlextResult[FlextCliAuth].fail(f"Failed to create auth service: {e}")

    @staticmethod
    def create_api_client(
        *,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float | None = None,
        verify_ssl: bool = True
    ) -> FlextResult[FlextApiClient]:
        """Create API client with configuration."""
        try:
            client = FlextApiClient(
                base_url=base_url,
                token=token,
                timeout=timeout,
                verify_ssl=verify_ssl
            )
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            return FlextResult[FlextApiClient].fail(f"Failed to create API client: {e}")

    @staticmethod
    def create_default_auth_service() -> FlextResult[FlextCliAuth]:
        """Create default authentication service with all dependencies."""
        try:
            # Create config
            config = FlextCliConfig()
            
            # Create API client
            client_result = FlextCliFactory.create_api_client()
            if client_result.is_failure:
                return FlextResult[FlextCliAuth].fail(f"Failed to create API client: {client_result.error}")
            
            # Create auth service with injected client
            auth_result = FlextCliFactory.create_auth_service(
                config=config,
                auth_client=client_result.value
            )
            
            return auth_result
        except Exception as e:
            return FlextResult[FlextCliAuth].fail(f"Failed to create default auth service: {e}")