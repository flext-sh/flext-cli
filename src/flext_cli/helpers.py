"""FlextCli Helpers - Advanced boilerplate reduction utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar, Union

from flext_core import FlextResult

# Type definitions for massive boilerplate reduction
FlextCliData = Union[list[dict[str, Any]], dict[str, Any], Any]
FlextCliCallback = Callable[[Any], Any]
FlextCliPredicate = Callable[[Any], bool]
FlextCliTransform = Callable[[Any], Any]

T = TypeVar("T")
R = TypeVar("R")


class FlextCliMixin:
    """Base mixin providing common FlextResult patterns."""

    def _success(self, data: Any = None) -> FlextResult[Any]:
        """Helper for success results."""
        return FlextResult(success=True, data=data, error=None)

    def _fail(self, error: str) -> FlextResult[Any]:
        """Helper for failure results."""
        return FlextResult(success=False, data=None, error=error)

    def _try_execute(self, operation: Callable[[], T], error_prefix: str = "") -> FlextResult[T]:
        """Execute operation with automatic error handling."""
        try:
            result = operation()
            return self._success(result)
        except Exception as e:
            error_msg = f"{error_prefix}: {e}" if error_prefix else str(e)
            return self._fail(error_msg)


class FlextCliDataMixin(FlextCliMixin):
    """Mixin for data operations with massive boilerplate reduction."""

    def _normalize_data(self, data: FlextCliData) -> list[dict[str, Any]]:
        """Normalize any data to list of dicts."""
        if data is None:
            return []
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        # Convert other types to dict representation
        if hasattr(data, "__dict__"):
            return [data.__dict__]
        return [{"value": data}]

    def _validate_data(self, data: FlextCliData, operation: str = "operation") -> FlextResult[list[dict[str, Any]]]:
        """Validate and normalize data with error handling."""
        try:
            normalized = self._normalize_data(data)
            if not normalized:
                return self._fail(f"No data provided for {operation}")
            return self._success(normalized)
        except Exception as e:
            return self._fail(f"Data validation failed for {operation}: {e}")

    def _apply_transform(self, data: list[dict[str, Any]], transform: FlextCliTransform) -> list[dict[str, Any]]:
        """Apply transformation to data safely."""
        try:
            if callable(transform):
                return [transform(item) for item in data]
            return data
        except Exception:
            return data  # Return original on error

    def _filter_data(self, data: list[dict[str, Any]], predicate: FlextCliPredicate) -> list[dict[str, Any]]:
        """Filter data safely."""
        try:
            if callable(predicate):
                return [item for item in data if predicate(item)]
            return data
        except Exception:
            return data  # Return original on error




def flext_cli_chain(*operations: Callable[[Any], FlextResult[Any]]) -> Callable[[Any], FlextResult[Any]]:
    """Chain multiple FlextResult operations."""
    def chained_operation(data: Any) -> FlextResult[Any]:
        current_result = FlextResult(success=True, data=data, error=None)

        for operation in operations:
            if not current_result.success:
                break
            current_result = operation(current_result.data)

        return current_result

    return chained_operation


def flext_cli_safe_call[T](func: Callable[..., T], *args: Any, **kwargs: Any) -> FlextResult[T]:
    """Safely call any function with FlextResult wrapping."""
    try:
        result = func(*args, **kwargs)
        return FlextResult(success=True, data=result, error=None)
    except Exception as e:
        return FlextResult(success=False, data=None, error=str(e))


class FlextCliDict(dict):
    """Enhanced dict with FlextResult operations."""

    def safe_get(self, key: str, default: Any = None) -> FlextResult[Any]:
        """Get value safely with FlextResult."""
        try:
            value = self.get(key, default)
            if value is None and key not in self:
                return FlextResult(success=False, data=None, error=f"Key '{key}' not found")
            return FlextResult(success=True, data=value, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def safe_update(self, other: dict) -> FlextResult[FlextCliDict]:
        """Update dict safely with FlextResult."""
        try:
            self.update(other)
            return FlextResult(success=True, data=self, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def transform_values(self, transform: Callable[[Any], Any]) -> FlextResult[FlextCliDict]:
        """Transform all values with FlextResult."""
        try:
            new_dict = FlextCliDict()
            for key, value in self.items():
                new_dict[key] = transform(value)
            return FlextResult(success=True, data=new_dict, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def filter_keys(self, predicate: Callable[[str], bool]) -> FlextResult[FlextCliDict]:
        """Filter keys with FlextResult."""
        try:
            new_dict = FlextCliDict({k: v for k, v in self.items() if predicate(k)})
            return FlextResult(success=True, data=new_dict, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))


class FlextCliList(list):
    """Enhanced list with FlextResult operations."""

    def safe_append(self, item: Any) -> FlextResult[FlextCliList]:
        """Append item safely with FlextResult."""
        try:
            self.append(item)
            return FlextResult(success=True, data=self, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def safe_transform(self, transform: Callable[[Any], Any]) -> FlextResult[FlextCliList]:
        """Transform all items with FlextResult."""
        try:
            new_list = FlextCliList(transform(item) for item in self)
            return FlextResult(success=True, data=new_list, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def safe_filter(self, predicate: Callable[[Any], bool]) -> FlextResult[FlextCliList]:
        """Filter items with FlextResult."""
        try:
            new_list = FlextCliList(item for item in self if predicate(item))
            return FlextResult(success=True, data=new_list, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))

    def safe_reduce(self, func: Callable[[Any, Any], Any], initial: Any = None) -> FlextResult[Any]:
        """Reduce list safely with FlextResult."""
        try:
            if initial is not None:
                result = functools.reduce(func, self, initial)
            else:
                result = functools.reduce(func, self)
            return FlextResult(success=True, data=result, error=None)
        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))


def flext_cli_batch_process(
    items: list[Any],
    processor: Callable[[Any], FlextResult[Any]],
    fail_fast: bool = False,
) -> FlextResult[list[Any]]:
    """Process items in batch with comprehensive error handling."""
    results = []
    errors = []

    for i, item in enumerate(items):
        try:
            result = processor(item)
            if result.success:
                results.append(result.data)
            else:
                error_msg = f"Item {i}: {result.error}"
                errors.append(error_msg)
                if fail_fast:
                    return FlextResult(success=False, data=None, error=error_msg)
                results.append(None)  # Placeholder for failed item
        except Exception as e:
            error_msg = f"Item {i}: Unexpected error: {e}"
            errors.append(error_msg)
            if fail_fast:
                return FlextResult(success=False, data=None, error=error_msg)
            results.append(None)

    if errors and fail_fast:
        return FlextResult(success=False, data=None, error=f"Batch processing failed: {errors[0]}")

    # Return success even with some errors if not fail_fast
    return FlextResult(
        success=True,
        data={
            "results": results,
            "errors": errors,
            "success_count": len([r for r in results if r is not None]),
            "error_count": len(errors),
        },
        error=None,
    )


class FlextCliBuilder:
    """Fluent builder for complex operations."""

    def __init__(self) -> None:
        self._data: Any = None
        self._transforms: list[Callable] = []
        self._filters: list[Callable] = []
        self._validators: list[Callable] = []

    def with_data(self, data: Any) -> FlextCliBuilder:
        """Set data for processing."""
        self._data = data
        return self

    def transform(self, func: Callable[[Any], Any]) -> FlextCliBuilder:
        """Add transformation step."""
        self._transforms.append(func)
        return self

    def filter(self, predicate: Callable[[Any], bool]) -> FlextCliBuilder:
        """Add filter step."""
        self._filters.append(predicate)
        return self

    def validate(self, validator: Callable[[Any], bool]) -> FlextCliBuilder:
        """Add validation step."""
        self._validators.append(validator)
        return self

    def execute(self) -> FlextResult[Any]:
        """Execute all operations in sequence."""
        try:
            current_data = self._data

            # Apply transformations
            for transform in self._transforms:
                if isinstance(current_data, list):
                    current_data = [transform(item) for item in current_data]
                else:
                    current_data = transform(current_data)

            # Apply filters
            for filter_func in self._filters:
                if isinstance(current_data, list):
                    current_data = [item for item in current_data if filter_func(item)]
                elif not filter_func(current_data):
                    return FlextResult(success=False, data=None, error="Data failed filter validation")

            # Apply validators
            for validator in self._validators:
                if isinstance(current_data, list):
                    if not all(validator(item) for item in current_data):
                        return FlextResult(success=False, data=None, error="Data failed validation")
                elif not validator(current_data):
                    return FlextResult(success=False, data=None, error="Data failed validation")

            return FlextResult(success=True, data=current_data, error=None)

        except Exception as e:
            return FlextResult(success=False, data=None, error=str(e))


# Convenience functions for massive boilerplate reduction
def flext_cli_quick_dict(**kwargs: Any) -> FlextCliDict:
    """Create FlextCliDict with fluent operations."""
    return FlextCliDict(kwargs)


def flext_cli_quick_list(*items: Any) -> FlextCliList:
    """Create FlextCliList with fluent operations."""
    return FlextCliList(items)


def flext_cli_quick_builder(data: Any = None) -> FlextCliBuilder:
    """Create FlextCliBuilder for fluent operations."""
    builder = FlextCliBuilder()
    if data is not None:
        builder.with_data(data)
    return builder


def flext_cli_pipeline_simple(
    data: Any,
    *operations: Callable[[Any], Any],
) -> FlextResult[Any]:
    """Simple pipeline for data transformations."""
    try:
        current_data = data
        for operation in operations:
            current_data = operation(current_data)
        return FlextResult(success=True, data=current_data, error=None)
    except Exception as e:
        return FlextResult(success=False, data=None, error=str(e))


# Export helpers for boilerplate reduction
__all__ = [
    # Builder pattern
    "FlextCliBuilder",
    "FlextCliCallback",
    # Type definitions
    "FlextCliData",
    "FlextCliDataMixin",
    # Enhanced containers
    "FlextCliDict",
    "FlextCliList",
    # Mixins
    "FlextCliMixin",
    "FlextCliPredicate",
    "FlextCliTransform",
    # Batch processing
    "flext_cli_batch_process",
    "flext_cli_chain",
    "flext_cli_pipeline_simple",
    "flext_cli_quick_builder",
    # Quick helpers
    "flext_cli_quick_dict",
    "flext_cli_quick_list",
    "flext_cli_safe_call",
]
