"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.JsonValue
as data contracts. Reuse TestsFlextModels types where possible; add
test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated, ClassVar, Self

from flext_tests import FlextTestsModels

from flext_cli import m
from tests import c, t


class TestsFlextCliModels(FlextTestsModels, m):
    """Test namespace facade for flext-cli models.

    Use m alias; preserves all test model types.
    """

    class Tests(FlextTestsModels.Tests):
        """Test-specific model definitions for flext-cli."""

        class ApiResponse(m.BaseModel):
            """API response for type scenario tests -- Pydantic v2."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")
            status: Annotated[str, m.Field(description="Status")]
            data: Annotated[
                t.JsonMapping | None,
                m.Field(description="Payload"),
            ] = None
            message: Annotated[str, m.Field(description="Message")]
            error: Annotated[str | None, m.Field(description="Error")] = None

        # --- Version test models ---

        class VersionTestScenario(m.BaseModel):
            """Version test scenario data."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

            name: Annotated[str, m.Field(description="Scenario name")]
            version_string: Annotated[
                str | None, m.Field(description="Version string under test")
            ] = None
            version_info: Annotated[
                tuple[int | str, ...] | None,
                m.Field(description="Version info tuple under test"),
            ] = None
            should_pass: Annotated[
                bool,
                m.Field(
                    description="Whether scenario should pass validation",
                ),
            ] = True

            @classmethod
            def string_cases(cls) -> tuple[Self, ...]:
                """Get parametrized test cases for version string validation."""
                cases = c.Tests.VERSION_STR_CASES
                return (
                    cls(
                        name="valid_semver",
                        version_string=cases["valid_semver"],
                        should_pass=True,
                    ),
                    cls(
                        name="valid_complex",
                        version_string=cases["valid_semver_complex"],
                        should_pass=True,
                    ),
                    cls(
                        name="invalid_no_dots",
                        version_string=cases["invalid_no_dots"],
                        should_pass=False,
                    ),
                    cls(
                        name="invalid_non_numeric",
                        version_string=cases["invalid_non_numeric"],
                        should_pass=False,
                    ),
                    cls(name="invalid_empty", version_string="", should_pass=False),
                )

            @classmethod
            def info_cases(cls) -> tuple[Self, ...]:
                """Get parametrized test cases for version info validation."""
                return (
                    cls(
                        name="valid_tuple",
                        version_info=c.Tests.VERSION_INFO_VALID_TUPLE,
                        should_pass=True,
                    ),
                    cls(
                        name="valid_complex_tuple",
                        version_info=c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        should_pass=True,
                    ),
                    cls(
                        name="short_tuple",
                        version_info=c.Tests.VERSION_INFO_SHORT_TUPLE,
                        should_pass=False,
                    ),
                    cls(
                        name="empty_tuple",
                        version_info=c.Tests.VERSION_INFO_EMPTY_TUPLE,
                        should_pass=False,
                    ),
                )

            @classmethod
            def consistency_cases(cls) -> tuple[Self, ...]:
                """Get parametrized test cases for version consistency validation."""
                cases = c.Tests.VERSION_STR_CASES
                return (
                    cls(
                        name="valid_match",
                        version_string=cases["valid_semver"],
                        version_info=c.Tests.VERSION_INFO_VALID_TUPLE,
                        should_pass=True,
                    ),
                    cls(
                        name="valid_complex_match",
                        version_string=cases["valid_semver_complex"],
                        version_info=c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        should_pass=True,
                    ),
                    cls(
                        name="invalid_mismatch",
                        version_string=cases["invalid_no_dots"],
                        version_info=c.Tests.VERSION_INFO_SHORT_TUPLE,
                        should_pass=False,
                    ),
                )

        # --- Config test models ---

        class ConfigTestScenario(m.BaseModel):
            """Test scenario with data."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

            name: Annotated[str, m.Field(description="Scenario name")]
            test_type: Annotated[
                t.Tests.ConfigTestType,
                m.Field(description="Scenario test type"),
            ]
            data: Annotated[
                t.JsonMapping | None,
                m.Field(description="Scenario input data"),
            ] = None
            should_pass: Annotated[
                bool, m.Field(description="Whether scenario is expected to pass")
            ] = True

        # --- CLI Service test models ---

        class SampleInput(m.BaseModel):
            """Small request model for exercising model-driven CLI generation."""

            name: Annotated[str, m.Field(description="Target name")]
            count: Annotated[int, m.Field(description="How many times")] = 1
            dry_run: Annotated[bool, m.Field(description="Dry-run mode")] = False
            output_format: Annotated[
                c.Cli.OutputFormats, m.Field(description="Output format")
            ] = c.Cli.OutputFormats.TABLE

        class SampleOutput(m.BaseModel):
            """Concrete output model for result-route tests."""

            message: Annotated[str, m.Field(description="User-facing success message")]

        class RepeatableInput(m.BaseModel):
            """Exercise repeatable CLI options derived from list-typed fields."""

            make_arg: Annotated[
                list[str],
                m.Field(default_factory=list, description="Repeatable make-style arg"),
            ] = m.Field(default_factory=list)


m = TestsFlextCliModels

__all__: list[str] = [
    "TestsFlextCliModels",
    "m",
]
