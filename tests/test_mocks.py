"""Mock implementations for testing flext-cli without external dependencies.

This module provides comprehensive mock implementations that eliminate the need
for real HTTP calls during testing, following SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self
from unittest.mock import MagicMock

from flext_core import FlextResult
from flext_core.constants import FlextConstants


class MockFlextApiClient:
    """Complete mock implementation of FlextCLIApiClient for testing."""

    def __init__(
      self,
      base_url: str | None = None,
      token: str | None = None,
      timeout: float = 30.0,
    ) -> None:
      """Initialize mock API client."""
      if base_url:
          self.base_url = base_url
      else:
          self.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
      self.token = token
      self.timeout = timeout
      self._available = True

    def is_available(self) -> bool:
      """Check if API integration is available."""
      return self._available

    def get_client(self) -> object:
      """Get mock API client."""
      return MagicMock()

    async def __aenter__(self) -> Self:
      """Async context manager entry."""
      return self

    async def __aexit__(
      self,
      exc_type: object,
      exc_val: object,
      exc_tb: object,
    ) -> None:
      """Async context manager exit."""

    async def test_connection(self) -> FlextResult[bool]:
      """Mock connection test - always succeeds."""
      return FlextResult.ok(True)

    async def get_system_status(self) -> FlextResult[dict[str, object]]:
      """Mock system status - returns healthy status."""
      return FlextResult.ok(
          {"version": "1.0.0", "status": "healthy", "uptime": "24h"},
      )

    async def list_services(self) -> FlextResult[list[dict[str, object]]]:
      """Mock service listing."""
      return FlextResult.ok(
          [
              {
                  "name": "FlexCore",
                  "url": f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXCORE_PORT}",
                  "status": "healthy",
                  "response_time": 0.05,
              },
              {
                  "name": "FLEXT Service",
                  "url": f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXSERVICE_PORT}",
                  "status": "healthy",
                  "response_time": 0.03,
              },
          ],
      )

    async def login(
      self,
      username: str,  # noqa: ARG002
      password: str,  # noqa: ARG002
    ) -> FlextResult[dict[str, object]]:
      """Mock login - always succeeds with valid token."""
      return FlextResult.ok(
          {
              "access_token": "mock-token-12345",
              "token_type": "bearer",
              "expires_in": 3600,
          },
      )

    async def logout(self) -> FlextResult[None]:
      """Mock logout - always succeeds."""
      return FlextResult.ok(None)

    async def get_current_user(self) -> FlextResult[dict[str, object]]:
      """Mock user info."""
      return FlextResult.ok(
          {"id": "user123", "username": "testuser", "email": "test@example.com"},
      )

    async def close(self) -> None:
      """Mock close - no-op."""


class MockFailingApiClient(MockFlextApiClient):
    """Mock API client that simulates connection failures."""

    async def test_connection(self) -> FlextResult[bool]:
      """Mock connection test - always fails."""
      return FlextResult.fail("Connection failed")

    async def get_system_status(self) -> FlextResult[dict[str, object]]:
      """Mock system status - fails."""
      return FlextResult.fail("Status unavailable")

    async def list_services(self) -> FlextResult[list[dict[str, object]]]:
      """Mock service listing - fails."""
      return FlextResult.fail("Service discovery failed")


def create_mock_api_client(**kwargs: object) -> MockFlextApiClient:
    """Factory function for creating mock API clients."""
    return MockFlextApiClient(**kwargs)


def create_failing_api_client(**kwargs: object) -> MockFailingApiClient:
    """Factory function for creating failing mock API clients."""
    return MockFailingApiClient(**kwargs)


# Mock flext-api integration
def mock_create_flext_api() -> object:
    """Mock the create_flext_api function."""
    mock_api = MagicMock()

    def mock_create_client(
      config: dict[str, object],
    ) -> FlextResult[MockFlextApiClient]:
      """Mock client creation."""
      return FlextResult.ok(
          MockFlextApiClient(
              base_url=config.get(
                  "base_url",
                  f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}",
              ),
              timeout=config.get("timeout", 30.0),
          ),
      )

    mock_api.flext_api_create_client = mock_create_client
    return mock_api
