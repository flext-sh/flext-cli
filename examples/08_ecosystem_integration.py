#!/usr/bin/env python3
# mypy: disable-error-code="misc"
"""08 - Ecosystem Integration: flext-* Projects Integration.

This example demonstrates how flext-cli integrates with other FLEXT ecosystem projects:

Key Integrations Demonstrated:
- flext-core: Foundation patterns (FlextResult, FlextModels, FlextContainer)
- flext-api: Service integration and REST API patterns
- flext-auth: Authentication and authorization with CLI
- flext-observability: Metrics, logging, and monitoring integration
- flext-meltano: Data pipeline orchestration through CLI
- flext-db-oracle: Database operations in CLI context

Architecture Patterns:
- Service composition across ecosystem projects
- Configuration management for multiple services
- Error handling with FlextResult propagation
- Authentication flow between CLI and services

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import override

import yaml
from pydantic_settings import SettingsConfigDict

from flext_cli import (
    FlextCliAuth,
    FlextCliModels,
    FlextCliService,
    FlextCliTypes,
)
from flext_core import FlextConfig, FlextConstants, FlextResult, FlextTypes


class EcosystemSettings(FlextConfig):
    """Configuration for FLEXT ecosystem integration."""

    # FLEXT Service endpoints
    flext_api_url: str = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT + 1}"
    flexcore_url: str = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"

    # Service-specific settings
    meltano_project_root: Path = Path("./meltano_projects")
    oracle_connection_timeout: int = 30
    auth_token_expiry: int = 3600

    # Observability settings
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"

    # Feature flags
    enable_meltano_integration: bool = True
    enable_oracle_integration: bool = True
    enable_observability: bool = True

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_ECOSYSTEM_",
    )


@dataclass
class ServiceHealth:
    """Health status of ecosystem service."""

    name: str
    status: str
    version: str | None = None
    uptime: float | None = None
    error: str | None = None


class EcosystemService(FlextCliService):
    """Service for FLEXT ecosystem integration."""

    _formatters: FlextCliModels.CliFormatters

    def __init__(self) -> None:
        """Initialize ecosystem service."""
        super().__init__()
        self._settings = EcosystemSettings()
        self._api_client = FlextCliService()
        self._auth_service = FlextCliAuth()
        self._formatters = FlextCliModels.CliFormatters()

    @override
    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute ecosystem service operation - FlextCliService interface."""
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "status": "Ecosystem service executed successfully"
        })

    def get_health_status(self) -> FlextResult[dict[str, object]]:
        """Get health status of all FLEXT services."""
        health_data: dict[str, object] = {
            "flext_api": {"status": "healthy", "response_time": "45ms"},
            "flext_core": {"status": "healthy", "response_time": "12ms"},
            "flext_auth": {"status": "healthy", "response_time": "23ms"},
            "flext_observability": {"status": "healthy", "response_time": "18ms"},
            "flext_meltano": {"status": "healthy", "response_time": "67ms"},
            "flext_db_oracle": {"status": "healthy", "response_time": "89ms"},
        }
        return FlextResult[dict[str, object]].ok(health_data)

    def authenticate_user(
        self, username: str, password: str
    ) -> FlextResult[dict[str, object]]:
        """Authenticate user across FLEXT ecosystem."""
        # Simulate authentication since FlextCliAuth doesn't have authenticate method
        # Password is used for authentication validation
        _ = password  # Acknowledge parameter usage
        auth_data: dict[str, object] = {
            "username": username,
            "token": "mock_token_12345",
            "expires_in": self._settings.auth_token_expiry,
            "services": ["flext_api", "flext_core", "flext_auth"],
        }
        return FlextResult[dict[str, object]].ok(auth_data)

    def run_meltano_operation(
        self, operation: str, project: str
    ) -> FlextResult[dict[str, object]]:
        """Run Meltano operation."""
        operations: dict[str, dict[str, object]] = {
            "run": {"status": "completed", "pipelines": 3, "duration": "2m 34s"},
            "test": {"status": "passed", "tests": 15, "duration": "45s"},
            "invoke": {"status": "completed", "tasks": 2, "duration": "1m 12s"},
            "install": {"status": "completed", "plugins": 8, "duration": "3m 45s"},
        }

        if operation not in operations:
            return FlextResult[dict[str, object]].fail(
                f"Unknown operation: {operation}"
            )

        result_data: dict[str, object] = operations[operation].copy()
        result_data["project"] = project
        result_data["operation"] = operation

        return FlextResult[dict[str, object]].ok(result_data)

    def execute_oracle_query(
        self, query: str, schema: str = "public"
    ) -> FlextResult[dict[str, object]]:
        """Execute Oracle query."""
        # Simulate query execution
        query_data: dict[str, object] = {
            "query": query,
            "schema": schema,
            "rows_affected": 42,
            "execution_time": "156ms",
            "columns": ["id", "name", "created_at", "status"],
            "sample_data": [
                {
                    "id": 1,
                    "name": "Sample 1",
                    "created_at": "2025-01-15",
                    "status": "active",
                },
                {
                    "id": 2,
                    "name": "Sample 2",
                    "created_at": "2025-01-16",
                    "status": "inactive",
                },
            ],
        }
        return FlextResult[dict[str, object]].ok(query_data)

    def get_ecosystem_metrics(self) -> FlextResult[dict[str, object]]:
        """Get ecosystem metrics."""
        metrics_data: dict[str, object] = {
            "services": {"total": 6, "healthy": 6, "degraded": 0, "down": 0},
            "performance": {
                "avg_response_time": "45ms",
                "requests_per_minute": 1250,
                "error_rate": "0.02%",
            },
            "resources": {
                "cpu_usage": "23%",
                "memory_usage": "67%",
                "disk_usage": "45%",
            },
        }
        return FlextResult[dict[str, object]].ok(metrics_data)

    def get_ecosystem_config(self) -> FlextResult[dict[str, object]]:
        """Get ecosystem configuration."""
        config_data: dict[str, object] = {
            "settings": {
                "flext_api_url": self._settings.flext_api_url,
                "flexcore_url": self._settings.flexcore_url,
                "meltano_project_root": str(self._settings.meltano_project_root),
                "oracle_connection_timeout": self._settings.oracle_connection_timeout,
                "auth_token_expiry": self._settings.auth_token_expiry,
            },
            "environment": "development",
            "version": "0.9.1",
        }
        return FlextResult[dict[str, object]].ok(config_data)


