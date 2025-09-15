#!/usr/bin/env python3
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

import yaml
from flext_cli import (
    FlextApiClient,
    FlextCliAuth,
    FlextCliFormatters,
    FlextCliService,
)
from flext_core import FlextConfig, FlextResult


class EcosystemSettings(FlextConfig):
    """Configuration for FLEXT ecosystem integration."""

    # FLEXT Service endpoints
    flext_api_url: str = "http://localhost:8081"
    flexcore_url: str = "http://localhost:8080"

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

    class Config:
        """Pydantic model configuration."""

        env_prefix = "FLEXT_ECOSYSTEM_"


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

    def __init__(self) -> None:
        """Initialize ecosystem service."""
        super().__init__()
        self._settings = EcosystemSettings()
        self._api_client = FlextApiClient()
        self._auth_service = FlextCliAuth()
        self._formatters = FlextCliFormatters()

    def execute(self) -> FlextResult[str]:
        """Execute ecosystem service operation - FlextCliService interface."""
        return FlextResult[str].ok("Ecosystem service executed successfully")

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

    def authenticate_user(self, username: str, password: str) -> FlextResult[dict[str, object]]:
        """Authenticate user across FLEXT ecosystem."""
        # Simulate authentication since FlextCliAuth doesn't have authenticate method
        # Password is used for authentication validation
        _ = password  # Acknowledge parameter usage
        auth_data: dict[str, object] = {
            "username": username,
            "token": "mock_token_12345",
            "expires_in": self._settings.auth_token_expiry,
            "services": ["flext_api", "flext_core", "flext_auth"]
        }
        return FlextResult[dict[str, object]].ok(auth_data)

    def run_meltano_operation(self, operation: str, project: str) -> FlextResult[dict[str, object]]:
        """Run Meltano operation."""
        operations = {
            "run": {"status": "completed", "pipelines": 3, "duration": "2m 34s"},
            "test": {"status": "passed", "tests": 15, "duration": "45s"},
            "invoke": {"status": "completed", "tasks": 2, "duration": "1m 12s"},
            "install": {"status": "completed", "plugins": 8, "duration": "3m 45s"}
        }

        if operation not in operations:
            return FlextResult[dict[str, object]].fail(f"Unknown operation: {operation}")

        result_data: dict[str, object] = operations[operation].copy()
        result_data["project"] = project
        result_data["operation"] = operation

        return FlextResult[dict[str, object]].ok(result_data)

    def execute_oracle_query(self, query: str, schema: str = "public") -> FlextResult[dict[str, object]]:
        """Execute Oracle query."""
        # Simulate query execution
        query_data: dict[str, object] = {
            "query": query,
            "schema": schema,
            "rows_affected": 42,
            "execution_time": "156ms",
            "columns": ["id", "name", "created_at", "status"],
            "sample_data": [
                {"id": 1, "name": "Sample 1", "created_at": "2025-01-15", "status": "active"},
                {"id": 2, "name": "Sample 2", "created_at": "2025-01-16", "status": "inactive"},
            ]
        }
        return FlextResult[dict[str, object]].ok(query_data)

    def get_ecosystem_metrics(self) -> FlextResult[dict[str, object]]:
        """Get ecosystem metrics."""
        metrics_data: dict[str, object] = {
            "services": {
                "total": 6,
                "healthy": 6,
                "degraded": 0,
                "down": 0
            },
            "performance": {
                "avg_response_time": "45ms",
                "requests_per_minute": 1250,
                "error_rate": "0.02%"
            },
            "resources": {
                "cpu_usage": "23%",
                "memory_usage": "67%",
                "disk_usage": "45%"
            }
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
                "auth_token_expiry": self._settings.auth_token_expiry
            },
            "environment": "development",
            "version": "0.9.1"
        }
        return FlextResult[dict[str, object]].ok(config_data)


# CLI Functions - Using flext-cli patterns
# Note: This example demonstrates ecosystem integration patterns
# In production, use FlextCliMain for proper CLI implementation

def ecosystem_cli() -> None:
    """FLEXT Ecosystem Integration CLI - Example implementation."""
    print("FLEXT Ecosystem Integration CLI")
    print("This example demonstrates ecosystem integration patterns")
    print("Use FlextCliMain for production CLI implementation")

def health() -> None:
    """Show ecosystem health status."""
    service = EcosystemService()
    health_result = service.get_health_status()

    if health_result.is_success:
        health_data = health_result.unwrap()
        print("=== FLEXT Ecosystem Health ===")
        for service_name, status in health_data.items():
            if isinstance(status, dict) and isinstance(service_name, str):
                status_dict = status
                print(f"{service_name}: {status_dict.get('status', 'unknown')} ({status_dict.get('response_time', 'unknown')})")
    else:
        print(f"Health check failed: {health_result.error}")

