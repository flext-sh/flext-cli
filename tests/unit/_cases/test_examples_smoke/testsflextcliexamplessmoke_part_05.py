"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from examples import (
    Ex06Settings,
    t as et,
)
from examples.ex_12_pydantic_driven_cli import (
    convert_and_validate_with_pydantic,
    create_database_config_from_cli,
    perform_connection_test,
    validate_business_rules,
    validate_required_fields,
)
from flext_tests import tm


class TestsFlextCliExamplesSmoke:
    """Implementation part for TestsFlextCliExamplesSmoke."""

    def test_settings_and_pydantic_examples_validate_production_flow(
        self,
        tmp_path: Path,
    ) -> None:
        """Settings examples must honor env overrides and typed workflow rules."""
        cache_dir = tmp_path / "cache"
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "API_KEY": "prod-secret",
                "MAX_WORKERS": "25",
                "TEMP_DIR": str(cache_dir),
            },
            clear=False,
        ):
            settings_result = Ex06Settings.load_application_settings()
            tm.ok(settings_result)
            tm.that(
                settings_result.value["max_workers"],
                eq=20,
            )
            tm.that(
                settings_result.value["enable_metrics"],
                eq=True,
            )
            tm.that(
                settings_result.value["services_initialized"],
                eq=True,
            )
            tm.that(
                Path(str(settings_result.value["temp_dir"])).exists(),
                eq=True,
            )

            database_result = create_database_config_from_cli()
            tm.ok(database_result)
            tm.that(
                database_result.value.port,
                eq=5433,
            )
            tm.that(
                database_result.value.ssl_enabled,
                eq=True,
            )
            tm.that(
                database_result.value.connection_pool,
                eq=20,
            )

    def test_pydantic_driven_example_surfaces_validation_and_connection_failures(
        self,
    ) -> None:
        """Pydantic-driven example must fail through its public railway steps when input is invalid."""
        missing_fields = validate_required_fields({"host": "db.example.com"})
        tm.fail(missing_fields)

        invalid_model = convert_and_validate_with_pydantic(
            et.Cli.JSON_MAPPING_ADAPTER.validate_python({
                "host": "db.example.com",
                "port": "bad-port",
                "name": "prod",
                "username": "user",
                "password": "secret",
                "ssl_enabled": True,
                "connection_pool": 10,
            })
        )
        tm.fail(invalid_model)

        base_config = convert_and_validate_with_pydantic(
            et.Cli.JSON_MAPPING_ADAPTER.validate_python({
                "host": "db.example.com",
                "port": 5432,
                "name": "prod",
                "username": "user",
                "password": "secret-pass",
                "ssl_enabled": False,
                "connection_pool": 10,
            })
        )
        tm.ok(base_config)

        oversized_localhost = base_config.value.model_copy(
            update={"host": "localhost", "connection_pool": 60},
        )
        business_rule_result = validate_business_rules(
            oversized_localhost,
        )
        tm.fail(business_rule_result)

        failing_connection = base_config.value.model_copy(
            update={"host": "fail-db.example.com"},
        )
        connection_result = perform_connection_test(
            failing_connection,
        )
        tm.fail(connection_result)


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
