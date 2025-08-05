"""FLEXT Meltano commands for flext-cli.

FLEXT Meltano CLI commands integrated into the unified FLEXT CLI.
Preserves ALL original functionality from flext-meltano/cli.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import click
import yaml

if TYPE_CHECKING:
    from flext_meltano import FlextMeltanoConfig
    from flext_meltano.base import FlextMeltanoBaseService
    from flext_meltano.core import FlextMeltanoOrchestrationService

try:
    from flext_meltano import FlextMeltanoConfig, create_flext_meltano_bridge
    from flext_meltano.base import FlextMeltanoBaseService
    from flext_meltano.core import FlextMeltanoOrchestrationService

    FLEXT_MELTANO_AVAILABLE = True
except ImportError as e:
    # Graceful handling when flext-meltano is not available
    click.echo(f"Warning: FLEXT Meltano not available: {e}", err=True)
    FlextMeltanoConfig = type(None)
    create_flext_meltano_bridge = type(None)
    FlextMeltanoOrchestrationService = type(None)
    FlextMeltanoBaseService = type(None)
    FLEXT_MELTANO_AVAILABLE = False


def _validate_command_args(args: list[str]) -> None:
    """Validate command arguments for security.

    Args:
        args: Command arguments to validate

    Raises:
        ValueError: If arguments contain unsafe characters

    """
    if not args:
        no_args_msg = "No command arguments provided"
        raise ValueError(no_args_msg)

    # Check for command injection patterns
    unsafe_chars = [";", "&", "|", "`", "$", "$(", ")", ">", "<", "*", "?"]
    for arg in args:
        if any(char in str(arg) for char in unsafe_chars):
            unsafe_char_msg: str = f"Unsafe character detected in argument: {arg}"
            raise ValueError(unsafe_char_msg)

    # Validate first argument is the expected meltano command
    if args[0] != "meltano":
        invalid_command_msg: str = f"Expected 'meltano' command, got: {args[0]}"
        raise ValueError(invalid_command_msg)


def _safe_subprocess_run(
    cmd: list[str],
    cwd: str | None = None,
    *,
    capture_output: bool = False,
    timeout: int = 300,
) -> subprocess.CompletedProcess[bytes]:
    """Securely execute subprocess with validation.

    Args:
        cmd: Command and arguments to execute
        cwd: Working directory for execution
        capture_output: Whether to capture stdout/stderr
        timeout: Timeout in seconds

    Returns:
        CompletedProcess result

    Raises:
        ValueError: If command validation fails
        subprocess.TimeoutExpired: If command times out

    """
    # Validate command arguments
    _validate_command_args(cmd)

    # Validate working directory if provided
    if cwd and not Path(cwd).is_dir():
        invalid_dir_msg: str = f"Working directory does not exist: {cwd}"
        raise ValueError(invalid_dir_msg)

    try:
        return subprocess.run(  # noqa: S603
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            check=False,
            timeout=timeout,
            # Security: Prevent shell injection
            shell=False,
            # Security: Use safe environment
            env=None,  # Inherit safe environment
        )
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(
            cmd,
            timeout,
            f"Command timed out after {timeout}s",
        ) from e


@click.group(name="meltano")
@click.version_option(version="0.9.0")
@click.pass_context
def meltano(ctx: click.Context) -> None:
    """FLEXT Meltano - Enterprise ETL/ELT Pipeline Engine."""
    if not FLEXT_MELTANO_AVAILABLE:
        click.echo(
            "Error: FLEXT Meltano package not available. Please install flext-meltano.",
            err=True,
        )
        ctx.exit(1)

    ctx.ensure_object(dict)


@meltano.command()
@click.option("--format", "output_format", default="table", help="Output format")
@click.option("--quiet", is_flag=True, help="Quiet mode")
@click.option(
    "--project-root",
    type=click.Path(exists=True),
    default=".",
    help="Root directory to search for projects",
)
@click.pass_context
def projects(
    ctx: click.Context,
    output_format: str,
    *,
    quiet: bool,
    project_root: str,
) -> None:
    """Discover and manage Meltano projects in the specified directory.

    Args:
        ctx: Click context
        output_format: Output format for results
        quiet: Suppress output
        project_root: Root directory to search

    """
    try:
        project_root_path = Path(project_root)

        if not quiet:
            click.echo("FLEXT Meltano Projects")
            click.echo("=" * 25)

        # Find meltano.yml files to identify projects
        projects_list = []
        for meltano_yml in project_root_path.rglob("meltano.yml"):
            project_path = meltano_yml.parent
            project_name = project_path.name
            projects_list.append({"name": project_name, "path": str(project_path)})

        if output_format == "table":
            for project in projects_list:
                click.echo(f"• {project['name']} ({project['path']})")
        elif output_format == "json":
            click.echo(json.dumps(projects_list, indent=2))
        elif output_format == "yaml":
            click.echo(yaml.dump(projects_list, default_flow_style=False))

        if not quiet and not projects_list:
            click.echo("No Meltano projects found.")
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to list projects: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument("project_name")
@click.option("--directory", type=click.Path(), help="Project directory")
@click.option("--template", help="Project template to use")
@click.pass_context
def init(
    ctx: click.Context,
    project_name: str,
    directory: str | None,
    template: str | None,
) -> None:
    """Initialize a new Meltano project.

    Args:
        ctx: Click context
        project_name: Name of the project to create
        directory: Optional parent directory
        template: Optional project template

    """
    try:
        # Determine parent directory
        parent_dir = Path(directory) if directory else Path.cwd()

        # Initialize project manager with parent directory
        if not FLEXT_MELTANO_AVAILABLE or FlextMeltanoBaseService is None:
            click.echo(
                "❌ FLEXT Meltano not available. Please install flext-meltano.",
                err=True,
            )
            ctx.exit(1)

        # Create configuration and bridge
        config = FlextMeltanoConfig(project_root=str(parent_dir))
        create_flext_meltano_bridge(config)

        click.echo(f"🚀 Initializing Meltano project: {project_name}")
        click.echo(f"📁 Parent directory: {parent_dir}")
        click.echo(f"📁 Project will be created at: {parent_dir / project_name}")

        if template:
            click.echo(f"📋 Template: {template}")

        # Create the project directory - meltano init will be handled via subprocess
        project_path = parent_dir / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Use meltano CLI to initialize project
        from flext_meltano.execution import flext_meltano_run_command

        result = flext_meltano_run_command(
            ["init", project_name],
            cwd=str(parent_dir)
        )

        if result.success:
            project_path = parent_dir / project_name
            click.echo("✅ Meltano project initialized successfully!")
            click.echo(f"📍 Project path: {project_path}")
            click.echo(f"📄 Configuration: {project_path}/meltano.yml")

            if template:
                click.echo("⚠️  Template support not yet implemented in project manager")
        else:
            click.echo(f"❌ Failed to initialize project: {result.error_message}", err=True)
            ctx.exit(1)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to initialize project: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument(
    "plugin_type",
    type=click.Choice(
        ["extractor", "loader", "transformer", "orchestrator", "utility"],
    ),
)
@click.argument("plugin_name")
@click.option("--variant", help="Plugin variant")
@click.option("--pip-url", help="Custom pip URL")
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.pass_context
def add(  # noqa: PLR0913
    ctx: click.Context,
    plugin_type: str,
    plugin_name: str,
    variant: str | None,
    pip_url: str | None,
    project_dir: str | None,
) -> None:
    """Add a plugin to the Meltano project.

    Args:
        ctx: Click context
        plugin_type: Type of plugin to add
        plugin_name: Name of the plugin
        variant: Optional plugin variant
        pip_url: Optional custom pip URL
        project_dir: Optional project directory

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo(f"📦 Adding {plugin_type}: {plugin_name}")
        if variant:
            click.echo(f"🔧 Variant: {variant}")
        if pip_url:
            click.echo(f"🔗 Pip URL: {pip_url}")

        # Build meltano add command
        cmd = ["meltano", "add", plugin_type, plugin_name]
        if variant:
            cmd.extend(["--variant", variant])
        if pip_url:
            cmd.extend(["--pip-url", pip_url])

        # Execute meltano command
        result = _safe_subprocess_run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            timeout=300,
        )

        if result.returncode == 0:
            click.echo("✅ Plugin added successfully!")
            if result.stdout:
                click.echo(result.stdout.decode())
        else:
            click.echo("❌ Failed to add plugin", err=True)
            if result.stderr:
                click.echo(result.stderr.decode(), err=True)
            ctx.exit(result.returncode)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to add plugin: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument("job_name")
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.option("--environment", help="Environment to use")
@click.option("--full-refresh", is_flag=True, help="Run full refresh")
@click.pass_context
def run(
    ctx: click.Context,
    job_name: str,
    project_dir: str | None,
    environment: str | None,
    *,
    full_refresh: bool,
) -> None:
    """Run a Meltano job.

    Args:
        ctx: Click context
        job_name: Name of the job to run
        project_dir: Optional project directory
        environment: Optional environment name
        full_refresh: Whether to run full refresh

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo(f"🏃 Running Meltano job: {job_name}")
        if environment:
            click.echo(f"🌍 Environment: {environment}")
        if full_refresh:
            click.echo("🔄 Full refresh mode")

        # Build meltano run command
        cmd = ["meltano", "run", job_name]
        if full_refresh:
            cmd.append("--full-refresh")

        # Set environment if specified
        env = os.environ.copy()
        if environment:
            env["MELTANO_ENVIRONMENT"] = environment

        # Execute meltano command
        result = subprocess.run(  # noqa: S603
            cmd,
            check=False,
            cwd=str(project_path),
            env=env,
            shell=False,
            timeout=3600,  # 1 hour timeout for job execution
        )

        if result.returncode == 0:
            click.echo("✅ Job completed successfully!")
        else:
            click.echo(f"❌ Job failed with exit code: {result.returncode}", err=True)
            ctx.exit(result.returncode)

    except subprocess.TimeoutExpired:
        click.echo("❌ Job timed out after 1 hour", err=True)
        ctx.exit(1)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to run job: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument("plugin_name")
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.pass_context
def discover(
    ctx: click.Context,
    plugin_name: str,
    project_dir: str | None,
) -> None:
    """Discover schema for a plugin.

    Args:
        ctx: Click context
        plugin_name: Name of the plugin to discover
        project_dir: Optional project directory

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo(f"🔍 Discovering schema for: {plugin_name}")

        # Build meltano discover command
        cmd = ["meltano", "discover", plugin_name]

        # Execute meltano command
        result = _safe_subprocess_run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            timeout=120,
        )

        if result.returncode == 0:
            click.echo("✅ Schema discovery completed!")
            if result.stdout:
                # Pretty print the catalog

                try:
                    catalog = json.loads(result.stdout.decode())
                    click.echo(json.dumps(catalog, indent=2))
                except json.JSONDecodeError:
                    click.echo(result.stdout.decode())
        else:
            click.echo("❌ Schema discovery failed", err=True)
            if result.stderr:
                click.echo(result.stderr.decode(), err=True)
            ctx.exit(result.returncode)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to discover schema: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument("plugin_name")
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.pass_context
def test(
    ctx: click.Context,
    plugin_name: str,
    project_dir: str | None,
) -> None:
    """Test a plugin.

    Args:
        ctx: Click context
        plugin_name: Name of the plugin to test
        project_dir: Optional project directory

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo(f"🧪 Testing plugin: {plugin_name}")

        # Build meltano test command
        cmd = ["meltano", "test", plugin_name]

        # Execute meltano command
        result = _safe_subprocess_run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            timeout=60,
        )

        if result.returncode == 0:
            click.echo("✅ Plugin test passed!")
            if result.stdout:
                click.echo(result.stdout.decode())
        else:
            click.echo("❌ Plugin test failed", err=True)
            if result.stderr:
                click.echo(result.stderr.decode(), err=True)
            ctx.exit(result.returncode)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to test plugin: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.pass_context
def install(
    ctx: click.Context,
    project_dir: str | None,
) -> None:
    """Install all plugins for a Meltano project.

    Args:
        ctx: Click context
        project_dir: Optional project directory

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo("📦 Installing all Meltano plugins...")

        # Build meltano install command
        cmd = ["meltano", "install"]

        # Execute meltano command
        result = _safe_subprocess_run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            timeout=600,  # 10 minutes for installation
        )

        if result.returncode == 0:
            click.echo("✅ All plugins installed successfully!")
            if result.stdout:
                click.echo(result.stdout.decode())
        else:
            click.echo("❌ Plugin installation failed", err=True)
            if result.stderr:
                click.echo(result.stderr.decode(), err=True)
            ctx.exit(result.returncode)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to install plugins: {e}", err=True)
        ctx.exit(1)


