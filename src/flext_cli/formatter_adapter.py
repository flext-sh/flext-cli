"""FlextCli Formatter Adapter - Clean protocol implementation."""

from __future__ import annotations

import json

from flext_core import FlextResult
from rich.table import Table


class FlextCliFormatterAdapter:
    """Clean adapter implementing FlextCliFormatterProtocol."""

    def __init__(self, default_format: str = "table") -> None:
        self.default_format = default_format

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data to specified output format."""
        try:
            if format_type == "json":
                return self.format_json(data)
            if format_type == "yaml":
                return self.format_yaml(data)
            if format_type == "csv":
                return self.format_csv(data)
            # Default to string representation
            return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(f"Format failed: {e}")

    def format_table(
        self, data: object, title: str | None = None
    ) -> FlextResult[Table]:
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

    def format_json(self, data: object, indent: int = 2) -> FlextResult[str]:
        """Format data as JSON string."""
        try:
            json_str = json.dumps(data, ensure_ascii=False, default=str, indent=indent)
            return FlextResult[str].ok(json_str)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def format_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML string."""
        try:
            import yaml

            yaml_str = yaml.safe_dump(data)
            return FlextResult[str].ok(yaml_str)
        except ImportError:
            return FlextResult[str].fail("YAML library not available")
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def format_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV string."""
        try:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                lines = [",".join(keys)]
                lines.extend(
                    ",".join(str(row.get(k, "")) for k in keys) for row in data
                )
                return FlextResult[str].ok("\n".join(lines))
            if isinstance(data, dict):
                keys = list(data.keys())
                lines = [",".join(keys), ",".join(str(data.get(k, "")) for k in keys)]
                return FlextResult[str].ok("\n".join(lines))
            if isinstance(data, list):
                return FlextResult[str].ok(",".join(str(v) for v in data))
            return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")


__all__ = ["FlextCliFormatterAdapter"]
