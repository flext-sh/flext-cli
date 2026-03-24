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

import collections.abc
import math
import threading
import time
from collections.abc import Mapping, Sequence
from enum import StrEnum, unique
from typing import (
    Annotated,
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)

import pytest
from flext_core import r
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import FlextCliTypes, t
from tests import ApiResponse, UserData, c

from ..helpers import FlextCliTestHelpers


@unique
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

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    test_type: Annotated[TypingTestType, Field(description="Typing test category")]
    description: Annotated[str, Field(description="Typing test case description")]
    expected_success: Annotated[
        bool,
        Field(
            default=True,
            description="Whether test case is expected to succeed",
        ),
    ]


class TestsCliTypings:
    """Comprehensive tests for flext_cli.typings.FlextCliTypes module.

    Uses factory patterns, dynamic testing, and advanced Python 3.13 features
    to achieve maximum coverage with minimal, maintainable code.
    """

    class TypingTestFactory:
        """Factory for creating typing test data and cases."""

        @staticmethod
        def create_comprehensive_test_cases() -> Sequence[TypingTestCase]:
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
        def create_type_test_data() -> t.ContainerMapping:
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
        def validate_type_initialization(types_class: type[FlextCliTypes]) -> r[bool]:
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
        def validate_type_usage(data: t.ContainerMapping, type_hint: str) -> r[bool]:
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

    def _execute_initialization_tests(self) -> None:
        """Execute initialization-related tests."""
        validation_result = self.TypingValidators.validate_type_initialization(t)
        tm.ok(validation_result)
        test_data: t.ContainerMapping = {"key": "value"}
        tm.that(test_data, is_=dict)

    def _execute_basic_functionality_tests(self) -> None:
        """Execute basic functionality tests."""
        test_data = self.TypingTestFactory.create_type_test_data()
        config_data_obj = test_data["config_data"]
        if not isinstance(config_data_obj, dict):
            error_msg = "config_data must be a dict"
            raise TypeError(error_msg)
        config_dict: t.ContainerMapping = config_data_obj
        config_result = self.TypingValidators.validate_type_usage(
            config_dict,
            "CliConfigData",
        )
        tm.ok(config_result)
        format_data_obj = test_data["format_data"]
        if not isinstance(format_data_obj, dict):
            error_msg = "format_data must be a dict"
            raise TypeError(error_msg)
        format_dict: t.ContainerMapping = format_data_obj
        format_result = self.TypingValidators.validate_type_usage(
            format_dict,
            "CliFormatData",
        )
        tm.ok(format_result)
        tm.that(config_dict["output_format"], eq=c.Cli.OutputFormats.JSON.value)
        tm.that(config_dict["debug"] is True, eq=True)

    def _execute_type_definition_tests(self) -> None:
        """Execute type definition tests."""
        TypeVar("t")
        generic_type = Generic

        class Test(Protocol):
            def method(self) -> str: ...

        tm.that(t, none=False)
        tm.that(generic_type, none=False)
        tm.that(Test, none=False)
        user_data: t.ContainerMapping = {"key": "value", "number": 42}
        user_list: Sequence[t.ContainerMapping] = [user_data]
        tm.that(user_data, is_=dict)
        tm.that(user_list, is_=list)
        tm.that(len(user_list), eq=1)

    def _execute_type_validation_tests(self) -> None:
        """Execute type validation tests."""

        def process_value(value: str | int) -> str:
            """Process value and return string."""
            if isinstance(value, str):
                return value.upper()
            return str(value)

        def process_optional(value: str | None) -> str:
            return value or "default"

        tm.that(process_value("hello"), eq="HELLO")
        tm.that(process_value(42), eq="42")
        tm.that(process_optional("test"), eq="test")
        tm.that(process_optional(None), eq="default")
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
                self._store: Mapping[K_local, V_local] = {}

            def set(self, key: K_local, value: V_local) -> None:
                self._store[key] = value

            def get(self, key: K_local) -> V_local | None:
                return self._store.get(key)

        string_container = Container("test")
        int_container = Container(42)
        tm.that(string_container.get_value(), eq="test")
        tm.that(int_container.get_value(), eq=42)
        kv_store = KeyValueStore[str, int]()
        kv_store.set("key1", 100)
        kv_store.set("key2", 200)
        tm.that(kv_store.get("key1"), eq=100)
        tm.that(kv_store.get("key2"), eq=200)
        tm.that(kv_store.get("key3"), none=True)

    def _execute_type_conversion_tests(self) -> None:
        """Execute type conversion tests."""

        def process_data(data: str) -> str:
            if not isinstance(data, str):
                error_msg = "data must be a str"
                raise TypeError(error_msg)
            return data.upper()

        def process_data_safe(data: int | str) -> str:
            return str(data).upper()

        tm.that(process_data("hello"), eq="HELLO")
        tm.that(process_data_safe("hello"), eq="HELLO")
        tm.that(process_data_safe(123), eq="123")

        def process_union(value: str | int) -> str:
            """Process union value and return string."""
            if isinstance(value, str):
                return value.upper()
            return str(value)

        def process_optional(value: str | None) -> str:
            return value.upper() if value else "default"

        tm.that(process_union("hello"), eq="HELLO")
        tm.that(process_union(42), eq="42")
        tm.that(process_optional("test"), eq="TEST")
        tm.that(process_optional(None), eq="default")

    def _execute_type_utilities_tests(self) -> None:
        """Execute type utilities tests."""

        def typed_function(
            name: str,
            age: int,
            *,
            active: bool = True,
        ) -> Mapping[str, bool | int | str]:
            return {"name": name, "age": age, "active": active}

        hints = get_type_hints(typed_function)
        tm.that(hints["name"] is str, eq=True)
        tm.that(hints["age"] is int, eq=True)
        tm.that(hints["active"] is bool, eq=True)
        tm.that(hints["return"], eq=Mapping[str, bool | int | str])

        def complex_function(data: Sequence[Mapping[str, str | int]]) -> str | None:
            return "result" if data else None

        complex_hints = get_type_hints(complex_function)
        tm.that(complex_hints["data"], eq=Sequence[Mapping[str, str | int]])
        tm.that(complex_hints["return"], eq=str | None)

        class TypedClass:
            def __init__(self, name: str, value: int) -> None:
                self.name = name
                self.value = value

            def process(self, data: t.StrSequence) -> Mapping[str, int]:
                return {item: len(item) for item in data}

        init_hints = get_type_hints(TypedClass.__init__)
        tm.that(init_hints["name"] is str, eq=True)
        tm.that(init_hints["value"] is int, eq=True)
        process_hints = get_type_hints(TypedClass.process)
        tm.that(process_hints["data"], eq=t.StrSequence)
        tm.that(process_hints["return"], eq=Mapping[str, int])
        instance = TypedClass("test", 42)
        result = instance.process(["str1", "str2"])
        tm.that(len(result), eq=2)
        tm.that("str1" in result or "STR1" in result, eq=True)
        tm.that("str2" in result or "STR2" in result, eq=True)
        values = list(result.values())
        tm.that(all(isinstance(v, int) for v in values), eq=True)

    def _execute_type_scenario_tests(self) -> None:
        """Execute type scenario tests."""

        def create_user_response(user: UserData) -> ApiResponse:
            return ApiResponse(
                status="success",
                data=user.model_dump(),
                message="User created successfully",
                error=None,
            )

        def create_users_response(users: Sequence[UserData]) -> ApiResponse:
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
            id=user_id,
            name=user_name,
            email=user_email,
            active=user_active,
        )
        user_response = create_user_response(user_data)
        tm.that(user_response, is_=ApiResponse)
        tm.that(user_response.status, eq="success")
        tm.that(user_response.message, eq="User created successfully")
        users_response = create_users_response([user_data])
        tm.that(users_response, is_=ApiResponse)
        tm.that(users_response.status, eq="success")
        users_data = users_response.data
        tm.that(users_data, is_=list)
        tm.that(len(users_data), eq=1)
        processing_result = (
            FlextCliTestHelpers.TypingHelpers.create_processing_test_data()
        )
        tm.ok(processing_result)
        if processing_result.is_success and processing_result.value:
            string_list, number_list, mixed_dict = processing_result.value
            tm.that(len(string_list), eq=3)
            tm.that(len(number_list), eq=5)
            tm.that(mixed_dict, is_=dict)

    def _execute_type_performance_tests(self) -> None:
        """Execute type performance tests."""

        def process_list(data: t.StrSequence) -> t.StrSequence:
            return [item.upper() for item in data]

        def process_dict(data: t.ContainerMapping) -> t.StrMapping:
            return {key: str(value) for key, value in data.items()}

        test_list = ["hello", "world", "test"]
        test_dict = {"key1": 123, "key2": "value"}
        result_list: t.StrSequence = []
        result_dict: t.StrMapping = {}
        start_time = time.time()
        for _ in range(1000):
            result_list = process_list(test_list)
            result_dict = process_dict(test_dict)
        end_time = time.time()
        processing_time = end_time - start_time
        tm.that(processing_time, lt=0.1)
        tm.that(result_list, eq=["HELLO", "WORLD", "TEST"])
        tm.that(result_dict["key1"], eq="123")

    def _execute_type_edge_tests(self) -> None:
        """Execute type edge case tests."""

        def handle_edge_cases(value: t.NormalizedValue) -> str:
            if value is None:
                return "None"
            if isinstance(value, str) and (not value):
                return "Empty"
            if isinstance(value, (str, int, float)):
                return str(value)
            return "Unknown"

        tm.that(handle_edge_cases(None), eq="None")
        tm.that(handle_edge_cases(""), eq="Empty")
        tm.that(handle_edge_cases("hello"), eq="hello")
        tm.that(handle_edge_cases(42), eq="42")
        result = handle_edge_cases(math.pi)
        tm.that(result.startswith("3.14"), eq=True)
        tm.that(handle_edge_cases([]), eq="Unknown")
        tm.that(handle_edge_cases({}), eq="Unknown")

        def thread_safe_operation(data: t.StrSequence, results: t.StrSequence) -> None:
            processed = [item.upper() for item in data]
            results.extend(processed)

        test_data = ["str1", "str2"]
        results: t.StrSequence = []
        threads: Sequence[threading.Thread] = []
        for _ in range(5):
            thread = threading.Thread(
                target=thread_safe_operation,
                args=(test_data, results),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        tm.that(len(results), eq=10)
        tm.that(all(item in {"STR1", "STR2"} for item in results), eq=True)

    def test_full_type_workflow_integration(self) -> None:
        """Test complete type workflow integration."""
        typed_data_result = FlextCliTestHelpers.TypingHelpers.create_typed_dict_data()
        tm.ok(typed_data_result)
        api_data_result = FlextCliTestHelpers.TypingHelpers.create_api_response_data()
        tm.ok(api_data_result)
        complex_type = Sequence[Mapping[str, str | int]]
        optional_type = t.StrSequence | None
        union_type = t.Scalar
        tm.that(get_origin(complex_type) is collections.abc.Sequence, eq=True)
        complex_args = get_args(complex_type)
        tm.that(len(complex_args), eq=1)
        tm.that(get_origin(complex_args[0]) is collections.abc.Mapping, eq=True)
        tm.that(get_origin(optional_type), none=False)
        optional_args = get_args(optional_type)
        tm.that(type(None) in optional_args, eq=True)
        tm.that(t.StrSequence in optional_args, eq=True)
        tm.that(hasattr(union_type, "__value__"), eq=True)
        union_args = get_args(union_type.__value__)
        tm.that(len(union_args), gte=2)
        # Scalar = Primitives | datetime — verify nested alias components
        primitives_alias = union_args[0]
        tm.that(hasattr(primitives_alias, "__value__"), eq=True)
        primitives_args = get_args(primitives_alias.__value__)
        tm.that(str in primitives_args, eq=True)
        tm.that(bool in primitives_args, eq=True)

    def test_type_workflow_integration(self) -> None:
        """Test type workflow integration with helpers."""

        @runtime_checkable
        class Test(Protocol):
            def operation(self, data: t.StrSequence) -> t.ContainerMapping: ...

        class Implementation:
            def operation(self, data: t.StrSequence) -> t.ContainerMapping:
                time.sleep(0.001)
                return {
                    "processed": [item.upper() for item in data],
                    "count": len(data),
                    "timestamp": "2025-01-01T00:00:00Z",
                }

        impl = Implementation()
        tm.that(impl, is_=Test)
        test_data = ["str1", "str2"]
        result = impl.operation(test_data)
        processed: t.NormalizedValue = result.get("processed")
        tm.that(processed, eq=["STR1", "STR2"])
        count: t.NormalizedValue = result.get("count")
        tm.that(count, eq=2)
        tm.that(result, has="timestamp")
        tm.that(t, none=False)
        tm.that(hasattr(t, "Cli"), eq=True)
        tm.that(hasattr(t.Cli, "FormatableResult"), eq=True)
        tm.that(hasattr(t.Cli, "ResultFormatter"), eq=True)