@meltano.command()
@click.argument("plugin_name")
@click.argument("setting_name")
@click.argument("value")
@click.option(
    "--project-dir",
    type=click.Path(exists=True),
    help="Meltano project directory",
)
@click.pass_context
def config(
    ctx: click.Context,
    plugin_name: str,
    setting_name: str,
    value: str,
    project_dir: str | None,
) -> None:
    """Configure a plugin setting.

    Args:
        ctx: Click context
        plugin_name: Name of the plugin
        setting_name: Name of the setting
        value: Value to set
        project_dir: Optional project directory

    """
    try:
        project_path = Path(project_dir) if project_dir else Path.cwd()

        click.echo(f"⚙️  Configuring {plugin_name}.{setting_name} = {value}")

        # Build meltano config command
        cmd = ["meltano", "config", plugin_name, "set", setting_name, value]

        # Execute meltano command
        result = _safe_subprocess_run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            timeout=30,
        )

        if result.returncode == 0:
            click.echo("✅ Configuration updated successfully!")
            if result.stdout:
                click.echo(result.stdout.decode())
        else:
            click.echo("❌ Configuration update failed", err=True)
            if result.stderr:
                click.echo(result.stderr.decode(), err=True)
            ctx.exit(result.returncode)
    except (RuntimeError, ValueError, TypeError) as e:
        click.echo(f"❌ Failed to update configuration: {e}", err=True)
        ctx.exit(1)


# Legacy CLI entry point for backward compatibility
@click.group()
@click.version_option(version="0.9.0")
def cli() -> None:
    """FLEXT Meltano CLI (legacy entry point)."""


# Add all commands to legacy CLI for backward compatibility
cli.add_command(projects)
cli.add_command(init)
cli.add_command(add)
cli.add_command(run)
cli.add_command(discover)
cli.add_command(test)
cli.add_command(install)
cli.add_command(config)


def main() -> None:
    """Main entry point for backward compatibility."""
    cli()


if __name__ == "__main__":
    main()
