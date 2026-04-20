"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.Container as data contracts.
Reuse TestsFlextModels types where possible; add test-specific input models only when needed.

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


class TestsFlextCliModels(FlextTestsModels, m):
    """Test namespace facade for flext-cli models. Use m alias; preserves all test model types."""

    class Cli(m.Cli):
        """CLI models with test-specific extensions."""

        class Tests:
            """Test-specific model definitions for flext-cli."""

            class PositionalModel(m.BaseModel):
                """Model accepting positional data for test scenarios."""

                model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

                def __init__(
                    self,
                    data: Mapping[str, t.Cli.JsonValue] | None = None,
                    /,
                    **kwargs: t.Cli.JsonValue,
                ) -> None:
                    payload: MutableMapping[str, t.Cli.JsonValue] = {}
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
                data: Annotated[t.Container, m.Field(description="Payload")] = None
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
                def validation_type(self) -> t.Cli.Tests.ValidationType:
                    """Determine validation type based on data provided."""
                    if self.version_string and self.version_info:
                        return t.Cli.Tests.ValidationType.CONSISTENCY
                    if self.version_info:
                        return t.Cli.Tests.ValidationType.INFO
                    return t.Cli.Tests.ValidationType.STRING

            class VersionScenarios:
                """Factory methods for version test scenarios."""

                @classmethod
                def string_cases(
                    cls,
                ) -> Sequence[TestsFlextCliModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version string validation."""
                    from tests import c

                    data_class = TestsFlextCliModels.Cli.Tests.VersionTestScenario
                    ex = c.Cli.Tests.VersionExamples
                    return [
                        data_class(
                            name="valid_semver",
                            version_string=ex.VALID_SEMVER,
                            should_pass=True,
                        ),
                        data_class(
                            name="valid_complex",
                            version_string=ex.VALID_SEMVER_COMPLEX,
                            should_pass=True,
                        ),
                        data_class(
                            name="invalid_no_dots",
                            version_string=ex.INVALID_NO_DOTS,
                            should_pass=False,
                        ),
                        data_class(
                            name="invalid_non_numeric",
                            version_string=ex.INVALID_NON_NUMERIC,
                            should_pass=False,
                        ),
                        data_class(
                            name="invalid_empty", version_string="", should_pass=False
                        ),
                    ]

                @classmethod
                def info_cases(
                    cls,
                ) -> Sequence[TestsFlextCliModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version info validation."""
                    from tests import c

                    data_class = TestsFlextCliModels.Cli.Tests.VersionTestScenario
                    info = c.Cli.Tests.VersionInfoTuples
                    return [
                        data_class(
                            name="valid_tuple",
                            version_info=info.VALID_TUPLE,
                            should_pass=True,
                        ),
                        data_class(
                            name="valid_complex_tuple",
                            version_info=info.VALID_COMPLEX_TUPLE,
                            should_pass=True,
                        ),
                        data_class(
                            name="short_tuple",
                            version_info=info.SHORT_TUPLE,
                            should_pass=False,
                        ),
                        data_class(
                            name="empty_tuple",
                            version_info=info.EMPTY_TUPLE,
                            should_pass=False,
                        ),
                    ]

                @classmethod
                def consistency_cases(
                    cls,
                ) -> Sequence[TestsFlextCliModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version consistency validation."""
                    from tests import c

                    data_class = TestsFlextCliModels.Cli.Tests.VersionTestScenario
                    ex = c.Cli.Tests.VersionExamples
                    info = c.Cli.Tests.VersionInfoTuples
                    return [
                        data_class(
                            name="valid_match",
                            version_string=ex.VALID_SEMVER,
                            version_info=info.VALID_TUPLE,
                            should_pass=True,
                        ),
                        data_class(
                            name="valid_complex_match",
                            version_string=ex.VALID_SEMVER_COMPLEX,
                            version_info=info.VALID_COMPLEX_TUPLE,
                            should_pass=True,
                        ),
                        data_class(
                            name="invalid_mismatch",
                            version_string=ex.INVALID_NO_DOTS,
                            version_info=info.SHORT_TUPLE,
                            should_pass=False,
                        ),
                    ]

            # --- Config test models ---

            class ConfigTestScenario(m.BaseModel):
                """Test scenario with data."""

                model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

                name: Annotated[str, m.Field(description="Scenario name")]
                test_type: Annotated[
                    t.Cli.Tests.ConfigTestType,
                    m.Field(description="Scenario test type"),
                ]
                data: Annotated[
                    Mapping[str, t.Container] | None,
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

                message: Annotated[
                    str, m.Field(description="User-facing success message")
                ]

            class RepeatableInput(m.BaseModel):
                """Exercise repeatable CLI options derived from list-typed fields."""

                make_arg: Annotated[
                    list[str],
                    m.Field(
                        default_factory=list, description="Repeatable make-style arg"
                    ),
                ] = m.Field(default_factory=list)

            class SampleRoute(m.Cli.ResultCommandRoute):
                """Concrete route model for test-time generic stability."""


m = TestsFlextCliModels

__all__: list[str] = [
    "TestsFlextCliModels",
    "m",
]
