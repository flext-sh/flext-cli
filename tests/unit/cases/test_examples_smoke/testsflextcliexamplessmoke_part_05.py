"""Smoke tests for flext-cli examples using the public cli facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from examples import ExamplesFlextCliSettings
from examples.ex_12_pydantic_driven_cli import ExamplesFlextCliPydanticDrivenCli

from tests import c, m, tm, u


class TestsFlextCliExamplesSmokePart05:
    """Implementation part for TestsFlextCliExamplesSmokePart05."""

    @staticmethod
    def test_business_rules_preserve_input_and_validate_subclass_constraints() -> None:
        """Port replacement respects consumer constraints and frozen inputs."""
        restricted = m.Tests.RestrictedDatabaseConfig(
            host="db.example.com",
            port=5432,
            name="prod",
            username="user",
            password="p" + "3" * 10,
            ssl_enabled=True,
            connection_pool=10,
        )
        original = restricted.model_dump()
        rejected = ExamplesFlextCliPydanticDrivenCli.validate_business_rules(
            restricted,
        )
        tm.fail(rejected)
        tm.that(rejected.exception, is_=c.ValidationError)
        tm.that(restricted.model_dump(), eq=original)

        unrestricted = m.Examples.AdvancedDatabaseConfig.model_validate(original)
        accepted = ExamplesFlextCliPydanticDrivenCli.validate_business_rules(
            unrestricted,
        )
        tm.ok(accepted)
        tm.that(accepted.value.port, eq=5433)
        tm.that(unrestricted.model_dump(), eq=original)

        unchanged = ExamplesFlextCliPydanticDrivenCli.validate_business_rules(
            accepted.value,
        )
        tm.ok(unchanged)
        tm.ok(unchanged.value is accepted.value)

    @staticmethod
    def test_settings_and_pydantic_examples_validate_production_flow(
        tmp_path: Path,
    ) -> None:
        """Settings examples consume injected models and typed workflow rules."""
        cache_dir = tmp_path / "cache"
        settings_result = ExamplesFlextCliSettings.load_application_settings(
            m.Examples.AppSettingsAdvanced(
                environment=c.DeploymentEnvironment.PRODUCTION,
                api_key="k" + "3" * 14,
                max_workers=25,
                temp_dir=cache_dir,
            ),
        )
        tm.ok(settings_result)
        tm.that(settings_result.value["max_workers"], eq=20)
        tm.ok(settings_result.value["enable_metrics"])
        tm.ok(settings_result.value["services_initialized"])
        tm.ok(Path(str(settings_result.value["temp_dir"])).exists())

        database_result = (
            ExamplesFlextCliPydanticDrivenCli.create_database_config_from_cli()
        )
        tm.ok(database_result)
        tm.that(database_result.value.port, eq=5433)
        tm.ok(database_result.value.ssl_enabled)
        tm.that(database_result.value.connection_pool, eq=20)

    @staticmethod
    def test_pydantic_driven_example_surfaces_validation_and_connection_failures() -> (
        None
    ):
        """Fail a Pydantic-driven example through its public railway steps."""
        missing_fields = ExamplesFlextCliPydanticDrivenCli.validate_required_fields({
            "host": "db.example.com"
        })
        tm.fail(missing_fields)

        invalid_model = (
            ExamplesFlextCliPydanticDrivenCli.convert_and_validate_with_pydantic(
                u.Cli.JSON_MAPPING_ADAPTER.validate_python({
                    "host": "db.example.com",
                    "port": "bad-port",
                    "name": "prod",
                    "username": "user",
                    "password": c.Tests.CREDENTIAL_SAMPLE_VALUE,
                    "ssl_enabled": True,
                    "connection_pool": 10,
                }),
            )
        )
        tm.fail(invalid_model)

        base_config = (
            ExamplesFlextCliPydanticDrivenCli.convert_and_validate_with_pydantic(
                u.Cli.JSON_MAPPING_ADAPTER.validate_python({
                    "host": "db.example.com",
                    "port": 5432,
                    "name": "prod",
                    "username": "user",
                    "password": "p" + "3" * 10,
                    "ssl_enabled": False,
                    "connection_pool": 10,
                }),
            )
        )
        tm.ok(base_config)

        payload = base_config.value.model_dump(mode="json")
        required_fields = ExamplesFlextCliPydanticDrivenCli.validate_required_fields(
            payload,
        )
        tm.ok(required_fields)
        tm.that(required_fields.value, eq=payload)

        oversized_localhost = base_config.value.model_copy(
            update={"host": "localhost", "connection_pool": 60},
        )
        business_rule_result = (
            ExamplesFlextCliPydanticDrivenCli.validate_business_rules(
                oversized_localhost
            )
        )
        tm.fail(business_rule_result)

        failing_connection = base_config.value.model_copy(
            update={"host": "fail-db.example.com"},
        )
        connection_result = ExamplesFlextCliPydanticDrivenCli.perform_connection_test(
            failing_connection
        )
        tm.fail(connection_result)
