"""FLEXT API Client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self
from urllib.parse import urljoin

import httpx

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
            computed_result = self._compute_default_base_url()
            self.base_url = computed_result.unwrap_or(
                FlextCliConstants.FALLBACK_API_URL
            )

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

    def _update_from_config(self) -> None:
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
        """Get request headers with authentication.

        Returns:
            FlextTypes.Core.Headers: Headers dictionary with authentication token.


        Returns:
            FlextTypes.Core.Headers: Description of return value.

        """
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
        """Enter async context manager.

        Returns:
            Self: The client instance for context management.


        Returns:
            Self: Description of return value.

        """
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close client."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.aclose()

    def _url(self, path: str) -> str:
        """Build full URL from path.

        Returns:
            str: Complete URL combining base URL and path.


        Returns:
            str: Description of return value.

        """
        return urljoin(self.base_url, path)

    # Public accessor methods
    def _get_headers_public(self) -> FlextTypes.Core.Headers:
        """Get request headers with authentication.

        Returns:
            FlextTypes.Core.Headers: Headers dictionary with authentication token.


        Returns:
            FlextTypes.Core.Headers: Description of return value.

        """
        return self._get_headers()

    def _build_url(self, path: str) -> str:
        """Build full URL from path.

        Returns:
            str: Complete URL combining base URL and path.


        Returns:
            str: Description of return value.

        """
        return self._url(path)

    def _parse_json_response(
        self, response: httpx.Response
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Parse JSON response using railway pattern with Pydantic validation.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Parsed JSON data or error result.


        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """

        def extract_json_data(resp: httpx.Response) -> FlextResult[dict[str, object]]:
            """Extract JSON data from response - using safe_call for railway pattern.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            return FlextResult.safe_call(resp.json)

        def validate_response_format(
            json_data: dict[str, object],
        ) -> FlextResult[FlextCliModels.ApiJsonResponse]:
            """Validate JSON response format using Pydantic - explicit error handling.

            Returns:
            FlextResult[FlextCliModels.ApiJsonResponse]: Description of return value.

            """
            return FlextResult.safe_call(
                lambda: FlextCliModels.ApiJsonResponse(data=json_data)
            )

        def extract_data(
            validated_response: FlextCliModels.ApiJsonResponse,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Extract data from validated response.

            Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

            """
            return FlextResult[FlextTypes.Core.Dict].ok(validated_response.data)

        # Railway pattern composition - NO try/except needed
        return (
            extract_json_data(response)
            .flat_map(validate_response_format)
            .flat_map(extract_data)
        )

    def _parse_json_list_response(
        self,
        response: httpx.Response,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Parse JSON response as list using railway pattern with Pydantic validation.

        Returns:
            FlextResult[list[FlextTypes.Core.Dict]]: Description of return value.

        """

        def extract_json_data(
            resp: httpx.Response,
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract JSON list data from response - using safe_call for railway pattern.

            Returns:
            FlextResult[list[dict[str, object]]]: Description of return value.

            """
            result = FlextResult.safe_call(resp.json)
            return result.flat_map(
                lambda data: (
                    FlextResult[list[dict[str, object]]].ok(data)
                    if isinstance(data, list)
                    else FlextResult[list[dict[str, object]]].fail(
                        "Expected JSON array response"
                    )
                )
            )

        def validate_list_response_format(
            json_data: list[dict[str, object]],
        ) -> FlextResult[FlextCliModels.ApiListResponse]:
            """Validate JSON list response format using Pydantic - explicit error handling.

            Returns:
            FlextResult[FlextCliModels.ApiListResponse]: Description of return value.

            """
            return FlextResult.safe_call(
                lambda: FlextCliModels.ApiListResponse(data=json_data)
            )

        def extract_list_data(
            validated_response: FlextCliModels.ApiListResponse,
        ) -> FlextResult[list[FlextTypes.Core.Dict]]:
            """Extract list data from validated response.

            Returns:
            FlextResult[list[FlextTypes.Core.Dict]]: Description of return value.

            """
            return FlextResult[list[FlextTypes.Core.Dict]].ok(validated_response.data)

        # Railway pattern composition - NO try/except needed
        return (
            extract_json_data(response)
            .flat_map(validate_list_response_format)
            .flat_map(extract_list_data)
        )

    def _extract_string_list(
        self,
        data: FlextTypes.Core.Dict,
        key: str,
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """Extract string list from dict using railway pattern with Pydantic validation.

        Returns:
            FlextResult[FlextTypes.Core.StringList]: Description of return value.

        """

        def validate_key_exists(
            data_dict: FlextTypes.Core.Dict, target_key: str
        ) -> FlextResult[object]:
            """Validate that key exists in response data.

            Returns:
            FlextResult[object]: Description of return value.

            """
            if target_key not in data_dict:
                return FlextResult[object].fail(
                    f"Key '{target_key}' not found in response"
                )
            return FlextResult[object].ok(data_dict[target_key])

        def validate_list_type(
            value: object, target_key: str
        ) -> FlextResult[list[object]]:
            """Validate that value is a list.

            Returns:
            FlextResult[list[object]]: Description of return value.

            """
            if not isinstance(value, list):
                return FlextResult[list[object]].fail(
                    f"Expected list for key '{target_key}', got {type(value).__name__}"
                )
            return FlextResult[list[object]].ok(value)

        def validate_string_list_format(
            value: list[object], _target_key: str
        ) -> FlextResult[FlextCliModels.StringListResponse]:
            """Validate string list format using Pydantic.

            Returns:
            FlextResult[FlextCliModels.StringListResponse]: Description of return value.

            """
            # Convert objects to strings for Pydantic validation
            string_list = [str(item) for item in value]
            return FlextResult.safe_call(
                lambda: FlextCliModels.StringListResponse(logs=string_list)
            )

        def extract_string_list(
            validated_response: FlextCliModels.StringListResponse,
        ) -> FlextResult[FlextTypes.Core.StringList]:
            """Extract string list from validated response.

            Returns:
            FlextResult[FlextTypes.Core.StringList]: Description of return value.

            """
            return FlextResult[FlextTypes.Core.StringList].ok(validated_response.logs)

        # Railway pattern composition - NO try/except needed
        return (
            validate_key_exists(data, key)
            .flat_map(lambda value: validate_list_type(value, key))
            .flat_map(lambda value: validate_string_list_format(value, key))
            .flat_map(extract_string_list)
        )

    def _extract_dict_list(
        self,
        data: FlextTypes.Core.Dict,
        key: str,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Extract dict list from dict using railway pattern with Pydantic validation.

        Returns:
            FlextResult[list[FlextTypes.Core.Dict]]: Description of return value.

        """

        def validate_key_exists(
            data_dict: FlextTypes.Core.Dict, target_key: str
        ) -> FlextResult[object]:
            """Validate that key exists in response data.

            Returns:
            FlextResult[object]: Description of return value.

            """
            if target_key not in data_dict:
                return FlextResult[object].fail(
                    f"Key '{target_key}' not found in response"
                )
            return FlextResult[object].ok(data_dict[target_key])

        def validate_list_type(
            value: object, target_key: str
        ) -> FlextResult[list[object]]:
            """Validate that value is a list.

            Returns:
            FlextResult[list[object]]: Description of return value.

            """
            if not isinstance(value, list):
                return FlextResult[list[object]].fail(
                    f"Expected list for key '{target_key}', got {type(value).__name__}"
                )
            return FlextResult[list[object]].ok(value)

        def validate_dict_list_format(
            value: list[object], target_key: str
        ) -> FlextResult[list[FlextTypes.Core.Dict]]:
            """Validate dict list format using Pydantic - key-specific logic.

            Returns:
            FlextResult[list[FlextTypes.Core.Dict]]: Description of return value.

            """
            # Convert list[object] to list[dict[str, object]] for Pydantic validation
            dict_list = []
            for item in value:
                if isinstance(item, dict):
                    dict_list.append(item)
                else:
                    return FlextResult[list[FlextTypes.Core.Dict]].fail(
                        f"Expected dict in list for key '{target_key}', got {type(item).__name__}"
                    )

            if target_key == "plugins":
                return FlextResult.safe_call(
                    lambda: FlextCliModels.PluginListResponse(plugins=dict_list)
                ).map(lambda resp: resp.plugins)

            # Generic dict list validation
            return FlextResult.safe_call(
                lambda: FlextCliModels.ApiListResponse(data=dict_list)
            ).map(lambda resp: resp.data)

        # Railway pattern composition - NO try/except needed
        return (
            validate_key_exists(data, key)
            .flat_map(lambda value: validate_list_type(value, key))
            .flat_map(lambda value: validate_dict_list_format(value, key))
        )

    async def _request(
        self,
        method: str,
        path: str,
        json_data: FlextTypes.Core.Dict | None = None,
        params: dict[str, str | int | float | bool | None] | None = None,
    ) -> httpx.Response:
        """Make HTTP request to API.

        Returns:
            httpx.Response: Description of return value.

        """
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
    def _compute_default_base_url(cls) -> FlextResult[str]:
        """Return default base URL using railway pattern with explicit error handling.

        Returns:
            FlextResult[str]: Description of return value.

        """

        def get_platform_constants() -> FlextResult[
            tuple[str | None, str | None, str | None]
        ]:
            """Get platform constants using safe attribute access.

            Returns:
            FlextResult[
            tuple[str | None, str | None, str | None]
            ]: Description of return value.

            """
            return FlextResult.safe_call(
                lambda: (
                    getattr(FlextConstants.Platform, "DEFAULT_BASE_URL", None),
                    getattr(FlextConstants.Platform, "DEFAULT_HOST", None),
                    getattr(FlextConstants.Platform, "FLEXT_API_PORT", None),
                )
            )

        def construct_base_url(
            constants: tuple[str | None, str | None, str | None],
        ) -> FlextResult[str]:
            """Construct base URL from platform constants.

            Returns:
            FlextResult[str]: Description of return value.

            """
            base, host, port = constants

            # Prefer explicit DEFAULT_BASE_URL, fallback to http://{host}
            if not base and host:
                base = f"{FlextCliConstants.HTTP.http_scheme}://{host}"

            if not base:
                return FlextResult[str].fail("No base URL or host available")

            if port:
                # Avoid duplicating port if already present
                final_url = (
                    base if str(port) in base.rsplit(":", 1)[-1] else f"{base}:{port}"
                )
                return FlextResult[str].ok(final_url)

            return FlextResult[str].ok(base)

        # Railway pattern composition - NO try/except needed
        return get_platform_constants().flat_map(construct_base_url)

    # Authentication methods - USING COMPOSITION TO ELIMINATE DUPLICATION
    async def login(
        self,
        username: str,
        password: str,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Login with username and password using railway pattern - SOLID principles.

        Returns:
            FlextResult with login response containing token and user info



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """

        def validate_credentials(user: str, pwd: str) -> FlextResult[dict[str, object]]:
            """Validate login credentials - Single Responsibility.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            if not user or not pwd:
                return FlextResult[dict[str, object]].fail(
                    "Username and password required"
                )
            return FlextResult[dict[str, object]].ok({
                "username": user,
                "password": pwd,
            })

        async def execute_login_request(
            login_data: dict[str, object],
        ) -> FlextResult[httpx.Response]:
            """Execute login request using flext-core safe patterns.

            Returns:
            FlextResult[httpx.Response]: Description of return value.

            """
            try:
                response = await self._request(
                    FlextCliConstants.Enums.HttpMethod.POST,
                    "/api/v1/auth/login",
                    json_data=login_data,
                )
                return FlextResult[httpx.Response].ok(response)
            except Exception as e:
                return FlextResult[httpx.Response].fail(f"Login request failed: {e}")

        def process_login_response(
            response: httpx.Response,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Process login response and extract auth data.

            Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

            """
            if response.status_code != HTTP_OK:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Login failed with status {response.status_code}"
                )

            # Use existing railway pattern method
            return self._parse_json_response(response).map(update_token_from_auth_data)

        def update_token_from_auth_data(
            auth_data: FlextTypes.Core.Dict,
        ) -> FlextTypes.Core.Dict:
            """Update token from auth data - Side effect isolation.

            Returns:
            FlextTypes.Core.Dict: Description of return value.

            """
            if isinstance(auth_data, dict) and "access_token" in auth_data:
                self.token = str(auth_data["access_token"])
            return auth_data

        # Railway pattern composition - leveraging flext-core patterns
        credentials_result = validate_credentials(username, password)
        if credentials_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                credentials_result.error or "Credentials validation failed"
            )

        response_result = await execute_login_request(credentials_result.unwrap())
        if response_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                response_result.error or "Login request failed"
            )

        return process_login_response(response_result.unwrap())

    async def logout(self) -> FlextResult[None]:
        """Logout the current user using railway pattern - SOLID principles.

        Returns:
            FlextResult[None]: Description of return value.

        """

        async def execute_logout_request() -> FlextResult[httpx.Response]:
            """Execute logout request using flext-core safe patterns.

            Returns:
            FlextResult[httpx.Response]: Description of return value.

            """
            try:
                response = await self._request(
                    FlextCliConstants.Enums.HttpMethod.POST,
                    "/api/v1/auth/logout",
                )
                return FlextResult[httpx.Response].ok(response)
            except Exception as e:
                return FlextResult[httpx.Response].fail(f"Logout request failed: {e}")

        def process_logout_response(response: httpx.Response) -> FlextResult[None]:
            """Process logout response and clear token.

            Returns:
            FlextResult[None]: Description of return value.

            """
            if response.status_code != HTTP_OK:
                return FlextResult[None].fail(
                    f"Logout failed with status {response.status_code}"
                )

            # Clear local token on successful logout - Side effect isolation
            self.token = None
            return FlextResult[None].ok(None)

        # Railway pattern composition - leveraging flext-core patterns
        response_result = await execute_logout_request()
        if response_result.is_failure:
            return FlextResult[None].fail(
                f"Logout request failed: {response_result.error}"
            )

        return process_logout_response(response_result.unwrap())

    async def get_current_user(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get current authenticated user information using railway pattern.

        Returns:
            FlextResult with user information dictionary



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        response = await self._request(
            FlextCliConstants.Enums.HttpMethod.GET,
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



        Returns:
            FlextCliModels.PipelineList: Description of return value.

        """
        params: dict[str, str | int | float | bool | None] = {
            "page": page,
            "page_size": page_size,
        }
        if status:
            params["status"] = status

        response = await self._request(
            FlextCliConstants.Enums.HttpMethod.GET,
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



        Returns:
            FlextCliModels.Pipeline: Description of return value.

        """
        response = await self._request(
            FlextCliConstants.Enums.HttpMethod.GET,
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



        Returns:
            FlextCliModels.Pipeline: Description of return value.

        """
        response = await self._request(
            FlextCliConstants.Enums.HttpMethod.POST,
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



        Returns:
            FlextCliModels.Pipeline: Description of return value.

        """
        response = await self._request(
            FlextCliConstants.Enums.HttpMethod.PUT,
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
            FlextCliConstants.Enums.HttpMethod.DELETE,
            f"/api/v1/pipelines/{pipeline_id}",
        )

    async def run_pipeline(
        self,
        pipeline_id: str,
        *,
        full_refresh: bool = False,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Run a pipeline manually using railway pattern.

        Args:
            pipeline_id: Pipeline ID to run
            full_refresh: Whether to perform full refresh

        Returns:
            FlextResult containing pipeline execution response



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not pipeline_id.strip():
            return FlextResult[FlextTypes.Core.Dict].fail("Pipeline ID cannot be empty")

        try:
            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.POST,
                f"/api/v1/pipelines/{pipeline_id}/run",
                json_data={"full_refresh": full_refresh},
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to run pipeline: {e}"
            )

    async def get_pipeline_status(
        self, pipeline_id: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Get current pipeline status using railway pattern.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            FlextResult containing pipeline status information



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not pipeline_id.strip():
            return FlextResult[FlextTypes.Core.Dict].fail("Pipeline ID cannot be empty")

        try:
            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                f"/api/v1/pipelines/{pipeline_id}/status",
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to get pipeline status: {e}"
            )

    async def get_pipeline_logs(
        self,
        pipeline_id: str,
        execution_id: str | None = None,
        tail: int = 100,
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """Get pipeline execution logs using railway pattern.

        Args:
            pipeline_id: Pipeline ID
            execution_id: Specific execution ID (optional)
            tail: Number of lines to return

        Returns:
            FlextResult containing list of log lines



        Returns:
            FlextResult[FlextTypes.Core.StringList]: Description of return value.

        """
        if not pipeline_id.strip():
            return FlextResult[FlextTypes.Core.StringList].fail(
                "Pipeline ID cannot be empty"
            )

        if tail <= 0:
            return FlextResult[FlextTypes.Core.StringList].fail(
                "Tail must be a positive number"
            )

        try:
            params: dict[str, str | int | float | bool | None] = {"tail": tail}
            if execution_id:
                params["execution_id"] = execution_id

            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                f"/api/v1/pipelines/{pipeline_id}/logs",
                params=params,
            )

            # Railway pattern composition - no try/except needed
            return self._parse_json_response(response).flat_map(
                lambda result: self._extract_string_list(result, "logs")
            )
        except Exception as e:
            return FlextResult[FlextTypes.Core.StringList].fail(
                f"Failed to get pipeline logs: {e}"
            )

    # Plugin methods
    async def list_plugins(
        self,
        plugin_type: str | None = None,
        *,
        installed_only: bool = False,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """List available plugins using railway pattern.

        Args:
            plugin_type: Filter by plugin type ('tap', 'target', 'transform')
            installed_only: Show only installed plugins

        Returns:
            FlextResult containing list of plugin information dictionaries



        Returns:
            FlextResult[list[FlextTypes.Core.Dict]]: Description of return value.

        """
        # Validate plugin_type if provided
        if plugin_type and plugin_type.strip() not in {"tap", "target", "transform"}:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                "Plugin type must be one of: tap, target, transform"
            )

        try:
            params: dict[str, str | int | float | bool | None] = {
                "installed_only": installed_only,
            }
            if plugin_type:
                params["type"] = plugin_type.strip()

            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                "/api/v1/plugins",
                params=params,
            )

            # Railway pattern composition - no try/except needed
            return self._parse_json_response(response).flat_map(
                lambda result: self._extract_dict_list(result, "plugins")
            )
        except Exception as e:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                f"Failed to list plugins: {e}"
            )

    async def get_plugin(self, plugin_id: str) -> FlextResult[FlextTypes.Core.Dict]:
        """Get detailed plugin information using railway pattern.

        Args:
            plugin_id: Plugin ID

        Returns:
            FlextResult containing plugin information dictionary



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not plugin_id.strip():
            return FlextResult[FlextTypes.Core.Dict].fail("Plugin ID cannot be empty")

        try:
            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                f"/api/v1/plugins/{plugin_id}",
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Failed to get plugin: {e}")

    async def install_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Install a plugin using railway pattern.

        Args:
            plugin_id: Plugin ID to install
            version: Specific version (optional)

        Returns:
            FlextResult containing installation response



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not plugin_id.strip():
            return FlextResult[FlextTypes.Core.Dict].fail("Plugin ID cannot be empty")

        try:
            json_data: FlextTypes.Core.Dict = {"plugin_id": plugin_id.strip()}
            if version and version.strip():
                json_data["version"] = version.strip()

            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.POST,
                "/api/v1/plugins/install",
                json_data=json_data,
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to install plugin: {e}"
            )

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin ID to uninstall

        """
        await self._request(
            FlextCliConstants.Enums.HttpMethod.DELETE,
            f"/api/v1/plugins/{plugin_id}",
        )

    async def update_plugin(
        self,
        plugin_id: str,
        version: str | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Update a plugin to newer version using railway pattern.

        Args:
            plugin_id: Plugin ID to update
            version: Target version (optional, defaults to latest)

        Returns:
            FlextResult containing update response



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not plugin_id.strip():
            return FlextResult[FlextTypes.Core.Dict].fail("Plugin ID cannot be empty")

        try:
            json_data: FlextTypes.Core.Dict = {"plugin_id": plugin_id.strip()}
            if version and version.strip():
                json_data["version"] = version.strip()

            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.PUT,
                f"/api/v1/plugins/{plugin_id}",
                json_data=json_data,
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to update plugin: {e}"
            )

    # System methods
    async def get_system_status(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get system status and health information using railway pattern.

        Returns:
            FlextResult containing system status dictionary



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        try:
            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                "/api/v1/system/status",
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to get system status: {e}"
            )

    async def get_system_metrics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get system performance metrics using railway pattern.

        Returns:
            FlextResult containing system metrics dictionary



        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        try:
            response = await self._request(
                FlextCliConstants.Enums.HttpMethod.GET,
                "/api/v1/system/metrics",
            )
            return self._parse_json_response(response)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to get system metrics: {e}"
            )

    async def test_connection(self) -> FlextResult[bool]:
        """Test API connection using railway pattern - improved SOLID compliance.

        Returns:
            FlextResult[bool] - True if connection successful, False with error details



        Returns:
            FlextResult[bool]: Description of return value.

        """

        async def execute_health_check() -> FlextResult[httpx.Response]:
            """Execute health check request using flext-core safe patterns.

            Returns:
            FlextResult[httpx.Response]: Description of return value.

            """
            try:
                response = await self._request(
                    FlextCliConstants.Enums.HttpMethod.GET, "/api/v1/health"
                )
                return FlextResult[httpx.Response].ok(response)
            except Exception as e:
                return FlextResult[httpx.Response].fail(f"Health check failed: {e}")

        def process_connection_result(_response: httpx.Response) -> FlextResult[bool]:
            """Process connection test result.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            # Any successful response indicates connection is working
            return FlextResult[bool].ok(value=True)

        def log_connection_failure(error: str) -> FlextResult[bool]:
            """Log connection failure and return False - Single Responsibility.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            logger = FlextLogger(__name__)
            logger.warning(f"Connection test failed: {error}")
            return FlextResult[bool].ok(
                value=False
            )  # Connection test failure is not an error state

        # Railway pattern composition - leveraging flext-core patterns
        response_result = await execute_health_check()
        if response_result.is_failure:
            return log_connection_failure(response_result.error or "Unknown error")

        return process_connection_result(response_result.unwrap())


# ARCHITECTURAL COMPLIANCE: Aliases removed - use FlextCliModels.Pipeline directly


__all__ = ["FlextCliClient"]
