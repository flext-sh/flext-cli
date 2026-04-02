"""Smoke tests for flext-cli examples using the public cli singleton API."""

from __future__ import annotations

from pathlib import Path

from examples import (
    ex_01_getting_started as getting_started,
    ex_02_output_formatting as output_formatting,
    ex_04_file_operations as file_operations,
    ex_05_authentication as authentication,
    ex_06_configuration as configuration,
)
from flext_tests import tm

from flext_cli import FlextCliSettings, cli


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
        preferences = {
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
        deployment_config = {"environment": "dev", "replicas": 2}
        tm.that(
            file_operations.save_deployment_config(
                deployment_config,
                deployment_file,
            ),
            eq=True,
        )

        deployment_result = file_operations.load_deployment_config(deployment_file)
        tm.ok(deployment_result)
        tm.that(deployment_result.value.content["environment"], eq="dev")

        import_file = tmp_path / "record.json"
        import_file.write_text(
            '{"id": 1, "name": "Alice", "value": "ok"}',
            encoding="utf-8",
        )
        validation_result = file_operations.validate_and_import_data(import_file)
        tm.ok(validation_result)
        tm.that(validation_result.value.content["name"], eq="Alice")

    def test_authentication_and_configuration_examples(self, tmp_path: Path) -> None:
        """Auth and config examples must work through cli.settings and cli auth APIs."""
        cli.settings.token_file = str(tmp_path / "auth_token.json")

        settings = configuration.get_cli_settings()
        tm.that(settings, is_=FlextCliSettings)
        tm.that(settings.token_file, eq=cli.settings.token_file)

        tm.that(authentication.login_to_service("demo", "secret"), eq=True)

        token_result = authentication.get_saved_token()
        tm.ok(token_result)
        tm.that(len(token_result.value) >= 20, eq=True)
        tm.that(authentication.validate_current_token(), eq=True)

        locations = configuration.show_config_locations()
        tm.that(locations.data["Token Exists"], eq="Yes")

        profile_result = configuration.load_profile_config("development")
        tm.ok(profile_result)
        tm.that(profile_result.value.debug, eq=True)
        tm.that(profile_result.value.output_format, eq="table")

        authentication.logout()
        cleared_result = cli.get_auth_token()
        tm.fail(cleared_result)
