"""FLEXT CLI Data Processing - Direct flext-core usage.

NO WRAPPERS - Direct usage of flext-core FlextUtilities.
Eliminates duplicate data processing patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextUtilities


class FlextCliDataProcessing:
    """Direct flext-core FlextUtilities usage - NO WRAPPERS."""

    @staticmethod
    def validate_data(data: object, validator: object) -> FlextResult[object]:
        """Validate data using flext-core directly."""
        try:
            if callable(validator):
                result = FlextUtilities.ValidationUtils.validate_with_callable(data, validator)
                if result.is_success:
                    return FlextResult[object].ok(data)
                return FlextResult[object].fail(result.error or "Validation failed")
            return FlextResult[object].fail("Validator must be callable")
        except Exception as e:
            return FlextResult[object].fail(f"Validation failed: {e}")

    @staticmethod
    def batch_process_items(items: object, processor: object) -> FlextResult[object]:
        """Process items in batch using flext-core directly."""
        try:
            if isinstance(items, list) and callable(processor):
                # Create a wrapper that returns FlextResult
                def wrapped_processor(item: object) -> FlextResult[object]:
                    try:
                        result = processor(item)
                        return FlextResult[object].ok(result)
                    except Exception as e:
                        return FlextResult[object].fail(f"Processing failed: {e}")

                result = FlextUtilities.batch_process(items, wrapped_processor)
                if result.is_failure:
                    return FlextResult[object].fail(result.error or "Batch processing failed")
                return FlextResult[object].ok(result.unwrap())
            return FlextResult[object].fail("Invalid items format")
        except Exception as e:
            return FlextResult[object].fail(f"Batch processing failed: {e}")

    @staticmethod
    def safe_json_stringify(data: object) -> FlextResult[str]:
        """Safe JSON stringify using flext-core directly."""
        try:
            result = FlextUtilities.safe_json_stringify(data)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"JSON stringify failed: {e}")


__all__ = [
    "FlextCliDataProcessing",
]
