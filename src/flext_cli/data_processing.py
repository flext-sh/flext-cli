"""FLEXT CLI Data Processing - Data transformation utilities using flext-core.

Provides FlextCliDataProcessing class for data workflows, validation,
transformation, and aggregation leveraging flext-core utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import FlextResult, FlextUtilities


class FlextCliDataProcessing:
    """Consolidated data processing utilities using flext-core capabilities.

    Provides comprehensive data processing operations including workflow
    execution, validation and transformation, aggregation, and batch
    operations leveraging flext-core utilities for maximum reuse.

    Features:
        - Multi-step workflow processing
        - Data validation and transformation
        - Aggregation from multiple sources
        - Type-safe conversions via FlextUtilities
        - Pipeline processing with error handling
    """

    def __init__(self) -> None:
        """Initialize data processing utilities."""

    def process_workflow(
        self,
        data: dict[str, object],
        steps: list[tuple[str, Callable[[object], FlextResult[object]]]],
    ) -> FlextResult[object]:
        """Process data through multi-step workflow.

        Args:
            data: Initial data to process
            steps: List of (name, function) tuples for processing steps

        Returns:
            FlextResult containing final processed data

        """
        try:
            current: object = data
            for step_name, step_func in steps:
                result = step_func(current)
                if isinstance(result, FlextResult) and result.is_failure:
                    return FlextResult[object].fail(
                        f"Step '{step_name}' failed: {result.error}"
                    )
                current = result.value if isinstance(result, FlextResult) else result
            return FlextResult[object].ok(current)
        except Exception as e:
            return FlextResult[object].fail(f"Workflow processing failed: {e}")

    def validate_and_transform(
        self,
        data: dict[str, object],
        validators: dict[str, str],
        transforms: dict[str, Callable[[object], object]] | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Validate and transform data dictionary with type checking.

        Args:
            data: Data dictionary to validate
            validators: Field validation rules (field_name -> type_name)
            transforms: Optional field transformations

        Returns:
            FlextResult containing validated and transformed data

        """
        try:
            output = dict(data)

            # Validation phase using FlextUtilities
            for field, expected_type in validators.items():
                value = output.get(field)
                if value is None:
                    continue

                if expected_type == "int":
                    converted = FlextUtilities.Conversions.safe_int(value, -1)
                    if converted == -1 and str(value) not in {"0", "0.0", ""}:
                        return FlextResult[dict[str, object]].fail(
                            f"Invalid integer for field '{field}': {value}"
                        )
                    output[field] = converted or 0

                elif expected_type == "str":
                    output[field] = FlextUtilities.TextProcessor.safe_string(value, "")

                elif expected_type == "bool":
                    if isinstance(value, bool):
                        output[field] = value
                    else:
                        # Convert string representations to boolean
                        str_value = str(value).lower()
                        if str_value in {"true", "1", "yes", "on"}:
                            output[field] = True
                        elif str_value in {"false", "0", "no", "off"}:
                            output[field] = False
                        else:
                            return FlextResult[dict[str, object]].fail(
                                f"Invalid boolean for field '{field}': {value}"
                            )

            # Transformation phase
            if transforms:
                for field, transform_func in transforms.items():
                    if field in output:
                        try:
                            output[field] = transform_func(output[field])
                        except Exception as e:
                            return FlextResult[dict[str, object]].fail(
                                f"Transform failed for field '{field}': {e}"
                            )

            return FlextResult[dict[str, object]].ok(output)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Validation and transform failed: {e}"
            )

    def aggregate_data(
        self, sources: dict[str, Callable[[], FlextResult[object]]]
    ) -> FlextResult[dict[str, object]]:
        """Aggregate data from multiple sources with error handling.

        Args:
            sources: Dictionary of source_name -> data_provider_function

        Returns:
            FlextResult containing aggregated data from all sources

        """
        try:
            result: dict[str, object] = {}
            errors: list[str] = []

            for name, provider in sources.items():
                try:
                    provider_result = provider()
                    if isinstance(provider_result, FlextResult):
                        if provider_result.is_success:
                            result[name] = provider_result.value
                        else:
                            errors.append(f"{name}: {provider_result.error}")
                            result[name] = None
                    else:
                        result[name] = provider_result
                except Exception as e:
                    errors.append(f"{name}: {e}")
                    result[name] = None

            if errors:
                # Include errors in metadata but don't fail completely
                result["_errors"] = errors

            return FlextResult[dict[str, object]].ok(result)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Data aggregation failed: {e}")

    def transform_data_pipeline(
        self, data: list[dict[str, object]], pipeline_config: dict[str, object]
    ) -> FlextResult[list[dict[str, object]]]:
        """Transform data through configurable pipeline.

        Args:
            data: List of data dictionaries to transform
            pipeline_config: Pipeline configuration settings

        Returns:
            FlextResult containing transformed data

        """
        try:
            # Extract configuration with proper typing
            filter_field_raw = pipeline_config.get("filter_field")
            filter_field = str(filter_field_raw) if filter_field_raw else None
            filter_value = pipeline_config.get("filter_value")
            sort_field_raw = pipeline_config.get("sort_field")
            sort_field = str(sort_field_raw) if sort_field_raw else None
            sort_reverse = bool(pipeline_config.get("sort_reverse"))

            result: list[dict[str, object]] = list(data)  # Create copy

            # Apply filtering if configured
            if filter_field and filter_value is not None:
                result = [
                    item
                    for item in result
                    if isinstance(item, dict) and item.get(filter_field) == filter_value
                ]

            # Apply sorting if configured
            if sort_field:
                try:

                    def sort_key(x: dict[str, object]) -> str:
                        if isinstance(x, dict) and sort_field:
                            val = x.get(sort_field, "")
                            return str(val) if val is not None else ""
                        return ""

                    result.sort(key=sort_key, reverse=sort_reverse)
                except Exception as e:
                    return FlextResult[list[dict[str, object]]].fail(
                        f"Sorting by '{sort_field}' failed: {e}"
                    )

            return FlextResult[list[dict[str, object]]].ok(result)
        except Exception as e:
            return FlextResult[list[dict[str, object]]].fail(
                f"Pipeline transformation failed: {e}"
            )

    def batch_validate(self, values: list[object]) -> FlextResult[list[object]]:
        """Validate batch of values for consistency.

        Args:
            values: List of values to validate

        Returns:
            FlextResult containing validated values

        """
        try:
            validated = []
            for i, value in enumerate(values):
                if value is None or (isinstance(value, str) and not value.strip()):
                    return FlextResult[list[object]].fail(
                        f"Invalid empty value at index {i}"
                    )
                validated.append(value)

            return FlextResult[list[object]].ok(validated)
        except Exception as e:
            return FlextResult[list[object]].fail(f"Batch validation failed: {e}")


__all__ = ["FlextCliDataProcessing"]
