"""Focused tests for FlextUtilities to achieve 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from unittest.mock import Mock
from uuid import UUID

import pytest
from flext_core import FlextUtilities
from pydantic import BaseModel, EmailStr, HttpUrl, ValidationError

from flext_cli.utils import FlextCliUtilities


class TestFlextUtilitiesCoverageFocused:
    """Focused FlextUtilities tests targeting 100% coverage."""

    def test_conversions_safe_int_edge_cases(self) -> None:
        """Test safe_int with various edge cases to hit exception paths."""
        # Test normal cases
        assert FlextUtilities.Conversions.safe_int("123") == 123
        assert FlextUtilities.Conversions.safe_int(45.7) == 45
        assert FlextUtilities.Conversions.safe_int("456", default=99) == 456

        # Test ValueError cases
        assert FlextUtilities.Conversions.safe_int("invalid") == 0
        assert FlextUtilities.Conversions.safe_int("not_a_number", default=42) == 42
        assert FlextUtilities.Conversions.safe_int("") == 0

        # Test TypeError cases
        assert FlextUtilities.Conversions.safe_int(None) == 0
        assert FlextUtilities.Conversions.safe_int(None, default=123) == 123
        assert FlextUtilities.Conversions.safe_int(object()) == 0

        # Test complex object that might raise TypeError
        mock_obj = Mock()
        mock_obj.__int__ = Mock(side_effect=TypeError("Cannot convert"))
        assert FlextUtilities.Conversions.safe_int(mock_obj, default=999) == 999

    def test_conversions_safe_bool_comprehensive(self) -> None:
        """Test safe_bool with comprehensive coverage of all paths."""
        # Test actual boolean values
        assert FlextUtilities.Conversions.safe_bool(True) is True
        assert FlextUtilities.Conversions.safe_bool(False) is False

        # Test string true values
        assert FlextUtilities.Conversions.safe_bool("true") is True
        assert FlextUtilities.Conversions.safe_bool("TRUE") is True
        assert FlextUtilities.Conversions.safe_bool("True") is True
        assert FlextUtilities.Conversions.safe_bool("1") is True
        assert FlextUtilities.Conversions.safe_bool("yes") is True
        assert FlextUtilities.Conversions.safe_bool("YES") is True
        assert FlextUtilities.Conversions.safe_bool("on") is True
        assert FlextUtilities.Conversions.safe_bool("ON") is True

        # Test string false values
        assert FlextUtilities.Conversions.safe_bool("false") is False
        assert FlextUtilities.Conversions.safe_bool("FALSE") is False
        assert FlextUtilities.Conversions.safe_bool("False") is False
        assert FlextUtilities.Conversions.safe_bool("0") is False
        assert FlextUtilities.Conversions.safe_bool("no") is False
        assert FlextUtilities.Conversions.safe_bool("NO") is False
        assert FlextUtilities.Conversions.safe_bool("off") is False
        assert FlextUtilities.Conversions.safe_bool("OFF") is False

        # Test string default case (unrecognized strings)
        assert FlextUtilities.Conversions.safe_bool("invalid") is False
        assert FlextUtilities.Conversions.safe_bool("maybe", default=True) is True
        assert FlextUtilities.Conversions.safe_bool("unknown") is False

        # Test non-string, non-bool values with truthy/falsy
        assert FlextUtilities.Conversions.safe_bool(1) is True
        assert FlextUtilities.Conversions.safe_bool(0) is False
        assert FlextUtilities.Conversions.safe_bool([1, 2, 3]) is True
        assert FlextUtilities.Conversions.safe_bool([]) is False
        assert FlextUtilities.Conversions.safe_bool({"key": "value"}) is True
        assert FlextUtilities.Conversions.safe_bool({}) is False

        # Test None and default handling
        assert FlextUtilities.Conversions.safe_bool(None) is False
        assert FlextUtilities.Conversions.safe_bool(None, default=True) is True

        # Test exception handling paths
        mock_obj = Mock()
        mock_obj.__bool__ = Mock(side_effect=ValueError("Cannot convert to bool"))
        assert FlextUtilities.Conversions.safe_bool(mock_obj) is False
        assert FlextUtilities.Conversions.safe_bool(mock_obj, default=True) is True

        # Test TypeError path
        mock_obj2 = Mock()
        mock_obj2.__bool__ = Mock(side_effect=TypeError("Type error"))
        assert FlextUtilities.Conversions.safe_bool(mock_obj2, default=True) is True

    def test_conversions_safe_float_edge_cases(self) -> None:
        """Test safe_float with various edge cases to hit exception paths."""
        # Test normal cases
        assert FlextUtilities.Conversions.safe_float("123.45") == 123.45
        assert FlextUtilities.Conversions.safe_float(67.89) == 67.89
        assert FlextUtilities.Conversions.safe_float("456.78", default=99.9) == 456.78

        # Test ValueError cases
        assert FlextUtilities.Conversions.safe_float("invalid") == 0.0
        assert (
            FlextUtilities.Conversions.safe_float("not_a_number", default=42.5) == 42.5
        )
        assert FlextUtilities.Conversions.safe_float("") == 0.0

        # Test TypeError cases
        assert FlextUtilities.Conversions.safe_float(None) == 0.0
        assert FlextUtilities.Conversions.safe_float(None, default=123.4) == 123.4
        assert FlextUtilities.Conversions.safe_float(object()) == 0.0

        # Test complex object that might raise TypeError
        mock_obj = Mock()
        mock_obj.__float__ = Mock(side_effect=TypeError("Cannot convert"))
        assert FlextUtilities.Conversions.safe_float(mock_obj, default=999.9) == 999.9

    def test_generators_edge_cases(self) -> None:
        """Test Generators class methods for edge case coverage."""
        # Test generate_entity_id
        id1 = FlextUtilities.Generators.generate_entity_id()
        id2 = FlextUtilities.Generators.generate_entity_id()
        assert id1 != id2
        assert isinstance(id1, str)
        assert len(id1) > 0

        # Test generate_correlation_id
        corr_id = FlextUtilities.Generators.generate_correlation_id()
        assert isinstance(corr_id, str)
        assert len(corr_id) > 0

    def test_text_processor_edge_cases(self) -> None:
        """Test TextProcessor class methods for edge case coverage."""
        # Test clean_text with various inputs
        assert (
            FlextUtilities.TextProcessor.clean_text("valid_name.txt")
            == "valid_name.txt"
        )
        result = FlextUtilities.TextProcessor.slugify("file/with\\slashes")
        assert isinstance(result, str)
        assert "file" in result
        assert "with" in result

        # Test safe_string
        assert FlextUtilities.TextProcessor.safe_string("hello") == "hello"
        assert (
            FlextUtilities.TextProcessor.safe_string(None)
            == ""
        )

        # Test edge cases
        assert FlextUtilities.TextProcessor.safe_string("") == ""
        # Test is_non_empty_string
        assert FlextUtilities.TextProcessor.is_non_empty_string("hello") is True
        assert FlextUtilities.TextProcessor.is_non_empty_string("") is False

    def test_type_guards_comprehensive(self) -> None:
        """Test TypeGuards class methods comprehensively."""
        # Test is_string_non_empty
        assert FlextUtilities.TypeGuards.is_string_non_empty("hello") is True
        assert FlextUtilities.TypeGuards.is_string_non_empty("") is False
        assert FlextUtilities.TypeGuards.is_string_non_empty(None) is False
        assert FlextUtilities.TypeGuards.is_string_non_empty(123) is False

        # Test is_dict_non_empty
        assert FlextUtilities.TypeGuards.is_dict_non_empty({"key": "value"}) is True
        assert FlextUtilities.TypeGuards.is_dict_non_empty({}) is False
        assert FlextUtilities.TypeGuards.is_dict_non_empty(None) is False

        # Test is_list_non_empty
        assert FlextUtilities.TypeGuards.is_list_non_empty([1, 2, 3]) is True
        assert FlextUtilities.TypeGuards.is_list_non_empty([]) is False
        assert FlextUtilities.TypeGuards.is_list_non_empty(None) is False

    def test_utility_functions_edge_cases(self) -> None:
        """Test utility functions for edge case coverage."""
        # Test generate_iso_timestamp
        timestamp = FlextUtilities.generate_iso_timestamp()
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format contains T

        # Test safe_json_stringify with various data types
        result = FlextUtilities.safe_json_stringify({"key": "value"})
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result
        result2 = FlextUtilities.safe_json_stringify([1, 2, 3])
        assert isinstance(result2, str)
        assert "1" in result2
        assert "2" in result2
        assert "3" in result2
        result3 = FlextUtilities.safe_json_stringify("simple string")
        assert isinstance(result3, str)
        assert "simple string" in result3

        # Test with non-serializable object (should return fallback)
        non_serializable = object()
        result = FlextUtilities.safe_json_stringify(non_serializable)
        assert isinstance(result, str)
        assert result == "{}"  # Non-serializable objects return empty JSON

    def test_validation_with_pydantic_models(self) -> None:
        """Test validation using Pydantic v2 models directly."""

        # Test UUID validation using Pydantic v2
        class UUIDModel(BaseModel):
            uuid_field: UUID

        valid_uuid = str(uuid.uuid4())

        # Valid UUID should work
        model = UUIDModel(uuid_field=UUID(valid_uuid))
        assert str(model.uuid_field) == valid_uuid

        # Invalid UUIDs should raise ValidationError
        with pytest.raises(ValidationError):
            UUIDModel(uuid_field="invalid-uuid")

        # Test EmailStr validation using Pydantic v2
        class EmailModel(BaseModel):
            email: EmailStr

        valid_email = EmailModel(email="test@example.com")
        assert str(valid_email.email) == "test@example.com"

        with pytest.raises(ValidationError):
            EmailModel(email="invalid-email")

        # Test HttpUrl validation using Pydantic v2
        class UrlModel(BaseModel):
            url: HttpUrl

        valid_url = UrlModel(url=HttpUrl("https://example.com"))
        assert str(valid_url.url) == "https://example.com/"

        with pytest.raises(ValidationError):
            UrlModel(url="invalid-url")

        # Test validate_with_pydantic_model utility
        data = {"uuid_field": valid_uuid}
        result = FlextCliUtilities.validate_with_pydantic_model(data, UUIDModel)
        assert result.is_success
        assert isinstance(result.unwrap(), UUIDModel)

        # Test validation failure
        invalid_data = {"uuid_field": "invalid-uuid"}
        result = FlextCliUtilities.validate_with_pydantic_model(invalid_data, UUIDModel)
        assert result.is_failure
        assert "Validation failed" in (result.error or "")

    def test_conversions_with_mock_exceptions(self) -> None:
        """Test conversion methods with mocked exceptions to ensure all paths are covered."""
        # Create mock objects that raise specific exceptions

        # Test safe_int with object that raises ValueError in __int__
        mock_obj = Mock()
        mock_obj.__int__ = Mock(side_effect=ValueError("Mock ValueError"))
        assert FlextUtilities.Conversions.safe_int(mock_obj, default=555) == 555

        # Test safe_float with object that raises ValueError in __float__
        mock_obj2 = Mock()
        mock_obj2.__float__ = Mock(side_effect=ValueError("Mock ValueError"))
        assert FlextUtilities.Conversions.safe_float(mock_obj2, default=777.7) == 777.7
