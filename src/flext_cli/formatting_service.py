"""CLI Formatting Service - Single responsibility for data formatting.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import yaml

from flext_cli.formatters import FlextCliFormatters
from flext_core import FlextDomainService, FlextLogger, FlextResult

# Constants
DATASET_TUPLE_EXPECTED_LENGTH = 2


class FlextCliFormattingService(FlextDomainService[str]):
    """Unified formatting service using single responsibility principle.

    Handles ALL data formatting operations for CLI ecosystem.
    ARCHITECTURAL COMPLIANCE: One class per module, nested helpers pattern.
    """

    def __init__(self) -> None:
        """Initialize formatting service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._formatters = FlextCliFormatters()

    class _FormatValidationHelper:
        """Nested helper for format validation - no loose functions."""

        @staticmethod
        def validate_format_type(format_type: str) -> FlextResult[str]:
            """Validate format type parameter."""
            if not format_type or not isinstance(format_type, str):
                return FlextResult[str].fail("Format type must be a non-empty string")

            valid_formats = {"json", "yaml", "csv", "table", "plain"}
            if format_type.lower() not in valid_formats:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

            return FlextResult[str].ok(format_type.lower())

        @staticmethod
        def validate_data_structure(data: object) -> FlextResult[object]:
            """Validate data structure for formatting."""
            if data is None:
                return FlextResult[object].fail("Data cannot be None")

            return FlextResult[object].ok(data)

    class _FilePathHelper:
        """Nested helper for file path operations - no loose functions."""

        @staticmethod
        def validate_file_path(file_path: object) -> FlextResult[Path]:
            """Validate and convert file path."""
            if not isinstance(file_path, (str, Path)):
                return FlextResult[Path].fail("File path must be string or Path")

            path = Path(file_path)
            if not path.parent.exists():
                return FlextResult[Path].fail(
                    f"Parent directory does not exist: {path.parent}"
                )

            return FlextResult[Path].ok(path)

    def execute(self) -> FlextResult[str]:
        """Execute formatting operation - FlextDomainService interface."""
        self._logger.info("Executing formatting service operation")
        return FlextResult[str].ok("Formatting service operational")

    def format_data(
        self,
        data: object,
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data using specified format type - single responsibility."""
        # Input validation using nested helper
        format_validation = self._FormatValidationHelper.validate_format_type(
            format_type
        )
        if format_validation.is_failure:
            return FlextResult[str].fail(
                format_validation.error or "Format validation failed"
            )

        data_validation = self._FormatValidationHelper.validate_data_structure(data)
        if data_validation.is_failure:
            return FlextResult[str].fail(
                data_validation.error or "Data validation failed"
            )

        validated_format = format_validation.unwrap()
        validated_data = data_validation.unwrap()

        # Delegate to appropriate formatter based on type
        match validated_format:
            case "json":
                return self._format_as_json(validated_data)
            case "yaml":
                return self._format_as_yaml(validated_data)
            case "csv":
                return self._format_as_csv(validated_data)
            case "table":
                return self._format_as_table(validated_data, **options)
            case "plain":
                return FlextResult[str].ok(str(validated_data))
            case _:
                return FlextResult[str].fail(f"Unsupported format: {validated_format}")

    def _format_as_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON using standard library."""
        try:
            result = json.dumps(data, default=str, indent=2, ensure_ascii=False)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def _format_as_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML using standard library."""
        try:
            result = yaml.dump(
                data, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def _format_as_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV using proper CSV handling."""
        try:
            output = io.StringIO()

            if isinstance(data, list) and data and isinstance(data[0], dict):
                # List of dictionaries - standard CSV format
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            elif isinstance(data, dict):
                # Single dictionary - convert to single row
                fieldnames = list(data.keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
            else:
                # Fallback to string representation
                string_writer = csv.writer(output)
                string_writer.writerow([str(data)])

            result = output.getvalue()
            output.close()
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

    def _format_as_table(self, data: object, **options: object) -> FlextResult[str]:
        """Format data as table with proper type casting."""
        if not data:
            return FlextResult[str].fail("Cannot create table from empty data")

        try:
            headers_value = options.get("headers")
            headers = headers_value if isinstance(headers_value, list) else None

            title_value = options.get("title")
            title = title_value if isinstance(title_value, str) else None

            show_lines_value = options.get("show_lines", True)
            show_lines = (
                show_lines_value if isinstance(show_lines_value, bool) else True
            )

            table_result = self._formatters.create_table(
                data=data, headers=headers, title=title, show_lines=show_lines
            )

            if table_result.is_failure:
                return FlextResult[str].fail(
                    f"Table creation failed: {table_result.error or 'Unknown error'}"
                )

            return FlextResult[str].ok(str(table_result.unwrap()))
        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e!s}")

    def export_formatted_data(
        self,
        data: object,
        file_path: str | Path,
        format_type: str = "json",
    ) -> FlextResult[Path]:
        """Export formatted data to file - single responsibility."""
        # Validate file path using nested helper
        path_validation = self._FilePathHelper.validate_file_path(file_path)
        if path_validation.is_failure:
            return FlextResult[Path].fail(
                path_validation.error or "File path validation failed"
            )

        validated_path = path_validation.unwrap()

        # Format data using existing formatting logic
        format_result = self.format_data(data, format_type)
        if format_result.is_failure:
            return FlextResult[Path].fail(f"Formatting failed: {format_result.error}")

        formatted_content = format_result.unwrap()

        # Write to file
        try:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            validated_path.write_text(formatted_content, encoding="utf-8")
            return FlextResult[Path].ok(validated_path)
        except Exception as e:
            return FlextResult[Path].fail(f"File export failed: {e}")

    def batch_export_datasets(
        self,
        datasets: list[tuple[str, object]],
        base_path: str | Path,
        format_type: str = "json",
    ) -> FlextResult[list[Path]]:
        """Export multiple datasets to files - single responsibility."""
        if not isinstance(datasets, list):
            return FlextResult[list[Path]].fail("Datasets must be a list")

        # Validate base path using nested helper
        base_validation = self._FilePathHelper.validate_file_path(base_path)
        if base_validation.is_failure:
            return FlextResult[list[Path]].fail(
                base_validation.error or "Base path validation failed"
            )

        base = base_validation.unwrap()
        exported_files: list[Path] = []

        for dataset_item in datasets:
            if (
                not isinstance(dataset_item, tuple)
                or len(dataset_item) != DATASET_TUPLE_EXPECTED_LENGTH
            ):
                return FlextResult[list[Path]].fail(
                    "Each dataset must be a tuple of (name, data)"
                )

            name, data = dataset_item

            if not isinstance(name, str) or not name:
                return FlextResult[list[Path]].fail(
                    "Dataset names must be non-empty strings"
                )

            filename = f"{name}.{format_type}"
            file_path = base / filename

            # Export individual dataset
            export_result = self.export_formatted_data(data, file_path, format_type)
            if export_result.is_failure:
                return FlextResult[list[Path]].fail(
                    f"Export failed for {name}: {export_result.error}"
                )

            exported_files.append(export_result.unwrap())

        return FlextResult[list[Path]].ok(exported_files)


__all__ = ["FlextCliFormattingService"]
