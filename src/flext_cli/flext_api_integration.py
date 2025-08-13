"""FLEXT-API Integration Module - Proper integration with flext-api library.

This module provides the correct integration between flext-cli and flext-api,
eliminating code duplication and ensuring consistent HTTP client patterns
across the FLEXT ecosystem.

Integration Features:
    - Uses flext-api's FlextApiClient with plugin support
    - Leverages flext-core patterns (FlextResult, error handling)
    - Provides CLI-specific convenience methods
    - Maintains configuration consistency with CLI settings
    - Supports both FlexCore (port 8080) and FLEXT Service (port 8081)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Self

from flext_api import (
    FlextApiClient,
    create_flext_api,
)
from flext_core import FlextResult, get_logger

from flext_cli.config import get_config as get_cli_config

logger = get_logger(__name__)

# HTTP status constants
HTTP_OK = 200


class FlextCLIApiClient:
    """CLI-specific wrapper around flext-api client.

    Provides CLI-specific convenience methods while leveraging the full
    power of flext-api's HTTP client infrastructure with plugin support.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize CLI API client with flext-api integration.

        Args:
            base_url: API base URL (defaults from CLI config)
            token: Authentication token
            timeout: Request timeout in seconds

        """
        self.config = get_cli_config()
        self.base_url = base_url or self._get_default_base_url()
        self.token = token
        self.timeout = timeout

        # Type annotation for MyPy
        self._api_client: FlextApiClient | None = None

        # Initialize flext-api client if available
        self._init_flext_api_client()

    def _get_default_base_url(self) -> str:
        """Get default base URL from CLI configuration."""
        # Try CLI config first, then fall back to defaults
        if hasattr(self.config, "api") and hasattr(self.config.api, "url"):
            return self.config.api.url

        # Default to FLEXT Service (port 8081) - main data platform
        return "http://localhost:8081"

    def _init_flext_api_client(self) -> None:
        """Initialize flext-api client with proper configuration."""
        try:
            # Create flext-api instance with CLI-specific configuration
            self._flext_api = create_flext_api()

            # Create HTTP client with flext-api patterns
            client_config = {
                "base_url": self.base_url,
                "timeout": self.timeout,
            }

            # Add authentication if available
            if self.token:
                client_config["headers"] = {
                    "Authorization": f"Bearer {self.token}",
                }

            client_result = self._flext_api.flext_api_create_client(client_config)

            if client_result.success:
                self._api_client = client_result.data
                logger.info(
                    "flext-api client initialized",
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
            else:
                logger.error(
                    "Failed to create flext-api client",
                    error=client_result.error,
                )
                self._api_client = None

        except Exception:
            logger.exception("Error initializing flext-api client")
            self._api_client = None

    def is_available(self) -> bool:
        """Check if flext-api integration is available and working."""
        return self._api_client is not None

    def get_client(self) -> FlextApiClient | None:
        """Get the underlying flext-api client for advanced operations."""
        return self._api_client

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        if self._api_client is None:
            error_msg = "API client not initialized"
            raise RuntimeError(error_msg)
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    # CLI-specific convenience methods using flext-api patterns

    async def test_connection(self) -> FlextResult[bool]:
        """Test connection to FLEXT services using flext-api patterns."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            # Use flext-api client to test connection
            if self._api_client is None:
                return FlextResult.fail("API client not initialized")

            # Get response from API client - handle FlextResult
            response_result = await self._api_client.get("/health")
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(f"Connection failed: {response_result.error}")

            response = response_result.data
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                logger.info("Connection test successful", base_url=self.base_url)
                return FlextResult.ok(data=True)
            return FlextResult.fail(f"Health check failed: {status_code}")

        except Exception as e:
            logger.exception("Connection test failed")
            return FlextResult.fail(f"Connection test failed: {e}")

    async def get_system_status(self) -> FlextResult[dict[str, object]]:
        """Get system status using flext-api patterns."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult.fail("API client not initialized")

            # Get response from API client - handle FlextResult
            response_result = await self._api_client.get("/api/v1/system/status")
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(
                    f"Status request failed: {response_result.error}",
                )

            response = response_result.data
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                # Safe JSON access with getattr
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult.ok(json_data)
            return FlextResult.fail(f"Status request failed: {status_code}")

        except Exception as e:
            logger.exception("Failed to get system status")
            return FlextResult.fail(f"System status failed: {e}")

    async def list_services(self) -> FlextResult[list[dict[str, object]]]:
        """List available FLEXT services."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            # Try both FlexCore (8080) and FLEXT Service (8081)
            services = []

            # FlexCore service check
            flexcore_result = await self._check_service(
                "FlexCore",
                "http://localhost:8080",
            )
            if flexcore_result.success and flexcore_result.data:
                services.append(flexcore_result.data)

            # FLEXT Service check
            flext_result = await self._check_service(
                "FLEXT Service",
                "http://localhost:8081",
            )
            if flext_result.success and flext_result.data:
                services.append(flext_result.data)

            return FlextResult.ok(services)

        except Exception as e:
            logger.exception("Failed to list services")
            return FlextResult.fail(f"Service listing failed: {e}")

    async def _check_service(
        self,
        name: str,
        url: str,
    ) -> FlextResult[dict[str, object]]:
        """Check individual service status."""
        try:
            # Create temporary client for service check
            service_config = {"base_url": url, "timeout": 5.0}
            client_result = self._flext_api.flext_api_create_client(service_config)

            if not client_result.success:
                return FlextResult.fail(f"{name} client creation failed")

            client = client_result.data
            if client is None:
                return FlextResult.fail(f"{name} client is None")

            # Get response from API client - handle FlextResult
            response_result = await client.get("/health")
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(
                    f"{name} health check failed: {response_result.error}",
                )

            response = response_result.data
            # Handle response safely
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                # Get elapsed time safely
                elapsed = getattr(response, "elapsed", None)
                response_time = elapsed.total_seconds() if elapsed else 0.0

                return FlextResult.ok(
                    {
                        "name": name,
                        "url": url,
                        "status": "healthy",
                        "response_time": response_time,
                    },
                )
            return FlextResult.fail(f"{name} unhealthy: {status_code}")

        except (ConnectionError, TimeoutError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"{name} check failed: {e}")

    async def login(
        self,
        username: str,
        password: str,
    ) -> FlextResult[dict[str, object]]:
        """Login with username and password."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult.fail("API client not initialized")

            # Post credentials to login endpoint
            login_data = json.dumps(
                {
                    "username": username,
                    "password": password,
                },
            )
            response_result = await self._api_client.post(
                "/auth/login",
                data=login_data,
            )
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(f"Login failed: {response_result.error}")

            response = response_result.data
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult.ok(json_data)
            return FlextResult.fail(f"Login failed: {status_code}")

        except Exception as e:
            logger.exception("Login failed")
            return FlextResult.fail(f"Login failed: {e}")

    async def logout(self) -> FlextResult[None]:
        """Logout from the API."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult.fail("API client not initialized")

            # Post to logout endpoint
            response_result = await self._api_client.post("/auth/logout")
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(f"Logout failed: {response_result.error}")

            response = response_result.data
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                return FlextResult.ok(None)
            return FlextResult.fail(f"Logout failed: {status_code}")

        except Exception as e:
            logger.exception("Logout failed")
            return FlextResult.fail(f"Logout failed: {e}")

    async def get_current_user(self) -> FlextResult[dict[str, object]]:
        """Get current user information."""
        if not self.is_available():
            return FlextResult.fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult.fail("API client not initialized")

            # Get current user from API
            response_result = await self._api_client.get("/auth/me")
            if not response_result.success or response_result.data is None:
                return FlextResult.fail(f"Get user failed: {response_result.error}")

            response = response_result.data
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult.ok(json_data)
            return FlextResult.fail(f"Get user failed: {status_code}")

        except Exception as e:
            logger.exception("Get user failed")
            return FlextResult.fail(f"Get user failed: {e}")

    async def close(self) -> None:
        """Close the API client."""
        if self._api_client and hasattr(self._api_client, "stop"):
            try:
                await self._api_client.stop()
                logger.info("flext-api client closed")
            except (ConnectionError, OSError, RuntimeError, AttributeError) as e:
                logger.warning("Error closing API client: %s", e)


# Factory functions for CLI integration


def create_cli_api_client(
    base_url: str | None = None,
    token: str | None = None,
    timeout: float = 30.0,
) -> FlextCLIApiClient:
    """Create CLI API client with flext-api integration.

    Args:
        base_url: API base URL
        token: Authentication token
        timeout: Request timeout

    Returns:
        CLI API client instance

    """
    return FlextCLIApiClient(base_url=base_url, token=token, timeout=timeout)


def get_default_cli_client() -> FlextCLIApiClient:
    """Get default CLI API client with configuration from CLI settings."""
    config = get_cli_config()

    # Extract configuration
    base_url = None
    token = None

    if hasattr(config, "api"):
        base_url = getattr(config.api, "url", None)
        token = getattr(config.api, "token", None)

    return create_cli_api_client(base_url=base_url, token=token)


# Availability flag expected by tests
FLEXT_API_AVAILABLE = True

# Export the integration API
__all__ = [
    "FLEXT_API_AVAILABLE",
    "FlextCLIApiClient",
    "create_cli_api_client",
    "get_default_cli_client",
]
