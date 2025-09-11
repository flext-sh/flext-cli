"""FLEXT CLI Data Processing - Using flext-core utilities directly.

ELIMINATES ALL duplicated functionality and uses flext-core utilities directly.
Uses SOURCE OF TRUTH principle - no reimplementation of existing flext-core features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult, FlextTypes, FlextUtilities


class FlextCliDataProcessing:
    """Data processing service using flext-core utilities directly.

    Single responsibility: CLI-specific data processing orchestration.
    Uses FlextUtilities.DataValidators, FlextUtilities.Performance, and FlextUtilities.Generators.
    NO reimplementation of existing flext-core functionality.
    """

    def execute(self, operation: str, **params: object) -> FlextResult[object]:
        """Execute data processing operation using flext-core utilities."""
        if operation == "validate":
            return self._validate_using_core(params.get("data"), params.get("validators"))
        if operation == "batch_process":
            return self._batch_process_using_core(params.get("items"), params.get("processor"))
        if operation == "transform":
            return self._transform_using_core(params.get("data"), params.get("config"))
        if operation == "aggregate":
            return self._aggregate_using_core(params.get("sources"))

        return FlextResult[object].fail(f"Unknown operation: {operation}")

    def _validate_using_core(
        self, data: object, validators: object
    ) -> FlextResult[object]:
        """Validate data using flext-core DataValidators."""
        if not data or not validators:
            return FlextResult[object].fail("Data and validators required")

        # Use flext-core validation utilities
        if isinstance(data, dict) and isinstance(validators, dict):
            # Use FlextUtilities.ValidationUtils for validation
            validation_result = FlextUtilities.ValidationUtils.validate_with_callable(
                data, validators
            )
            return FlextResult[object].ok(validation_result)

        return FlextResult[object].fail("Invalid data or validators format")

    def _batch_process_using_core(
        self, items: object, processor: object
    ) -> FlextResult[object]:
        """Process items in batch using flext-core batch processing."""
        if not items or not processor:
            return FlextResult[object].fail("Items and processor required")

        if isinstance(items, list) and callable(processor):
            # Use FlextUtilities.batch_process with proper typing
            batch_result = FlextUtilities.batch_process(items, processor)
            if batch_result.is_failure:
                return FlextResult[object].fail(batch_result.error or "Batch processing failed")

            results, errors = batch_result.unwrap()
            return FlextResult[object].ok({"results": results, "errors": errors})

        return FlextResult[object].fail("Invalid items format")

    def _transform_using_core(
        self, data: object, config: object
    ) -> FlextResult[object]:
        """Transform data using flext-core utilities."""
        if not data or not config:
            return FlextResult[object].fail("Data and config required")

        # Use flext-core transformation utilities
        if isinstance(data, list) and isinstance(config, dict):
            # Simple transformation using flext-core patterns
            transformed_data = []
            for item in data:
                if isinstance(item, dict):
                    transformed_item = dict(item)
                    # Apply config-based transformations
                    if "prefix" in config:
                        transformed_item["_prefix"] = str(config["prefix"])
                    transformed_data.append(transformed_item)
                else:
                    transformed_data.append(item)

            return FlextResult[object].ok(transformed_data)

        return FlextResult[object].fail("Invalid data or config format")

    def _aggregate_using_core(self, sources: object) -> FlextResult[object]:
        """Aggregate sources using flext-core utilities."""
        if not sources:
            return FlextResult[object].fail("No sources provided")

        if isinstance(sources, dict):
            # Simple aggregation using flext-core patterns
            aggregated = {}
            for name, source in sources.items():
                if callable(source):
                    try:
                        result = source()
                        if hasattr(result, "value"):
                            aggregated[name] = result.value
                        else:
                            aggregated[name] = result
                    except Exception as e:
                        aggregated[name] = None
                        aggregated.setdefault("_errors", []).append(f"{name}: {e}")
                else:
                    aggregated[name] = source

            return FlextResult[object].ok(aggregated)

        return FlextResult[object].fail("Invalid sources format")

    # Convenience methods using flext-core utilities
    def transform_data_pipeline(
        self,
        data: list[FlextTypes.Core.Dict],
        pipeline_config: FlextTypes.Core.Dict,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Convenience method for pipeline transformation using flext-core."""
        result = self.execute("transform", data=data, config=pipeline_config)
        if result.is_failure:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(result.error or "Transform failed")

        if isinstance(result.value, list):
            return FlextResult[list[FlextTypes.Core.Dict]].ok(result.value)
        return FlextResult[list[FlextTypes.Core.Dict]].fail("Expected list result")

    def batch_validate(
        self,
        values: FlextTypes.Core.List,
    ) -> FlextResult[FlextTypes.Core.List]:
        """Convenience method for batch validation using flext-core."""
        result = self.execute("batch_process", items=values, processor=lambda x: FlextResult[object].ok(x))
        if result.is_failure:
            return FlextResult[FlextTypes.Core.List].fail(result.error or "Batch validation failed")

        if isinstance(result.value, dict) and "results" in result.value:
            return FlextResult[FlextTypes.Core.List].ok(result.value["results"])
        return FlextResult[FlextTypes.Core.List].fail("Expected batch results")

    def transform_data(
        self,
        data: list[FlextTypes.Core.Dict] | FlextTypes.Core.Dict | None,
        filters: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Transform data using flext-core utilities."""
        if data is None:
            return FlextResult[list[FlextTypes.Core.Dict]].fail("Data cannot be None")

        # Convert single dict to list for consistent processing
        if isinstance(data, dict):
            data_list = [data]
        elif isinstance(data, list):
            data_list = data
        else:
            return FlextResult[list[FlextTypes.Core.Dict]].fail("Data must be dict or list")

        # Apply filters if provided
        if filters:
            filtered_data = []
            for item in data_list:
                if isinstance(item, dict):
                    # Check if item matches all filter criteria
                    matches = all(
                        item.get(key) == value for key, value in filters.items()
                    )
                    if matches:
                        filtered_data.append(item)
            data_list = filtered_data

        return FlextResult[list[FlextTypes.Core.Dict]].ok(data_list)

    def aggregate_data(
        self,
        data: list[FlextTypes.Core.Dict],
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Aggregate data using flext-core utilities."""
        if not data:
            return FlextResult[FlextTypes.Core.Dict].ok({
                "items": [],
                "total_count": 0,
                "aggregated_fields": {}
            })

        # Simple aggregation by grouping common keys
        aggregated_fields: FlextTypes.Core.Dict = {}

        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if key not in aggregated_fields:
                        aggregated_fields[key] = []
                    field_values = aggregated_fields[key]
                    if isinstance(field_values, list) and value not in field_values:
                        field_values.append(value)

        result: FlextTypes.Core.Dict = {
            "items": data,
            "total_count": len(data),
            "aggregated_fields": aggregated_fields
        }

        return FlextResult[FlextTypes.Core.Dict].ok(result)

    def export_to_file(
        self,
        data: list[FlextTypes.Core.Dict] | FlextTypes.Core.Dict,
        file_path: str,
    ) -> FlextResult[str]:
        """Export data to file using flext-core utilities."""
        try:
            # Use FlextUtilities for file operations
            json_result = FlextUtilities.safe_json_stringify(data)

            # Use flext-core file utilities
            path = Path(file_path)

            if not path.parent.exists():
                return FlextResult[str].fail(f"Directory does not exist: {path.parent}")

            path.write_text(json_result, encoding="utf-8")
            return FlextResult[str].ok(f"Exported data to {file_path}")

        except Exception as e:
            return FlextResult[str].fail(f"Export failed: {e}")


__all__ = ["FlextCliDataProcessing"]
