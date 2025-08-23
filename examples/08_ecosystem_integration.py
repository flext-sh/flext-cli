#!/usr/bin/env python3
"""08 - Ecosystem Integration: flext-* Projects Integration.

This example demonstrates how flext-cli integrates with other FLEXT ecosystem projects:

Key Integrations Demonstrated:
- flext-core: Foundation patterns (FlextResult, FlextModel, FlextContainer)
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

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
from flext_core import FlextResult, FlextSettings
from rich.console import Console
from rich.table import Table

from flext_cli import (
    FlextApiClient,
    FlextCliService,
    cli_create_table,
    cli_enhanced,
    cli_format_output,
    measure_time,
    require_auth,
    save_auth_token,
)

# =============================================================================
# ECOSYSTEM CONFIGURATION - Multi-service configuration
# =============================================================================


class EcosystemSettings(FlextSettings):
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


# =============================================================================
# ECOSYSTEM SERVICE INTEGRATION
# =============================================================================


class EcosystemService(FlextCliService[dict[str, Any]]):
    """Service for integrating with FLEXT ecosystem projects."""

    def __init__(self, settings: EcosystemSettings, **data: object) -> None:
        super().__init__(service_name="ecosystem_integration", **data)
        self.settings = settings
        self.api_client = FlextApiClient(base_url=settings.flext_api_url)

    def check_service_health(
        self, service_name: str, _url: str
    ) -> FlextResult[ServiceHealth]:
        """Check health of ecosystem service."""
        try:
            # Simulate health check (in real implementation, make HTTP request)
            # health_endpoint = urljoin(url, "/health")  # Would be used for actual HTTP request

            # Mock response for demonstration
            if service_name == "flext-api":
                return FlextResult[str].ok(
                    ServiceHealth(
                        name=service_name,
                        status="healthy",
                        version="2.0.0",
                        uptime=1234.5,
                    )
                )
            if service_name == "flexcore":
                return FlextResult[str].ok(
                    ServiceHealth(
                        name=service_name,
                        status="healthy",
                        version="1.5.0",
                        uptime=987.3,
                    )
                )
            return FlextResult[str].ok(
                ServiceHealth(
                    name=service_name, status="unknown", error="Service not recognized"
                )
            )

        except Exception as e:
            return FlextResult[str].fail(f"Health check failed for {service_name}: {e}")

    def get_ecosystem_status(self) -> FlextResult[list[ServiceHealth]]:
        """Get status of all ecosystem services."""
        services = [
            ("flext-api", self.settings.flext_api_url),
            ("flexcore", self.settings.flexcore_url),
        ]

        health_results = []

        for service_name, url in services:
            health_result = self.check_service_health(service_name, url)
            if health_result.is_success:
                health_results.append(health_result.value)
            else:
                health_results.append(
                    ServiceHealth(
                        name=service_name, status="error", error=health_result.error
                    )
                )

        return FlextResult[str].ok(health_results)

    def authenticate_with_services(
        self, username: str, password: str
    ) -> FlextResult[dict[str, str]]:
        """Authenticate with FLEXT services and get tokens."""
        auth_results = {}

        # Authenticate with FLEXT API
        api_auth_result = self.api_client.authenticate(username, password)
        if api_auth_result.is_success:
            auth_results["flext-api"] = "authenticated"

            # Save token for CLI usage
            token_save_result = save_auth_token(api_auth_result.value.get("token", ""))
            if token_save_result.is_failure:
                return FlextResult[str].fail(
                    f"Failed to save auth token: {token_save_result.error}"
                )
        else:
            auth_results["flext-api"] = f"failed: {api_auth_result.error}"

        # Mock authentication with other services
        auth_results["flexcore"] = "authenticated"
        auth_results["flext-observability"] = "authenticated"

        return FlextResult[str].ok(auth_results)

    def execute_meltano_operation(
        self, operation: str, project: str
    ) -> FlextResult[dict[str, Any]]:
        """Execute Meltano operation through flext-meltano integration."""
        if not self.settings.enable_meltano_integration:
            return FlextResult[str].fail("Meltano integration is disabled")

        # Mock Meltano operation (in real implementation, use flext-meltano)
        try:
            result = {
                "operation": operation,
                "project": project,
                "status": "completed",
                "duration": 45.2,
                "records_processed": 1000 if operation == "run" else 0,
                "message": f"Meltano {operation} completed successfully",
            }
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"Meltano operation failed: {e}")

    def query_oracle_database(
        self, _query: str, _schema: str
    ) -> FlextResult[list[dict[str, Any]]]:
        """Query Oracle database through flext-db-oracle integration."""
        if not self.settings.enable_oracle_integration:
            return FlextResult[str].fail("Oracle integration is disabled")

        # Mock Oracle query (in real implementation, use flext-db-oracle)
        try:
            mock_results = [
                {"id": 1, "name": "Project Alpha", "status": "active"},
                {"id": 2, "name": "Project Beta", "status": "completed"},
                {"id": 3, "name": "Project Gamma", "status": "pending"},
            ]
            return FlextResult[str].ok(mock_results)
        except Exception as e:
            return FlextResult[str].fail(f"Oracle query failed: {e}")

    def get_observability_metrics(self) -> FlextResult[dict[str, Any]]:
        """Get metrics from flext-observability."""
        if not self.settings.enable_observability:
            return FlextResult[str].fail("Observability is disabled")

        # Mock metrics (in real implementation, use flext-observability)
        try:
            metrics = {
                "api_requests_total": 15420,
                "api_request_duration_avg": 0.245,
                "error_rate": 0.02,
                "active_sessions": 45,
                "database_connections": 12,
                "memory_usage_mb": 256.8,
                "cpu_usage_percent": 12.5,
            }
            return FlextResult[str].ok(metrics)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to get metrics: {e}")


# =============================================================================
# CLI COMMANDS - Ecosystem integration interface
# =============================================================================


@click.group()
@click.pass_context
def ecosystem_cli(ctx: click.Context) -> None:
    """FLEXT Ecosystem Integration CLI."""
    ctx.ensure_object(dict)
    ctx.obj["console"] = Console()
    ctx.obj["settings"] = EcosystemSettings()
    ctx.obj["service"] = EcosystemService(ctx.obj["settings"])


@ecosystem_cli.command()
@click.pass_context
@cli_enhanced
@measure_time
def health(ctx: click.Context) -> None:
    """Check health of all ecosystem services."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    console.print("[blue]Checking ecosystem service health...[/blue]")

    result = service.get_ecosystem_status()

    if result.is_success:
        health_data = result.value

        table = Table(title="FLEXT Ecosystem Health")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Uptime (s)", style="blue")
        table.add_column("Error", style="red")

        for health in health_data:
            status_color = "green" if health.status == "healthy" else "red"
            table.add_row(
                health.name,
                f"[{status_color}]{health.status}[/{status_color}]",
                health.version or "N/A",
                str(health.uptime) if health.uptime else "N/A",
                health.error or "",
            )

        console.print(table)
    else:
        console.print(f"[red]❌ Failed to check ecosystem health: {result.error}[/red]")


