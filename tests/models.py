# AUTO-GENERATED FILE — Regenerate with: make gen
"""Declarative consumer models for flext-cli public contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from examples import c, m as examples_m
from flext_tests import m as flext_tests_m

from flext_cli import m as flext_cli_m
from tests._models import (
    TestsFlextCliModelsCli,
    TestsFlextCliModelsPart01,
    TestsFlextCliModelsRuntime,
)


class TestsFlextCliModels(
    TestsFlextCliModelsPart01,
    flext_tests_m,
    examples_m,
    flext_cli_m,
):
    """Test model facade composed from canonical FLEXT model owners."""

    class Tests(
        TestsFlextCliModelsPart01.Tests,
        TestsFlextCliModelsRuntime,
        TestsFlextCliModelsCli,
        flext_tests_m.Tests,
    ):
        """Consumer-owned records used to exercise typed YAML ingress."""

        class InheritedSettings(flext_cli_m.BaseSettings):
            """Consumer-owned settings using the inherited native configuration."""

            model_config = flext_cli_m.SettingsConfigDict(
                env_prefix="FLEXT_SETTINGS_REGRESSION_",
                case_sensitive=True,
            )

            topic: str = "fixture-default"

        class ServiceGreeting(flext_cli_m.FrozenModel):
            """Concrete validation model declared once on the greeting operation."""

            name: str = flext_cli_m.Field(description="Name to greet.")
            times: int = flext_cli_m.Field(
                default=1,
                ge=1,
                description="Number of greetings.",
            )

        class ServiceStatus(flext_cli_m.FrozenModel):
            """Owned result payload rendered by the service CLI."""

            ready: int = flext_cli_m.Field(description="Readiness indicator.")

        class RestrictedDatabaseConfig(examples_m.Examples.AdvancedDatabaseConfig):
            """Database consumer that disallows the example's SSL port rewrite."""

            port: Annotated[
                int,
                flext_cli_m.Field(ge=1, le=5432),
            ] = c.EXAMPLE_DEFAULT_DB_PORT

        class YamlService(flext_cli_m.FrozenModel):
            """Strict service endpoint loaded from external YAML."""

            host: Annotated[str, flext_cli_m.Field(description="Service host name.")]
            port: Annotated[int, flext_cli_m.Field(description="Service port number.")]

        class YamlFeatures(flext_cli_m.FrozenModel):
            """Strict feature configuration loaded from external YAML."""

            enabled: Annotated[
                bool, flext_cli_m.Field(description="Feature activation flag.")
            ]

        class YamlConsumerConfig(flext_cli_m.FrozenModel):
            """Strict consumer configuration returned by the public loader."""

            service: TestsFlextCliModels.Tests.YamlService
            features: TestsFlextCliModels.Tests.YamlFeatures

        class TemplateEmpty(flext_cli_m.FrozenModel):
            """Empty template render context (no variables provided)."""

        class TemplateValue(flext_cli_m.FrozenModel):
            """Template render context exposing a single ``value`` field."""

            value: Annotated[int, flext_cli_m.Field(description="Template value.")]

        class TemplateServer(flext_cli_m.FrozenModel):
            """Template render context nested ``server`` record."""

            port: Annotated[int, flext_cli_m.Field(description="Server port number.")]

        class TemplateWidthContext(flext_cli_m.FrozenModel):
            """Template render context exposing a Markdown wrap ``width``."""

            width: Annotated[int, flext_cli_m.Field(description="Wrap width.")]

        class TemplateServerContext(flext_cli_m.FrozenModel):
            """Template render context exposing a nested ``server`` field."""

            server: TestsFlextCliModels.Tests.TemplateServer


m = TestsFlextCliModels
__all__: list[str] = ["TestsFlextCliModels", "m"]
