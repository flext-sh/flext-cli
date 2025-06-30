"""FLEXT API Client - HTTP/gRPC client for FLEXT platform communication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field

from flext_cli.utils.auth import get_auth_token
from flext_cli.utils.config import get_config_value


class PipelineConfig(BaseModel):
    """Pipeline configuration model."""

    name: str = Field(description="Pipeline name")
    schedule: str | None = Field(None, description="Cron schedule")
    tap: str = Field(description="Source tap plugin")
    target: str = Field(description="Target plugin")
    transform: str | None = Field(None, description="Transform plugin")
    state: dict[str, Any] | None = Field(None, description="Pipeline state")
    config: dict[str, Any] | None = Field(None, description="Additional config")


class Pipeline(BaseModel):
    """Pipeline model."""

    id: str = Field(description="Pipeline ID")
    name: str = Field(description="Pipeline name")
    status: str = Field(description="Pipeline status")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Update timestamp")
    config: PipelineConfig = Field(description="Pipeline configuration")


class PipelineList(BaseModel):
    """Pipeline list response."""

    pipelines: list[Pipeline] = Field(description="List of pipelines")
    total: int = Field(description="Total count")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")


class FlextApiClient:
    """HTTP API client for FLEXT platform.

    Provides methods for interacting with the FLEXT REST API including
    authentication, pipeline management, and plugin operations.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize API client.

        Args:
        ----
            base_url: API base URL (defaults to config)
            token: Authentication token (defaults to stored token)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates

        """
        self.base_url = base_url or get_config_value("api_url", "http://localhost:8000")
        self.base_url = self.base_url.rstrip("/")
        self.token = token or get_auth_token()
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Create HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers including auth token."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "FLEXT-CLI/0.1.0",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    async def __aenter__(self) -> FlextApiClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    def _url(self, path: str) -> str:
        """Build full URL for API endpoint."""
        return urljoin(self.base_url, path.lstrip("/"))

    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make HTTP request to API."""
        response = await self._client.request(
            method=method,
            url=self._url(path),
            json=json_data,
            params=params,
        )
        response.raise_for_status()
        return response

    # Authentication methods

    async def login(self, username: str, password: str) -> dict[str, Any]:
        """Login and get authentication token."""
        response = await self._request(
            "POST",
            "/api/v1/auth/login",
            json_data={"username": username, "password": password},
        )
        return response.json()

    async def logout(self) -> None:
        """Logout and invalidate token."""
        await self._request("POST", "/api/v1/auth/logout")

    async def get_current_user(self) -> dict[str, Any]:
        """Get current authenticated user."""
        response = await self._request("GET", "/api/v1/auth/me")
        return response.json()

    # Pipeline methods

    async def list_pipelines(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> PipelineList:
        """List all pipelines."""
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status

        response = await self._request("GET", "/api/v1/pipelines", params=params)
        return PipelineList.model_validate(response.json())

    async def get_pipeline(self, pipeline_id: str) -> Pipeline:
        """Get pipeline by ID."""
        response = await self._request("GET", f"/api/v1/pipelines/{pipeline_id}")
        return Pipeline.model_validate(response.json())

    async def create_pipeline(self, config: PipelineConfig) -> Pipeline:
        """Create new pipeline."""
        response = await self._request(
            "POST",
            "/api/v1/pipelines",
            json_data=config.model_dump(exclude_none=True),
        )
        return Pipeline.model_validate(response.json())

    async def update_pipeline(
        self,
        pipeline_id: str,
        config: PipelineConfig,
    ) -> Pipeline:
        """Update pipeline configuration."""
        response = await self._request(
            "PUT",
            f"/api/v1/pipelines/{pipeline_id}",
            json_data=config.model_dump(exclude_none=True),
        )
        return Pipeline.model_validate(response.json())

    async def delete_pipeline(self, pipeline_id: str) -> None:
        """Delete pipeline."""
        await self._request("DELETE", f"/api/v1/pipelines/{pipeline_id}")

    async def run_pipeline(
        self,
        pipeline_id: str,
        full_refresh: bool = False,
    ) -> dict[str, Any]:
        """Run pipeline execution."""
        response = await self._request(
            "POST",
            f"/api/v1/pipelines/{pipeline_id}/run",
            json_data={"full_refresh": full_refresh},
        )
        return response.json()

    async def get_pipeline_status(self, pipeline_id: str) -> dict[str, Any]:
        """Get pipeline execution status."""
        response = await self._request(
            "GET",
            f"/api/v1/pipelines/{pipeline_id}/status",
        )
        return response.json()

    async def get_pipeline_logs(
        self,
        pipeline_id: str,
        execution_id: str | None = None,
        tail: int = 100,
    ) -> list[str]:
        """Get pipeline execution logs."""
        params = {"tail": tail}
        if execution_id:
            params["execution_id"] = execution_id

        response = await self._request(
            "GET",
            f"/api/v1/pipelines/{pipeline_id}/logs",
            params=params,
        )
        return response.json()["logs"]

    # Plugin methods

    async def list_plugins(
        self,
        plugin_type: str | None = None,
        installed_only: bool = False,
    ) -> list[dict[str, Any]]:
        """List available plugins."""
        params = {"installed_only": installed_only}
        if plugin_type:
            params["type"] = plugin_type

        response = await self._request("GET", "/api/v1/plugins", params=params)
        return response.json()["plugins"]

    async def get_plugin(self, plugin_id: str) -> dict[str, Any]:
        """Get plugin details."""
        response = await self._request("GET", f"/api/v1/plugins/{plugin_id}")
        return response.json()

    async def install_plugin(
        self, plugin_id: str, version: str | None = None
    ) -> dict[str, Any]:
        """Install plugin."""
        json_data = {"plugin_id": plugin_id}
        if version:
            json_data["version"] = version

        response = await self._request(
            "POST", "/api/v1/plugins/install", json_data=json_data
        )
        return response.json()

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall plugin."""
        await self._request("POST", f"/api/v1/plugins/{plugin_id}/uninstall")

    async def update_plugin(
        self, plugin_id: str, version: str | None = None
    ) -> dict[str, Any]:
        """Update plugin."""
        json_data = {}
        if version:
            json_data["version"] = version

        response = await self._request(
            "POST",
            f"/api/v1/plugins/{plugin_id}/update",
            json_data=json_data,
        )
        return response.json()

    # System methods

    async def get_system_status(self) -> dict[str, Any]:
        """Get system status and health."""
        response = await self._request("GET", "/api/v1/system/status")
        return response.json()

    async def get_system_metrics(self) -> dict[str, Any]:
        """Get system metrics."""
        response = await self._request("GET", "/api/v1/system/metrics")
        return response.json()

    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            await self._request("GET", "/api/v1/health")
            return True
        except Exception:
            return False
