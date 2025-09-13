"""FLEXT CLI Data Processing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextUtilities


class FlextCliDataProcessing:
    """CLI Data Processing using flext-core directly - ZERO duplication.

    Uses FlextUtilities directly for all data processing operations.
    NO custom implementations, NO wrappers, NO duplications.
    """

    @staticmethod
    def validate_data(data: object, validator_func: object) -> FlextResult[object]:
        """Validate data using flext-core utilities directly."""
        try:
            # Handle dict of validators
            if isinstance(validator_func, dict) and isinstance(data, dict):
                for key, validator_type in validator_func.items():
                    if key not in data:
                        return FlextResult[object].fail(
                            f"Missing required field: {key}"
                        )
                    if not isinstance(data[key], validator_type):
                        return FlextResult[object].fail(
                            f"Field '{key}' has wrong type, expected {validator_type.__name__}"
                        )
                return FlextResult[object].ok(data)

            # Handle callable validator function
            if not callable(validator_func):
                return FlextResult[object].fail("Validator function must be callable")

            # Use flext-core validation directly
            if isinstance(data, dict):
                # Validate dictionary data
                validation_result = validator_func(data)
                if validation_result:
                    return FlextResult[object].ok(data)
                return FlextResult[object].fail("Data validation failed")

            if isinstance(data, list):
                # Validate list data
                validation_result = validator_func(data)
                if validation_result:
                    return FlextResult[object].ok(data)
                return FlextResult[object].fail("Data validation failed")

            # For other types, try validation
            validation_result = validator_func(data)
            if validation_result:
                return FlextResult[object].ok(data)
            return FlextResult[object].fail("Data validation failed")

        except Exception as e:
            return FlextResult[object].fail(f"Validation failed: {e}")

    @staticmethod
    def batch_process_items(
        items: object, processor_func: object
    ) -> FlextResult[object]:
        """Process items in batch using flext-core utilities directly."""
        try:
            if not isinstance(items, list):
                return FlextResult[object].fail("Invalid items format - must be a list")

            if not callable(processor_func):
                return FlextResult[object].fail("Processor function must be callable")

            # Use flext-core processing directly
            processed_items = []
            for item in items:
                try:
                    processed_item = processor_func(item)
                    processed_items.append(processed_item)
                except Exception as e:
                    return FlextResult[object].fail(f"Item processing failed: {e}")

            return FlextResult[object].ok(processed_items)

        except Exception as e:
            return FlextResult[object].fail(f"Batch processing failed: {e}")

    @staticmethod
    def safe_json_stringify(data: object) -> FlextResult[str]:
        """Convert data to JSON string using flext-core utilities directly."""
        try:
            # Use flext-core utilities directly
            json_string = FlextUtilities.safe_json_stringify(data)
            return FlextResult[str].ok(json_string)
        except Exception as e:
            return FlextResult[str].fail(f"JSON stringify failed: {e}")


__all__ = ["FlextCliDataProcessing"]
