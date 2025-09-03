"""FlextCliFormatters - Class-based formatting utilities and factory."""

from __future__ import annotations

import importlib
import json
from io import StringIO
from typing import ClassVar, Protocol

from flext_core import FlextResult
from rich.console import Console
from rich.table import Table


class OutputFormatter(Protocol):
    """Protocol for formatter classes used by the CLI."""

    def format(self, data: object, console: Console) -> None: ...


class TableFormatter:
    """Render data in a Rich Table with best-effort heuristics."""

    def format(self, data: object, console: Console) -> None:
        table = Table(title="Data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Add columns from dict keys
            for key in data[0]:
                table.add_column(str(key))
            for row in data:
                table.add_row(*[str(row.get(k, "")) for k in data[0]])
        elif isinstance(data, dict):
            table.add_column("Key")
            table.add_column("Value")
            for k, v in data.items():
                table.add_row(str(k), str(v))
        else:
            table.add_column("Value")
            if isinstance(data, list):
                for item in data:
                    table.add_row(str(item))
            else:
                table.add_row(str(data))
        console.print(table)


class JSONFormatter:
    """Pretty-print data as JSON using safe defaults."""

    def format(self, data: object, console: Console) -> None:
        console.print(json.dumps(data, ensure_ascii=False, default=str, indent=2))


class YAMLFormatter:
    """Render data as YAML; falls back to str on failure."""

    def format(self, data: object, console: Console) -> None:
        try:
            yaml_mod = importlib.import_module("yaml")
            buf = StringIO()
            yaml_mod.safe_dump(data, buf)
            # Avoid misleading multi-character strip: use removesuffix for '...'
            text = buf.getvalue().rstrip("\n").removesuffix("...").strip()
            console.print(text)
        except Exception:
            console.print(str(data))


class CSVFormatter:
    """Render tabular-like data as CSV text."""

    def format(self, data: object, console: Console) -> None:
        # Very small CSV: header from first row keys
        if isinstance(data, list) and data and isinstance(data[0], dict):
            keys = list(data[0].keys())
            console.print(",".join(keys))
            for row in data:
                console.print(",".join(str(row.get(k, "")) for k in keys))
        elif isinstance(data, dict):
            keys = list(data.keys())
            console.print(",".join(keys))
            console.print(",".join(str(data.get(k, "")) for k in keys))
        elif isinstance(data, list):
            # print as a line of values
            console.print(",".join(str(v) for v in data))
        else:
            console.print(str(data))


class PlainFormatter:
    """Render data as human-friendly plain text."""

    def format(self, data: object, console: Console) -> None:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            for row in data:
                for k, v in row.items():
                    console.print(f"{k}: {v}")
        elif isinstance(data, dict):
            for k, v in data.items():
                console.print(f"{k}: {v}")
        elif isinstance(data, list):
            for v in data:
                console.print(str(v))
        else:
            console.print(str(data))


type FormatterCtor = type[OutputFormatter]


class FlextCliFormatters:
    """Factory and registry for output formatters used by the CLI."""

    _registry: ClassVar[dict[str, FormatterCtor]] = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "csv": CSVFormatter,
        "plain": PlainFormatter,
    }

    @classmethod
    def create(cls, name: str) -> OutputFormatter:
        ctor = cls._registry.get(name)
        if not ctor:
            msg = "Unknown formatter type"
            raise ValueError(msg)
        return ctor()

    @classmethod
    def register(cls, name: str, ctor: FormatterCtor) -> None:
        cls._registry[name] = ctor

    @classmethod
    def list_formats(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def format_output(cls, data: object, fmt: str, console: Console) -> None:
        cls.create(fmt).format(data, console)

    # Protocol implementation methods
    @classmethod
    def format_data(cls, data: object, format_type: str) -> FlextResult[str]:
        """Format data to specified output format."""
        try:
            from io import StringIO

            from rich.console import Console

            console = Console(file=StringIO(), width=120)
            cls.format_output(data, format_type, console)
            output = (
                console.file.getvalue()
                if hasattr(console.file, "getvalue")
                else str(data)
            )
            return FlextResult[str].ok(output)
        except Exception as e:
            return FlextResult[str].fail(f"Format failed: {e}")

    @classmethod
    def format_table(cls, data: object, title: str | None = None) -> FlextResult[Table]:
        """Format data as a table representation."""
        try:
            table = Table(title=title or "Data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                for key in data[0]:
                    table.add_column(str(key))
                for row in data:
                    table.add_row(*[str(row.get(k, "")) for k in data[0]])
            elif isinstance(data, dict):
                table.add_column("Key")
                table.add_column("Value")
                for k, v in data.items():
                    table.add_row(str(k), str(v))
            else:
                table.add_column("Value")
                if isinstance(data, list):
                    for item in data:
                        table.add_row(str(item))
                else:
                    table.add_row(str(data))
            return FlextResult[Table].ok(table)
        except Exception as e:
            return FlextResult[Table].fail(f"Table creation failed: {e}")

    @classmethod
    def format_json(cls, data: object, indent: int = 2) -> FlextResult[str]:
        """Format data as JSON string."""
        try:
            json_str = json.dumps(data, ensure_ascii=False, default=str, indent=indent)
            return FlextResult[str].ok(json_str)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    @classmethod
    def format_yaml(cls, data: object) -> FlextResult[str]:
        """Format data as YAML string."""
        try:
            yaml_mod = importlib.import_module("yaml")
            yaml_str = yaml_mod.safe_dump(data)
            return FlextResult[str].ok(yaml_str)
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    @classmethod
    def format_csv(cls, data: object) -> FlextResult[str]:
        """Format data as CSV string."""
        try:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                csv_lines = [",".join(keys)]
                csv_lines.extend(
                    ",".join(str(row.get(k, "")) for k in keys) for row in data
                )
                return FlextResult[str].ok("\n".join(csv_lines))
            if isinstance(data, dict):
                keys = list(data.keys())
                csv_lines = [
                    ",".join(keys),
                    ",".join(str(data.get(k, "")) for k in keys),
                ]
                return FlextResult[str].ok("\n".join(csv_lines))
            if isinstance(data, list):
                return FlextResult[str].ok(",".join(str(v) for v in data))
            return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")


__all__ = [
    "FlextCliFormatters",
    "OutputFormatter",
]