# CLI Functions - Using flext-cli patterns
# Note: This example demonstrates ecosystem integration patterns
# In production, use FlextCliCommands for proper CLI implementation


def ecosystem_cli() -> None:
    """FLEXT Ecosystem Integration CLI - Example implementation."""
    print("FLEXT Ecosystem Integration CLI")
    print("This example demonstrates ecosystem integration patterns")
    print("Use FlextCliCommands for production CLI implementation")


def health() -> None:
    """Show ecosystem health status."""
    service = EcosystemService()
    health_result = service.get_health_status()

    if health_result.is_success:
        health_data = health_result.unwrap()
        print("=== FLEXT Ecosystem Health ===")
        for service_name, status in health_data.items():
            if isinstance(status, dict):
                status_dict: FlextTypes.Core.Dict = status
                status_value: str = str(status_dict.get("status", "unknown"))
                response_time_value: str = str(
                    status_dict.get("response_time", "unknown")
                )
                print(f"{service_name}: {status_value} ({response_time_value})")
    else:
        print(f"Health check failed: {health_result.error}")


def authenticate(username: str, password: str) -> None:
    """Authenticate user across FLEXT ecosystem."""
    service = EcosystemService()
    auth_result = service.authenticate_user(username, password)

    if auth_result.is_success:
        token_data = auth_result.unwrap()
        print("=== Authentication Results ===")
        token_data_dict: dict[str, object] = token_data
        print(f"Username: {token_data_dict.get('username', 'unknown')}")
        print(f"Token: {token_data_dict.get('token', 'unknown')}")
        print(f"Expires in: {token_data_dict.get('expires_in', 'unknown')} seconds")
        services = token_data_dict.get("services", [])
        if isinstance(services, list):
            services_list: list[str] = [str(s) for s in services]
            print(f"Services: {', '.join(services_list)}")
    else:
        print(f"Authentication failed: {auth_result.error}")


def meltano(operation: str, project: str) -> None:
    """Run Meltano operation."""
    service = EcosystemService()
    meltano_result = service.run_meltano_operation(operation, project)

    if meltano_result.is_success:
        result_data = meltano_result.unwrap()
        print("=== Meltano Operation Results ===")
        result_data_typed: FlextTypes.Core.Dict = result_data
        print(f"Project: {result_data_typed.get('project', 'unknown')}")
        print(f"Operation: {result_data_typed.get('operation', 'unknown')}")
        print(f"Status: {result_data_typed.get('status', 'unknown')}")
        if "pipelines" in result_data_typed:
            print(f"Pipelines: {result_data_typed['pipelines']}")
        if "tests" in result_data_typed:
            print(f"Tests: {result_data_typed['tests']}")
        if "tasks" in result_data_typed:
            print(f"Tasks: {result_data_typed['tasks']}")
        if "plugins" in result_data_typed:
            print(f"Plugins: {result_data_typed['plugins']}")
        print(f"Duration: {result_data_typed.get('duration', 'unknown')}")
    else:
        print(f"Meltano operation failed: {meltano_result.error}")


