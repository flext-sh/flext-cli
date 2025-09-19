"""FLEXT API Client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from flext_cli.configs import FlextCliConfigs
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_core import FlextConstants, FlextLogger, FlextResult, FlextTypes

HTTP_OK = 200


class FlextCliClient:
    """Client for FLEXT API operations.

    Provides async methods for interacting with the FLEXT API.
    Uses FlextConfig singleton as the single source of truth for all configuration.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float | None = None,
        *,
        verify_ssl: bool | None = None,
    ) -> None:
        """Initialize API client using FlextConfig singleton as single source of truth.

        Args:
            base_url: API base URL (overrides config if provided)
            token: Authentication token (overrides config if provided)
            timeout: Request timeout in seconds (overrides config if provided)
            verify_ssl: Whether to verify SSL certificates (overrides config if provided)

        """
        # Get FlextConfig singleton as single source of truth
        config = FlextCliConfigs.get_global_instance()

        # Use config values as defaults, allow overrides
        if base_url:
            self.base_url = base_url
        elif config.base_url:
            self.base_url = config.base_url
        else:
            computed = self._compute_default_base_url()
            self.base_url = computed or FlextCliConstants.FALLBACK_API_URL

        self.token = token or getattr(config, "api_key", None) or None
        self.timeout = timeout or config.timeout_seconds
        self.verify_ssl = (
            verify_ssl
            if verify_ssl is not None
            else getattr(config, "verify_ssl", True)
        )
        self._session: httpx.AsyncClient | None = None

        # Store reference to config for future use
        self._config = config

    def update_from_config(self) -> None:
        """Update client configuration from FlextConfig singleton.

        This method allows the client to refresh its configuration
        from the FlextConfig singleton, ensuring it always uses
        the latest configuration values.
        """
        config = FlextCliConfigs.get_global_instance()

        # Update configuration values
        if config.base_url:
            self.base_url = config.base_url
        self.token = getattr(config, "api_key", self.token)
        self.timeout = config.timeout_seconds
        self.verify_ssl = getattr(config, "verify_ssl", True)

        # Update stored config reference
        self._config = config

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

    # Public accessor methods
    def get_headers(self) -> FlextTypes.Core.Headers:
        """Get request headers with authentication."""
        return self._get_headers()

    def build_url(self, path: str) -> str:
        """Build full URL from path."""
        return self._url(path)

    def _parse_json_response(self, response: httpx.Response) -> FlextTypes.Core.Dict:
        """Parse JSON response using Pydantic validation."""
        json_data = response.json()
        # Use Pydantic model for validation instead of manual isinstance check
        try:
            validated_response = FlextCliModels.ApiJsonResponse(data=json_data)
            return validated_response.data
        except ValidationError as e:
            msg = f"Invalid JSON response format: {e}"
            raise TypeError(msg) from e

    def _parse_json_list_response(
        self,
        response: httpx.Response,
    ) -> list[FlextTypes.Core.Dict]:
        """Parse JSON response as list using Pydantic validation."""
        json_data = response.json()
        # Use Pydantic model for validation instead of manual isinstance check
        try:
            validated_response = FlextCliModels.ApiListResponse(data=json_data)
            return validated_response.data
        except ValidationError as e:
            msg = f"Invalid JSON list response format: {e}"
            raise TypeError(msg) from e

    def _extract_string_list(
        self,
        data: FlextTypes.Core.Dict,
        key: str,
    ) -> FlextTypes.Core.StringList:
        """Extract string list from dict using Pydantic validation."""
        if key not in data:
            msg = f"Key '{key}' not found in response"
            raise KeyError(msg)

        value = data[key]
        # Validate that value is a list before passing to Pydantic
        if not isinstance(value, list):
            msg = f"Expected list for key '{key}', got {type(value).__name__}"
            raise TypeError(msg)

        # Use Pydantic model for validation instead of manual isinstance checks
        try:
            if key == "logs":
                validated_response = FlextCliModels.StringListResponse(logs=value)
                return validated_response.logs
            # Generic string list validation
            validated_response = FlextCliModels.StringListResponse(logs=value)
            return validated_response.logs
        except ValidationError as e:
            msg = f"Invalid string list for key '{key}': {e}"
            raise TypeError(msg) from e

    def _extract_dict_list(
        self,
        data: FlextTypes.Core.Dict,
        key: str,
    ) -> list[FlextTypes.Core.Dict]:
        """Extract dict list from dict using Pydantic validation."""
        if key not in data:
            msg = f"Key '{key}' not found in response"
            raise KeyError(msg)

        value = data[key]
        # Validate that value is a list before passing to Pydantic
        if not isinstance(value, list):
            msg = f"Expected list for key '{key}', got {type(value).__name__}"
            raise TypeError(msg)

        # Use Pydantic model for validation instead of manual isinstance checks
        try:
            if key == "plugins":
                plugin_response = FlextCliModels.PluginListResponse(plugins=value)
                return plugin_response.plugins
            # Generic dict list validation
            api_response = FlextCliModels.ApiListResponse(data=value)
            return api_response.data
        except ValidationError as e:
            msg = f"Invalid dict list for key '{key}': {e}"
            raise TypeError(msg) from e

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
        self,
        username: str,
        password: str,
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
                json_data=login_data,
            )

            if response.status_code == HTTP_OK:
                auth_data = response.json()
                if isinstance(auth_data, dict) and "access_token" in auth_data:
                    self.token = str(auth_data["access_token"])
                return FlextResult[dict[str, object]].ok(auth_data)
            return FlextResult[dict[str, object]].fail(
                f"Login failed with status {response.status_code}",
            )

        except (AttributeError, ValueError) as e:
            return FlextResult[dict[str, object]].fail(
                f"Login to SOURCE OF TRUTH failed: {e}",
            )

    async def logout(self) -> FlextResult[None]:
        """Logout the current user directly."""
        try:
            response = await self._request(
                FlextCliConstants.HttpMethod.POST,
                "/api/v1/auth/logout",
            )

            if response.status_code == HTTP_OK:
                # Clear local token on successful logout
                self.token = None
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(
                f"Logout failed with status {response.status_code}",
            )

        except (AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Logout failed: {e}")

    async def get_current_user(self) -> FlextTypes.Core.Dict:
        """Get current authenticated user information.

        Returns:
            User information dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            "/api/v1/auth/user",
        )
        return self._parse_json_response(response)

    # Pipeline methods
    async def list_pipelines(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> FlextCliModels.PipelineList:
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
            FlextCliConstants.HttpMethod.GET,
            "/api/v1/pipelines",
            params=params,
        )
        return FlextCliModels.PipelineList(**response.json())

    async def get_pipeline(self, pipeline_id: str) -> FlextCliModels.Pipeline:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline information

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            f"/api/v1/pipelines/{pipeline_id}",
        )
        return FlextCliModels.Pipeline(**response.json())

    async def create_pipeline(
        self,
        config: FlextCliModels.PipelineConfig,
    ) -> FlextCliModels.Pipeline:
        """Create new pipeline.

        Args:
            config: Pipeline configuration

        Returns:
            Created pipeline

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.POST,
            "/api/v1/pipelines",
            json_data=config.model_dump(mode="json"),
        )
        return FlextCliModels.Pipeline(**response.json())

    async def update_pipeline(
        self,
        pipeline_id: str,
        config: FlextCliModels.PipelineConfig,
    ) -> FlextCliModels.Pipeline:
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
            json_data=config.model_dump(mode="json"),
        )
        return FlextCliModels.Pipeline(**response.json())

    async def delete_pipeline(self, pipeline_id: str) -> None:
        """Delete pipeline.

        Args:
            pipeline_id: Pipeline ID to delete

        """
        await self._request(
            FlextCliConstants.HttpMethod.DELETE,
            f"/api/v1/pipelines/{pipeline_id}",
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
        return self._parse_json_response(response)

    async def get_pipeline_status(self, pipeline_id: str) -> FlextTypes.Core.Dict:
        """Get current pipeline status.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline status information

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            f"/api/v1/pipelines/{pipeline_id}/status",
        )
        return self._parse_json_response(response)

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
        result = self._parse_json_response(response)
        return self._extract_string_list(result, "logs")

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
            FlextCliConstants.HttpMethod.GET,
            "/api/v1/plugins",
            params=params,
        )
        result = self._parse_json_response(response)
        return self._extract_dict_list(result, "plugins")

    async def get_plugin(self, plugin_id: str) -> FlextTypes.Core.Dict:
        """Get detailed plugin information.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin information dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            f"/api/v1/plugins/{plugin_id}",
        )
        return self._parse_json_response(response)

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
        return self._parse_json_response(response)

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin ID to uninstall

        """
        await self._request(
            FlextCliConstants.HttpMethod.DELETE,
            f"/api/v1/plugins/{plugin_id}",
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
        return self._parse_json_response(response)

    # System methods
    async def get_system_status(self) -> FlextTypes.Core.Dict:
        """Get system status and health information.

        Returns:
            System status dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            "/api/v1/system/status",
        )
        return self._parse_json_response(response)

    async def get_system_metrics(self) -> FlextTypes.Core.Dict:
        """Get system performance metrics.

        Returns:
            System metrics dictionary

        """
        response = await self._request(
            FlextCliConstants.HttpMethod.GET,
            "/api/v1/system/metrics",
        )
        return self._parse_json_response(response)

    async def test_connection(self) -> bool:
        """Test API connection.

        Returns:
            True if connection is successful, False otherwise.

        """
        try:
            await self._request(FlextCliConstants.HttpMethod.GET, "/api/v1/health")
        except (RuntimeError, ValueError, TypeError) as e:
            logger = FlextLogger(__name__)
            warning_msg = f"Connection test failed: {e}"
            logger.warning(warning_msg)
            return False
        else:
            return True


# ARCHITECTURAL COMPLIANCE: Aliases removed - use FlextCliModels.Pipeline directly


__all__ = ["FlextCliClient"]
