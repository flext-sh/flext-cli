"""Class-based Facade for API convenience operations (no free helpers)."""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

from flext_core import FlextResult
from rich.table import Table

from flext_cli.api import FlextCliApi


class FlextCliApiFunctions:
    """Class-based facade replacing module-level API helpers."""

    @classmethod
    def format(cls, data: object, format_type: str) -> FlextResult[str]:
        res = FlextCliApi().format_data(data, format_type)
        if res.is_failure:
            return FlextResult[str].fail(f"Format error: {res.error}")
        return res

    @classmethod
    def table(cls, data: object, title: str | None = None) -> FlextResult[Table]:
        try:
            table = cls._create_table(data, title)
            return FlextResult[Table].ok(table)
        except Exception as e:
            return FlextResult[Table].fail(str(e))

    @classmethod
    def _create_table(cls, data: object, title: str | None) -> Table:
        """Create a Rich Table from provided data."""
        table = Table(title=title or "Data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            cls._add_dict_list_to_table(table, data)
        elif isinstance(data, dict):
            cls._add_dict_to_table(table, data)
        else:
            cls._add_simple_data_to_table(table, data)
        return table

    @classmethod
    def _add_dict_list_to_table(
        cls, table: Table, data: list[dict[str, object]]
    ) -> None:
        """Add list of dictionaries to table."""
        for key in data[0]:
            table.add_column(str(key))
        for row in data:
            table.add_row(*[str(row.get(k, "")) for k in data[0]])

    @classmethod
    def _add_dict_to_table(cls, table: Table, data: dict[str, object]) -> None:
        """Add dictionary to table."""
        table.add_column("Key")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(str(k), str(v))

    @classmethod
    def _add_simple_data_to_table(cls, table: Table, data: object) -> None:
        """Add simple data to table."""
        table.add_column("Value")
        if isinstance(data, list):
            for v in data:
                table.add_row(str(v))
        else:
            table.add_row(str(data))

    @classmethod
    def transform_data(
        cls,
        data: list[dict[str, object]],
        filter_func: Callable[[dict[str, object]], bool] | None = None,
        sort_key: str | None = None,
        *,
        reverse: bool = False,
    ) -> FlextResult[list[dict[str, object]]]:
        return FlextCliApi().transform_data(
            data,
            filter_func=filter_func,
            sort_key=sort_key,
            reverse=reverse,
        )

    @classmethod
    def aggregate_data(
        cls,
        data: list[dict[str, object]],
        *,
        group_by: str,
        sum_fields: list[str] | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        return FlextCliApi().aggregate_data(data, group_by, sum_fields)

    @classmethod
    def export(
        cls, data: object, file_path: str | Path, format_type: str
    ) -> FlextResult[str]:
        # Minimal CSV export for list of dicts
        if format_type == "csv":
            if not (isinstance(data, list) and data and isinstance(data[0], dict)):
                return FlextResult[str].fail("CSV export requires list of dictionaries")
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                keys = list(data[0].keys())
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    for row in data:
                        writer.writerow({k: row.get(k, "") for k in keys})
                return FlextResult[str].ok(f"Data exported to {file_path}")
            except Exception as e:
                return FlextResult[str].fail(str(e))
        # Delegate others to API
        res = FlextCliApi().export_data(data, file_path, format_type)
        if res.is_failure:
            return FlextResult[str].fail("Unsupported export format")
        return res

    @classmethod
    def batch_export(
        cls, datasets: dict[str, object], directory: str | Path, format_type: str
    ) -> FlextResult[list[str]]:
        try:
            out_files: list[str] = []
            base = Path(directory)
            base.mkdir(parents=True, exist_ok=True)
            for name, dataset in datasets.items():
                target = base / f"{name}.{format_type}"
                res = cls.export(dataset, target, format_type)
                if res.is_failure:
                    return FlextResult[list[str]].fail(
                        f"Failed to export {name}: {res.error}"
                    )
                out_files.append(str(target))
            return FlextResult[list[str]].ok(out_files)
        except Exception as e:
            return FlextResult[list[str]].fail(str(e))

    @classmethod
    def unwrap_or_default[T](cls, result: FlextResult[T], default: T) -> T:
        return result.value if result.is_success else default

    @classmethod
    def unwrap_or_none[T](cls, result: FlextResult[T]) -> T | None:
        return result.value if result.is_success else None


__all__ = [
    "FlextCliApiFunctions",
]