@ecosystem_cli.command()
@click.option("--username", required=True, help="Username for authentication")
@click.option("--password", required=True, hide_input=True, help="Password")
@click.pass_context
@cli_enhanced
@measure_time
def authenticate(ctx: click.Context, username: str, password: str) -> None:
    """Authenticate with all ecosystem services."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    console.print("[blue]Authenticating with ecosystem services...[/blue]")

    result = service.authenticate_with_services(username, password)

    if result.is_success:
        auth_results = result.value

        table = Table(title="Authentication Results")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")

        for service_name, status in auth_results.items():
            status_color = "green" if status == "authenticated" else "red"
            table.add_row(service_name, f"[{status_color}]{status}[/{status_color}]")

        console.print(table)
        console.print("[green]✅ Authentication tokens saved for CLI usage[/green]")
    else:
        console.print(f"[red]❌ Authentication failed: {result.error}[/red]")


@ecosystem_cli.command()
@click.option(
    "--operation",
    required=True,
    type=click.Choice(["run", "test", "invoke", "install"]),
    help="Meltano operation to execute",
)
@click.option("--project", required=True, help="Meltano project name")
@click.pass_context
@cli_enhanced
@measure_time
@require_auth()
def meltano(ctx: click.Context, operation: str, project: str) -> None:
    """Execute Meltano operations through flext-meltano integration."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    console.print(
        f"[blue]Executing Meltano {operation} for project {project}...[/blue]"
    )

    result = service.execute_meltano_operation(operation, project)

    if result.is_success:
        data = result.value
        console.print(f"[green]✅ {data['message']}[/green]")
        console.print(f"Duration: {data['duration']:.1f}s")
        if data["records_processed"] > 0:
            console.print(f"Records processed: {data['records_processed']:,}")
    else:
        console.print(f"[red]❌ Meltano operation failed: {result.error}[/red]")


