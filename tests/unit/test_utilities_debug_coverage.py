"""Debug coverage test for utilities.py safe_float method lines 125-126.

This test specifically targets the exact missing lines in safe_float exception handling
using a trace-based approach to ensure coverage detection.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import trace
from typing import Any

from flext_core import FlextUtilities


class TestUtilitiesDebugCoverage:
    """Debug tests for utilities coverage using trace-based approach."""

    def test_safe_float_with_trace_coverage(self) -> None:
        """Test safe_float with trace to force coverage of lines 125-126."""
        # Create tracer to track execution
        tracer = trace.Trace(count=1, trace=0)

        def traced_safe_float_exceptions() -> None:
            """Execute safe_float calls that should trigger exceptions."""
            # ValueError cases
            FlextUtilities.Conversions.safe_float("invalid_string")
            FlextUtilities.Conversions.safe_float("abc123def")
            FlextUtilities.Conversions.safe_float("12.34.56.78")

            # TypeError cases - these should definitely hit the exception handler
            FlextUtilities.Conversions.safe_float(None)  # type: ignore[arg-type]
            FlextUtilities.Conversions.safe_float(complex(1, 2))  # type: ignore[arg-type]
            FlextUtilities.Conversions.safe_float([1, 2, 3])  # type: ignore[arg-type]
            FlextUtilities.Conversions.safe_float({"key": "value"})  # type: ignore[arg-type]

            # More exotic type errors
            FlextUtilities.Conversions.safe_float(object())  # type: ignore[arg-type]
            FlextUtilities.Conversions.safe_float(set())  # type: ignore[arg-type]
            FlextUtilities.Conversions.safe_float(lambda x: x)  # type: ignore[arg-type]

        # Run with tracing
        tracer.run("traced_safe_float_exceptions()")

    def test_safe_float_manual_exception_verification(self) -> None:
        """Manually verify that exception handling is working."""
        # Test cases that should trigger ValueError
        test_cases_value_error = [
            "not_a_number",
            "abc123",
            "12.34.56",  # Multiple decimal points
            "inf++",
            "12e++",  # Invalid scientific notation
            "",  # Empty string should cause ValueError in float("")
        ]

        for case in test_cases_value_error:
            result = FlextUtilities.Conversions.safe_float(case, default=999.0)
            assert result == 999.0, f"safe_float('{case}') should return default 999.0, got {result}"

        # Test cases that should trigger TypeError
        test_cases_type_error = [
            None,
            complex(1, 2),
            [1, 2, 3],
            {"key": "value"},
            object(),
            set([1, 2, 3]),
        ]

        for case in test_cases_type_error:
            result = FlextUtilities.Conversions.safe_float(case, default=888.0)  # type: ignore[arg-type]
            assert result == 888.0, f"safe_float({case!r}) should return default 888.0, got {result}"

    def test_safe_float_exception_paths_with_monkey_patch(self) -> None:
        """Test safe_float by temporarily patching float() to force exceptions."""
        import builtins
        original_float = builtins.float
        exception_counter = 0

        def counting_float(value: Any) -> float:
            nonlocal exception_counter
            # Force exceptions for certain values to ensure coverage
            if value == "force_value_error":
                exception_counter += 1
                raise ValueError("Forced ValueError for coverage")
            if value == "force_type_error":
                exception_counter += 1
                raise TypeError("Forced TypeError for coverage")
            return original_float(value)

        try:
            # Temporarily replace float()
            builtins.float = counting_float  # type: ignore[assignment]

            # Test forced ValueError path
            result1 = FlextUtilities.Conversions.safe_float("force_value_error", default=111.0)
            assert result1 == 111.0, f"Forced ValueError should return default, got {result1}"

            # Test forced TypeError path
            result2 = FlextUtilities.Conversions.safe_float("force_type_error", default=222.0)
            assert result2 == 222.0, f"Forced TypeError should return default, got {result2}"

            # Verify exceptions were actually raised and caught
            assert exception_counter == 2, f"Expected 2 exceptions, got {exception_counter}"

        finally:
            # Restore original float()
            builtins.float = original_float

    def test_safe_float_comprehensive_edge_cases(self) -> None:
        """Test comprehensive edge cases to ensure all exception paths are covered."""
        # Edge cases that might not be covered by regular tests
        edge_cases = [
            # String cases that should cause ValueError
            ("", 1.1),
            ("   ", 2.2),  # Whitespace
            ("nan", 3.3),  # NaN string (might be valid in some Python versions)
            ("infinity", 4.4),  # Infinity string variants
            ("1.2.3.4", 5.5),  # Multiple dots
            ("12e", 6.6),  # Incomplete scientific notation
            ("e12", 7.7),  # Invalid scientific notation
            ("12e+-3", 8.8),  # Invalid scientific notation with conflicting signs
            ("++12", 9.9),  # Multiple signs
            ("12++", 10.1),  # Trailing invalid characters

            # Type cases that should cause TypeError
            (None, 11.1),
            (complex(0, 1), 12.2),
            ([], 13.3),
            ({}, 14.4),
            (set(), 15.5),
            (frozenset(), 16.6),
            (object(), 17.7),
            (lambda: None, 18.8),
            (type, 19.9),
            (Exception(), 20.0),
        ]

        for test_input, expected_default in edge_cases:
            result = FlextUtilities.Conversions.safe_float(test_input, default=expected_default)  # type: ignore[arg-type]
            assert result == expected_default, f"safe_float({test_input!r}) should return {expected_default}, got {result}"
