"""FLEXT CLI Typings Tests - Type System Validation.

Modules tested: flext_cli.typings.FlextCliTypes
"""

from __future__ import annotations

import time
from collections.abc import (
    Mapping,
    Sequence,
)
from typing import Protocol, runtime_checkable

from flext_tests import tm

from tests import m, t


class TestsCliTypings:
    """Tests for flext_cli.typings.FlextCliTypes module."""

    def test_full_type_workflow_integration(self) -> None:
        """Test complete type workflow integration."""
        typed_data = {"key": "value", "number": 42}
        tm.that(typed_data, is_=dict)
        api_data = m.Cli.Tests.ApiResponse(
            status="success",
            data={"id": 1},
            message="ok",
            error=None,
        )
        tm.that(api_data, is_=m.Cli.Tests.ApiResponse)
        tm.that(api_data.data, eq={"id": 1})

        complex_type_adapter = m.TypeAdapter(Sequence[Mapping[str, str | int]])
        complex_value = complex_type_adapter.validate_python([
            {"name": "entry", "count": 1},
        ])
        tm.that(complex_value, eq=[{"name": "entry", "count": 1}])

        optional_type_adapter = m.TypeAdapter(t.StrSequence | None)
        tm.that(
            optional_type_adapter.validate_python(["alpha", "beta"]),
            eq=["alpha", "beta"],
        )
        tm.that(optional_type_adapter.validate_python(None), none=True)

        scalar_type_adapter = m.TypeAdapter(t.Scalar)
        tm.that(scalar_type_adapter.validate_python("value"), eq="value")
        tm.that(scalar_type_adapter.validate_python(True), eq=True)

    def test_type_workflow_integration(self) -> None:
        """Test type workflow integration with helpers."""

        @runtime_checkable
        class Test(Protocol):
            def operation(self, data: t.StrSequence) -> t.JsonMapping: ...

        class Implementation:
            def operation(self, data: t.StrSequence) -> t.JsonMapping:
                time.sleep(0.001)
                return {
                    "processed": [item.upper() for item in data],
                    "count": len(data),
                    "timestamp": "2025-01-01T00:00:00Z",
                }

        impl: Test = Implementation()
        test_data = ["str1", "str2"]
        result = impl.operation(test_data)
        processed: t.JsonValue | None = result.get("processed")
        tm.that(processed, eq=["STR1", "STR2"])
        count: t.JsonValue | None = result.get("count")
        tm.that(count, eq=2)
        tm.that(result, has="timestamp")
        tm.that(t, none=False)