@ecosystem_cli.command()
@click.option("--query", required=True, help="SQL query to execute")
@click.option("--schema", default="public", help="Database schema")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
@click.pass_context
@cli_enhanced
@measure_time
@require_auth()
def oracle_query(
    ctx: click.Context, query: str, schema: str, output_format: str
) -> None:
    """Query Oracle database through flext-db-oracle integration."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    console.print(f"[blue]Executing Oracle query in schema {schema}...[/blue]")

    result = service.query_oracle_database(query, schema)

    if result.is_success:
        data = result.value

        if output_format == "table":
            table = cli_create_table(data, title=f"Query Results ({len(data)} rows)")
            console.print(table)
        else:
            formatted_result = cli_format_output(data, output_format)
            if formatted_result.is_success:
                console.print(formatted_result.value)
            else:
                console.print(f"[red]❌ Format error: {formatted_result.error}[/red]")
    else:
        console.print(f"[red]❌ Oracle query failed: {result.error}[/red]")


@ecosystem_cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.pass_context
@cli_enhanced
@measure_time
def metrics(ctx: click.Context, output_format: str) -> None:
    """Get observability metrics from flext-observability."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    console.print("[blue]Fetching observability metrics...[/blue]")

    result = service.get_observability_metrics()

    if result.is_success:
        metrics_data = result.value

        if output_format == "table":
            table = Table(title="FLEXT Ecosystem Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            for metric, value in metrics_data.items():
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                elif isinstance(value, int):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = str(value)

                table.add_row(metric.replace("_", " ").title(), formatted_value)

            console.print(table)
        else:
            formatted_result = cli_format_output(metrics_data, output_format)
            if formatted_result.is_success:
                console.print(formatted_result.value)
            else:
                console.print(f"[red]❌ Format error: {formatted_result.error}[/red]")
    else:
        console.print(f"[red]❌ Failed to get metrics: {result.error}[/red]")


@ecosystem_cli.command()
@click.pass_context
@cli_enhanced
def config(ctx: click.Context) -> None:
    """Show ecosystem integration configuration."""
    console: Console = ctx.obj["console"]
    settings: EcosystemSettings = ctx.obj["settings"]

    table = Table(title="Ecosystem Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    config_items = [
        ("FLEXT API URL", settings.flext_api_url),
        ("FlexCore URL", settings.flexcore_url),
        ("Meltano Project Root", str(settings.meltano_project_root)),
        ("Oracle Timeout", f"{settings.oracle_connection_timeout}s"),
        ("Auth Token Expiry", f"{settings.auth_token_expiry}s"),
        ("Log Level", settings.log_level),
        ("Meltano Integration", "✅" if settings.enable_meltano_integration else "❌"),
        ("Oracle Integration", "✅" if settings.enable_oracle_integration else "❌"),
        ("Observability", "✅" if settings.enable_observability else "❌"),
        ("Metrics", "✅" if settings.enable_metrics else "❌"),
        ("Tracing", "✅" if settings.enable_tracing else "❌"),
    ]

    for setting, value in config_items:
        table.add_row(setting, str(value))

    console.print(table)


def main() -> None:
    """Run ecosystem integration demonstration."""
    print("🌐 Ecosystem Integration: FLEXT-* Projects Integration")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("✅ flext-core foundation integration")
    print("✅ flext-api service communication")
    print("✅ flext-auth authentication flow")
    print("✅ flext-meltano data pipeline operations")
    print("✅ flext-db-oracle database integration")
    print("✅ flext-observability metrics collection")
    print("✅ Cross-service configuration management")
    print()
    print("Try these commands:")
    print("  python examples/08_ecosystem_integration.py health")
    print("  python examples/08_ecosystem_integration.py authenticate --username admin")
    print("  python examples/08_ecosystem_integration.py config")
    print(
        "  python examples/08_ecosystem_integration.py meltano --operation run --project tap-to-target"
    )
    print(
        "  python examples/08_ecosystem_integration.py oracle-query --query 'SELECT * FROM projects'"
    )
    print("  python examples/08_ecosystem_integration.py metrics")
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        main()
    else:
        ecosystem_cli()
