"""Declarative consumer models for flext-cli public contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from examples import ExamplesFlextCliModels, c
from flext_tests import FlextTestsModels

from flext_cli import FlextCliModels
from tests._models import TestsFlextCliModelsPart01


class TestsFlextCliModels(
    TestsFlextCliModelsPart01,
    FlextTestsModels,
    ExamplesFlextCliModels,
    FlextCliModels,
):
    """Test model facade composed from canonical FLEXT model owners."""

    class Tests(TestsFlextCliModelsPart01.Tests):
        """Consumer-owned records used to exercise typed YAML ingress."""

        class InheritedSettings(FlextCliModels.BaseSettings):
            """Consumer-owned settings using the inherited native configuration."""

            model_config = FlextCliModels.SettingsConfigDict(
                env_prefix="FLEXT_SETTINGS_REGRESSION_",
                case_sensitive=True,
            )

            topic: str = "fixture-default"

        class ServiceGreeting(FlextCliModels.FrozenModel):
            """Concrete validation model declared once on the greeting operation."""

            name: str = FlextCliModels.Field(description="Name to greet.")
            times: int = FlextCliModels.Field(
                default=1,
                ge=1,
                description="Number of greetings.",
            )

        class ServiceStatus(FlextCliModels.FrozenModel):
            """Owned result payload rendered by the service CLI."""

            ready: int = FlextCliModels.Field(description="Readiness indicator.")

        class RestrictedDatabaseConfig(
            ExamplesFlextCliModels.Examples.AdvancedDatabaseConfig
        ):
            """Database consumer that disallows the example's SSL port rewrite."""

            port: Annotated[
                int,
                FlextCliModels.Field(ge=1, le=5432),
            ] = c.EXAMPLE_DEFAULT_DB_PORT

        class YamlService(FlextCliModels.FrozenModel):
            """Strict service endpoint loaded from external YAML."""

            host: Annotated[str, FlextCliModels.Field(description="Service host name.")]
            port: Annotated[
                int, FlextCliModels.Field(description="Service port number.")
            ]

        class YamlFeatures(FlextCliModels.FrozenModel):
            """Strict feature configuration loaded from external YAML."""

            enabled: Annotated[
                bool, FlextCliModels.Field(description="Feature activation flag.")
            ]

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

            port: Annotated[
                int, FlextCliModels.Field(description="Server port number.")
            ]

        class TemplateWidthContext(FlextCliModels.FrozenModel):
            """Template render context exposing a Markdown wrap ``width``."""

            width: Annotated[int, FlextCliModels.Field(description="Wrap width.")]

        class TemplateServerContext(FlextCliModels.FrozenModel):
            """Template render context exposing a nested ``server`` field."""

            server: TestsFlextCliModels.Tests.TemplateServer


m = TestsFlextCliModels

__all__: list[str] = ["TestsFlextCliModels", "m"]
