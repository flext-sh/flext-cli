"""Output utilities shim for backward compatibility.

Delegates to `flext_cli.cli_utils` equivalents.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

# Lightweight façade over cli_utils. Keep logic centralized in cli_utils.


def setup_console(*, no_color: bool = False, quiet: bool = False) -> Console:
    """Create a Rich Console honoring simple flags.

    Back-compat API used by tests.
    """
    return Console(color_system=None if no_color else "auto", quiet=quiet)


def print_success(console: Console, message: str) -> None:
    """Print a success message to the console."""
    """Print a success message with standard formatting."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(console: Console, message: str, details: str | None = None) -> None:
    """Print an error message to the console with optional details."""
    """Print an error message with optional details block."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    if details:
        console.print("[dim]" + details + "[/dim]")


def print_warning(console: Console, message: str) -> None:
    """Print a warning message to the console."""
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(console: Console, message: str) -> None:
    """Print an informational message to the console."""
    """Print an informational message."""
    console.print(f"[bold blue]i[/bold blue] {message}")


def format_plugin_list(
    console: Console, plugins: list[dict[str, object]], fmt: str,
) -> None:
    """Render plugins list as table or json.

    Delegates formatting to cli_utils where possible to avoid duplication.
    """
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    if fmt.lower() == "json":
        import json as _json

        console.print(_json.dumps(plugins, indent=2))
        return

    table = Table(title="Available Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Version", style="green")
    table.add_column("Description", style="dim")

    for plugin in plugins:
        name = str(plugin.get("name", "Unknown"))
        ptype = str(plugin.get("type", "Unknown"))
        version = str(plugin.get("version", "Unknown"))
        desc = str(plugin.get("description", "No description"))
        table.add_row(name, ptype, version, desc)

    console.print(table)


def format_pipeline_list(console: Console, pipeline_list: object) -> None:
    """Render pipeline list with paging data.

    Expects object with attributes: pipelines (list), total, page, page_size.
    """
    pipelines = getattr(pipeline_list, "pipelines", [])
    if not pipelines:
        console.print("[yellow]No pipelines found[/yellow]")
        return

    total = int(getattr(pipeline_list, "total", len(pipelines) or 1))
    page = int(getattr(pipeline_list, "page", 1))
    page_size = int(getattr(pipeline_list, "page_size", len(pipelines) or 1))
    total_pages = (total + page_size - 1) // page_size if page_size else 1

    table = Table(title=f"Pipelines (Page {page} of {total_pages})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    def _status_color(status: str) -> str:
        s = status.lower()
        color = {
            "running": "green",
            "failed": "red",
            "pending": "yellow",
            "completed": "blue",
        }.get(s, "white")
        return f"[{color}]{status}[/{color}]"

    for p in pipelines:
        pid = str(getattr(p, "id", ""))
        short_id = pid[:8] if pid else ""
        name = str(getattr(p, "name", ""))
        status = str(getattr(p, "status", "unknown"))
        created = str(getattr(p, "created_at", ""))
        table.add_row(short_id, name, _status_color(status), created)

    console.print(table)
    console.print(f"\nTotal: {total} pipelines")


def format_pipeline(console: Console, pipeline: object) -> None:
    """Format and print pipeline information using Rich tables."""
    """Render details of a single pipeline object."""
    name = str(getattr(pipeline, "name", ""))
    pid = str(getattr(pipeline, "id", ""))
    status = str(getattr(pipeline, "status", ""))
    created = str(getattr(pipeline, "created_at", ""))
    updated = str(getattr(pipeline, "updated_at", ""))

    console.print(f"\n[bold cyan]{name}[/bold cyan]")
    console.print(f"ID: {pid}")
    console.print(f"Status: {status}")
    if created:
        console.print(f"Created: {created}")
    if updated:
        console.print(f"Updated: {updated}")

    cfg = getattr(pipeline, "config", None)
    if cfg is not None:
        console.print("\n[bold]Configuration:[/bold]")
        tap = getattr(cfg, "tap", None)
        target = getattr(cfg, "target", None)
        transform = getattr(cfg, "transform", None)
        schedule = getattr(cfg, "schedule", None)
        config_map = getattr(cfg, "config", None)
        if tap:
            console.print(f"  Tap: {tap}")
        if target:
            console.print(f"  Target: {target}")
        if transform:
            console.print(f"  Transform: {transform}")
        if schedule:
            console.print(f"  Schedule: {schedule}")
        if config_map:
            console.print("  Config:")
            for key, value in dict(config_map).items():
                console.print(f"    {key}: {value}")


def format_json(data: object) -> str:
    """Return JSON-formatted string from data."""
    """Return pretty JSON string for arbitrary data."""
    import json as _json

    return _json.dumps(data, indent=2, default=str)


def format_yaml(data: object) -> str:
    """Return YAML-formatted string from data."""
    """Return nicely formatted YAML string for arbitrary data."""
    import yaml as _yaml

    if data is None:
        return "null"
    dumped = _yaml.dump(data, default_flow_style=False)
    return dumped.replace("\n...\n", "\n").strip()


__all__ = [
    "format_json",
    "format_pipeline",
    "format_pipeline_list",
    "format_plugin_list",
    "format_yaml",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "setup_console",
]
