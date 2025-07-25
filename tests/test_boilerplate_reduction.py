"""Test boilerplate reduction helpers and decorators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

import pytest
from flext_cli import (
    FlextCliDataMixin,
    FlextCliMixin,
    FlextResult,
    flext_cli_auto_export,
    flext_cli_batch_process,
    flext_cli_cache_result,
    flext_cli_chain,
    flext_cli_data_validator,
    flext_cli_pipeline_simple,
    flext_cli_pipeline_step,
    flext_cli_quick_builder,
    flext_cli_quick_cache,
    flext_cli_quick_dict,
    flext_cli_quick_list,
    flext_cli_quick_retry,
    flext_cli_quick_timing,
    flext_cli_result_wrapper,
    flext_cli_retry,
    flext_cli_safe_call,
    flext_cli_timing,
)


class TestFlextCliMixins:
    """Test FlextCli mixins for common patterns."""

    def test_base_mixin_success_helper(self) -> None:
        """Test base mixin success helper."""
        class TestClass(FlextCliMixin):
            def test_method(self) -> FlextResult[str]:
                return self._success("test data")

        instance = TestClass()
        result = instance.test_method()

        assert result.success
        assert result.data == "test data"
        assert result.error is None

    def test_base_mixin_fail_helper(self) -> None:
        """Test base mixin fail helper."""
        class TestClass(FlextCliMixin):
            def test_method(self) -> FlextResult[str]:
                return self._fail("test error")

        instance = TestClass()
        result = instance.test_method()

        assert not result.success
        assert result.data is None
        assert result.error == "test error"

    def test_base_mixin_try_execute(self) -> None:
        """Test base mixin try_execute helper."""
        class TestClass(FlextCliMixin):
            def test_success(self) -> FlextResult[int]:
                return self._try_execute(lambda: 42, "Test operation")

            def test_failure(self) -> FlextResult[int]:
                return self._try_execute(lambda: 1 / 0, "Division")

        instance = TestClass()

        # Test successful execution
        success_result = instance.test_success()
        assert success_result.success
        assert success_result.data == 42

        # Test failed execution
        fail_result = instance.test_failure()
        assert not fail_result.success
        assert "Division:" in fail_result.error

    def test_data_mixin_normalize_data(self) -> None:
        """Test data mixin normalize data functionality."""
        class TestClass(FlextCliDataMixin):
            def normalize(self, data: Any) -> list[dict[str, Any]]:
                return self._normalize_data(data)

        instance = TestClass()

        # Test dict normalization
        dict_result = instance.normalize({"key": "value"})
        assert dict_result == [{"key": "value"}]

        # Test list passthrough
        list_result = instance.normalize([{"a": 1}, {"b": 2}])
        assert list_result == [{"a": 1}, {"b": 2}]

        # Test None handling
        none_result = instance.normalize(None)
        assert none_result == []

        # Test object with __dict__
        class TestObject:
            def __init__(self) -> None:
                self.attr = "value"

        obj_result = instance.normalize(TestObject())
        assert obj_result == [{"attr": "value"}]

    def test_data_mixin_validate_data(self) -> None:
        """Test data mixin validate data functionality."""
        class TestClass(FlextCliDataMixin):
            def validate(self, data: Any) -> FlextResult[list[dict[str, Any]]]:
                return self._validate_data(data, "test operation")

        instance = TestClass()

        # Test valid data
        valid_result = instance.validate([{"key": "value"}])
        assert valid_result.success
        assert valid_result.data == [{"key": "value"}]

        # Test empty data
        empty_result = instance.validate([])
        assert not empty_result.success
        assert "No data provided" in empty_result.error

    def test_data_mixin_transform_data(self) -> None:
        """Test data mixin transform data functionality."""
        class TestClass(FlextCliDataMixin):
            def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
                return self._apply_transform(data, lambda x: {**x, "transformed": True})

        instance = TestClass()
        data = [{"id": 1}, {"id": 2}]
        result = instance.transform(data)

        assert all("transformed" in item for item in result)
        assert all(item["transformed"] is True for item in result)

    def test_data_mixin_filter_data(self) -> None:
        """Test data mixin filter data functionality."""
        class TestClass(FlextCliDataMixin):
            def filter(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
                return self._filter_data(data, lambda x: x.get("keep", False))

        instance = TestClass()
        data = [
            {"id": 1, "keep": True},
            {"id": 2, "keep": False},
            {"id": 3, "keep": True},
        ]
        result = instance.filter(data)

        assert len(result) == 2
        assert all(item["keep"] is True for item in result)


class TestFlextCliEnhancedContainers:
    """Test enhanced containers with FlextResult operations."""

    def test_flext_cli_dict_safe_get(self) -> None:
        """Test FlextCliDict safe_get method."""
        data = flext_cli_quick_dict(name="Alice", age=30)

        # Test successful get
        name_result = data.safe_get("name")
        assert name_result.success
        assert name_result.data == "Alice"

        # Test missing key
        missing_result = data.safe_get("missing")
        assert not missing_result.success
        assert "not found" in missing_result.error

        # Test with default
        default_result = data.safe_get("missing", "default_value")
        assert default_result.success
        assert default_result.data == "default_value"

    def test_flext_cli_dict_safe_update(self) -> None:
        """Test FlextCliDict safe_update method."""
        data = flext_cli_quick_dict(name="Alice")

        update_result = data.safe_update({"age": 30, "city": "NYC"})
        assert update_result.success
        assert "age" in data
        assert "city" in data

    def test_flext_cli_dict_transform_values(self) -> None:
        """Test FlextCliDict transform_values method."""
        data = flext_cli_quick_dict(a=1, b=2, c=3)

        result = data.transform_values(lambda x: x * 2)
        assert result.success

        transformed = result.data
        assert transformed["a"] == 2
        assert transformed["b"] == 4
        assert transformed["c"] == 6

    def test_flext_cli_dict_filter_keys(self) -> None:
        """Test FlextCliDict filter_keys method."""
        data = flext_cli_quick_dict(name="Alice", age=30, temp_data="remove")

        result = data.filter_keys(lambda k: not k.startswith("temp"))
        assert result.success

        filtered = result.data
        assert "name" in filtered
        assert "age" in filtered
        assert "temp_data" not in filtered

    def test_flext_cli_list_safe_operations(self) -> None:
        """Test FlextCliList safe operations."""
        data = flext_cli_quick_list(1, 2, 3)

        # Test safe_append
        append_result = data.safe_append(4)
        assert append_result.success
        assert 4 in data

        # Test safe_transform
        transform_result = data.safe_transform(lambda x: x * 2)
        assert transform_result.success
        assert transform_result.data == [2, 4, 6, 8]

        # Test safe_filter
        filter_result = data.safe_filter(lambda x: x > 2)
        assert filter_result.success
        assert filter_result.data == [3, 4]

    def test_flext_cli_list_safe_reduce(self) -> None:
        """Test FlextCliList safe_reduce method."""
        data = flext_cli_quick_list(1, 2, 3, 4, 5)

        # Test sum reduction
        sum_result = data.safe_reduce(lambda acc, x: acc + x, 0)
        assert sum_result.success
        assert sum_result.data == 15

        # Test without initial value
        product_result = data.safe_reduce(lambda acc, x: acc * x)
        assert product_result.success
        assert product_result.data == 120


class TestFlextCliFluentBuilder:
    """Test fluent builder for complex operations."""

    def test_fluent_builder_basic_operations(self) -> None:
        """Test basic fluent builder operations."""
        data = [{"id": 1, "value": 10}, {"id": 2, "value": 20}, {"id": 3, "value": 5}]

        result = (flext_cli_quick_builder(data)
            .transform(lambda x: {**x, "doubled": x["value"] * 2})
            .filter(lambda x: x["value"] > 7)
            .validate(lambda x: "doubled" in x)
            .execute()
        )

        assert result.success
        processed = result.data
        assert len(processed) == 2  # Only items with value > 7
        assert all("doubled" in item for item in processed)

    def test_fluent_builder_validation_failure(self) -> None:
        """Test fluent builder with validation failure."""
        data = [{"id": 1, "name": "Alice"}]

        result = (flext_cli_quick_builder(data)
            .validate(lambda x: "missing_field" in x)
            .execute()
        )

        assert not result.success
        assert "validation" in result.error.lower()

    def test_fluent_builder_empty_data(self) -> None:
        """Test fluent builder with no data."""
        result = (flext_cli_quick_builder()
            .with_data([{"test": "data"}])
            .transform(lambda x: {**x, "processed": True})
            .execute()
        )

        assert result.success
        assert result.data[0]["processed"] is True


class TestBatchProcessing:
    """Test batch processing utilities."""

    def test_batch_process_success(self) -> None:
        """Test successful batch processing."""
        items = [1, 2, 3, 4, 5]

        def processor(item: int) -> FlextResult[int]:
            return FlextResult(success=True, data=item * 2, error=None)

        result = flext_cli_batch_process(items, processor)
        assert result.success

        data = result.data
        assert data["success_count"] == 5
        assert data["error_count"] == 0
        assert data["results"] == [2, 4, 6, 8, 10]

    def test_batch_process_with_errors(self) -> None:
        """Test batch processing with some errors."""
        items = [1, 2, 3, 4, 5]

        def processor(item: int) -> FlextResult[int]:
            if item % 2 == 0:  # Even numbers fail
                return FlextResult(success=False, data=None, error=f"Even number: {item}")
            return FlextResult(success=True, data=item * 2, error=None)

        result = flext_cli_batch_process(items, processor, fail_fast=False)
        assert result.success

        data = result.data
        assert data["success_count"] == 3  # 1, 3, 5
        assert data["error_count"] == 2   # 2, 4
        assert len(data["errors"]) == 2

    def test_batch_process_fail_fast(self) -> None:
        """Test batch processing with fail_fast=True."""
        items = [1, 2, 3, 4, 5]

        def processor(item: int) -> FlextResult[int]:
            if item == 2:
                return FlextResult(success=False, data=None, error="Failed on 2")
            return FlextResult(success=True, data=item * 2, error=None)

        result = flext_cli_batch_process(items, processor, fail_fast=True)
        assert not result.success
        assert "Failed on 2" in result.error


class TestDecorators:
    """Test advanced decorators for boilerplate reduction."""

    def test_result_wrapper_decorator(self) -> None:
        """Test automatic FlextResult wrapping decorator."""
        @flext_cli_result_wrapper("Math operation failed")
        def add_numbers(a: int, b: int) -> int:
            return a + b

        # Test successful operation
        result = add_numbers(2, 3)
        assert result.success
        assert result.data == 5

        # Test with error (this would require causing an exception)
        @flext_cli_result_wrapper("Division failed")
        def divide(a: int, b: int) -> float:
            return a / b

        error_result = divide(1, 0)
        assert not error_result.success
        assert "Division failed" in error_result.error

    def test_retry_decorator(self) -> None:
        """Test retry decorator."""
        call_count = 0

        @flext_cli_retry(max_attempts=3, delay=0.01, backoff=1.0)
        def flaky_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "Temporary failure"
                raise ValueError(msg)
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_cache_decorator(self) -> None:
        """Test cache decorator."""
        call_count = 0

        @flext_cli_cache_result(ttl_seconds=1)
        def expensive_operation(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x

        # First call
        result1 = expensive_operation(5)
        assert result1 == 25
        assert call_count == 1

        # Second call (should use cache)
        result2 = expensive_operation(5)
        assert result2 == 25
        assert call_count == 1  # No additional call

        # Different argument (should call function)
        result3 = expensive_operation(6)
        assert result3 == 36
        assert call_count == 2

    def test_timing_decorator(self) -> None:
        """Test timing decorator."""
        @flext_cli_timing(log_result=False)
        def timed_function() -> str:
            time.sleep(0.01)  # Small delay
            return "completed"

        result = timed_function()
        assert result == "completed"
        assert hasattr(timed_function, "last_execution_time")
        assert timed_function.last_execution_time > 0.01

    def test_data_validator_decorator(self) -> None:
        """Test data validator decorator."""
        @flext_cli_data_validator(required_keys=["name", "id"], min_items=1)
        def process_users(users: list[dict[str, Any]]) -> int:
            return len(users)

        # Test valid data
        valid_users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = process_users(valid_users)
        assert result == 2

        # Test invalid data (missing key)
        with pytest.raises(ValueError, match="Missing required keys"):
            invalid_users = [{"id": 1}]  # Missing "name"
            process_users(invalid_users)

        # Test invalid data (too few items)
        with pytest.raises(ValueError, match="at least 1 items"):
            process_users([])

    def test_pipeline_step_decorator(self) -> None:
        """Test pipeline step decorator."""
        @flext_cli_pipeline_step("Data Processing", log_progress=False)
        def process_step(data: list[int]) -> list[int]:
            return [x * 2 for x in data]

        result = process_step([1, 2, 3])
        assert result == [2, 4, 6]
        assert hasattr(process_step, "step_name")
        assert process_step.step_name == "Data Processing"
        assert process_step.is_pipeline_step is True

    def test_auto_export_decorator(self) -> None:
        """Test auto export decorator."""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "exports"

            @flext_cli_auto_export(
                formats=["json"],
                base_path=str(export_path),
                auto_timestamp=False,
            )
            def generate_data() -> list[dict[str, Any]]:
                return [{"id": 1, "name": "test"}]

            result = generate_data()
            assert result == [{"id": 1, "name": "test"}]

            # Check if export file was created
            expected_file = export_path / "generate_data.json"
            assert expected_file.exists()

    def test_quick_decorators(self) -> None:
        """Test quick convenience decorators."""
        @flext_cli_quick_retry(attempts=2)
        def quick_retry_func() -> str:
            return "success"

        @flext_cli_quick_cache(minutes=1)
        def quick_cache_func(x: int) -> int:
            return x * 2

        @flext_cli_quick_timing()
        def quick_timing_func() -> str:
            return "timed"

        # Test that decorators work
        assert quick_retry_func() == "success"
        assert quick_cache_func(5) == 10
        assert quick_timing_func() == "timed"

        # Test decorator attributes
        assert hasattr(quick_cache_func, "cache_info")
        assert hasattr(quick_timing_func, "last_execution_time")


class TestUtilityFunctions:
    """Test utility functions for massive boilerplate reduction."""

    def test_chain_operations(self) -> None:
        """Test chaining FlextResult operations."""
        def double_value(data: int) -> FlextResult[int]:
            return FlextResult(success=True, data=data * 2, error=None)

        def add_ten(data: int) -> FlextResult[int]:
            return FlextResult(success=True, data=data + 10, error=None)

        def validate_positive(data: int) -> FlextResult[int]:
            if data > 0:
                return FlextResult(success=True, data=data, error=None)
            return FlextResult(success=False, data=None, error="Must be positive")

        chained_operation = flext_cli_chain(double_value, add_ten, validate_positive)
        result = chained_operation(5)

        assert result.success
        assert result.data == 20  # (5 * 2) + 10

    def test_chain_operations_with_failure(self) -> None:
        """Test chaining operations with failure."""
        def fail_operation(data: int) -> FlextResult[int]:
            return FlextResult(success=False, data=None, error="Operation failed")

        def never_called(data: int) -> FlextResult[int]:
            return FlextResult(success=True, data=data, error=None)

        chained_operation = flext_cli_chain(fail_operation, never_called)
        result = chained_operation(5)

        assert not result.success
        assert "Operation failed" in result.error

    def test_safe_call(self) -> None:
        """Test safe function calling."""
        def safe_function(a: int, b: int) -> int:
            return a + b

        def unsafe_function(a: int, b: int) -> float:
            return a / b

        # Test successful call
        safe_result = flext_cli_safe_call(safe_function, 2, 3)
        assert safe_result.success
        assert safe_result.data == 5

        # Test failed call
        unsafe_result = flext_cli_safe_call(unsafe_function, 1, 0)
        assert not unsafe_result.success
        assert "division by zero" in unsafe_result.error.lower()

    def test_pipeline_simple(self) -> None:
        """Test simple pipeline processing."""
        def double(x: list[int]) -> list[int]:
            return [i * 2 for i in x]

        def filter_even(x: list[int]) -> list[int]:
            return [i for i in x if i % 2 == 0]

        def sum_all(x: list[int]) -> int:
            return sum(x)

        result = flext_cli_pipeline_simple([1, 2, 3, 4], double, filter_even, sum_all)

        assert result.success
        assert result.data == 20  # [2, 4, 6, 8] -> [2, 4, 6, 8] -> 20

    def test_pipeline_simple_with_error(self) -> None:
        """Test simple pipeline with error."""
        def fail_operation(x: Any) -> Any:
            msg = "Pipeline step failed"
            raise ValueError(msg)

        result = flext_cli_pipeline_simple([1, 2, 3], fail_operation)

        assert not result.success
        assert "Pipeline step failed" in result.error


class TestIntegrationScenarios:
    """Test integration scenarios demonstrating massive boilerplate reduction."""

    def test_complete_data_processing_workflow(self) -> None:
        """Test complete workflow using multiple helpers."""
        # Start with raw data
        raw_data = [
            {"id": 1, "name": "Alice", "score": 85, "active": True},
            {"id": 2, "name": "Bob", "score": 92, "active": False},
            {"id": 3, "name": "Carol", "score": 78, "active": True},
        ]

        # Use fluent builder for complex processing
        processing_result = (flext_cli_quick_builder(raw_data)
            .filter(lambda x: x["active"])  # Only active users
            .transform(lambda x: {**x, "grade": "A" if x["score"] >= 90 else "B"})
            .validate(lambda x: "grade" in x)
            .execute()
        )

        assert processing_result.success
        processed_data = processing_result.data
        assert len(processed_data) == 2  # Alice and Carol
        assert all("grade" in item for item in processed_data)

        # Use enhanced dict for metadata
        metadata = flext_cli_quick_dict(
            total_processed=len(processed_data),
            timestamp="2024-01-15",
            processor="flext_cli_workflow",
        )

        # Add computed values safely
        avg_score_result = metadata.safe_get("total_processed")
        assert avg_score_result.success

        # Transform metadata values
        string_metadata_result = metadata.transform_values(str)
        assert string_metadata_result.success

    def test_decorator_combination_workflow(self) -> None:
        """Test combining multiple decorators for maximum boilerplate reduction."""
        @flext_cli_result_wrapper("Processing failed")
        @flext_cli_quick_retry(attempts=2)
        @flext_cli_quick_timing()
        @flext_cli_data_validator(required_keys=["id", "value"])
        def complex_processing(data: list[dict[str, Any]]) -> dict[str, Any]:
            total = sum(item["value"] for item in data)
            return {"total": total, "count": len(data), "average": total / len(data)}

        test_data = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20},
            {"id": 3, "value": 30},
        ]

        result = complex_processing(test_data)

        assert result.success
        summary = result.data
        assert summary["total"] == 60
        assert summary["count"] == 3
        assert summary["average"] == 20.0

        # Verify decorator functionality worked (function executed successfully)
        # The decorators worked correctly as evidenced by the successful result

    def test_error_resilient_batch_workflow(self) -> None:
        """Test error-resilient batch processing workflow."""
        # Mixed data with some invalid items
        mixed_data = [
            {"valid": True, "value": 10},
            {"valid": False},  # Missing value field
            {"valid": True, "value": 20},
            None,  # Invalid item
            {"valid": True, "value": 30},
        ]

        def safe_processor(item: Any) -> FlextResult[dict[str, Any]]:
            try:
                if item is None or not isinstance(item, dict):
                    return FlextResult(success=False, data=None, error="Invalid item type")

                if not item.get("valid", False):
                    return FlextResult(success=False, data=None, error="Item marked as invalid")

                if "value" not in item:
                    return FlextResult(success=False, data=None, error="Missing value field")

                processed = {"original_value": item["value"], "doubled": item["value"] * 2}
                return FlextResult(success=True, data=processed, error=None)

            except Exception as e:
                return FlextResult(success=False, data=None, error=str(e))

        batch_result = flext_cli_batch_process(mixed_data, safe_processor, fail_fast=False)

        assert batch_result.success
        summary = batch_result.data
        assert summary["success_count"] == 3  # Valid items
        assert summary["error_count"] == 2   # Invalid items
        assert len(summary["results"]) == 5   # All items processed (with None for failures)
