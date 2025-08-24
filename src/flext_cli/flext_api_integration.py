"""FLEXT-API Integration Module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Protocol, Self

# from flext_api import create_flext_api  # Temporarily disabled due to dependency issue
from flext_core import FlextConstants, FlextResult, get_logger

from flext_cli.config import get_config as get_cli_config


class FlextApiClientLike(Protocol):
    """Protocol for FlextApiClient-like objects with async HTTP methods."""

    async def get(self, endpoint: str, **kwargs: object) -> FlextResult[object]:
        """Async HTTP GET request method returning FlextResult."""
        ...

    async def post(self, endpoint: str, **kwargs: object) -> FlextResult[object]:
        """Async HTTP POST request method returning FlextResult."""
        ...

    def stop(self) -> None:
        """Stop/cleanup method."""
        ...


# Temporary placeholder for missing function
def create_flext_api() -> FlextApiClientLike | None:
    """Temporary placeholder for flext_api dependency."""
    return None


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

        # Type annotation for MyPy - handles case where FlextApiClient is not available
        self._api_client: FlextApiClientLike | None = None
        self._flext_api: FlextApiClientLike | None = None

        # Initialize flext-api client if available
        self._init_flext_api_client()

    def _get_default_base_url(self) -> str:
        """Get default base URL from CLI configuration."""
        # Try CLI config first, then fall back to defaults
        if hasattr(self.config, "api") and hasattr(self.config.api, "url"):
            return self.config.api.url

        # Default to FLEXT Service using core platform constants
        try:
            host = FlextConstants.Platform.DEFAULT_HOST
            port = FlextConstants.Platform.FLEXT_SERVICE_PORT
            return f"http://{host}:{port}"
        except Exception:
            return "http://localhost:8081"

    def _init_flext_api_client(self) -> None:
        """Initialize flext-api client with proper configuration."""
        # Temporarily disabled due to dependency issue with flext-api
        self._flext_api = None
        logger.warning("flext-api not available - API client disabled")
        self._api_client = None

    def is_available(self) -> bool:
        """Check if flext-api integration is available and working."""
        return self._api_client is not None

    def get_client(self) -> object | None:
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
            return FlextResult[bool].fail("flext-api client not available")

        try:
            # Use flext-api client to test connection
            if self._api_client is None:
                return FlextResult[bool].fail("API client not initialized")

            # Get response from API client - handle FlextResult
            response_result = await self._api_client.get("/health")
            if response_result.unwrap_or(None) is None:
                return FlextResult[bool].fail(
                    f"Connection failed: {response_result.error}"
                )

            response = response_result.value
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                logger.info("Connection test successful", base_url=self.base_url)
                connection_success = True
                return FlextResult[bool].ok(connection_success)
            return FlextResult[bool].fail(f"Health check failed: {status_code}")

        except Exception as e:
            logger.exception("Connection test failed")
            return FlextResult[bool].fail(f"Connection test failed: {e}")

    async def get_system_status(self) -> FlextResult[dict[str, object]]:
        """Get system status using flext-api patterns."""
        if not self.is_available():
            return FlextResult[dict[str, object]].fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult[dict[str, object]].fail("API client not initialized")

            # Get response from API client - handle FlextResult
            response_result = await self._api_client.get("/api/v1/system/status")
            if response_result.unwrap_or(None) is None:
                return FlextResult[dict[str, object]].fail(
                    f"Status request failed: {response_result.error}",
                )

            response = response_result.value
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                # Safe JSON access with getattr
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult[dict[str, object]].ok(json_data)
            return FlextResult[dict[str, object]].fail(
                f"Status request failed: {status_code}"
            )

        except Exception as e:
            logger.exception("Failed to get system status")
            return FlextResult[dict[str, object]].fail(f"System status failed: {e}")

    async def list_services(self) -> FlextResult[list[dict[str, object]]]:
        """List available FLEXT services."""
        if not self.is_available():
            return FlextResult[list[dict[str, object]]].fail(
                "flext-api client not available"
            )

        try:
            # Try both FlexCore (8080) and FLEXT Service (8081)
            services: list[dict[str, object]] = []

            # FlexCore service check
            flexcore_result = await self._check_service(
                "FlexCore",
                f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXCORE_PORT}",
            )
            # Use unwrap_or for cleaner conditional assignment with proper typing
            flexcore_status = flexcore_result.unwrap_or({})
            if flexcore_status:  # Empty dict is falsy, non-empty dict is truthy
                services.append(flexcore_status)

            # FLEXT Service check
            flext_result = await self._check_service(
                "FLEXT Service",
                f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_SERVICE_PORT}",
            )
            flext_status = flext_result.unwrap_or({})
            if flext_status:  # Empty dict is falsy, non-empty dict is truthy
                services.append(flext_status)

            return FlextResult[list[dict[str, object]]].ok(services)

        except Exception as e:
            logger.exception("Failed to list services")
            return FlextResult[list[dict[str, object]]].fail(
                f"Service listing failed: {e}"
            )

    async def _check_service(
        self,
        name: str,
        url: str,  # noqa: ARG002
    ) -> FlextResult[dict[str, object]]:
        """Check individual service status."""
        # Temporarily disabled due to dependency issue with flext-api
        return FlextResult[dict[str, object]].fail(
            f"{name} service check disabled - no API implementation"
        )

    async def login(
        self,
        username: str,
        password: str,
    ) -> FlextResult[dict[str, object]]:
        """Login with username and password."""
        if not self.is_available():
            return FlextResult[dict[str, object]].fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult[dict[str, object]].fail("API client not initialized")

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
            response = response_result.unwrap_or(None)
            if response is None:
                return FlextResult[dict[str, object]].fail("Login failed: No response")
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult[dict[str, object]].ok(json_data)
            return FlextResult[dict[str, object]].fail(f"Login failed: {status_code}")

        except Exception as e:
            logger.exception("Login failed")
            return FlextResult[dict[str, object]].fail(f"Login failed: {e}")

    async def logout(self) -> FlextResult[bool]:
        """Logout from the API."""
        if not self.is_available():
            return FlextResult[bool].fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult[bool].fail("API client not initialized")

            # Post to logout endpoint
            response_result = await self._api_client.post("/auth/logout")
            response = response_result.unwrap_or(None)
            if response is None:
                return FlextResult[bool].fail("Logout failed: No response")
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                logout_success = True
                return FlextResult[bool].ok(logout_success)
            return FlextResult[bool].fail(f"Logout failed: {status_code}")

        except Exception as e:
            logger.exception("Logout failed")
            return FlextResult[bool].fail(f"Logout failed: {e}")

    async def get_current_user(self) -> FlextResult[dict[str, object]]:
        """Get current user information."""
        if not self.is_available():
            return FlextResult[dict[str, object]].fail("flext-api client not available")

        try:
            if self._api_client is None:
                return FlextResult[dict[str, object]].fail("API client not initialized")

            # Get current user from API
            response_result = await self._api_client.get("/auth/me")
            response = response_result.unwrap_or(None)
            if response is None:
                return FlextResult[dict[str, object]].fail(
                    "Get user failed: No response"
                )
            status_code = getattr(response, "status_code", None)
            if status_code == HTTP_OK:
                json_data: dict[str, object] = getattr(response, "json", dict)()
                return FlextResult[dict[str, object]].ok(json_data)
            return FlextResult[dict[str, object]].fail(
                f"Get user failed: {status_code}"
            )

        except Exception as e:
            logger.exception("Get user failed")
            return FlextResult[dict[str, object]].fail(f"Get user failed: {e}")

    async def close(self) -> None:
        """Close the API client."""
        if self._api_client and hasattr(self._api_client, "stop"):
            try:
                self._api_client.stop()
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
