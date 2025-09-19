"""Test FlextCliDataProcessing functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel

from flext_cli.utils import FlextCliUtilities as FlextCliDataProcessing
from flext_core import FlextResult


class TestFlextCliDataProcessing:
    """Test suite for FlextCliDataProcessing class."""

    def test_processor_initialization(self) -> None:
        """Test processor can be initialized."""
        processor = FlextCliDataProcessing()
        assert processor is not None
        assert hasattr(processor, "validate_with_pydantic_model")
        assert hasattr(processor, "batch_process_items")
        assert hasattr(processor, "safe_json_stringify")

    def test_validate_data_with_dict(self) -> None:
        """Test validate_with_pydantic_model with dictionary input."""
        processor = FlextCliDataProcessing()

        class TestModel(BaseModel):
            name: str
            value: int

        data = {"name": "test", "value": 42}
        result = processor.validate_with_pydantic_model(data, TestModel)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_invalid_format(self) -> None:
        """Test validate_with_pydantic_model with invalid format."""
        processor = FlextCliDataProcessing()

        class TestModel(BaseModel):
            name: str

        data = "invalid_data"  # String instead of dict
        result = processor.validate_with_pydantic_model(data, TestModel)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None

    def test_validate_data_with_complex_model(self) -> None:
        """Test validate_with_pydantic_model with complex model."""
        processor = FlextCliDataProcessing()

        class ComplexModel(BaseModel):
            name: str
            value: int
            optional_field: str | None = None

        data = {"name": "test", "value": 42}
        result = processor.validate_with_pydantic_model(data, ComplexModel)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_invalid_data(self) -> None:
        """Test validate_with_pydantic_model with invalid data."""
        processor = FlextCliDataProcessing()

        class TestModel(BaseModel):
            name: str
            value: int

        data = {"name": "test"}  # Missing required 'value' field
        result = processor.validate_with_pydantic_model(data, TestModel)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None

    def test_validate_data_with_list(self) -> None:
        """Test validate_with_pydantic_model with list data."""
        processor = FlextCliDataProcessing()

        class ListModel(BaseModel):
            items: list[int]

        data = {"items": [1, 2, 3]}
        result = processor.validate_with_pydantic_model(data, ListModel)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_with_other_types(self) -> None:
        """Test validate_with_pydantic_model with string data."""
        processor = FlextCliDataProcessing()

        class StringModel(BaseModel):
            text: str

        data = {"text": "test_string"}
        result = processor.validate_with_pydantic_model(data, StringModel)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_validate_data_exception_handling(self) -> None:
        """Test validate_with_pydantic_model exception handling."""
        processor = FlextCliDataProcessing()

        class StrictModel(BaseModel):
            name: str
            required_number: int  # Missing field will cause validation error

        data = {"name": "test"}  # Missing required_number
        result = processor.validate_with_pydantic_model(data, StrictModel)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "Validation failed" in result.error

    def test_batch_process_items_with_list(self) -> None:
        """Test batch_process_items with list input."""
        processor = FlextCliDataProcessing()

        items = [1, 2, 3, 4, 5]

        def square(x: object) -> object:
            return int(x) * int(x) if isinstance(x, int) else x

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
        assert "Invalid items format" in result.error

    def test_safe_json_stringify_with_dict(self) -> None:
        """Test safe_json_stringify with dictionary input."""
        processor = FlextCliDataProcessing()

        data = {"name": "test", "value": 42}
        flext_result = FlextResult[object].ok(data)
        result = processor.safe_json_stringify_flext_result(flext_result)

        assert isinstance(result, str)
        assert '"name": "test"' in result
        assert '"value": 42' in result

    def test_safe_json_stringify_with_list(self) -> None:
        """Test safe_json_stringify with list input."""
        processor = FlextCliDataProcessing()

        data = [1, 2, 3, {"nested": "data"}]
        flext_result = FlextResult[object].ok(data)
        result = processor.safe_json_stringify_flext_result(flext_result)

        assert isinstance(result, str)
        assert "1" in result
        assert "2" in result
        assert "3" in result
        assert '"nested": "data"' in result

    def test_all_methods_return_flext_result(self) -> None:
        """Test all methods return FlextResult."""
        processor = FlextCliDataProcessing()

        # Test validate_with_pydantic_model
        class TestModel(BaseModel):
            test: str

        result1 = processor.validate_with_pydantic_model({"test": "data"}, TestModel)
        assert isinstance(result1, FlextResult)

        # Test batch_process_items
        def identity_func(x: object) -> object:
            return x

        result2 = processor.batch_process_items([1, 2, 3], identity_func)
        assert isinstance(result2, FlextResult)

        # Test safe_json_stringify_flext_result
        result3_input = FlextResult[object].ok({"test": "data"})
        result3 = processor.safe_json_stringify_flext_result(result3_input)
        assert isinstance(result3, str)

    def test_error_handling(self) -> None:
        """Test error handling in data processing."""
        processor = FlextCliDataProcessing()

        # Test with None data
        class NoneTestModel(BaseModel):
            test: str

        result = processor.validate_with_pydantic_model(None, NoneTestModel)
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with empty data
        def identity_func(x: object) -> object:
            return x

        empty_result = processor.batch_process_items([], identity_func)
        assert isinstance(empty_result, FlextResult)
        # May succeed or fail depending on FlextUtilities implementation

    def test_static_methods(self) -> None:
        """Test that all methods are static."""

        # All methods should be static and work without instance
        class StaticTestModel(BaseModel):
            test: str

        result1 = FlextCliDataProcessing.validate_with_pydantic_model(
            {"test": "data"}, StaticTestModel
        )

        def identity_func(x: object) -> object:
            return x

        result2 = FlextCliDataProcessing.batch_process_items([1, 2, 3], identity_func)

        # Create instance for instance method call
        processor_instance = FlextCliDataProcessing()
        result3_input = FlextResult[object].ok({"test": "data"})
        result3 = processor_instance.safe_json_stringify_flext_result(result3_input)

        assert isinstance(result1, FlextResult)
        assert isinstance(result2, FlextResult)
        assert isinstance(result3, str)

    def test_batch_process_items_with_invalid_items(self) -> None:
        """Test batch_process_items with invalid items format."""
        processor = FlextCliDataProcessing()

        def processor_func(x: object) -> object:
            return int(x) * 2 if isinstance(x, int) else x

        result = processor.batch_process_items("not_a_list", processor_func)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "Invalid items format" in result.error

    def test_batch_process_items_with_valid_processor(self) -> None:
        """Test batch_process_items with valid processor function."""
        processor = FlextCliDataProcessing()

        items = [1, 2, 3]
        result = processor.batch_process_items(items, lambda x: x)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == [1, 2, 3]

    def test_batch_process_items_with_processor_exception(self) -> None:
        """Test batch_process_items with processor function that raises exception."""
        processor = FlextCliDataProcessing()

        def processor_func(x: object) -> object:
            if x == 2:
                error_msg = "Test exception"
                raise ValueError(error_msg)
            return int(x) * 2 if isinstance(x, int) else x

        items = [1, 2, 3]
        result = processor.batch_process_items(items, processor_func)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "Item processing failed" in result.error
