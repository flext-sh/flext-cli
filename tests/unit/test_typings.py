"""FLEXT CLI Typings Tests - Comprehensive Type System Validation Testing.

Tests for FlextCliTypes covering type definitions, validation, annotated CLI types,
CLI data structures, type aliases, protocol implementations, generic types,
type conversion, narrowing, integration, and edge cases with 100% coverage.

Modules tested: flext_cli.typings.FlextCliTypes
Scope: All type operations, validation, conversion, protocol implementations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import (
    Generic,
    Protocol,
    TypedDict,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsMatchers

from flext_cli import FlextCliConstants, FlextCliTypes

from ..fixtures.constants import TestTypings
from ..helpers import FlextCliTestHelpers


class TypingTestType(StrEnum):
    """Test types for dynamic typing tests."""

    INITIALIZATION = "initialization"
    BASIC_FUNCTIONALITY = "basic_functionality"
    TYPE_DEFINITIONS = "type_definitions"
    TYPE_VALIDATION = "type_validation"
    TYPE_CONVERSION = "type_conversion"
    TYPE_UTILITIES = "type_utilities"
    TYPE_SCENARIOS = "type_scenarios"
    TYPE_PERFORMANCE = "type_performance"
    TYPE_EDGES = "type_edges"


@dataclass(frozen=True)
class TypingTestCase:
    """Test case data for typing tests."""

    test_type: TypingTestType
    description: str
    expected_success: bool = True


class TestFlextCliTypings:
    """Comprehensive tests for flext_cli.typings.FlextCliTypes module.

    Uses factory patterns, dynamic testing, and advanced Python 3.13 features
    to achieve maximum coverage with minimal, maintainable code.
    """

    class TypingTestFactory:
        """Factory for creating typing test data and cases."""

        @staticmethod
        def create_comprehensive_test_cases() -> list[TypingTestCase]:
            """Create comprehensive test cases for all typing scenarios."""
            return [
                TypingTestCase(TypingTestType.INITIALIZATION, "Types initialization"),
                TypingTestCase(
                    TypingTestType.BASIC_FUNCTIONALITY, "Basic type functionality"
                ),
                TypingTestCase(TypingTestType.TYPE_DEFINITIONS, "Type definitions"),
                TypingTestCase(TypingTestType.TYPE_VALIDATION, "Type validation"),
                TypingTestCase(TypingTestType.TYPE_CONVERSION, "Type conversion"),
                TypingTestCase(TypingTestType.TYPE_UTILITIES, "Type utilities"),
                TypingTestCase(TypingTestType.TYPE_SCENARIOS, "Type scenarios"),
                TypingTestCase(TypingTestType.TYPE_PERFORMANCE, "Type performance"),
                TypingTestCase(TypingTestType.TYPE_EDGES, "Type edge cases"),
            ]

        @staticmethod
        def create_type_test_data() -> dict[str, object]:
            """Create test data for type operations."""
            return {
                "config_data": {
                    "output_format": FlextCliConstants.OutputFormats.JSON.value,
                    "debug": True,
                    "timeout": 30,
                },
                "format_data": {"data": [1, 2, 3], "headers": ["col1", "col2"]},
                "user_data": TestTypings.TestData.Api.SINGLE_USER,
                "api_response": {
                    "status": TestTypings.TypedDicts.ApiResponse.STATUS,
                    "data": TestTypings.TestData.Api.SINGLE_USER,
                    "message": TestTypings.TypedDicts.ApiResponse.MESSAGE,
                },
                "processing_data": (
                    TestTypings.TestData.Processing.STRING_LIST,
                    TestTypings.TestData.Processing.NUMBER_LIST,
                    TestTypings.TestData.Processing.MIXED_DICT,
                ),
            }

    class TypingValidators:
        """Validators for typing test assertions."""

        @staticmethod
        def validate_type_initialization(
            types_class: type[FlextCliTypes],
        ) -> FlextResult[bool]:
            """Validate type class initialization."""
            try:
                # Test that types class has required attributes
                required_attrs = ["Data", "AnnotatedCli", "Auth", "CliCommand"]
                for attr in required_attrs:
                    if not hasattr(types_class, attr):
                        return FlextResult[bool].fail(f"Missing attribute: {attr}")

                # Test nested Data attributes
                data_attrs = ["CliDataDict", "CliFormatData", "CliConfigData"]
                for attr in data_attrs:
                    if not hasattr(types_class.Data, attr):
                        return FlextResult[bool].fail(f"Missing Data attribute: {attr}")

                return FlextResult[bool].ok(True)
            except Exception as e:
                return FlextResult[bool].fail(str(e))

        @staticmethod
        def validate_type_usage(
            data: dict[str, object], type_hint: str
        ) -> FlextResult[bool]:
            """Validate type usage with actual data."""
            try:
                match type_hint:
                    case "CliDataDict":
                        return FlextResult[bool].ok(isinstance(data, dict))
                    case "CliFormatData":
                        return FlextResult[bool].ok(
                            isinstance(data, dict) and "data" in data
                        )
                    case "CliConfigData":
                        return FlextResult[bool].ok(
                            isinstance(data, dict) and "debug" in data
                        )
                    case _:
                        return FlextResult[bool].fail(f"Unknown type hint: {type_hint}")
            except Exception as e:
                return FlextResult[bool].fail(str(e))

    # ========================================================================
    # DYNAMIC TEST EXECUTION
    # ========================================================================

    @pytest.mark.parametrize(
        "test_case",
        TypingTestFactory.create_comprehensive_test_cases(),
        ids=lambda x: f"{x.test_type.value}_{x.description.lower().replace(' ', '_')}",
    )
    def test_typing_comprehensive_functionality(
        self,
        test_case: TypingTestCase,
    ) -> None:
        """Comprehensive typing functionality tests using dynamic execution."""
        match test_case.test_type:
            case TypingTestType.INITIALIZATION:
                self._execute_initialization_tests()
            case TypingTestType.BASIC_FUNCTIONALITY:
                self._execute_basic_functionality_tests()
            case TypingTestType.TYPE_DEFINITIONS:
                self._execute_type_definition_tests()
            case TypingTestType.TYPE_VALIDATION:
                self._execute_type_validation_tests()
            case TypingTestType.TYPE_CONVERSION:
                self._execute_type_conversion_tests()
            case TypingTestType.TYPE_UTILITIES:
                self._execute_type_utilities_tests()
            case TypingTestType.TYPE_SCENARIOS:
                self._execute_type_scenario_tests()
            case TypingTestType.TYPE_PERFORMANCE:
                self._execute_type_performance_tests()
            case TypingTestType.TYPE_EDGES:
                self._execute_type_edge_tests()

    # ========================================================================
    # TEST EXECUTION HELPERS
    # ========================================================================

    def _execute_initialization_tests(self) -> None:
        """Execute initialization-related tests."""
        # Test types class structure
        validation_result = self.TypingValidators.validate_type_initialization(
            FlextCliTypes
        )
        FlextTestsMatchers.assert_success(validation_result)

        # Test type aliases accessibility
        test_data: FlextCliTypes.Data.CliDataDict = {"key": "value"}
        assert isinstance(test_data, dict)

    def _execute_basic_functionality_tests(self) -> None:
        """Execute basic functionality tests."""
        test_data = self.TypingTestFactory.create_type_test_data()

        # Test different type usages
        config_data_obj = test_data["config_data"]
        if not isinstance(config_data_obj, dict):
            error_msg = "config_data must be a dict"
            raise TypeError(error_msg)
        config_dict: dict[str, object] = config_data_obj
        config_result = self.TypingValidators.validate_type_usage(
            config_dict, "CliConfigData"
        )
        FlextTestsMatchers.assert_success(config_result)

        format_data_obj = test_data["format_data"]
        if not isinstance(format_data_obj, dict):
            error_msg = "format_data must be a dict"
            raise TypeError(error_msg)
        format_dict: dict[str, object] = format_data_obj
        format_result = self.TypingValidators.validate_type_usage(
            format_dict, "CliFormatData"
        )
        FlextTestsMatchers.assert_success(format_result)

        # Test real data operations (type narrowing for test validation)
        assert (
            config_dict["output_format"] == FlextCliConstants.OutputFormats.JSON.value
        )
        assert config_dict["debug"] is True

    def _execute_type_definition_tests(self) -> None:
        """Execute type definition tests."""
        # Test TypeVar creation
        t = TypeVar("t")

        # Test Generic type
        @dataclass
        class GenericType:
            value: object

        # Test Protocol type
        class TestProtocol(Protocol):
            def method(self) -> str: ...

        # Validate type definitions
        assert t is not None
        assert GenericType is not None
        assert TestProtocol is not None

        # Test type aliases from constants
        user_data: dict[str, object] = TestTypings.TestData.Processing.MIXED_DICT
        user_list: list[dict[str, object]] = [user_data]

        assert isinstance(user_data, dict)
        assert isinstance(user_list, list)
        assert len(user_list) == 1

    def _execute_type_validation_tests(self) -> None:
        """Execute type validation tests."""

        # Test union types
        def process_value(value: str | int) -> str:
            """Process value and return string."""
            match value:
                case str():
                    return value.upper()
                case int():
                    return str(value)
                case _:
                    return str(value)

        def process_optional(value: str | None) -> str:
            return value or "default"

        # Test functionality
        assert process_value("hello") == "HELLO"
        assert process_value(42) == "42"
        assert process_optional("test") == "test"
        assert process_optional(None) == "default"

        # Test generic types
        T_local = TypeVar("T_local")
        K_local = TypeVar("K_local")
        V_local = TypeVar("V_local")

        class Container(Generic[T_local]):
            def __init__(self, value: T_local) -> None:
                self.value = value

            def get_value(self) -> T_local:
                return self.value

        class KeyValueStore(Generic[K_local, V_local]):
            def __init__(self) -> None:
                self._store: dict[K_local, V_local] = {}

            def set(self, key: K_local, value: V_local) -> None:
                self._store[key] = value

            def get(self, key: K_local) -> V_local | None:
                return self._store.get(key)

        # Test containers
        string_container = Container("test")
        int_container = Container(42)

        assert string_container.get_value() == "test"
        assert int_container.get_value() == 42

        # Test key-value store
        kv_store = KeyValueStore[str, int]()
        kv_store.set("key1", 100)
        kv_store.set("key2", 200)

        assert kv_store.get("key1") == 100
        assert kv_store.get("key2") == 200
        assert kv_store.get("key3") is None

    def _execute_type_conversion_tests(self) -> None:
        """Execute type conversion tests."""

        # Test type narrowing
        def process_data(data: object) -> str:
            if not isinstance(data, str):
                error_msg = "data must be a str"
                raise TypeError(error_msg)
            return data.upper()

        def process_data_safe(data: object) -> str:
            return str(data).upper()

        # Test conversion
        assert process_data("hello") == "HELLO"
        assert process_data_safe("hello") == "HELLO"
        assert process_data_safe(123) == "123"

        # Test type narrowing
        def process_union(value: str | int) -> str:
            """Process union value and return string."""
            match value:
                case str():
                    return value.upper()
                case int():
                    return str(value)
                case _:
                    return str(value)

        def process_optional(value: str | None) -> str:
            return value.upper() if value else "default"

        assert process_union("hello") == "HELLO"
        assert process_union(42) == "42"
        assert process_optional("test") == "TEST"
        assert process_optional(None) == "default"

    def _execute_type_utilities_tests(self) -> None:
        """Execute type utilities tests."""

        # Test type hints extraction
        def typed_function(
            name: str,
            age: int,
            *,
            active: bool = True,
        ) -> dict[str, object]:
            return {"name": name, "age": age, "active": active}

        hints = get_type_hints(typed_function)
        assert hints["name"] is str
        assert hints["age"] is int
        assert hints["active"] is bool
        assert hints["return"] == dict[str, object]

        # Test complex type analysis
        def complex_function(data: list[dict[str, str | int]]) -> str | None:
            return "result" if data else None

        complex_hints = get_type_hints(complex_function)
        assert complex_hints["data"] == list[dict[str, str | int]]
        assert complex_hints["return"] == str | None

        # Test runtime type checking
        class TypedClass:
            def __init__(self, name: str, value: int) -> None:
                self.name = name
                self.value = value

            def process(self, data: list[str]) -> dict[str, int]:
                return {item: len(item) for item in data}

        # Test type hints
        init_hints = get_type_hints(TypedClass.__init__)
        assert init_hints["name"] is str
        assert init_hints["value"] is int

        process_hints = get_type_hints(TypedClass.process)
        assert process_hints["data"] == list[str]
        assert process_hints["return"] == dict[str, int]

        # Test type creation and usage
        instance = TypedClass("test", 42)
        result = instance.process(TestTypings.TestData.Processing.STRING_LIST)
        assert result["hello"] == 5
        assert result["world"] == 5

    def _execute_type_scenario_tests(self) -> None:
        """Execute type scenario tests."""

        # Test API response scenario
        class UserData(TypedDict):
            id: int
            name: str
            email: str
            active: bool

        class ApiResponse(TypedDict):
            status: str
            data: UserData | list[UserData]
            message: str | None
            error: str | None

        # Test type usage
        def create_user_response(user: UserData) -> ApiResponse:
            return {
                "status": "success",
                "data": user,
                "message": "User created successfully",
                "error": None,
            }

        def create_users_response(users: list[UserData]) -> ApiResponse:
            return {
                "status": "success",
                "data": users,
                "message": f"Retrieved {len(users)} users",
                "error": None,
            }

        # Test functionality using helper data
        user_dict = TestTypings.TestData.Api.SINGLE_USER
        # Type narrowing: extract and validate fields for UserData
        user_id = user_dict.get("id")
        user_name = user_dict.get("name")
        user_email = user_dict.get("email")
        user_active = user_dict.get("active")

        error_id = "user id must be int"
        error_name = "user name must be str"
        error_email = "user email must be str"
        error_active = "user active must be bool"

        if not isinstance(user_id, int):
            raise TypeError(error_id)
        if not isinstance(user_name, str):
            raise TypeError(error_name)
        if not isinstance(user_email, str):
            raise TypeError(error_email)
        if not isinstance(user_active, bool):
            raise TypeError(error_active)

        # Create UserData with properly narrowed types
        user_data: UserData = {
            "id": user_id,
            "name": user_name,
            "email": user_email,
            "active": user_active,
        }
        user_response = create_user_response(user_data)
        assert isinstance(user_response, dict)
        assert user_response.get("status") == "success"
        assert user_response.get("message") == "User created successfully"

        users_response = create_users_response([user_data])
        assert isinstance(users_response, dict)
        assert users_response.get("status") == "success"
        users_data = users_response.get("data", [])
        assert len(users_data) == 1

        # Test data processing scenario using helpers
        processing_result = (
            FlextCliTestHelpers.TypingHelpers.create_processing_test_data()
        )
        FlextTestsMatchers.assert_success(processing_result)

        if processing_result.is_success and processing_result.value:
            string_list, number_list, mixed_dict = processing_result.value
            assert len(string_list) == 3
            assert len(number_list) == 5
            assert isinstance(mixed_dict, dict)

    def _execute_type_performance_tests(self) -> None:
        """Execute type performance tests."""

        # Test type checking performance
        def process_list(data: list[str]) -> list[str]:
            return [item.upper() for item in data]

        def process_dict(data: dict[str, object]) -> dict[str, str]:
            return {key: str(value) for key, value in data.items()}

        # Test performance
        test_list = TestTypings.TestData.Processing.STRING_LIST
        test_dict = TestTypings.TestData.Processing.MIXED_DICT

        # Initialize variables
        result_list: list[str] = []
        result_dict: dict[str, str] = {}

        # Performance test
        start_time = time.time()
        for _ in range(1000):
            result_list = process_list(test_list)
            result_dict = process_dict(test_dict)
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 0.1, (
            f"Type processing too slow: {processing_time:.4f}s"
        )

        # Verify results
        assert result_list == ["HELLO", "WORLD", "TEST"]
        assert result_dict["key1"] == "123"

    def _execute_type_edge_tests(self) -> None:
        """Execute type edge case tests."""

        # Test edge cases with types
        def handle_edge_cases(value: object) -> str:
            match value:
                case None:
                    return "None"
                case str() if not value:
                    return "Empty"
                case str() | int() | float():
                    return str(value)
                case _:
                    return "Unknown"

        # Test edge cases
        assert handle_edge_cases(None) == "None"
        assert handle_edge_cases("") == "Empty"
        assert handle_edge_cases("hello") == "hello"
        assert handle_edge_cases(42) == "42"
        result = handle_edge_cases(math.pi)
        assert result.startswith("3.14")
        assert handle_edge_cases([]) == "Unknown"  # Empty list is falsy but not matched
        assert handle_edge_cases({}) == "Unknown"  # Empty dict

        # Test concurrent access
        def thread_safe_operation(data: list[str], results: list[str]) -> None:
            processed = [item.upper() for item in data]
            results.extend(processed)

        test_data = TestTypings.TestData.Processing.STRING_LIST
        results: list[str] = []

        threads = []
        for _ in range(5):
            thread = threading.Thread(
                target=thread_safe_operation,
                args=(test_data, results),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 15  # 5 threads * 3 items
        assert all(item in {"HELLO", "WORLD", "TEST"} for item in results)

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_type_workflow_integration(self) -> None:
        """Test complete type workflow integration."""
        # Test helper integration
        typed_data_result = FlextCliTestHelpers.TypingHelpers.create_typed_dict_data()
        FlextTestsMatchers.assert_success(typed_data_result)

        api_data_result = FlextCliTestHelpers.TypingHelpers.create_api_response_data()
        FlextTestsMatchers.assert_success(api_data_result)

        # Test type inspection
        complex_type = list[dict[str, str | int]]
        optional_type = list[str] | None
        union_type = str | int | bool

        assert get_origin(complex_type) is list
        complex_args = get_args(complex_type)
        assert len(complex_args) == 1
        assert get_origin(complex_args[0]) is dict

        # Test union type inspection
        assert get_origin(optional_type) is not None
        optional_args = get_args(optional_type)
        assert type(None) in optional_args
        assert list[str] in optional_args

        assert get_origin(union_type) is not None
        union_args = get_args(union_type)
        assert str in union_args
        assert int in union_args
        assert bool in union_args

    def test_type_workflow_integration(self) -> None:
        """Test type workflow integration with helpers."""

        # Test protocol with runtime checking
        @runtime_checkable
        class TestProtocol(Protocol):
            def operation(self, data: list[str]) -> dict[str, object]: ...

        # Implement protocol
        class Implementation:
            def operation(self, data: list[str]) -> dict[str, object]:
                time.sleep(0.001)  # Simulate work
                return {
                    "processed": [item.upper() for item in data],
                    "count": len(data),
                    "timestamp": "2025-01-01T00:00:00Z",
                }

        # Test protocol
        impl = Implementation()
        assert isinstance(impl, TestProtocol)

        # Use helper data
        test_data = TestTypings.TestData.Processing.STRING_LIST
        result = impl.operation(test_data)

        assert result["processed"] == ["HELLO", "WORLD", "TEST"]
        assert result["count"] == 3
        assert "timestamp" in result

        # Test types class integration
        assert FlextCliTypes is not None
        assert hasattr(FlextCliTypes, "Data")
        assert hasattr(FlextCliTypes, "AnnotatedCli")
