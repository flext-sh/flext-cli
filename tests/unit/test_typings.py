"""FLEXT CLI Typings Tests - Type System Validation.

Modules tested: flext_cli.typings.FlextCliTypes
"""

from __future__ import annotations

import collections.abc
import time
from collections.abc import Mapping, Sequence
from typing import (
    Protocol,
    get_args,
    get_origin,
    runtime_checkable,
)

from flext_tests import tm

from tests import m, t


class TestsCliTypings:
    """Tests for flext_cli.typings.FlextCliTypes module."""

    def test_full_type_workflow_integration(self) -> None:
        """Test complete type workflow integration."""
        typed_data: t.ContainerMapping = {"key": "value", "number": 42}
        tm.that(typed_data, is_=dict)
        api_data = m.Cli.Test.ApiResponse(
            status="success",
            data={"id": 1},
            message="ok",
            error=None,
        )
        tm.that(api_data, is_=m.Cli.Test.ApiResponse)
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

        impl: Test = Implementation()
        test_data = ["str1", "str2"]
        result = impl.operation(test_data)
        processed: t.NormalizedValue = result.get("processed")
        tm.that(processed, eq=["STR1", "STR2"])
        count: t.NormalizedValue = result.get("count")
        tm.that(count, eq=2)
        tm.that(result, has="timestamp")
        tm.that(t, none=False)
        tm.that(hasattr(t, "Cli"), eq=True)
        tm.that(hasattr(t.Cli, "TabularData"), eq=True)
        tm.that(hasattr(t.Cli, "JsonValue"), eq=True)
