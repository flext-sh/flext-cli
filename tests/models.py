"""Declarative consumer models for flext-cli public contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_tests import FlextTestsModels

from flext_cli import FlextCliModels
from tests._models_parts.testsflextclimodels_part_01 import TestsFlextCliModelsPart01


class TestsFlextCliModels(TestsFlextCliModelsPart01, FlextTestsModels, FlextCliModels):
    """Test model facade composed from canonical FLEXT model owners."""

    class Tests(TestsFlextCliModelsPart01.Tests):
        """Consumer-owned records used to exercise typed YAML ingress."""

        class YamlService(FlextCliModels.FrozenModel):
            """Strict service endpoint loaded from external YAML."""

            host: Annotated[str, FlextCliModels.Field(description="Service host name.")]
            port: Annotated[int, FlextCliModels.Field(description="Service port number.")]

        class YamlFeatures(FlextCliModels.FrozenModel):
            """Strict feature configuration loaded from external YAML."""

            enabled: Annotated[bool, FlextCliModels.Field(description="Feature activation flag.")]

        class YamlConsumerConfig(FlextCliModels.FrozenModel):
            """Strict consumer configuration returned by the public loader."""

            service: TestsFlextCliModels.Tests.YamlService
            features: TestsFlextCliModels.Tests.YamlFeatures

        class TemplateEmpty(FlextCliModels.FrozenModel):
            """Empty template render context (no variables provided)."""

        class TemplateValue(FlextCliModels.FrozenModel):
            """Template render context exposing a single ``value`` field."""

            value: Annotated[int, FlextCliModels.Field(description="Template value.")]

        class TemplateServer(FlextCliModels.FrozenModel):
            """Template render context nested ``server`` record."""

            port: Annotated[int, FlextCliModels.Field(description="Server port number.")]

        class TemplateServerContext(FlextCliModels.FrozenModel):
            """Template render context exposing a nested ``server`` field."""

            server: TestsFlextCliModels.Tests.TemplateServer


m = TestsFlextCliModels

__all__: list[str] = ["TestsFlextCliModels", "m"]
