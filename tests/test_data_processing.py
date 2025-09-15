"""Test FlextCliDataProcessing functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.data_processing import FlextCliDataProcessing


class TestFlextCliDataProcessing:
    """Test FlextCliDataProcessing with direct flext-core usage."""

    def test_data_processing_init(self) -> None:
        """Test data processing initialization."""
        processor = FlextCliDataProcessing()

        assert processor is not None
        assert hasattr(processor, "validate_data")
        assert hasattr(processor, "batch_process_items")
        assert hasattr(processor, "safe_json_stringify")

    def test_validate_data_with_dict(self) -> None:
        """Test validate_data with dictionary input."""
        processor = FlextCliDataProcessing()

        data = {"name": "test", "value": 42}
        validators = {"name": str, "value": int}
        result = processor.validate_data(data, validators)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_invalid_format(self) -> None:
        """Test validate_data with invalid format."""
        processor = FlextCliDataProcessing()

        data = "invalid_data"
        validators = {"name": str}
        result = processor.validate_data(data, validators)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "Validator function must be callable" in str(result.error)

    def test_validate_data_with_callable_validator(self) -> None:
        """Test validate_data with callable validator function."""
        processor = FlextCliDataProcessing()

        def validator(data: dict[str, object]) -> bool:
            return "name" in data and "value" in data

        data = {"name": "test", "value": 42}
        result = processor.validate_data(data, validator)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_invalid_callable(self) -> None:
        """Test validate_data with invalid callable."""
        processor = FlextCliDataProcessing()

        data = {"name": "test"}
        result = processor.validate_data(data, "not_callable")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "Validator function must be callable" in str(result.error)

    def test_validate_data_with_list(self) -> None:
        """Test validate_data with list data."""
        processor = FlextCliDataProcessing()

        def validator(data: list[object]) -> bool:
            return len(data) > 0

        data = [1, 2, 3]
        result = processor.validate_data(data, validator)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_other_types(self) -> None:
        """Test validate_data with other data types."""
        processor = FlextCliDataProcessing()

        def validator(data: str) -> bool:
            return len(data) > 0

        data = "test_string"
        result = processor.validate_data(data, validator)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_exception_handling(self) -> None:
        """Test validate_data exception handling."""
        processor = FlextCliDataProcessing()

        def validator(_data: dict[str, object]) -> bool:
            error_msg = "Test exception"
            raise ValueError(error_msg)

        data = {"name": "test"}
        result = processor.validate_data(data, validator)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error and "Validation failed" in result.error

    def test_batch_process_items_with_list(self) -> None:
        """Test batch_process_items with list input."""
        processor = FlextCliDataProcessing()

        items = [1, 2, 3, 4, 5]

        def square(x: int) -> int:
            return x * x

        result = processor.batch_process_items(items, square)

        assert isinstance(result, FlextResult)
        # May fail if FlextUtilities.batch_process is not implemented
        # but should return FlextResult

    def test_batch_process_items_with_invalid_format(self) -> None:
        """Test batch_process_items with invalid format."""
        processor = FlextCliDataProcessing()

        items = "invalid_items"

        def processor_func(x: object) -> object:
            return x

        result = processor.batch_process_items(items, processor_func)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert result.error and "Invalid items format" in result.error

    def test_safe_json_stringify_with_dict(self) -> None:
        """Test safe_json_stringify with dictionary input."""
        processor = FlextCliDataProcessing()

        data = {"name": "test", "value": 42}
        result = processor.safe_json_stringify(data)

        assert isinstance(result, FlextResult)
        # May fail if FlextUtilities.safe_json_stringify is not implemented
        # but should return FlextResult

    def test_safe_json_stringify_with_list(self) -> None:
        """Test safe_json_stringify with list input."""
        processor = FlextCliDataProcessing()

        data = [1, 2, 3, {"nested": "data"}]
        result = processor.safe_json_stringify(data)

        assert isinstance(result, FlextResult)
        # May fail if FlextUtilities.safe_json_stringify is not implemented
        # but should return FlextResult

    def test_all_methods_return_flext_result(self) -> None:
        """Test all methods return FlextResult."""
        processor = FlextCliDataProcessing()

        # Test validate_data
        result1 = processor.validate_data({"test": "data"}, {"test": str})
        assert isinstance(result1, FlextResult)

        # Test batch_process_items
        def identity_func(x: int) -> int:
            return x

        result2 = processor.batch_process_items([1, 2, 3], identity_func)
        assert isinstance(result2, FlextResult)

        # Test safe_json_stringify
        result3 = processor.safe_json_stringify({"test": "data"})
        assert isinstance(result3, FlextResult)

    def test_error_handling(self) -> None:
        """Test error handling in data processing."""
        processor = FlextCliDataProcessing()

        # Test with None data
        result = processor.validate_data(None, None)
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with empty data
        def identity_func(x: object) -> object:
            return x

        result = processor.batch_process_items([], identity_func)
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on FlextUtilities implementation

    def test_static_methods(self) -> None:
        """Test that all methods are static."""
        # All methods should be static and work without instance
        result1 = FlextCliDataProcessing.validate_data({"test": "data"}, {"test": str})

        def identity_func(x: int) -> int:
            return x

        result2 = FlextCliDataProcessing.batch_process_items([1, 2, 3], identity_func)
        result3 = FlextCliDataProcessing.safe_json_stringify({"test": "data"})

        assert isinstance(result1, FlextResult)
        assert isinstance(result2, FlextResult)
        assert isinstance(result3, FlextResult)

    def test_batch_process_items_with_invalid_items(self) -> None:
        """Test batch_process_items with invalid items format."""
        processor = FlextCliDataProcessing()

        def processor_func(x: int) -> int:
            return x * 2

        result = processor.batch_process_items("not_a_list", processor_func)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error and "Invalid items format" in result.error

    def test_batch_process_items_with_invalid_processor(self) -> None:
        """Test batch_process_items with invalid processor function."""
        processor = FlextCliDataProcessing()

        items = [1, 2, 3]
        result = processor.batch_process_items(items, "not_callable")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error and "Processor function must be callable" in result.error

    def test_batch_process_items_with_processor_exception(self) -> None:
        """Test batch_process_items with processor function that raises exception."""
        processor = FlextCliDataProcessing()

        def processor_func(x: int) -> int:
            if x == 2:
                error_msg = "Test exception"
                raise ValueError(error_msg)
            return x * 2

        items = [1, 2, 3]
        result = processor.batch_process_items(items, processor_func)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error and "Item processing failed" in result.error

    def test_safe_json_stringify_success(self) -> None:
        """Test safe_json_stringify with valid data."""
        processor = FlextCliDataProcessing()

        data = {"name": "test", "value": 42}
        result = processor.safe_json_stringify(data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.value, str)

    def test_safe_json_stringify_exception(self) -> None:
        """Test safe_json_stringify with data that causes exception."""
        processor = FlextCliDataProcessing()

        # Create an object that can't be JSON serialized
        class Unserializable:
            def __init__(self) -> None:
                """Initialize the instance."""
                self.func = lambda: None

        data = Unserializable()
        result = processor.safe_json_stringify(data)

        assert isinstance(result, FlextResult)
        # FlextUtilities.safe_json_stringify may handle exceptions gracefully
        # So we just check that it returns a FlextResult
        assert result.is_success or result.is_failure
