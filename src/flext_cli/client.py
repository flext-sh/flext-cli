"""FLEXT API Client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
from typing import Self, cast
from urllib.parse import urljoin

import httpx
from flext_core import FlextLogger, FlextModel, FlextResult
from pydantic import Field

from flext_cli.config import get_config as get_cli_config


def _compute_default_base_url() -> str | None:
    """Return default base URL from flext_core constants if available."""
    try:
        mod = importlib.import_module("flext_core.constants")
        constants = getattr(mod, "FlextConstants", None)
        platform = (
            getattr(constants, "Platform", None) if constants is not None else None
        )
        host = getattr(platform, "DEFAULT_HOST", None) if platform is not None else None
        port = (
            getattr(platform, "FLEXT_API_PORT", None) if platform is not None else None
        )
        if host and port:
            return f"http://{host}:{port}"
        return None
    except Exception:
        return None


class PipelineConfig(FlextModel):
    """Pipeline configuration model for Singer/Meltano workflows."""

    name: str = Field(description="Pipeline name")
    schedule: str | None = Field(None, description="Cron schedule")
    tap: str = Field(description="Source tap plugin")
    target: str = Field(description="Target plugin")
    transform: str | None = Field(None, description="Transform plugin")
    state: dict[str, object] | None = Field(None, description="Pipeline state")
    config: dict[str, object] | None = Field(None, description="Additional config")


class Pipeline(FlextModel):
    """Pipeline model for API responses."""

    id: str = Field(description="Pipeline ID")
    name: str = Field(description="Pipeline name")
    status: str = Field(description="Pipeline status")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Update timestamp")
    config: PipelineConfig = Field(description="Pipeline configuration")


class PipelineList(FlextModel):
    """Pipeline list response."""

    pipelines: list[Pipeline] = Field(description="List of pipelines")
    total: int = Field(description="Total count")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")


class FlextApiClient:
    """Client for FLEXT API operations.

    Provides async methods for interacting with the FLEXT API.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        *,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize API client.

        Args:
            base_url: API base URL (defaults from config)
            token: Authentication token (optional)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates

        """
        config = get_cli_config()
        if base_url:
            self.base_url = base_url
        elif config.api.url:
            self.base_url = config.api.url
        else:
            computed = _compute_default_base_url()
            self.base_url = computed or "http://localhost:8000"
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close client."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.aclose()

    def _url(self, path: str) -> str:
        """Build full URL from path."""
        return urljoin(self.base_url, path)

    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict[str, object] | None = None,
        params: dict[str, str | int | float | bool | None] | None = None,
    ) -> httpx.Response:
        """Make HTTP request to API."""
        if not self._session:
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

        response = await self._session.request(
            method,
            self._url(path),
            headers=self._get_headers(),
            json=json_data,
            params=params,
        )
        response.raise_for_status()
        return response

    # Authentication methods
    async def login(
        self, username: str, password: str
    ) -> FlextResult[dict[str, object]]:
        """Login with username and password.

        Returns:
            FlextResult with login response containing token and user info

        """
        try:
            response = await self._request(
                "POST",
                "/api/v1/auth/login",
                json_data={"username": username, "password": password},
            )
            http_ok = 200
            if response.status_code == http_ok:
                return FlextResult[dict[str, object]].ok(
                    cast("dict[str, object]", response.json())
                )
            return FlextResult[dict[str, object]].fail(
                f"Login failed: {response.status_code} {response.text}"
            )
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Login error: {e}")

    async def logout(self) -> None:
        """Logout the current user and invalidate token."""
        await self._request("POST", "/api/v1/auth/logout")

    async def get_current_user(self) -> dict[str, object]:
        """Get current authenticated user information.

        Returns:
            User information dictionary

        """
        response = await self._request("GET", "/api/v1/auth/user")
        return cast("dict[str, object]", response.json())

    # Pipeline methods
    async def list_pipelines(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> PipelineList:
        """List pipelines with pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            status: Filter by status (optional)

        Returns:
            Paginated pipeline list

        """
        params: dict[str, str | int | float | bool | None] = {
            "page": page,
            "page_size": page_size,
        }
        if status:
            params["status"] = status

        response = await self._request("GET", "/api/v1/pipelines", params=params)
        return PipelineList.model_validate(response.json())

    async def get_pipeline(self, pipeline_id: str) -> Pipeline:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline information

        """
        response = await self._request("GET", f"/api/v1/pipelines/{pipeline_id}")
        return Pipeline.model_validate(response.json())

    async def create_pipeline(self, config: PipelineConfig) -> Pipeline:
        """Create new pipeline.

        Args:
            config: Pipeline configuration

        Returns:
            Created pipeline

        """
        response = await self._request(
            "POST",
            "/api/v1/pipelines",
            json_data=config.model_dump(),
        )
        return Pipeline.model_validate(response.json())

    async def update_pipeline(
        self,
        pipeline_id: str,
        config: PipelineConfig,
    ) -> Pipeline:
        """Update existing pipeline.

        Args:
            pipeline_id: Pipeline ID to update
            config: New pipeline configuration

        Returns:
            Updated pipeline

        """
        response = await self._request(
            "PUT",
            f"/api/v1/pipelines/{pipeline_id}",
            json_data=config.model_dump(),
        )
        return Pipeline.model_validate(response.json())

    async def delete_pipeline(self, pipeline_id: str) -> None:
        """Delete pipeline.

        Args:
            pipeline_id: Pipeline ID to delete

        """
        await self._request("DELETE", f"/api/v1/pipelines/{pipeline_id}")

    async def run_pipeline(
        self,
        pipeline_id: str,
        *,
        full_refresh: bool = False,
    ) -> dict[str, object]:
        """Run a pipeline manually.

        Args:
            pipeline_id: Pipeline ID to run
            full_refresh: Whether to perform full refresh

        Returns:
            Pipeline execution response

        """
        response = await self._request(
            "POST",
            f"/api/v1/pipelines/{pipeline_id}/run",
            json_data={"full_refresh": full_refresh},
        )
        return cast("dict[str, object]", response.json())

    async def get_pipeline_status(self, pipeline_id: str) -> dict[str, object]:
        """Get current pipeline status.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline status information

        """
        response = await self._request("GET", f"/api/v1/pipelines/{pipeline_id}/status")
        return cast("dict[str, object]", response.json())

    async def get_pipeline_logs(
        self,
        pipeline_id: str,
        execution_id: str | None = None,
        tail: int = 100,
    ) -> list[str]:
        """Get pipeline execution logs.

        Args:
            pipeline_id: Pipeline ID
            execution_id: Specific execution ID (optional)
            tail: Number of lines to return

        Returns:
            List of log lines

        """
        params: dict[str, str | int | float | bool | None] = {"tail": tail}
        if execution_id:
            params["execution_id"] = execution_id

        response = await self._request(
            "GET",
            f"/api/v1/pipelines/{pipeline_id}/logs",
            params=params,
        )
        result = cast("dict[str, object]", response.json())
        return cast("list[str]", result["logs"])

    # Plugin methods
    async def list_plugins(
        self,
        plugin_type: str | None = None,
        *,
        installed_only: bool = False,
    ) -> list[dict[str, object]]:
        """List available plugins.

        Args:
            plugin_type: Filter by plugin type ('tap', 'target', 'transform')
            installed_only: Show only installed plugins

        Returns:
            List of plugin information dictionaries

        """
        params: dict[str, str | int | float | bool | None] = {
            "installed_only": installed_only,
        }
        if plugin_type:
            params["type"] = plugin_type

        response = await self._request("GET", "/api/v1/plugins", params=params)
        result = cast("dict[str, object]", response.json())
        return cast("list[dict[str, object]]", result["plugins"])

    async def get_plugin(self, plugin_id: str) -> dict[str, object]:
        """Get detailed plugin information.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin information dictionary

        """
        response = await self._request("GET", f"/api/v1/plugins/{plugin_id}")
        return cast("dict[str, object]", response.json())

    async def install_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> dict[str, object]:
        """Install a plugin.

        Args:
            plugin_id: Plugin ID to install
            version: Specific version (optional)

        Returns:
            Installation response

        """
        json_data: dict[str, object] = {"plugin_id": plugin_id}
        if version:
            json_data["version"] = version

        response = await self._request(
            "POST",
            "/api/v1/plugins/install",
            json_data=json_data,
        )
        return cast("dict[str, object]", response.json())

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin ID to uninstall

        """
        await self._request("DELETE", f"/api/v1/plugins/{plugin_id}")

    async def update_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> dict[str, object]:
        """Update a plugin to newer version.

        Args:
            plugin_id: Plugin ID to update
            version: Target version (optional, defaults to latest)

        Returns:
            Update response

        """
        json_data: dict[str, object] = {"plugin_id": plugin_id}
        if version:
            json_data["version"] = version

        response = await self._request(
            "PUT",
            f"/api/v1/plugins/{plugin_id}",
            json_data=json_data,
        )
        return cast("dict[str, object]", response.json())

    # System methods
    async def get_system_status(self) -> dict[str, object]:
        """Get system status and health information.

        Returns:
            System status dictionary

        """
        response = await self._request("GET", "/api/v1/system/status")
        return cast("dict[str, object]", response.json())

    async def get_system_metrics(self) -> dict[str, object]:
        """Get system performance metrics.

        Returns:
            System metrics dictionary

        """
        response = await self._request("GET", "/api/v1/system/metrics")
        return cast("dict[str, object]", response.json())

    async def test_connection(self) -> bool:
        """Test API connection.

        Returns:
            True if connection is successful, False otherwise.

        """
        try:
            await self._request("GET", "/api/v1/health")
        except (RuntimeError, ValueError, TypeError) as e:
            logger = FlextLogger(__name__)
            logger.warning(f"Connection test failed: {e}")
            return False
        else:
            return True
