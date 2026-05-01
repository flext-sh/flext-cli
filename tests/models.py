"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.JsonValue
as data contracts. Reuse TestsFlextModels types where possible; add
test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
)
from typing import Annotated, ClassVar

from flext_tests import FlextTestsModels

from flext_cli import m
from tests import c, t
from tests.typings import TestsFlextCliTypes


class TestsFlextCliModels(FlextTestsModels, m):
    """Test namespace facade for flext-cli models.

    Use m alias; preserves all test model types.
    """

    class Tests(FlextTestsModels.Tests):
        """Test-specific model definitions for flext-cli."""

        class PositionalModel(m.BaseModel):
            """Model accepting positional data for test scenarios."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

            def __init__(
                self,
                data: Mapping[str, t.JsonValue] | None = None,
                /,
                **kwargs: t.JsonValue,
            ) -> None:
                payload: MutableMapping[str, t.JsonValue] = {}
                if data is not None:
                    payload.update(data)
                payload.update(kwargs)
                super().__init__(**payload)

        class UserData(PositionalModel):
            """User data for type scenario tests -- Pydantic v2."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")
            id: Annotated[int, m.Field(description="User id")]
            name: Annotated[str, m.Field(description="User name")]
            email: Annotated[str, m.Field(description="Email")]
            active: Annotated[bool, m.Field(description="Active flag")]

        class ApiResponse(PositionalModel):
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

            @property
            def validation_type(self) -> TestsFlextCliTypes.Tests.ValidationType:
                """Determine validation type based on data provided."""
                if self.version_string and self.version_info:
                    return TestsFlextCliTypes.Tests.ValidationType.CONSISTENCY
                if self.version_info:
                    return TestsFlextCliTypes.Tests.ValidationType.INFO
                return TestsFlextCliTypes.Tests.ValidationType.STRING

        class VersionScenarios:
            """Factory methods for version test scenarios."""

            @classmethod
            def string_cases(
                cls,
            ) -> Sequence[TestsFlextCliModels.Tests.VersionTestScenario]:
                """Get parametrized test cases for version string validation."""
                data_class = TestsFlextCliModels.Tests.VersionTestScenario
                cases = c.Tests.VERSION_STR_CASES
                return [
                    data_class(
                        name="valid_semver",
                        version_string=cases["valid_semver"],
                        should_pass=True,
                    ),
                    data_class(
                        name="valid_complex",
                        version_string=cases["valid_semver_complex"],
                        should_pass=True,
                    ),
                    data_class(
                        name="invalid_no_dots",
                        version_string=cases["invalid_no_dots"],
                        should_pass=False,
                    ),
                    data_class(
                        name="invalid_non_numeric",
                        version_string=cases["invalid_non_numeric"],
                        should_pass=False,
                    ),
                    data_class(
                        name="invalid_empty", version_string="", should_pass=False
                    ),
                ]

            @classmethod
            def info_cases(
                cls,
            ) -> Sequence[TestsFlextCliModels.Tests.VersionTestScenario]:
                """Get parametrized test cases for version info validation."""
                data_class = TestsFlextCliModels.Tests.VersionTestScenario
                return [
                    data_class(
                        name="valid_tuple",
                        version_info=c.Tests.VERSION_INFO_VALID_TUPLE,
                        should_pass=True,
                    ),
                    data_class(
                        name="valid_complex_tuple",
                        version_info=c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        should_pass=True,
                    ),
                    data_class(
                        name="short_tuple",
                        version_info=c.Tests.VERSION_INFO_SHORT_TUPLE,
                        should_pass=False,
                    ),
                    data_class(
                        name="empty_tuple",
                        version_info=c.Tests.VERSION_INFO_EMPTY_TUPLE,
                        should_pass=False,
                    ),
                ]

            @classmethod
            def consistency_cases(
                cls,
            ) -> Sequence[TestsFlextCliModels.Tests.VersionTestScenario]:
                """Get parametrized test cases for version consistency validation."""
                data_class = TestsFlextCliModels.Tests.VersionTestScenario
                cases = c.Tests.VERSION_STR_CASES
                return [
                    data_class(
                        name="valid_match",
                        version_string=cases["valid_semver"],
                        version_info=c.Tests.VERSION_INFO_VALID_TUPLE,
                        should_pass=True,
                    ),
                    data_class(
                        name="valid_complex_match",
                        version_string=cases["valid_semver_complex"],
                        version_info=c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        should_pass=True,
                    ),
                    data_class(
                        name="invalid_mismatch",
                        version_string=cases["invalid_no_dots"],
                        version_info=c.Tests.VERSION_INFO_SHORT_TUPLE,
                        should_pass=False,
                    ),
                ]

        # --- Config test models ---

        class ConfigTestScenario(m.BaseModel):
            """Test scenario with data."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

            name: Annotated[str, m.Field(description="Scenario name")]
            test_type: Annotated[
                TestsFlextCliTypes.Tests.ConfigTestType,
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

        class SampleRoute(m.Cli.ResultCommandRoute):
            """Concrete route model for test-time generic stability."""


m = TestsFlextCliModels

__all__: list[str] = [
    "TestsFlextCliModels",
    "m",
]
