"""GrupoNOS Meltano Native commands for flext-cli.

GrupoNOS Meltano Native CLI commands integrated into the unified FLEXT CLI.
Preserves ALL original functionality from gruponos-meltano-native/cli.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib.metadata
import json
import sys

import click
import structlog
import yaml

# Import GrupoNOS modules - preserving original imports
try:
    from gruponos_meltano_native.config import (
        GrupoNOSConfig,
    )
    from gruponos_meltano_native.orchestrator import (
        GrupoNOSMeltanoOrchestrator,
    )

    GRUPONOS_AVAILABLE = True
except ImportError as e:
    # Graceful handling when gruponos-meltano-native is not available
    click.echo(f"Warning: GrupoNOS Meltano Native not available: {e}", err=True)
    GRUPONOS_AVAILABLE = False

# Define fallback values when imports fail
if not GRUPONOS_AVAILABLE:
    GrupoNOSConfig = None
    GrupoNOSMeltanoOrchestrator = None

# Setup logger
logger = structlog.get_logger(__name__)


@click.group(name="gruponos")
@click.version_option()
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.pass_context
def gruponos(
    ctx: click.Context,
    *,
    debug: bool,
    config_file: str | None,
) -> None:
    """GrupoNOS Meltano Native - Enterprise ETL Pipeline."""
    if not GRUPONOS_AVAILABLE:
        click.echo(
            "Error: GrupoNOS Meltano Native package not available. Please install "
            "gruponos-meltano-native.",
            err=True,
        )
        ctx.exit(1)

    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["config_file"] = config_file

    # Configure logging level
    if debug:
        structlog.configure(
            processors=[
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
            cache_logger_on_first_use=True,
        )
        logger.debug("Debug mode enabled")
    else:
        structlog.configure(
            processors=[
                structlog.dev.ConsoleRenderer(colors=False),
            ],
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.make_filtering_bound_logger(30),  # WARNING level
            cache_logger_on_first_use=True,
        )

    try:
        if config_file:
            config = GrupoNOSConfig.from_file(config_file)
        else:
            config = GrupoNOSConfig()

        ctx.obj["config"] = config
        logger.info("Configuration loaded successfully")

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to load configuration")
        if debug:
            raise
        ctx.exit(1)


@gruponos.command()
@click.option(
    "--format",
    "output_format",
    default="table",
    help="Output format (table, json, yaml)",
)
@click.pass_context
def status(ctx: click.Context, output_format: str) -> None:
    """Display GrupoNOS Meltano Native status information."""
    try:
        config = ctx.obj["config"]
        # Get debug mode from context

        # Initialize orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        # Get status
        status_info = orchestrator.get_status()

        if output_format == "table":
            click.echo("GrupoNOS Meltano Native Status")
            click.echo("=" * 30)
            click.echo(f"Environment: {status_info.get('environment', 'unknown')}")
            click.echo(f"Version: {status_info.get('version', 'unknown')}")
            click.echo(f"Status: {status_info.get('status', 'unknown')}")
            click.echo(f"Last Run: {status_info.get('last_run', 'never')}")

            # Show pipelines
            pipelines = status_info.get("pipelines", [])
            if pipelines:
                click.echo("\nPipelines:")
                for pipeline in pipelines:
                    status_emoji = "✅" if pipeline.get("status") == "healthy" else "❌"
                    click.echo(
                        f"  {status_emoji} {pipeline.get('name', 'unknown')}: "
                        f"{pipeline.get('status', 'unknown')}",
                    )

        elif output_format == "json":
            click.echo(json.dumps(status_info, indent=2))

        elif output_format == "yaml":
            click.echo(yaml.dump(status_info, default_flow_style=False))

        else:
            click.echo(f"Unknown format: {output_format}", err=True)
            ctx.exit(1)

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to get status")
        if ctx.obj.get("debug"):
            raise
        ctx.exit(1)


@gruponos.command()
@click.argument("pipeline_name")
@click.option("--environment", help="Environment to run in")
@click.option("--full-refresh", is_flag=True, help="Run full refresh")
@click.option("--dry-run", is_flag=True, help="Dry run - don't actually execute")
@click.pass_context
async def run(
    ctx: click.Context,
    pipeline_name: str,
    environment: str | None,
    **kwargs: bool,
) -> None:
    """Run a GrupoNOS pipeline."""
    try:
        config = ctx.obj["config"]
        debug = ctx.obj.get("debug", False)
        full_refresh = kwargs.get("full_refresh", False)
        dry_run = kwargs.get("dry_run", False)

        # Initialize orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        if dry_run:
            click.echo(f"🔍 Dry run mode - would execute pipeline: {pipeline_name}")
            if environment:
                click.echo(f"Environment: {environment}")
            if full_refresh:
                click.echo("Mode: Full refresh")
            click.echo("✅ Dry run completed - no actual execution")
            return

        click.echo(f"🚀 Running pipeline: {pipeline_name}")
        if environment:
            click.echo(f"🌍 Environment: {environment}")
        if full_refresh:
            click.echo("🔄 Mode: Full refresh")

        # Execute pipeline
        result = await orchestrator.run_pipeline(
            pipeline_name=pipeline_name,
            environment=environment,
            full_refresh=full_refresh,
        )

        if result.success:
            click.echo("✅ Pipeline completed successfully!")
            if result.metrics:
                click.echo(
                    f"📊 Records processed: "
                    f"{result.metrics.get('records_processed', 0)}",
                )
                click.echo(f"⏱️  Duration: {result.metrics.get('duration', 'unknown')}")
        else:
            click.echo(f"❌ Pipeline failed: {result.error}", err=True)
            if debug and result.details:
                click.echo(f"Details: {result.details}", err=True)
            ctx.exit(1)

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to run pipeline")
        if debug:
            raise
        ctx.exit(1)


@gruponos.command()
@click.option(
    "--format",
    "output_format",
    default="table",
    help="Output format (table, json, yaml)",
)
@click.pass_context
def pipelines(ctx: click.Context, output_format: str) -> None:
    """List available GrupoNOS pipelines."""
    try:
        config = ctx.obj["config"]

        # Initialize orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        # Get pipelines
        pipelines_list = orchestrator.list_pipelines()

        if output_format == "table":
            click.echo("GrupoNOS Pipelines")
            click.echo("=" * 18)
            for pipeline in pipelines_list:
                status_emoji = "✅" if pipeline.get("status") == "active" else "⚠️"
                click.echo(f"{status_emoji} {pipeline.get('name', 'unknown')}")
                click.echo(
                    f"   Description: {pipeline.get('description', 'No description')}",
                )
                click.echo(f"   Schedule: {pipeline.get('schedule', 'manual')}")
                click.echo()

        elif output_format == "json":
            click.echo(json.dumps(pipelines_list, indent=2))

        elif output_format == "yaml":
            click.echo(yaml.dump(pipelines_list, default_flow_style=False))

        else:
            click.echo(f"Unknown format: {output_format}", err=True)
            ctx.exit(1)

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to list pipelines")
        if ctx.obj.get("debug"):
            raise
        ctx.exit(1)


@gruponos.command()
@click.argument("pipeline_name")
@click.option(
    "--format",
    "output_format",
    default="table",
    help="Output format (table, json, yaml)",
)
@click.pass_context
def logs(ctx: click.Context, pipeline_name: str, output_format: str) -> None:
    """View logs for a GrupoNOS pipeline."""
    try:
        config = ctx.obj["config"]

        # Initialize orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        # Get logs
        logs_data = orchestrator.get_pipeline_logs(pipeline_name)

        if output_format == "table":
            click.echo(f"Logs for pipeline: {pipeline_name}")
            click.echo("=" * (20 + len(pipeline_name)))

            for log_entry in logs_data:
                timestamp = log_entry.get("timestamp", "unknown")
                level = log_entry.get("level", "INFO")
                message = log_entry.get("message", "")

                # Color coding for log levels
                if level == "ERROR":
                    level_color = click.style(level, fg="red")
                elif level == "WARNING":
                    level_color = click.style(level, fg="yellow")
                elif level == "DEBUG":
                    level_color = click.style(level, fg="blue")
                else:
                    level_color = level

                click.echo(f"[{timestamp}] {level_color}: {message}")

        elif output_format == "json":
            click.echo(json.dumps(logs_data, indent=2))

        elif output_format == "yaml":
            click.echo(yaml.dump(logs_data, default_flow_style=False))

        else:
            click.echo(f"Unknown format: {output_format}", err=True)
            ctx.exit(1)

    except (RuntimeError, ValueError, TypeError):
        logger.exception(f"Failed to get logs for pipeline {pipeline_name}")
        if ctx.obj.get("debug"):
            raise
        ctx.exit(1)


@gruponos.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check GrupoNOS system health."""
    try:
        config = ctx.obj["config"]
        debug = ctx.obj.get("debug", False)

        # Initialize orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        click.echo("🏥 GrupoNOS Health Check")
        click.echo("=" * 24)

        # Perform health check
        health_status = orchestrator.health_check()

        # Database connectivity
        db_status = health_status.get("database", {})
        db_emoji = "✅" if db_status.get("status") == "healthy" else "❌"
        click.echo(f"{db_emoji} Database: {db_status.get('status', 'unknown')}")
        if debug and db_status.get("details"):
            click.echo(f"   Details: {db_status['details']}")

        # WMS connectivity
        wms_status = health_status.get("wms", {})
        wms_emoji = "✅" if wms_status.get("status") == "healthy" else "❌"
        click.echo(f"{wms_emoji} Oracle WMS: {wms_status.get('status', 'unknown')}")
        if debug and wms_status.get("details"):
            click.echo(f"   Details: {wms_status['details']}")

        # LDAP connectivity
        ldap_status = health_status.get("ldap", {})
        ldap_emoji = "✅" if ldap_status.get("status") == "healthy" else "❌"
        click.echo(f"{ldap_emoji} LDAP: {ldap_status.get('status', 'unknown')}")
        if debug and ldap_status.get("details"):
            click.echo(f"   Details: {ldap_status['details']}")

        # Overall status
        overall_status = health_status.get("overall", "unknown")
        overall_emoji = "✅" if overall_status == "healthy" else "❌"
        click.echo(f"\n{overall_emoji} Overall Status: {overall_status}")

        # Exit with error code if unhealthy
        if overall_status != "healthy":
            ctx.exit(1)

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Health check failed")
        click.echo("❌ Health check failed", err=True)
        if debug:
            raise
        ctx.exit(1)


