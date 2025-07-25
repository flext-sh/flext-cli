"""FlextCliDataExporter - Advanced data extraction using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Enterprise-grade data export with multiple formats (CSV, TSV, JSON, Parquet, SQLite).
"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any

from flext_core import FlextResult, get_logger


# Helper functions for cleaner FlextResult creation
def _success(data: Any = None) -> FlextResult[Any]:
    return FlextResult(success=True, data=data, error=None)

def _fail(error: str) -> FlextResult[Any]:
    return FlextResult(success=False, data=None, error=error)

logger = get_logger(__name__)


class FlextCliDataExporter:
    """Advanced data exporter with multiple formats built on flext-core patterns.

    Supports CSV, TSV, JSON, Parquet, SQLite with zero duplications.
    All operations return FlextResult for consistent error handling.
    """

    def __init__(self, default_format: str = "json") -> None:
        self.default_format = default_format
        self._supported_formats = {
            "csv", "tsv", "json", "jsonl", "parquet", "sqlite", "excel", "feather",
        }

    def export_data(
        self,
        data: list[dict[str, Any]] | dict[str, Any],
        filepath: str | Path,
        format_type: str | None = None,
        **options: Any,
    ) -> FlextResult[str]:
        """Export data to specified format using flext-core patterns.

        Args:
            data: Data to export (list of dicts or single dict)
            filepath: Output file path
            format_type: Export format (auto-detected from extension if None)
            **options: Format-specific options

        Returns:
            FlextResult with success message or error

        """
        try:
            filepath = Path(filepath)

            # Auto-detect format from extension
            if format_type is None:
                format_type = self._detect_format_from_extension(filepath)

            if format_type not in self._supported_formats:
                return _fail(f"Unsupported format: {format_type}")

            # Normalize data to list of dicts
            normalized_data = self._normalize_data(data)
            if not normalized_data:
                return _fail("No data to export")

            # Create parent directory if needed
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Export based on format
            export_method = getattr(self, f"_export_{format_type}")
            result = export_method(normalized_data, filepath, **options)

            if result.success:
                file_size = filepath.stat().st_size
                return _success(
                    f"Exported {len(normalized_data)} records to {filepath} "
                    f"({format_type.upper()}, {file_size:,} bytes)",
                )
            return result

        except Exception as e:
            logger.exception("Data export failed")
            return _fail(f"Export failed: {e}")

    def _detect_format_from_extension(self, filepath: Path) -> str:
        """Detect export format from file extension."""
        extension = filepath.suffix.lower()
        format_map = {
            ".csv": "csv",
            ".tsv": "tsv",
            ".json": "json",
            ".jsonl": "jsonl",
            ".parquet": "parquet",
            ".sqlite": "sqlite",
            ".db": "sqlite",
            ".xlsx": "excel",
            ".feather": "feather",
        }
        return format_map.get(extension, self.default_format)

    def _normalize_data(self, data: list[dict[str, Any]] | dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize data to list of dictionaries."""
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item if isinstance(item, dict) else {"value": item} for item in data]
        return []

    def _export_csv(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        delimiter: str = ",",
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as CSV."""
        try:
            if not data:
                return _fail("No data to export")

            fieldnames = list(data[0].keys())

            with filepath.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=delimiter,
                    **options,
                )
                writer.writeheader()
                writer.writerows(data)

            return _success(None)

        except Exception as e:
            return _fail(f"CSV export failed: {e}")

    def _export_tsv(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as TSV (Tab-Separated Values)."""
        return self._export_csv(data, filepath, delimiter="\t", **options)

    def _export_json(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        indent: int = 2,
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as JSON."""
        try:
            with filepath.open("w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=indent, default=str, **options)

            return _success(None)

        except Exception as e:
            return _fail(f"JSON export failed: {e}")

    def _export_jsonl(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as JSON Lines (one JSON object per line)."""
        try:
            with filepath.open("w", encoding="utf-8") as jsonlfile:
                for record in data:
                    json.dump(record, jsonlfile, default=str, **options)
                    jsonlfile.write("\n")

            return _success(None)

        except Exception as e:
            return _fail(f"JSONL export failed: {e}")

    def _export_parquet(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as Parquet (requires pandas/pyarrow)."""
        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_parquet(filepath, index=False, **options)

            return _success(None)

        except ImportError:
            return _fail("pandas and pyarrow required for Parquet export")
        except Exception as e:
            return _fail(f"Parquet export failed: {e}")

    def _export_sqlite(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        table_name: str = "data",
        **options: Any,
    ) -> FlextResult[None]:
        """Export data to SQLite database."""
        try:
            import pandas as pd

            df = pd.DataFrame(data)

            with sqlite3.connect(filepath) as conn:
                df.to_sql(table_name, conn, if_exists="replace", index=False, **options)

            return _success(None)

        except ImportError:
            return _fail("pandas required for SQLite export")
        except Exception as e:
            return _fail(f"SQLite export failed: {e}")

    def _export_excel(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        sheet_name: str = "Sheet1",
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as Excel file."""
        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_excel(filepath, sheet_name=sheet_name, index=False, **options)

            return _success(None)

        except ImportError:
            return _fail("pandas and openpyxl required for Excel export")
        except Exception as e:
            return _fail(f"Excel export failed: {e}")

    def _export_feather(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        **options: Any,
    ) -> FlextResult[None]:
        """Export data as Feather format."""
        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_feather(filepath, **options)

            return _success(None)

        except ImportError:
            return _fail("pandas and pyarrow required for Feather export")
        except Exception as e:
            return _fail(f"Feather export failed: {e}")

    def get_supported_formats(self) -> list[str]:
        """Get list of supported export formats."""
        return sorted(self._supported_formats)

    def export_multiple_formats(
        self,
        data: list[dict[str, Any]] | dict[str, Any],
        base_path: str | Path,
        formats: list[str],
        **options: Any,
    ) -> FlextResult[dict[str, str]]:
        """Export data to multiple formats simultaneously.

        Returns:
            FlextResult with dict mapping format -> result message

        """
        try:
            base_path = Path(base_path)
            results = {}

            for format_type in formats:
                if format_type not in self._supported_formats:
                    results[format_type] = f"Unsupported format: {format_type}"
                    continue

                # Generate filepath with appropriate extension
                extension_map = {
                    "csv": ".csv", "tsv": ".tsv", "json": ".json", "jsonl": ".jsonl",
                    "parquet": ".parquet", "sqlite": ".sqlite", "excel": ".xlsx",
                    "feather": ".feather",
                }

                filepath = base_path.with_suffix(extension_map.get(format_type, f".{format_type}"))
                result = self.export_data(data, filepath, format_type, **options)

                results[format_type] = result.unwrap() if result.success else result.error

            return FlextResult.ok(results)

        except Exception as e:
            return _fail(f"Multiple format export failed: {e}")

    @classmethod
    def create_csv_exporter(cls) -> FlextCliDataExporter:
        """Create exporter optimized for CSV format."""
        return cls(default_format="csv")

    @classmethod
    def create_json_exporter(cls) -> FlextCliDataExporter:
        """Create exporter optimized for JSON format."""
        return cls(default_format="json")

    @classmethod
    def create_parquet_exporter(cls) -> FlextCliDataExporter:
        """Create exporter optimized for Parquet format."""
        return cls(default_format="parquet")

    @classmethod
    def create_database_exporter(cls) -> FlextCliDataExporter:
        """Create exporter optimized for database formats."""
        return cls(default_format="sqlite")

    def get_format_info(self, format_type: str) -> FlextResult[dict[str, Any]]:
        """Get information about a specific format."""
        format_info = {
            "csv": {
                "description": "Comma-Separated Values",
                "use_case": "Tabular data, Excel compatibility",
                "pros": ["Universal compatibility", "Human readable", "Small size"],
                "cons": ["No data types", "No nested structures"],
            },
            "tsv": {
                "description": "Tab-Separated Values",
                "use_case": "Tabular data with commas in values",
                "pros": ["Handles commas in data", "Simple format"],
                "cons": ["Less common", "No data types"],
            },
            "json": {
                "description": "JavaScript Object Notation",
                "use_case": "API responses, configuration files",
                "pros": ["Nested structures", "Data types", "Human readable"],
                "cons": ["Larger file size", "No schema validation"],
            },
            "parquet": {
                "description": "Columnar storage format",
                "use_case": "Big data, analytics, data lakes",
                "pros": ["Efficient compression", "Fast queries", "Schema evolution"],
                "cons": ["Requires special tools", "Not human readable"],
            },
            "sqlite": {
                "description": "Embedded SQL database",
                "use_case": "Relational data, queries, indexing",
                "pros": ["SQL queries", "ACID transactions", "Compact"],
                "cons": ["Single writer", "Not distributed"],
            },
        }

        if format_type not in format_info:
            return _fail(f"Unknown format: {format_type}")

        return FlextResult.ok(format_info[format_type])

    def then_export(
        self,
        filepath: str | Path,
        format_type: str | None = None,
        **options: Any,
    ) -> ExportChain:
        """Create chainable export operation for massive code reduction.

        Example:
            result = (exporter
                .then_export("users.csv")
                .and_export("users.json")
                .and_export("users.parquet")
                .execute(data)
            )

        """
        return ExportChain(self).then_export(filepath, format_type, **options)

    def instant(
        self,
        data: Any,
        format_type: str | None = None,
        auto_name: bool = True,
    ) -> FlextResult[str]:
        """Ultra-fast export with auto-generated filename.

        Example:
            filepath = exporter.instant(data, "csv").unwrap()

        """
        try:
            if auto_name:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                format_ext = format_type or self.default_format
                filename = f"flext_export_{timestamp}.{format_ext}"
            else:
                format_ext = format_type or self.default_format
                filename = f"export.{format_ext}"

            result = self.export_data(data, filename, format_type)
            if result.success:
                return _success(filename)
            return result

        except Exception as e:
            logger.exception("Instant export failed")
            return _fail(f"Instant export failed: {e}")

    def batch_export(
        self,
        datasets: dict[str, Any],
        base_path: str | Path = "./exports",
        formats: list[str] | None = None,
    ) -> FlextResult[dict[str, Any]]:
        """Export multiple datasets simultaneously.

        Example:
            result = exporter.batch_export({
                "users": users_data,
                "orders": orders_data,
                "products": products_data
            }, formats=["csv", "json"])

        """
        try:
            if formats is None:
                formats = ["csv", "json"]

            base_path = Path(base_path)
            base_path.mkdir(parents=True, exist_ok=True)

            results = {}

            for name, data in datasets.items():
                dataset_results = {}
                for format_type in formats:
                    filepath = base_path / f"{name}.{format_type}"
                    export_result = self.export_data(data, filepath, format_type)
                    dataset_results[format_type] = {
                        "success": export_result.success,
                        "filepath": str(filepath) if export_result.success else None,
                        "error": export_result.error if not export_result.success else None,
                    }
                results[name] = dataset_results

            return _success(results)

        except Exception as e:
            logger.exception("Batch export failed")
            return _fail(f"Batch export failed: {e}")


class ExportChain:
    """Chainable export operations for massive code reduction."""

    def __init__(self, exporter: FlextCliDataExporter) -> None:
        self.exporter = exporter
        self.operations: list[dict[str, Any]] = []

    def then_export(
        self,
        filepath: str | Path,
        format_type: str | None = None,
        **options: Any,
    ) -> ExportChain:
        """Add export operation to chain."""
        self.operations.append({
            "filepath": filepath,
            "format_type": format_type,
            "options": options,
        })
        return self

    def and_export(
        self,
        filepath: str | Path,
        format_type: str | None = None,
        **options: Any,
    ) -> ExportChain:
        """Alias for then_export for better readability."""
        return self.then_export(filepath, format_type, **options)

    def execute(self, data: Any) -> FlextResult[dict[str, Any]]:
        """Execute all chained export operations."""
        try:
            results = {}

            for i, op in enumerate(self.operations):
                result = self.exporter.export_data(
                    data,
                    op["filepath"],
                    op["format_type"],
                    **op["options"],
                )

                operation_key = f"export_{i+1}"
                results[operation_key] = {
                    "filepath": str(op["filepath"]),
                    "success": result.success,
                    "message": result.data if result.success else result.error,
                }

                if not result.success:
                    logger.warning(f"Export {i+1} failed: {result.error}")

            return _success(results)

        except Exception as e:
            logger.exception("Chain execution failed")
            return _fail(f"Chain execution failed: {e}")
