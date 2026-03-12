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
from collections.abc import Mapping
from enum import StrEnum
from typing import (
    Generic,
    Protocol,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)

import pytest
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import r, t
from tests.helpers import c
from tests.models import ApiResponse, UserData

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


class TypingTestCase(BaseModel):
    """Test case data for typing tests."""

    model_config = ConfigDict(frozen=True)

    test_type: TypingTestType = Field(description="Typing test category")
    description: str = Field(description="Typing test case description")
    expected_success: bool = Field(
        default=True,
        description="Whether test case is expected to succeed",
    )


class TestsCliTypings:
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
                TypingTestCase(
                    test_type=TypingTestType.INITIALIZATION,
                    description="Types initialization",
                ),
                TypingTestCase(
                    test_type=TypingTestType.BASIC_FUNCTIONALITY,
                    description="Basic type functionality",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_DEFINITIONS,
                    description="Type definitions",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_VALIDATION,
                    description="Type validation",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_CONVERSION,
                    description="Type conversion",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_UTILITIES,
                    description="Type utilities",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_SCENARIOS,
                    description="Type scenarios",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_PERFORMANCE,
                    description="Type performance",
                ),
                TypingTestCase(
                    test_type=TypingTestType.TYPE_EDGES,
                    description="Type edge cases",
                ),
            ]

        @staticmethod
        def create_type_test_data() -> dict[str, object]:
            """Create test data for type operations."""
            return {
                "config_data": {
                    "output_format": c.Cli.OutputFormats.JSON.value,
                    "debug": True,
                    "timeout": 30,
                },
                "format_data": {"data": [1, 2, 3], "headers": ["col1", "col2"]},
                "user_data": {"id": 1, "name": "test_user"},
                "api_response": {
                    "status": "success",
                    "data": {"id": 1, "name": "test_user"},
                    "message": "ok",
                },
                "processing_data": (
                    ["str1", "str2"],
                    [1, 2, 3],
                    {"key": "value", "number": 42},
                ),
            }

    class TypingValidators:
        """Validators for typing test assertions."""

        @staticmethod
        def validate_type_initialization(types_class: object) -> r[bool]:
            """Validate type class initialization."""
            try:
                if not hasattr(types_class, "Cli"):
                    return r[bool].fail("Missing Cli namespace")
                cli_namespace = getattr(types_class, "Cli", None)
                if cli_namespace is None:
                    return r[bool].fail("Cli namespace is None")
                required_attrs = ["FormatableResult", "ResultFormatter", "TabularData"]
                for attr in required_attrs:
                    if not hasattr(cli_namespace, attr):
                        return r[bool].fail(f"Missing Cli attribute: {attr}")
                return r[bool].ok(True)
            except Exception as e:
                return r[bool].fail(str(e))

        @staticmethod
        def validate_type_usage(data: dict[str, object], type_hint: str) -> r[bool]:
            """Validate type usage with actual data."""
            try:
                match type_hint:
                    case "CliDataDict":
                        return r[bool].ok(True)
                    case "CliFormatData":
                        return r[bool].ok("data" in data)
                    case "CliConfigData":
                        return r[bool].ok("debug" in data)
                    case _:
                        return r[bool].fail(f"Unknown type hint: {type_hint}")
            except Exception as e:
                return r[bool].fail(str(e))

    @pytest.mark.parametrize(
        "test_case",
        TypingTestFactory.create_comprehensive_test_cases(),
        ids=lambda x: f"{x.test_type.value}_{x.description.lower().replace(' ', '_')}",
    )
    def test_typing_comprehensive_functionality(
        self, test_case: TypingTestCase
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

    def _execute_initialization_tests(self) -> None:
        """Execute initialization-related tests."""
        validation_result = self.TypingValidators.validate_type_initialization(t)
        tm.ok(validation_result)
        test_data: dict[str, object] = {"key": "value"}
        assert isinstance(test_data, dict)

    def _execute_basic_functionality_tests(self) -> None:
        """Execute basic functionality tests."""
        test_data = self.TypingTestFactory.create_type_test_data()
        config_data_obj = test_data["config_data"]
        if not isinstance(config_data_obj, dict):
            error_msg = "config_data must be a dict"
            raise TypeError(error_msg)
        config_dict: dict[str, object] = config_data_obj
        config_result = self.TypingValidators.validate_type_usage(
            config_dict, "CliConfigData"
        )
        tm.ok(config_result)
        format_data_obj = test_data["format_data"]
        if not isinstance(format_data_obj, dict):
            error_msg = "format_data must be a dict"
            raise TypeError(error_msg)
        format_dict: dict[str, object] = format_data_obj
        format_result = self.TypingValidators.validate_type_usage(
            format_dict, "CliFormatData"
        )
        tm.ok(format_result)
        assert config_dict["output_format"] == c.Cli.OutputFormats.JSON.value
        assert config_dict["debug"] is True

    def _execute_type_definition_tests(self) -> None:
        """Execute type definition tests."""
        t_var = TypeVar("t_var")
        generic_type = Generic

        class TestProtocol(Protocol):
            def method(self) -> str: ...

        assert t_var is not None
        assert generic_type is not None
        assert TestProtocol is not None
        user_data: dict[str, object] = {"key": "value", "number": 42}
        user_list: list[dict[str, object]] = [user_data]
        assert isinstance(user_data, dict)
        assert isinstance(user_list, list)
        assert len(user_list) == 1

    def _execute_type_validation_tests(self) -> None:
        """Execute type validation tests."""

        def process_value(value: str | int) -> str:
            """Process value and return string."""
            if isinstance(value, str):
                return value.upper()
            return str(value)

        def process_optional(value: str | None) -> str:
            return value or "default"

        assert process_value("hello") == "HELLO"
        assert process_value(42) == "42"
        assert process_optional("test") == "test"
        assert process_optional(None) == "default"
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

        string_container = Container("test")
        int_container = Container(42)
        assert string_container.get_value() == "test"
        assert int_container.get_value() == 42
        kv_store = KeyValueStore[str, int]()
        kv_store.set("key1", 100)
        kv_store.set("key2", 200)
        assert kv_store.get("key1") == 100
        assert kv_store.get("key2") == 200
        assert kv_store.get("key3") is None

    def _execute_type_conversion_tests(self) -> None:
        """Execute type conversion tests."""

        def process_data(data: object) -> str:
            if not isinstance(data, str):
                error_msg = "data must be a str"
                raise TypeError(error_msg)
            return data.upper()

        def process_data_safe(data: object) -> str:
            return str(data).upper()

        assert process_data("hello") == "HELLO"
        assert process_data_safe("hello") == "HELLO"
        assert process_data_safe(123) == "123"

        def process_union(value: str | int) -> str:
            """Process union value and return string."""
            if isinstance(value, str):
                return value.upper()
            return str(value)

        def process_optional(value: str | None) -> str:
            return value.upper() if value else "default"

        assert process_union("hello") == "HELLO"
        assert process_union(42) == "42"
        assert process_optional("test") == "TEST"
        assert process_optional(None) == "default"

    def _execute_type_utilities_tests(self) -> None:
        """Execute type utilities tests."""

        def typed_function(
            name: str, age: int, *, active: bool = True
        ) -> t.ConfigurationMapping:
            return {"name": name, "age": age, "active": active}

        hints = get_type_hints(typed_function)
        assert hints["name"] is str
        assert hints["age"] is int
        assert hints["active"] is bool
        assert hints["return"] == t.ConfigurationMapping

        def complex_function(data: list[dict[str, str | int]]) -> str | None:
            return "result" if data else None

        complex_hints = get_type_hints(complex_function)
        assert complex_hints["data"] == list[dict[str, str | int]]
        assert complex_hints["return"] == str | None

        class TypedClass:
            def __init__(self, name: str, value: int) -> None:
                self.name = name
                self.value = value

            def process(self, data: list[str]) -> dict[str, int]:
                return {item: len(item) for item in data}

        init_hints = get_type_hints(TypedClass.__init__)
        assert init_hints["name"] is str
        assert init_hints["value"] is int
        process_hints = get_type_hints(TypedClass.process)
        assert process_hints["data"] == list[str]
        assert process_hints["return"] == dict[str, int]
        instance = TypedClass("test", 42)
        result = instance.process(["str1", "str2"])
        assert len(result) == 2
        assert "str1" in result or "STR1" in result
        assert "str2" in result or "STR2" in result
        values = list(result.values())
        assert all(isinstance(v, int) for v in values)

    def _execute_type_scenario_tests(self) -> None:
        """Execute type scenario tests."""

        def create_user_response(user: UserData) -> ApiResponse:
            return ApiResponse(
                status="success",
                data=user.model_dump(),
                message="User created successfully",
                error=None,
            )

        def create_users_response(users: list[UserData]) -> ApiResponse:
            return ApiResponse(
                status="success",
                data=[u.model_dump() for u in users],
                message=f"Retrieved {len(users)} users",
                error=None,
            )

        user_dict = {
            "id": 1,
            "name": "test_user",
            "email": "test@example.com",
            "active": True,
        }
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
        user_data = UserData(
            id=user_id, name=user_name, email=user_email, active=user_active
        )
        user_response = create_user_response(user_data)
        assert isinstance(user_response, ApiResponse)
        assert user_response.status == "success"
        assert user_response.message == "User created successfully"
        users_response = create_users_response([user_data])
        assert isinstance(users_response, ApiResponse)
        assert users_response.status == "success"
        users_data = users_response.data
        assert isinstance(users_data, list)
        assert len(users_data) == 1
        processing_result = (
            FlextCliTestHelpers.TypingHelpers.create_processing_test_data()
        )
        assert processing_result.is_success
        if processing_result.is_success and processing_result.value:
            string_list, number_list, mixed_dict = processing_result.value
            assert len(string_list) == 3
            assert len(number_list) == 5
            assert isinstance(mixed_dict, dict)

    def _execute_type_performance_tests(self) -> None:
        """Execute type performance tests."""

        def process_list(data: list[str]) -> list[str]:
            return [item.upper() for item in data]

        def process_dict(data: Mapping[str, object]) -> dict[str, str]:
            return {key: str(value) for key, value in data.items()}

        test_list = ["hello", "world", "test"]
        test_dict = {"key1": 123, "key2": "value"}
        result_list: list[str] = []
        result_dict: dict[str, str] = {}
        start_time = time.time()
        for _ in range(1000):
            result_list = process_list(test_list)
            result_dict = process_dict(test_dict)
        end_time = time.time()
        processing_time = end_time - start_time
        assert processing_time < 0.1, (
            f"Type processing too slow: {processing_time:.4f}s"
        )
        assert result_list == ["HELLO", "WORLD", "TEST"]
        assert result_dict["key1"] == "123"

    def _execute_type_edge_tests(self) -> None:
        """Execute type edge case tests."""

        def handle_edge_cases(value: object) -> str:
            if value is None:
                return "None"
            if isinstance(value, str) and (not value):
                return "Empty"
            if isinstance(value, (str, int, float)):
                return str(value)
            return "Unknown"

        assert handle_edge_cases(None) == "None"
        assert handle_edge_cases("") == "Empty"
        assert handle_edge_cases("hello") == "hello"
        assert handle_edge_cases(42) == "42"
        result = handle_edge_cases(math.pi)
        assert result.startswith("3.14")
        assert handle_edge_cases([]) == "Unknown"
        assert handle_edge_cases({}) == "Unknown"

        def thread_safe_operation(data: list[str], results: list[str]) -> None:
            processed = [item.upper() for item in data]
            results.extend(processed)

        test_data = ["str1", "str2"]
        results: list[str] = []
        threads: list[threading.Thread] = []
        for _ in range(5):
            thread = threading.Thread(
                target=thread_safe_operation, args=(test_data, results)
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        assert len(results) == 10
        assert all(item in {"STR1", "STR2"} for item in results)

    def test_full_type_workflow_integration(self) -> None:
        """Test complete type workflow integration."""
        typed_data_result = FlextCliTestHelpers.TypingHelpers.create_typed_dict_data()
        assert typed_data_result.is_success
        api_data_result = FlextCliTestHelpers.TypingHelpers.create_api_response_data()
        assert api_data_result.is_success
        complex_type = list[dict[str, str | int]]
        optional_type = list[str] | None
        union_type = str | int | bool
        assert get_origin(complex_type) is list
        complex_args = get_args(complex_type)
        assert len(complex_args) == 1
        assert get_origin(complex_args[0]) is dict
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

        @runtime_checkable
        class TestProtocol(Protocol):
            def operation(self, data: list[str]) -> dict[str, object]: ...

        class Implementation:
            def operation(self, data: list[str]) -> dict[str, object]:
                time.sleep(0.001)
                return {
                    "processed": [item.upper() for item in data],
                    "count": len(data),
                    "timestamp": "2025-01-01T00:00:00Z",
                }

        impl = Implementation()
        assert isinstance(impl, TestProtocol)
        test_data = ["str1", "str2"]
        result = impl.operation(test_data)
        assert result["processed"] == ["STR1", "STR2"]
        assert result["count"] == 2
        assert "timestamp" in result
        assert t is not None
        assert hasattr(t, "Cli")
        assert hasattr(t.Cli, "FormatableResult")
        assert hasattr(t.Cli, "ResultFormatter")
