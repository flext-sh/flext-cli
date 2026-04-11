"""Smoke tests for flext-cli examples using the public cli singleton API."""

from __future__ import annotations

import os
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path

import examples.ex_01_getting_started as getting_started
import examples.ex_02_output_formatting as output_formatting
import examples.ex_04_file_operations as file_operations
import examples.ex_05_authentication as authentication
import examples.ex_06_configuration as configuration
import examples.ex_10_testing_utilities as testing_utilities
import examples.ex_11_complete_integration as complete_integration
import examples.ex_12_pydantic_driven_cli as pydantic_driven
from flext_tests import tm

from flext_cli import FlextCliSettings, cli
from tests import c, t


@contextmanager
def _temporary_environment(
    overrides: Mapping[str, str],
) -> Generator[None]:
    original_values = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class TestFlextCliExamplesSmoke:
    """Verify examples exercise the real public API paths."""

    def test_getting_started_and_output_examples(self, tmp_path: Path) -> None:
        """Examples must round-trip config data and format tables via cli."""
        example = getting_started.FlextCliGettingStarted()
        config_path = tmp_path / "config.json"
        config = getting_started.m.Cli.LoadedConfig(
            content={"theme": "dark", "retries": 3},
        )

        tm.that(example.save_config(config, str(config_path)), eq=True)

        load_result = example.load_config(str(config_path))
        tm.ok(load_result)
        tm.that(load_result.value.content, eq=config.content)

        example.display_user_data(
            getting_started.m.Cli.DisplayData(
                data={"name": "Alice", "role": "admin"},
            ),
        )

        report_result = output_formatting.export_report(
            [
                {"id": 1, "name": "Alice", "status": "active"},
                {"id": 2, "name": "Bob", "status": "inactive"},
            ],
        )
        tm.ok(report_result)
        tm.that(report_result.value, has="Alice")
        tm.that(report_result.value, has="Bob")

    def test_file_operation_examples(self, tmp_path: Path) -> None:
        """File-oriented examples must use cli file APIs successfully."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        preferences: t.ContainerMapping = {
            "theme": "dark",
            "notifications": True,
        }

        tm.that(
            file_operations.save_user_preferences(preferences, config_dir),
            eq=True,
        )

        preferences_result = file_operations.load_user_preferences(config_dir)
        tm.ok(preferences_result)
        assert preferences_result.value.content == preferences

        deployment_file = tmp_path / "deployment.yaml"
        deployment_config: t.ContainerMapping = {
            "environment": "dev",
            "replicas": 2,
        }
        tm.that(
            file_operations.save_deployment_config(
                deployment_config,
                deployment_file,
            ),
            eq=True,
        )

        deployment_result = file_operations.load_deployment_config(deployment_file)
        tm.ok(deployment_result)
        assert isinstance(deployment_result.value.content, Mapping)
        tm.that(deployment_result.value.content["environment"], eq="dev")

        import_file = tmp_path / "record.json"
        import_file.write_text(
            '{"id": 1, "name": "Alice", "value": "ok"}',
            encoding="utf-8",
        )
        validation_result = file_operations.validate_and_import_data(import_file)
        tm.ok(validation_result)
        assert isinstance(validation_result.value.content, Mapping)
        tm.that(validation_result.value.content["name"], eq="Alice")

    def test_authentication_and_configuration_examples(self, tmp_path: Path) -> None:
        """Auth and config examples must work through cli.settings and cli auth APIs."""
        cli.settings.token_file = str(tmp_path / "auth_token.json")

        settings = configuration.show_cli_settings()
        tm.that(settings, is_=FlextCliSettings)
        tm.that(settings.token_file, eq=cli.settings.token_file)

        tm.that(authentication.login_to_service("demo", "secret"), eq=True)

        token_result = authentication.fetch_saved_token()
        tm.ok(token_result)
        tm.that(len(token_result.value) >= 20, eq=True)
        tm.that(authentication.validate_current_token(), eq=True)

        locations = configuration.show_config_locations()
        assert isinstance(locations.data, Mapping)
        tm.that(locations.data["Token Exists"], eq="Yes")

        profile_result = configuration.load_profile_config("development")
        tm.ok(profile_result)
        tm.that(profile_result.value.debug, eq=True)
        tm.that(profile_result.value.output_format, eq=c.Cli.OutputFormats.TABLE)

        authentication.logout()
        cleared_result = cli.fetch_auth_token()
        tm.fail(cleared_result)

    def test_testing_utility_examples_run_real_cli_workflows(
        self,
        tmp_path: Path,
    ) -> None:
        """Testing examples must validate real CLI file and workflow behavior."""
        command_result = testing_utilities.my_cli_command("World")
        tm.ok(command_result)
        tm.that(command_result.value, eq="Hello, World!")

        save_result = testing_utilities.save_config_command(
            {"feature": "examples", "enabled": True},
            base_dir=tmp_path,
        )
        tm.ok(save_result)

        saved_config = cli.read_json_file(tmp_path / "test_config.json")
        tm.ok(saved_config)
        assert isinstance(saved_config.value, Mapping)
        tm.that(saved_config.value["feature"], eq="examples")
        tm.that(saved_config.value["enabled"], eq=True)

        workflow_result = testing_utilities.full_workflow_command(base_dir=tmp_path)
        tm.ok(workflow_result)
        tm.that(workflow_result.value["status"], eq="completed")
        tm.that(workflow_result.value["processed"], eq=True)
        tm.that((tmp_path / "workflow_test.json").exists(), eq=False)

    def test_complete_integration_example_persists_validated_workflow_data(
        self,
        tmp_path: Path,
    ) -> None:
        """Complete integration example must persist and reload real workflow data."""
        app = complete_integration.DataManagerCLI()
        app.data_file = tmp_path / "app_data.json"

        workflow_result = app.run_workflow()
        tm.ok(workflow_result)
        tm.that(app.data_file.exists(), eq=True)

        load_result = app.load_data()
        tm.ok(load_result)
        tm.that(load_result.value["sample_key"], eq="sample_value")

    def test_configuration_and_pydantic_examples_validate_production_flow(
        self,
        tmp_path: Path,
    ) -> None:
        """Configuration examples must honor env overrides and typed workflow rules."""
        cache_dir = tmp_path / "cache"
        with _temporary_environment({
            "ENVIRONMENT": "production",
            "API_KEY": "prod-secret",
            "MAX_WORKERS": "25",
            "TEMP_DIR": str(cache_dir),
        }):
            config_result = configuration.load_application_config()
            tm.ok(config_result)
            tm.that(config_result.value["max_workers"], eq=20)
            tm.that(config_result.value["enable_metrics"], eq=True)
            tm.that(config_result.value["services_initialized"], eq=True)
            tm.that(Path(str(config_result.value["temp_dir"])).exists(), eq=True)

            database_result = pydantic_driven.create_database_config_from_cli()
            tm.ok(database_result)
            tm.that(database_result.value.port, eq=5433)
            tm.that(database_result.value.ssl_enabled, eq=True)
            tm.that(database_result.value.connection_pool, eq=20)
