"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.JsonValue
as data contracts. Reuse TestsFlextModels types where possible; add
test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated

from flext_tests import FlextTestsModels

from flext_cli import m as flext_cli_m
from tests._models_parts.testsflextclimodels_part_01 import (
    TestsFlextCliModels as TestsFlextCliModelsPart01,
)


class _TemplateEmpty(flext_cli_m.ArbitraryTypesModel):
    """Validated empty template context."""


class _TemplateValue(flext_cli_m.ArbitraryTypesModel):
    """Validated scalar template context."""

    value: Annotated[int, flext_cli_m.Field(description="Rendered test value")]


class _TemplateServer(flext_cli_m.ArbitraryTypesModel):
    """Validated server data rendered by template tests."""

    port: Annotated[int, flext_cli_m.Field(description="Server port")]


class _TemplateServerContext(flext_cli_m.ArbitraryTypesModel):
    """Validated nested server template context."""

    server: Annotated[
        _TemplateServer,
        flext_cli_m.Field(description="Server rendered by the template"),
    ]


class TestsFlextCliModels(
    TestsFlextCliModelsPart01,
    FlextTestsModels,
    flext_cli_m,
):
    """Public facade for TestsFlextCliModels."""

    class Tests(TestsFlextCliModelsPart01.Tests):
        """Test-specific model namespace."""

        # NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): template
        # tests use canonical Pydantic contexts instead of JSON-shaped mappings.
        TemplateEmpty = _TemplateEmpty
        TemplateServer = _TemplateServer
        TemplateServerContext = _TemplateServerContext
        TemplateValue = _TemplateValue


m: type[TestsFlextCliModels] = TestsFlextCliModels

__all__: list[str] = ["TestsFlextCliModels", "m"]
