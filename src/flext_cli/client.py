"""FLEXT API Client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self, cast
from urllib.parse import urljoin

import httpx
from flext_core import FlextConstants, FlextLogger, FlextResult, FlextTypes
from flext_core.models import FlextModels
from pydantic import Field

# Lazy import to avoid circular dependency
# from flext_cli.auth import FlextCliAuth - moved to _get_auth()
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants

# HTTP status codes
HTTP_OK = 200


class FlextApiClient:
    """Client for FLEXT API operations.

    Provides async methods for interacting with the FLEXT API.
    """

    class PipelineConfig(FlextModels.Config):
        """Pipeline configuration model for Singer/Meltano workflows."""

        name: str = Field(description="Pipeline name")
        schedule: str | None = Field(None, description="Cron schedule")
        tap: str = Field(description="Source tap plugin")
        target: str = Field(description="Target plugin")
        transform: str | None = Field(None, description="Transform plugin")
        state: FlextTypes.Core.Dict | None = Field(None, description="Pipeline state")
        config: FlextTypes.Core.Dict | None = Field(
            None, description="Additional config"
        )

    class Pipeline(FlextModels.Config):
        """Pipeline model for API responses."""

        id: str = Field(description="Pipeline unique identifier")
        name: str = Field(description="Pipeline name")
        status: str = Field(description="Pipeline status")
        created_at: str = Field(description="Pipeline creation timestamp")
        updated_at: str = Field(description="Pipeline last update timestamp")
        config: FlextApiClient.PipelineConfig = Field(
            description="Pipeline configuration"
        )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline business rules."""
            if not self.name or not self.name.strip():
                return FlextResult[None].fail("Pipeline name cannot be empty")
            if self.status not in FlextCliConstants.VALID_PIPELINE_STATUSES:
                return FlextResult[None].fail(f"Invalid pipeline status: {self.status}")
            return FlextResult[None].ok(None)

    class PipelineList(FlextModels.Config):
        """Pipeline list response."""

        pipelines: list[FlextApiClient.Pipeline] = Field(
            description="List of pipelines"
        )
        total: int = Field(description="Total count")
        page: int = Field(1, description="Current page")
        page_size: int = Field(20, description="Page size")

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = FlextCliConstants.TIMEOUTS.default_api_timeout,
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
        config = FlextCliConfig()
        if base_url:
            self.base_url = base_url
        elif config.api_url:
            self.base_url = config.api_url
        else:
            computed = self._compute_default_base_url()
            self.base_url = computed or FlextCliConstants.FALLBACK_API_URL
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session: httpx.AsyncClient | None = None
        # No auth service composition to avoid circular dependency

    def _get_headers(self) -> FlextTypes.Core.Headers:
        """Get request headers with authentication."""
        headers = {
            FlextCliConstants.HTTP.header_content_type: FlextCliConstants.HTTP.content_type_json,
            FlextCliConstants.HTTP.header_accept: FlextCliConstants.HTTP.content_type_json,
        }

        if self.token:
            headers[FlextCliConstants.HTTP.header_authorization] = (
                f"{FlextCliConstants.HTTP.auth_bearer_prefix} {self.token}"
            )

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
        json_data: FlextTypes.Core.Dict | None = None,
        params: dict[str, str | int | float | bool | None] | None = None,
    ) -> httpx.Response:
        """Make HTTP request to API."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

        session: httpx.AsyncClient = self._session

        response = await session.request(
            method,
            self._url(path),
            headers=self._get_headers(),
            json=json_data,
            params=params,
        )
        response.raise_for_status()
        return response

    @classmethod
    def _compute_default_base_url(cls) -> str | None:
        """Return default base URL using flext_core root exports."""
        try:
            base = getattr(FlextConstants.Platform, "DEFAULT_BASE_URL", None)
            host = getattr(FlextConstants.Platform, "DEFAULT_HOST", None)
            port = getattr(FlextConstants.Platform, "FLEXT_API_PORT", None)

            # Prefer explicit DEFAULT_BASE_URL, fallback to http://{host}
            if not base and host:
                base = f"{FlextCliConstants.HTTP.http_scheme}://{host}"

            if base and port:
                # Avoid duplicating port if already present
                return (
                    base if str(port) in base.rsplit(":", 1)[-1] else f"{base}:{port}"
                )
            return base
        except (RuntimeError, ValueError, OSError):
            return None

    # Authentication methods - USING COMPOSITION TO ELIMINATE DUPLICATION
    async def login(
        self, username: str, password: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Login with username and password using auth service - ELIMINATES DUPLICATION.

        Returns:
            FlextResult with login response containing token and user info

        """
        try:
            # Direct login implementation without circular dependency
            login_data: dict[str, object] = {
                "username": username,
                "password": password,
            }

            response = await self._request(
                FlextCliConstants.HttpMethod.POST,
                "/api/v1/auth/login",
                json_data=login_data
            )

            if response.status_code == HTTP_OK:
                auth_data = response.json()
                if isinstance(auth_data, dict) and "access_token" in auth_data:
                    self.token = str(auth_data["access_token"])
                return FlextResult[dict[str, object]].ok(auth_data)
            return FlextResult[dict[str, object]].fail(f"Login failed with status {response.status_code}")

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Login to SOURCE OF TRUTH failed: {e}")

    async def logout(self) -> FlextResult[None]:
        """Logout the current user directly."""
        try:
            response = await self._request(
                FlextCliConstants.HttpMethod.POST,
                "/api/v1/auth/logout"
            )

            if response.status_code == HTTP_OK:
                # Clear local token on successful logout
                self.token = None
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Logout failed with status {response.status_code}")

        except Exception as e:
            return FlextResult[None].fail(f"Logout failed: {e}")

    async def get_current_user(self) -> FlextTypes.Core.Dict:
        """Get current authenticated user information.

        Returns:
            User information dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, "/api/v1/auth/user"
        )
        return cast("FlextTypes.Core.Dict", response.json())

    # Pipeline methods
    async def list_pipelines(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> FlextApiClient.PipelineList:
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

        response = await self._request(
            FlextCliConstants.HttpMethod.GET, "/api/v1/pipelines", params=params
        )
        return FlextApiClient.PipelineList(**response.json())

    async def get_pipeline(self, pipeline_id: str) -> FlextApiClient.Pipeline:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline information

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, f"/api/v1/pipelines/{pipeline_id}"
        )
        return FlextApiClient.Pipeline(**response.json())

    async def create_pipeline(
        self, config: FlextApiClient.PipelineConfig
    ) -> FlextApiClient.Pipeline:
        """Create new pipeline.

        Args:
            config: Pipeline configuration

        Returns:
            Created pipeline

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.POST,
            "/api/v1/pipelines",
            json_data=config.model_dump(),
        )
        return FlextApiClient.Pipeline(**response.json())

    async def update_pipeline(
        self,
        pipeline_id: str,
        config: FlextApiClient.PipelineConfig,
    ) -> FlextApiClient.Pipeline:
        """Update existing pipeline.

        Args:
            pipeline_id: Pipeline ID to update
            config: New pipeline configuration

        Returns:
            Updated pipeline

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.PUT,
            f"/api/v1/pipelines/{pipeline_id}",
            json_data=config.model_dump(),
        )
        return FlextApiClient.Pipeline(**response.json())

    async def delete_pipeline(self, pipeline_id: str) -> None:
        """Delete pipeline.

        Args:
            pipeline_id: Pipeline ID to delete

        """
        await self._request(
            FlextCliConstants.HttpMethod.DELETE, f"/api/v1/pipelines/{pipeline_id}"
        )

    async def run_pipeline(
        self,
        pipeline_id: str,
        *,
        full_refresh: bool = False,
    ) -> FlextTypes.Core.Dict:
        """Run a pipeline manually.

        Args:
            pipeline_id: Pipeline ID to run
            full_refresh: Whether to perform full refresh

        Returns:
            Pipeline execution response

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.POST,
            f"/api/v1/pipelines/{pipeline_id}/run",
            json_data={"full_refresh": full_refresh},
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def get_pipeline_status(self, pipeline_id: str) -> FlextTypes.Core.Dict:
        """Get current pipeline status.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline status information

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, f"/api/v1/pipelines/{pipeline_id}/status"
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def get_pipeline_logs(
        self,
        pipeline_id: str,
        execution_id: str | None = None,
        tail: int = 100,
    ) -> FlextTypes.Core.StringList:
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
            FlextCliConstants.HttpMethod.GET,
            f"/api/v1/pipelines/{pipeline_id}/logs",
            params=params,
        )
        result = cast("FlextTypes.Core.Dict", response.json())
        return cast("FlextTypes.Core.StringList", result["logs"])

    # Plugin methods
    async def list_plugins(
        self,
        plugin_type: str | None = None,
        *,
        installed_only: bool = False,
    ) -> list[FlextTypes.Core.Dict]:
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

        response = await self._request(
            FlextCliConstants.HttpMethod.GET, "/api/v1/plugins", params=params
        )
        result = cast("FlextTypes.Core.Dict", response.json())
        return cast("list[FlextTypes.Core.Dict]", result["plugins"])

    async def get_plugin(self, plugin_id: str) -> FlextTypes.Core.Dict:
        """Get detailed plugin information.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin information dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, f"/api/v1/plugins/{plugin_id}"
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def install_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> FlextTypes.Core.Dict:
        """Install a plugin.

        Args:
            plugin_id: Plugin ID to install
            version: Specific version (optional)

        Returns:
            Installation response

        """
        json_data: FlextTypes.Core.Dict = {"plugin_id": plugin_id}
        if version:
            json_data["version"] = version

        response = await self._request(
            FlextCliConstants.HttpMethod.POST,
            "/api/v1/plugins/install",
            json_data=json_data,
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin ID to uninstall

        """
        await self._request(
            FlextCliConstants.HttpMethod.DELETE, f"/api/v1/plugins/{plugin_id}"
        )

    async def update_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> FlextTypes.Core.Dict:
        """Update a plugin to newer version.

        Args:
            plugin_id: Plugin ID to update
            version: Target version (optional, defaults to latest)

        Returns:
            Update response

        """
        json_data: FlextTypes.Core.Dict = {"plugin_id": plugin_id}
        if version:
            json_data["version"] = version

        response = await self._request(
            FlextCliConstants.HttpMethod.PUT,
            f"/api/v1/plugins/{plugin_id}",
            json_data=json_data,
        )
        return cast("FlextTypes.Core.Dict", response.json())

    # System methods
    async def get_system_status(self) -> FlextTypes.Core.Dict:
        """Get system status and health information.

        Returns:
            System status dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, "/api/v1/system/status"
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def get_system_metrics(self) -> FlextTypes.Core.Dict:
        """Get system performance metrics.

        Returns:
            System metrics dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET, "/api/v1/system/metrics"
        )
        return cast("FlextTypes.Core.Dict", response.json())

    async def test_connection(self) -> bool:
        """Test API connection.

        Returns:
            True if connection is successful, False otherwise.

        """
        try:
            await self._request(FlextCliConstants.HttpMethod.GET, "/api/v1/health")
        except (RuntimeError, ValueError, TypeError) as e:
            logger = FlextLogger(__name__)
            logger.warning(f"Connection test failed: {e}")
            return False
        else:
            return True


__all__ = ["FlextApiClient"]
