"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.NormalizedValue as data contracts.
Reuse FlextTestsModels types where possible; add test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import Annotated, ClassVar, Literal

from flext_tests import FlextTestsModels
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import FlextCliModels, FlextCliTypes
from tests import t


class FlextCliTestModels(FlextTestsModels, FlextCliModels):
    """Test namespace facade for flext-cli models. Use m alias; preserves all test model types."""

    class Cli(FlextCliModels.Cli):
        """CLI models with test-specific extensions."""

        class Tests:
            """Test-specific model definitions for flext-cli."""

            class PositionalModel(BaseModel):
                """Model accepting positional data for test scenarios."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

                def __init__(
                    self,
                    data: Mapping[str, FlextCliTypes.ContainerValue] | None = None,
                    /,
                    **kwargs: FlextCliTypes.ContainerValue,
                ) -> None:
                    payload: MutableMapping[str, FlextCliTypes.ContainerValue] = {}
                    if data is not None:
                        payload.update(data)
                    payload.update(kwargs)
                    super().__init__(**payload)

            class UserData(PositionalModel):
                """User data for type scenario tests -- Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                id: Annotated[int, Field(description="User id")]
                name: Annotated[str, Field(description="User name")]
                email: Annotated[str, Field(description="Email")]
                active: Annotated[bool, Field(description="Active flag")]

            class ApiResponse(PositionalModel):
                """API response for type scenario tests -- Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                status: Annotated[str, Field(description="Status")]
                data: Annotated[
                    FlextCliTypes.NormalizedValue,
                    Field(default=None, description="Payload"),
                ]
                message: Annotated[str, Field(description="Message")]
                error: Annotated[str | None, Field(default=None, description="Error")]

            # --- Version test models ---

            class VersionTestScenario(BaseModel):
                """Version test scenario data."""

                model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

                name: Annotated[str, Field(description="Scenario name")]
                version_string: Annotated[
                    str | None,
                    Field(default=None, description="Version string under test"),
                ] = None
                version_info: Annotated[
                    tuple[int | str, ...] | None,
                    Field(default=None, description="Version info tuple under test"),
                ] = None
                should_pass: Annotated[
                    bool,
                    Field(
                        default=True,
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
                def get_string_cases(
                    cls,
                ) -> Sequence[FlextCliTestModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version string validation."""
                    from tests import c

                    data_class = FlextCliTestModels.Cli.Tests.VersionTestScenario
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
                def get_info_cases(
                    cls,
                ) -> Sequence[FlextCliTestModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version info validation."""
                    from tests import c

                    data_class = FlextCliTestModels.Cli.Tests.VersionTestScenario
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
                def get_consistency_cases(
                    cls,
                ) -> Sequence[FlextCliTestModels.Cli.Tests.VersionTestScenario]:
                    """Get parametrized test cases for version consistency validation."""
                    from tests import c

                    data_class = FlextCliTestModels.Cli.Tests.VersionTestScenario
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

            class ConfigTestScenario(BaseModel):
                """Test scenario with data."""

                model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

                name: Annotated[str, Field(description="Scenario name")]
                test_type: Annotated[
                    t.Cli.Tests.ConfigTestType, Field(description="Scenario test type")
                ]
                data: Annotated[
                    FlextCliTypes.ContainerMapping | None,
                    Field(default=None, description="Scenario input data"),
                ]
                should_pass: Annotated[
                    bool,
                    Field(
                        default=True, description="Whether scenario is expected to pass"
                    ),
                ]

            # --- CLI Service test models ---

            class SampleInput(BaseModel):
                """Small request model for exercising model-driven CLI generation."""

                name: Annotated[str, Field(description="Target name")]
                count: Annotated[int, Field(default=1, description="How many times")]
                dry_run: Annotated[
                    bool, Field(default=False, description="Dry-run mode")
                ]
                output_format: Annotated[
                    Literal["json", "table"],
                    Field(default="table", description="Output format"),
                ]

            class SampleOutput(BaseModel):
                """Concrete output model for result-route tests."""

                message: Annotated[
                    str, Field(description="User-facing success message")
                ]

            class RepeatableInput(BaseModel):
                """Exercise repeatable CLI options derived from list-typed fields."""

                make_arg: Annotated[
                    list[str],
                    Field(
                        default_factory=list, description="Repeatable make-style arg"
                    ),
                ] = Field(default_factory=list)

            class SampleRoute(
                FlextCliModels.Cli.ResultCommandRouteModel[SampleInput, SampleOutput]
            ):
                """Concrete route model for test-time generic stability."""


m = FlextCliTestModels

__all__ = [
    "FlextCliTestModels",
    "m",
]
