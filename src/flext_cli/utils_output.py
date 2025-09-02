"""FlextCliOutput - Class-based output utilities (no module-level helpers)."""

from __future__ import annotations

import importlib
import json
from typing import cast

from rich.console import Console
from rich.table import Table

from flext_cli.config import FlextCliConfig


class FlextCliOutput:
    """Output helpers for formatting and printing data in the CLI."""

    @staticmethod
    def _yaml_dump(data: object) -> str:
        """Dump data to YAML (class-internal to avoid module-level helpers)."""
        try:
            yaml_mod = importlib.import_module("yaml")
            raw_text = yaml_mod.safe_dump(data)
            text = cast("str", raw_text)
            return text.rstrip("\n").removesuffix("...").strip()
        except Exception:
            return str(data)

    @staticmethod
    def setup_console(*, no_color: bool = False, quiet: bool = False) -> Console:
        return Console(no_color=no_color, quiet=quiet)

    @staticmethod
    def print_success(console: Console, message: str) -> None:
        console.print(f"[bold green]✓[/bold green] {message}")

    @staticmethod
    def print_error(console: Console, message: str, details: str | None = None) -> None:
        console.print(f"[bold red]Error:[/bold red] {message}")
        if details:
            console.print(details)

    @staticmethod
    def print_warning(console: Console, message: str) -> None:
        console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    @staticmethod
    def print_info(console: Console, message: str) -> None:
        console.print(f"[bold blue]i[/bold blue] {message}")

    @staticmethod
    def format_json(data: object) -> str:
        return json.dumps(data, default=str, ensure_ascii=False, indent=2)

    @staticmethod
    def format_yaml(data: object) -> str:
        return FlextCliOutput._yaml_dump(data)

    @staticmethod
    def format_plugin_list(
        console: Console, plugins: list[dict[str, object]], fmt: str
    ) -> None:
        if fmt == "json":
            console.print(FlextCliOutput.format_json(plugins))
            return
        table = Table(title="Available Plugins")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Version")
        table.add_column("Description")
        for p in plugins:
            table.add_row(
                str(p.get("name", "Unknown")),
                str(p.get("type", "Unknown")),
                str(p.get("version", "Unknown")),
                str(p.get("description", "No description")),
            )
        if not plugins:
            console.print("No plugins found")
        else:
            console.print(table)

    @staticmethod
    def format_pipeline_list(console: Console, pipeline_list: object) -> None:
        pipelines = getattr(pipeline_list, "pipelines", [])
        if not pipelines:
            console.print("No pipelines found")
            return
        table = Table(title="Pipelines")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Created")
        for p in pipelines:
            table.add_row(
                str(getattr(p, "id", "")),
                str(getattr(p, "name", "")),
                str(getattr(p, "status", "")),
                str(getattr(p, "created_at", "")),
            )
        console.print(table)
        total = getattr(pipeline_list, "total", len(pipelines))
        console.print(f"Total: {total} pipelines")

    @staticmethod
    def format_pipeline(console: Console, pipeline: object) -> None:
        table = Table(title="Pipeline Detail")
        table.add_column("Field")
        table.add_column("Value")
        for field in ["id", "name", "status", "created_at", "updated_at"]:
            table.add_row(
                field.replace("_", " ").title() + ":", str(getattr(pipeline, field, ""))
            )
        console.print(table)
        cfg = getattr(pipeline, "config", None)
        console.print("Configuration:")
        console.print(FlextCliOutput.format_yaml(getattr(cfg, "__dict__", cfg)))

    @staticmethod
    def show_flext_cli_paths(console: Console) -> None:
        config = FlextCliOutput.get_config()
        console.print("FLEXT CLI Paths:")
        console.print(f"  config: {getattr(config, 'config_dir', '')}")
        console.print(f"  cache: {getattr(config, 'cache_dir', '')}")
        console.print(f"  logs: {getattr(config, 'log_dir', '')}")

    @staticmethod
    def get_config() -> FlextCliConfig:
        return FlextCliConfig()


__all__ = ["FlextCliOutput"]
