"""Declarative consumer models for flext-cli public contract tests."""

from __future__ import annotations

from typing import Annotated

from flext_tests import FlextTestsModels

from flext_cli import FlextCliModels, m
from tests._models_parts.testsflextclimodels_part_01 import (
    TestsFlextCliModels as TestsFlextCliModelsPart01,
)


class TestsFlextCliModels(
    TestsFlextCliModelsPart01,
    FlextTestsModels,
    FlextCliModels,
):
    """Test model facade composed from canonical FLEXT model owners."""

    class Tests(TestsFlextCliModelsPart01.Tests):
        """Consumer-owned records used to exercise typed YAML ingress."""

        class YamlService(m.FrozenModel):
            """Strict service endpoint loaded from external YAML."""

            host: Annotated[str, m.Field(description="Service host name.")]
            port: Annotated[int, m.Field(description="Service port number.")]

        class YamlFeatures(m.FrozenModel):
            """Strict feature configuration loaded from external YAML."""

            enabled: Annotated[bool, m.Field(description="Feature activation flag.")]

        class YamlConsumerConfig(m.FrozenModel):
            """Strict consumer configuration returned by the public loader."""

            service: TestsFlextCliModels.Tests.YamlService
            features: TestsFlextCliModels.Tests.YamlFeatures


m = TestsFlextCliModels

__all__: list[str] = ["TestsFlextCliModels", "m"]