def authenticate(username: str, password: str) -> None:
    """Authenticate user across FLEXT ecosystem."""
    service = EcosystemService()
    auth_result = service.authenticate_user(username, password)

    if auth_result.is_success:
        token_data = auth_result.unwrap()
        print("=== Authentication Results ===")
        if isinstance(token_data, dict):
            print(f"Username: {token_data.get('username', 'unknown')}")
            print(f"Token: {token_data.get('token', 'unknown')}")
            print(f"Expires in: {token_data.get('expires_in', 'unknown')} seconds")
            services = token_data.get("services", [])
            if isinstance(services, list):
                print(f"Services: {', '.join(str(s) for s in services)}")
    else:
        print(f"Authentication failed: {auth_result.error}")

def meltano(operation: str, project: str) -> None:
    """Run Meltano operation."""
    service = EcosystemService()
    meltano_result = service.run_meltano_operation(operation, project)

    if meltano_result.is_success:
        result_data = meltano_result.unwrap()
        print("=== Meltano Operation Results ===")
        if isinstance(result_data, dict):
            print(f"Project: {result_data.get('project', 'unknown')}")
            print(f"Operation: {result_data.get('operation', 'unknown')}")
            print(f"Status: {result_data.get('status', 'unknown')}")
            if "pipelines" in result_data:
                print(f"Pipelines: {result_data['pipelines']}")
            if "tests" in result_data:
                print(f"Tests: {result_data['tests']}")
            if "tasks" in result_data:
                print(f"Tasks: {result_data['tasks']}")
            if "plugins" in result_data:
                print(f"Plugins: {result_data['plugins']}")
            print(f"Duration: {result_data.get('duration', 'unknown')}")
    else:
        print(f"Meltano operation failed: {meltano_result.error}")

def oracle_query(query: str, schema: str = "public", output_format: str = "table") -> None:
    """Execute Oracle query."""
    service = EcosystemService()
    query_result = service.execute_oracle_query(query, schema)

    if query_result.is_success:
        query_data = query_result.unwrap()
        print("=== Oracle Query Results ===")
        if isinstance(query_data, dict):
            print(f"Query: {query_data.get('query', 'unknown')}")
            print(f"Schema: {query_data.get('schema', 'unknown')}")
            print(f"Rows affected: {query_data.get('rows_affected', 'unknown')}")
            print(f"Execution time: {query_data.get('execution_time', 'unknown')}")
            columns = query_data.get("columns", [])
            if isinstance(columns, list):
                print(f"Columns: {', '.join(str(c) for c in columns)}")

            sample_data = query_data.get("sample_data", [])
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
                            print(f"{row.get('id', '')},{row.get('name', '')},{row.get('created_at', '')},{row.get('status', '')}")
    else:
        print(f"Oracle query failed: {query_result.error}")

def metrics(output_format: str = "table") -> None:
    """Show ecosystem metrics."""
    service = EcosystemService()
    metrics_result = service.get_ecosystem_metrics()

    if metrics_result.is_success:
        metrics_data = metrics_result.unwrap()
        print("=== FLEXT Ecosystem Metrics ===")

        if isinstance(metrics_data, dict):
            if output_format == "table":
                print("Services:")
                services = metrics_data.get("services", {})
                if isinstance(services, dict):
                    print(f"  Total: {services.get('total', 'unknown')}")
                    print(f"  Healthy: {services.get('healthy', 'unknown')}")
                    print(f"  Degraded: {services.get('degraded', 'unknown')}")
                    print(f"  Down: {services.get('down', 'unknown')}")

                print("\nPerformance:")
                perf = metrics_data.get("performance", {})
                if isinstance(perf, dict):
                    print(f"  Avg Response Time: {perf.get('avg_response_time', 'unknown')}")
                    print(f"  Requests/min: {perf.get('requests_per_minute', 'unknown')}")
                    print(f"  Error Rate: {perf.get('error_rate', 'unknown')}")

                print("\nResources:")
                resources = metrics_data.get("resources", {})
                if isinstance(resources, dict):
                    print(f"  CPU Usage: {resources.get('cpu_usage', 'unknown')}")
                    print(f"  Memory Usage: {resources.get('memory_usage', 'unknown')}")
                    print(f"  Disk Usage: {resources.get('disk_usage', 'unknown')}")
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
        print("=== Ecosystem Configuration ===")
        if isinstance(config_data, dict):
            print(f"Environment: {config_data.get('environment', 'unknown')}")
            print(f"Version: {config_data.get('version', 'unknown')}")
            print("\nSettings:")
            settings = config_data.get("settings", {})
            if isinstance(settings, dict):
                for key, value in settings.items():
                    print(f"  {key}: {value}")
    else:
        print(f"Configuration retrieval failed: {config_result.error}")

