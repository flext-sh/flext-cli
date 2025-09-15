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

from dataclasses import dataclass
from pathlib import Path

from flext_core import FlextConfig, FlextResult, FlextTypes

from flext_cli import (
    FlextApiClient,
    FlextCliService,
    FlextCliFormatters,
    FlextCliAuth,
    FlextCliMain,
)


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
    """Service for integrating with FLEXT ecosystem projects."""

    def __init__(self, settings: EcosystemSettings, **data: object) -> None:
        super().__init__(**data)
        self.settings = settings
        self.api_client = FlextApiClient(base_url=settings.flext_api_url)

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute ecosystem service operations."""
        return FlextResult[FlextTypes.Core.Dict].ok(
            {
                "service": "ecosystem_integration",
                "status": "running",
            }
        )

    def check_service_health(
        self, service_name: str, _url: str
    ) -> FlextResult[ServiceHealth]:
        """Check health of ecosystem service."""
        try:
            # Simulate health check (in real implementation, make HTTP request)
            # health_endpoint = urljoin(url, "/health")  # Would be used for actual HTTP request

            # Mock response for demonstration
            if service_name == "flext-api":
                return FlextResult[ServiceHealth].ok(
                    ServiceHealth(
                        name=service_name,
                        status="healthy",
                        version="2.0.0",
                        uptime=1234.5,
                    )
                )
            if service_name == "flexcore":
                return FlextResult[ServiceHealth].ok(
                    ServiceHealth(
                        name=service_name,
                        status="healthy",
                        version="1.5.0",
                        uptime=987.3,
                    )
                )
            return FlextResult[ServiceHealth].ok(
                ServiceHealth(
                    name=service_name, status="unknown", error="Service not recognized"
                )
            )

        except Exception as e:
            return FlextResult[ServiceHealth].fail(
                f"Health check failed for {service_name}: {e}"
            )

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

        return FlextResult[list[ServiceHealth]].ok(health_results)

    def authenticate_with_services(
        self, username: str, password: str
    ) -> FlextResult[FlextTypes.Core.Headers]:
        """Authenticate with FLEXT services and get tokens."""
        # These parameters would be used for actual authentication
        # but are unused in this demo implementation
        _ = username, password
        auth_results = {}

        # Authenticate with FLEXT API
        # Simulate authentication since authenticate method doesn't exist
        try:
            # api_auth_result = self.api_client.authenticate(username, password)
            # FlextApiClient doesn't have authenticate method - simulate it
            api_auth_result = FlextResult[FlextTypes.Core.Headers].ok(
                {
                    "token": "demo_token",
                    "status": "authenticated",
                }
            )
        except Exception:
            api_auth_result = FlextResult[FlextTypes.Core.Headers].fail(
                "Authentication simulation failed"
            )
        if api_auth_result.is_success:
            auth_results["flext-api"] = "authenticated"

            # Save token for CLI usage
            token_save_result = save_auth_token(api_auth_result.value.get("token", ""))
            if token_save_result.is_failure:
                return FlextResult[FlextTypes.Core.Headers].fail(
                    f"Failed to save auth token: {token_save_result.error}"
                )
        else:
            auth_results["flext-api"] = f"failed: {api_auth_result.error}"

        # Mock authentication with other services
        auth_results["flexcore"] = "authenticated"
        auth_results["flext-observability"] = "authenticated"

        return FlextResult[FlextTypes.Core.Headers].ok(auth_results)

    def execute_meltano_operation(
        self, operation: str, project: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute Meltano operation through flext-meltano integration."""
        if not self.settings.enable_meltano_integration:
            return FlextResult[FlextTypes.Core.Dict].fail(
                "Meltano integration is disabled"
            )

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
            return FlextResult[FlextTypes.Core.Dict].ok(result)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Meltano operation failed: {e}")

    def query_oracle_database(
        self, _query: str, _schema: str
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Query Oracle database through flext-db-oracle integration."""
        if not self.settings.enable_oracle_integration:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                "Oracle integration is disabled"
            )

        # Mock Oracle query (in real implementation, use flext-db-oracle)
        try:
            mock_results = [
                {"id": 1, "name": "Project Alpha", "status": "active"},
                {"id": 2, "name": "Project Beta", "status": "completed"},
                {"id": 3, "name": "Project Gamma", "status": "pending"},
            ]
            return FlextResult[list[FlextTypes.Core.Dict]].ok(mock_results)
        except Exception as e:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                f"Oracle query failed: {e}"
            )

    def get_observability_metrics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get metrics from flext-observability."""
        if not self.settings.enable_observability:
            return FlextResult[FlextTypes.Core.Dict].fail("Observability is disabled")

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
            return FlextResult[FlextTypes.Core.Dict].ok(dict(metrics))
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Failed to get metrics: {e}")





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
        records = data["records_processed"]
        if isinstance(records, int) and records > 0:
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
@require_auth()
def oracle_query(ctx: click.Context, query: str, schema: str, output_format: str) -> None:
    """Query Oracle database through flext-db-oracle integration using advanced patterns."""
    console: Console = ctx.obj["console"]
    service: EcosystemService = ctx.obj["service"]

    # Use FlextPipeline pattern to reduce complexity and eliminate multiple returns
    def execute_query_pipeline() -> FlextResult[None]:
        """Execute Oracle query using pipeline pattern."""
        # Step 1: Announce execution
        console.print(f"[blue]Executing Oracle query in schema {schema}...[/blue]")

        # Step 2: Execute query
        query_result = service.query_oracle_database(query, schema)
        if query_result.is_failure:
            console.print(f"[red]❌ Oracle query failed: {query_result.error}[/red]")
            return FlextResult[None].fail(query_result.error)

        # Step 3: Format output using Python 3.13+ match-case
        format_result = _format_oracle_output(console, query_result.value, output_format)
        return format_result.map(lambda _: None)  # Convert to None for consistent return

    # Execute pipeline
    execute_query_pipeline()


def _format_oracle_output(console: Console, data: object, output_format: str) -> FlextResult[str]:
    """Format Oracle query output using Python 3.13+ match-case patterns."""
    # Python 3.13+ pattern matching for cleaner control flow
    match output_format:
        case "table":
            return _handle_table_format(console, data)
        case "json" | "csv":
            return _handle_structured_format(console, data, output_format)
        case _:
            error_msg = f"Unsupported output format: {output_format}"
            console.print(f"[red]❌ {error_msg}[/red]")
            return FlextResult[str].fail(error_msg)


def _handle_table_format(console: Console, data: object) -> FlextResult[str]:
    """Handle table output format with functional patterns."""
    # Convert data to list of dicts for table display
    table_data: list[FlextTypes.Core.Dict]
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        table_data = data
    elif isinstance(data, dict):
        table_data = [data]
    else:
        # Fallback: create a single-column table
        table_data = [{"value": str(data)}]

    row_count = len(table_data)
    table = cli_create_table(table_data, title=f"Query Results ({row_count} rows)")
    console.print(table)
    return FlextResult[str].ok(str(data))


def _handle_structured_format(console: Console, data: object, format_type: str) -> FlextResult[str]:
    """Handle JSON/CSV formats with error handling."""
    format_data = _prepare_display_data(data)
    formatted_result = cli_format_output(format_data, format_type)

    # cli_format_output returns a string, not FlextResult
    console.print(formatted_result)
    return FlextResult[str].ok(formatted_result)


def _prepare_display_data(data: object) -> str:
    """Prepare data for display using functional approach."""
    match data:
        case list() | dict() if data:
            return str(data)
        case _:
            return str(data)


def _calculate_row_count(data: object) -> int:
    """Calculate row count using safe pattern matching."""
    match data:
        case list() as items:
            return len(items)
        case dict() as mapping:
            return len(mapping)
        case _ if hasattr(data, "__len__"):
            return len(data)
        case _:
            return 0


def _display_formatted_success(console: Console, value: str) -> FlextResult[str]:
    """Display successful formatted output."""
    console.print(value)
    return FlextResult[str].ok(value)


def _display_format_error(console: Console, error: str) -> FlextResult[str]:
    """Display formatting error."""
    console.print(f"[red]❌ Format error: {error}[/red]")
    return FlextResult[str].fail(error)


@ecosystem_cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.pass_context
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
            # cli_format_output returns a string directly
            console.print(formatted_result)
    else:
        console.print(f"[red]❌ Failed to get metrics: {result.error}[/red]")


@ecosystem_cli.command()
@click.pass_context
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        main()
    else:
        ecosystem_cli()