@gruponos.command()
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show GrupoNOS configuration."""
    try:
        config = ctx.obj["config"]

        click.echo("GrupoNOS Configuration")
        click.echo("=" * 22)

        # Show configuration (mask sensitive values)
        config_dict = config.model_dump()

        # Mask sensitive fields
        sensitive_fields = ["password", "secret", "key", "token"]

        def mask_sensitive(obj: object, path: str = "") -> object:
            if isinstance(obj, dict):
                return {
                    k: mask_sensitive(v, f"{path}.{k}" if path else k)
                    for k, v in obj.items()
                }
            if isinstance(obj, str) and any(
                field in path.lower() for field in sensitive_fields
            ):
                return "*" * 8
            return obj

        masked_config = mask_sensitive(config_dict)

        click.echo(yaml.dump(masked_config, default_flow_style=False))

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to show configuration")
        if ctx.obj.get("debug"):
            raise
        ctx.exit(1)


@gruponos.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show GrupoNOS version information."""
    try:
        click.echo("GrupoNOS Meltano Native")
        click.echo("=" * 23)

        # Show versions

        try:
            version = importlib.metadata.version("gruponos-meltano-native")
            click.echo(f"GrupoNOS Meltano Native: {version}")
        except (RuntimeError, ValueError, TypeError):
            click.echo("GrupoNOS Meltano Native: Not installed")

        # Dependencies
        deps = [
            "meltano",
            "dbt-core",
            "flext-tap-oracle-wms",
            "flext-target-oracle",
            "flext-tap-ldap",
        ]

        for dep in deps:
            try:
                dep_version = importlib.metadata.version(dep)
                click.echo(f"{dep}: {dep_version}")
            except (RuntimeError, ValueError, TypeError):
                click.echo(f"{dep}: Not available")

        # Python version
        click.echo(f"Python: {sys.version}")

    except (RuntimeError, ValueError, TypeError):
        logger.exception("Failed to get version information")
        if ctx.obj.get("debug"):
            raise
        ctx.exit(1)


# Legacy CLI entry point for backward compatibility
@click.group()
@click.version_option()
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.pass_context
def main(
    ctx: click.Context,
    *,
    debug: bool,
    config_file: str | None,
) -> None:
    """GrupoNOS Meltano Native CLI (legacy entry point)."""
    gruponos.main(
        (["--debug"] if debug else [])
        + (["--config-file", config_file] if config_file else []),
        standalone_mode=False,
    )


# Add all commands to legacy CLI for backward compatibility
main.add_command(status)
main.add_command(run)
main.add_command(pipelines)
main.add_command(logs)
main.add_command(health)
main.add_command(config_show, name="config")
main.add_command(version)


if __name__ == "__main__":
    main()
