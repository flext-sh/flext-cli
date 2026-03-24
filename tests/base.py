"""Service base for flext-cli tests.

Provides TestsCliServiceBase, extending s with flext-cli-specific
service functionality. All generic test service functionality comes from flext_tests.

Architecture:
- s (flext_tests) = Generic service base for all FLEXT projects
- TestsCliServiceBase (tests/) = flext-cli-specific service base extending s

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import ClassVar, override

from flext_core import FlextHandlers, T, r
from flext_tests import s, td
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tests import c, m, t


class TestsCliServiceBase(s[T]):
    """Service base for flext-cli tests - extends s.

    Architecture: Extends s with flext-cli-specific service
    functionality. All generic service functionality from s
    is available through inheritance.

    Rules:
    - NEVER redeclare functionality from s
    - Only flext-cli-specific service functionality allowed
    - All generic service functionality comes from s
    """

    @override
    def execute(self) -> r[T]:
        return r[T].fail("not implemented")

    class HandlerTestCase(BaseModel):
        """Factory for handler test case configurations."""

        model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

        handler_id: str = Field(description="Handler identifier")
        handler_name: str | None = Field(
            default=None,
            description="Optional handler name",
        )
        handler_type: c.HandlerType = Field(
            default=c.HandlerType.COMMAND,
            description="Handler type used for test case",
        )
        expected_result: t.Container | None = Field(
            default=None,
            description="Expected handler result value",
        )
        should_fail: bool = Field(
            default=False,
            description="Whether handler is expected to fail",
        )
        error_message: str | None = Field(
            default=None,
            description="Expected error message when failure occurs",
        )
        description: str = Field(
            default="",
            description="Human readable scenario description",
        )

        def create_handler(
            self,
            process_fn: Callable[[t.Container], r[t.Container]] | None = None,
        ) -> FlextHandlers[t.Container, t.Container]:
            """Create handler instance for this test case."""
            return TestsCliServiceBase.Handlers.create_test_handler(
                handler_id=self.handler_id,
                handler_name=self.handler_name,
                handler_type=self.handler_type,
                process_fn=process_fn,
            )

    class HandlerFactories:
        """Centralized factories for test handlers."""

        @staticmethod
        def _to_expected_result(value: t.NormalizedValue) -> t.Container | None:
            if value is None:
                return None
            if isinstance(value, (str, int, float, bool, datetime, Path)):
                container_value: t.Container = value
                return container_value
            return None

        @staticmethod
        def _build_cases(
            *,
            should_fail: bool,
        ) -> Sequence[TestsCliServiceBase.HandlerTestCase]:
            cases: Sequence[TestsCliServiceBase.HandlerTestCase] = []
            for spec in td.default_handler_case_specs():
                spec_should_fail = bool(spec.get("should_fail", False))
                if spec_should_fail is not should_fail:
                    continue
                handler_type_name = str(spec["handler_type"])
                cases.append(
                    TestsCliServiceBase.HandlerTestCase(
                        handler_id=str(spec["handler_id"]),
                        handler_type=getattr(c.HandlerType, handler_type_name),
                        expected_result=TestsCliServiceBase.HandlerFactories._to_expected_result(
                            spec.get("expected_result"),
                        ),
                        should_fail=spec_should_fail,
                        error_message=(
                            str(spec["error_message"])
                            if isinstance(spec.get("error_message"), str)
                            else None
                        ),
                        description=str(spec["description"]),
                    ),
                )
            return cases

        @staticmethod
        def success_cases() -> Sequence[TestsCliServiceBase.HandlerTestCase]:
            """Generate success handler test cases."""
            return TestsCliServiceBase.HandlerFactories._build_cases(should_fail=False)

        @staticmethod
        def failure_cases() -> Sequence[TestsCliServiceBase.HandlerTestCase]:
            """Generate failure handler test cases."""
            return TestsCliServiceBase.HandlerFactories._build_cases(should_fail=True)

    class Handlers:
        """Handler creation utilities for tests."""

        @staticmethod
        def create_test_handler(
            handler_id: str,
            handler_name: str | None = None,
            handler_type: c.HandlerType = c.HandlerType.COMMAND,
            process_fn: Callable[[t.Container], r[t.Container]] | None = None,
        ) -> FlextHandlers[t.Container, t.Container]:
            """Factory for creating test handlers - reduces massive boilerplate.

            Args:
                handler_id: Unique handler identifier
                handler_name: Display name (defaults to handler_id.title())
                handler_type: Handler type (COMMAND, QUERY, EVENT)
                process_fn: Optional custom.Cli.processing function

            Returns:
                FlextHandlers instance ready for registration

            """

            class DynamicTestHandler(FlextHandlers[t.Container, t.Container]):
                """Dynamic test handler implementation."""

                def __init__(self) -> None:
                    if not handler_id:
                        msg = "Handler ID cannot be empty"
                        raise ValueError(msg)
                    config = m.Handler(
                        handler_id=handler_id,
                        handler_name=handler_name
                        or handler_id.replace("_", " ").title(),
                        handler_type=handler_type,
                        handler_mode=handler_type,
                    )
                    super().__init__(config=config)

                @override
                def handle(self, message: t.Container) -> r[t.Container]:
                    """Handle message with proper error handling."""
                    try:
                        if process_fn:
                            return process_fn(message)
                        return r[t.Container].ok(f"Handled: {message}")
                    except (ValueError, TypeError, ValidationError) as e:
                        return r[t.Container].fail(f"Handler error: {e}")

            return DynamicTestHandler()

        @staticmethod
        def create_simple_handler(
            handler_id: str,
            result_value: t.Container = "test",
        ) -> FlextHandlers[t.Container, t.Container]:
            """Create a simple handler that always returns the same value.

            Args:
                handler_id: Handler identifier (must not be empty)
                result_value: Value to return

            Returns:
                Handler that always succeeds with result_value

            """
            if not handler_id:
                msg = "Handler ID cannot be empty"
                raise ValueError(msg)

            def always_succeed(_msg: t.Container) -> r[t.Container]:
                """Always return success with configured value."""
                return r[t.Container].ok(result_value)

            return TestsCliServiceBase.Handlers.create_test_handler(
                handler_id,
                process_fn=always_succeed,
            )

        @staticmethod
        def create_failing_handler(
            handler_id: str,
            error_message: str = "Processing error",
        ) -> FlextHandlers[t.Container, t.Container]:
            """Create a handler that always fails.

            Args:
                handler_id: Handler identifier (must not be empty)
                error_message: Error message to return

            Returns:
                Handler that always fails with error_message

            """
            if not handler_id:
                msg = "Handler ID cannot be empty"
                raise ValueError(msg)
            if not error_message:
                error_message = "Processing error"

            def always_fail(_msg: t.Container) -> r[t.Container]:
                """Always return failure with configured error."""
                return r[t.Container].fail(error_message)

            return TestsCliServiceBase.Handlers.create_test_handler(
                handler_id,
                process_fn=always_fail,
            )

        @staticmethod
        def create_transform_handler(
            handler_id: str,
            transform_fn: Callable[[t.Container], t.Container],
        ) -> FlextHandlers[t.Container, t.Container]:
            """Create a handler that transforms messages.

            Args:
                handler_id: Handler identifier (must not be empty)
                transform_fn: Transformation function (must be callable)

            Returns:
                Handler that transforms messages using transform_fn

            """
            if not handler_id:
                msg = "Handler ID cannot be empty"
                raise ValueError(msg)

            def transform(msg: t.Container) -> r[t.Container]:
                """Transform message with proper error handling."""
                try:
                    result = transform_fn(msg)
                    return r[t.Container].ok(result)
                except (ValueError, TypeError, ValidationError) as e:
                    return r[t.Container].fail(f"Transformation failed: {e}")

            return TestsCliServiceBase.Handlers.create_test_handler(
                handler_id,
                process_fn=transform,
            )


__all__ = ["TestsCliServiceBase"]
s = TestsCliServiceBase
