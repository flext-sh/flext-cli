"""FlextCliFormatters - Class-based formatting utilities and factory."""

from __future__ import annotations

import importlib
import json
from io import StringIO
from typing import ClassVar, Protocol

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


__all__ = [
    "FlextCliFormatters",
    "OutputFormatter",
]