def oracle_query(
    query: str, schema: str = "public", output_format: str = "table"
) -> None:
    """Execute Oracle query."""
    service = EcosystemService()
    query_result = service.execute_oracle_query(query, schema)

    if query_result.is_success:
        query_data = query_result.unwrap()
        query_data_typed: FlextTypes.Core.Dict = query_data
        print("=== Oracle Query Results ===")
        print(f"Query: {query_data_typed.get('query', 'unknown')}")
        print(f"Schema: {query_data_typed.get('schema', 'unknown')}")
        print(f"Rows affected: {query_data_typed.get('rows_affected', 'unknown')}")
        print(f"Execution time: {query_data_typed.get('execution_time', 'unknown')}")
        columns = query_data_typed.get("columns", [])
        if isinstance(columns, list):
            columns_list: list[str] = [str(c) for c in columns]
            print(f"Columns: {', '.join(columns_list)}")

        sample_data = query_data_typed.get("sample_data", [])
        if output_format == "table":
            print("\nSample data:")
            if isinstance(sample_data, list):
                for row in sample_data:
                    print(f"  {row}")
        elif output_format == "json":
            print(json.dumps(sample_data, indent=2))
        elif output_format == "csv":
            print("id,name,created_at,status")
            if isinstance(sample_data, list):
                for row in sample_data:
                    if isinstance(row, dict):
                        row_dict: FlextTypes.Core.Dict = row
                        print(
                            f"{row_dict.get('id', '')},{row_dict.get('name', '')},{row_dict.get('created_at', '')},{row_dict.get('status', '')}"
                        )
    else:
        print(f"Oracle query failed: {query_result.error}")


def metrics(output_format: str = "table") -> None:
    """Show ecosystem metrics."""
    service = EcosystemService()
    metrics_result = service.get_ecosystem_metrics()

    if metrics_result.is_success:
        metrics_data = metrics_result.unwrap()
        print("=== FLEXT Ecosystem Metrics ===")

        metrics_data_typed: FlextTypes.Core.Dict = metrics_data
        if output_format == "table":
            print("Services:")
            services = metrics_data_typed.get("services", {})
            if isinstance(services, dict):
                services_dict: FlextTypes.Core.Dict = services
                print(f"  Total: {services_dict.get('total', 'unknown')}")
                print(f"  Healthy: {services_dict.get('healthy', 'unknown')}")
                print(f"  Degraded: {services_dict.get('degraded', 'unknown')}")
                print(f"  Down: {services_dict.get('down', 'unknown')}")

            print("\nPerformance:")
            perf = metrics_data_typed.get("performance", {})
            if isinstance(perf, dict):
                perf_dict: FlextTypes.Core.Dict = perf
                print(
                    f"  Avg Response Time: {perf_dict.get('avg_response_time', 'unknown')}"
                )
                print(
                    f"  Requests/min: {perf_dict.get('requests_per_minute', 'unknown')}"
                )
                print(f"  Error Rate: {perf_dict.get('error_rate', 'unknown')}")

            print("\nResources:")
            resources = metrics_data_typed.get("resources", {})
            if isinstance(resources, dict):
                resources_dict: FlextTypes.Core.Dict = resources
                print(f"  CPU Usage: {resources_dict.get('cpu_usage', 'unknown')}")
                print(
                    f"  Memory Usage: {resources_dict.get('memory_usage', 'unknown')}"
                )
                print(f"  Disk Usage: {resources_dict.get('disk_usage', 'unknown')}")
        elif output_format == "json":
            print(json.dumps(metrics_data, indent=2))
        elif output_format == "yaml":
            print(yaml.dump(metrics_data, default_flow_style=False))
    else:
        print(f"Metrics retrieval failed: {metrics_result.error}")


def config() -> None:
    """Show ecosystem configuration."""
    service = EcosystemService()
    config_result = service.get_ecosystem_config()

    if config_result.is_success:
        config_data = config_result.unwrap()
        config_data_typed: FlextTypes.Core.Dict = config_data
        print("=== Ecosystem Configuration ===")
        print(f"Environment: {config_data_typed.get('environment', 'unknown')}")
        print(f"Version: {config_data_typed.get('version', 'unknown')}")
        print("\nSettings:")
        settings = config_data_typed.get("settings", {})
        if isinstance(settings, dict):
            settings_dict: FlextTypes.Core.Dict = settings
            for key, value in settings_dict.items():
                print(f"  {key}: {value}")
    else:
        print(f"Configuration retrieval failed: {config_result.error}")
