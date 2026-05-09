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
                m.Field(description="Whether scenario should pass validation"),
            ] = True

            @classmethod
            def _build(
                cls,
                rows: t.SequenceOf[
                    tuple[str, str | None, tuple[int | str, ...] | None, bool]
                ],
            ) -> tuple[Self, ...]:
                return tuple(
                    cls(name=name, version_string=vs, version_info=vi, should_pass=ok)
                    for name, vs, vi, ok in rows
                )

            @classmethod
            def string_cases(cls) -> tuple[Self, ...]:
                """Parametrized cases for version string validation."""
                strs = c.Tests.VERSION_STR_CASES
                return cls._build([
                    ("valid_semver", strs["valid_semver"], None, True),
                    ("valid_complex", strs["valid_semver_complex"], None, True),
                    ("invalid_no_dots", strs["invalid_no_dots"], None, False),
                    ("invalid_non_numeric", strs["invalid_non_numeric"], None, False),
                    ("invalid_empty", "", None, False),
                ])

            @classmethod
            def info_cases(cls) -> tuple[Self, ...]:
                """Parametrized cases for version info tuple validation."""
                return cls._build([
                    ("valid_tuple", None, c.Tests.VERSION_INFO_VALID_TUPLE, True),
                    (
                        "valid_complex_tuple",
                        None,
                        c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        True,
                    ),
                    ("short_tuple", None, c.Tests.VERSION_INFO_SHORT_TUPLE, False),
                    ("empty_tuple", None, c.Tests.VERSION_INFO_EMPTY_TUPLE, False),
                ])

            @classmethod
            def consistency_cases(cls) -> tuple[Self, ...]:
                """Parametrized cases for version consistency validation."""
                strs = c.Tests.VERSION_STR_CASES
                return cls._build([
                    (
                        "valid_match",
                        strs["valid_semver"],
                        c.Tests.VERSION_INFO_VALID_TUPLE,
                        True,
                    ),
                    (
                        "valid_complex_match",
                        strs["valid_semver_complex"],
                        c.Tests.VERSION_INFO_VALID_COMPLEX_TUPLE,
                        True,
                    ),
                    (
                        "invalid_mismatch",
                        strs["invalid_no_dots"],
                        c.Tests.VERSION_INFO_SHORT_TUPLE,
                        False,
                    ),
                ])

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
