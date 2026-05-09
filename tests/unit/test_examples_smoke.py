"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from unittest.mock import patch

import pytest
from examples import (
    DataManagerCLI,
    Ex05Authentication,
    Ex06Settings,
    ExamplesFlextCliGettingStarted,
    c as ec,
    p as ep,
    t as et,
)
from examples.ex_02_output_formatting import export_report
from examples.ex_04_file_operations import (
    load_deployment_config,
    load_user_preferences,
    save_deployment_config,
    save_user_preferences,
    validate_and_import_data,
)
from examples.ex_12_pydantic_driven_cli import (
    convert_and_validate_with_pydantic,
    create_database_config_from_cli,
    perform_connection_test,
    validate_business_rules,
    validate_required_fields,
)

from flext_cli import cli
from tests import r, tm


class TestsFlextCliExamplesSmoke:
    """Verify examples exercise the real public API paths."""

    def test_getting_started_and_output_examples(self) -> None:
        """Examples must round-trip settings data and format tables via cli."""
        example = ExamplesFlextCliGettingStarted()
        settings_result = example.build_example_settings()
        tm.ok(settings_result)

        roundtrip_result = example.persist_example_settings(settings_result.value)
        tm.ok(roundtrip_result)
        tm.that(
            roundtrip_result.value.content["app_name"],
            eq=settings_result.value.app_name,
        )

        execute_result = example.execute()
        tm.ok(execute_result)
        tm.that(
            execute_result.value["app_name"],
            eq=settings_result.value.app_name,
        )

        report_result = export_report(
            [
                {"id": 1, "name": "Alice", "status": "active"},
                {"id": 2, "name": "Bob", "status": "inactive"},
            ],
        )
        tm.ok(report_result)
        tm.that(
            report_result.value,
            has="Alice",
        )
        tm.that(
            report_result.value,
            has="Bob",
        )

    def test_file_operation_examples(self, tmp_path: Path) -> None:
        """File-oriented examples must use cli file APIs successfully."""
        config_dir = tmp_path / "settings"
        config_dir.mkdir()
        preferences = {
            "theme": "dark",
            "notifications": True,
        }

        tm.that(
            save_user_preferences(preferences, config_dir),
            eq=True,
        )

        preferences_result = load_user_preferences(config_dir)
        tm.ok(preferences_result)
        assert preferences_result.value.content == preferences

        deployment_file = tmp_path / "deployment.yaml"
        deployment_config = {
            "environment": "dev",
            "replicas": 2,
        }
        tm.that(
            save_deployment_config(
                deployment_config,
                deployment_file,
            ),
            eq=True,
        )

        deployment_result = load_deployment_config(deployment_file)
        tm.ok(deployment_result)
        assert isinstance(deployment_result.value.content, Mapping)
        tm.that(
            deployment_result.value.content["environment"],
            eq="dev",
        )

        import_file = tmp_path / "record.json"
        import_file.write_text(
            '{"id": 1, "name": "Alice", "value": "ok"}',
            encoding="utf-8",
        )
        validation_result = validate_and_import_data(import_file)
        tm.ok(validation_result)
        assert isinstance(validation_result.value.content, Mapping)
        tm.that(
            validation_result.value.content["name"],
            eq="Alice",
        )

    def test_file_operation_examples_surface_failure_paths(
        self,
        tmp_path: Path,
    ) -> None:
        """File examples must report invalid filesystem and payload failures."""
        broken_config_root = tmp_path / "broken-config-root"
        broken_config_root.write_text("not-a-directory", encoding="utf-8")
        tm.that(
            save_user_preferences(
                {"theme": "dark"},
                broken_config_root,
            ),
            eq=False,
        )

        missing_preferences = load_user_preferences(tmp_path / "missing-config")
        tm.fail(missing_preferences)

        invalid_preferences_dir = tmp_path / "invalid-preferences"
        invalid_preferences_dir.mkdir()
        (invalid_preferences_dir / "preferences.json").write_text(
            '["a", "b"]',
            encoding="utf-8",
        )
        invalid_preferences = load_user_preferences(
            invalid_preferences_dir,
        )
        tm.fail(invalid_preferences)

        invalid_deployment_file = tmp_path / "invalid-deployment.yaml"
        invalid_deployment_file.write_text("- bad\n- config\n", encoding="utf-8")
        invalid_deployment = load_deployment_config(
            invalid_deployment_file,
        )
        tm.fail(invalid_deployment)

        missing_import = validate_and_import_data(tmp_path / "missing-record.json")
        tm.fail(missing_import)

        incomplete_import_file = tmp_path / "incomplete-record.json"
        incomplete_import_file.write_text(
            '{"id": 1, "name": "Alice"}',
            encoding="utf-8",
        )
        incomplete_import = validate_and_import_data(
            incomplete_import_file,
        )
        tm.fail(incomplete_import)

    def test_authentication_and_settings_examples(self, tmp_path: Path) -> None:
        """Auth and settings examples must work through cli.settings and cli auth APIs."""
        cli.settings.update_global(
            Cli={"token_file": str(tmp_path / "auth_token.json")},
        )

        settings = Ex06Settings.show_cli_settings()
        tm.that(
            settings,
            is_=ep.Cli.Settings,
        )
        tm.that(
            settings.Cli.token_file,
            eq=cli.settings.Cli.token_file,
        )

        login_result = Ex05Authentication.login_to_service(
            "demo",
            "secret",
        )
        tm.ok(login_result)

        token_result = Ex05Authentication.fetch_saved_token()
        tm.ok(token_result)
        tm.that(
            len(token_result.value) >= 20,
            eq=True,
        )
        validation_result = Ex05Authentication.validate_current_token()
        tm.ok(validation_result)

        locations = Ex06Settings.show_settings_locations()
        assert isinstance(locations.data, Mapping)
        tm.that(
            locations.data["Token Exists"],
            eq="Yes",
        )

        profile_result = Ex06Settings.load_profile_settings(
            ec.DeploymentEnvironment.DEVELOPMENT,
        )
        tm.ok(profile_result)
        tm.that(
            profile_result.value.debug,
            eq=True,
        )
        tm.that(
            profile_result.value.Cli.output_format,
            eq=ec.Cli.OutputFormats.TABLE,
        )

        logout_result = Ex05Authentication.logout()
        tm.ok(logout_result)
        cleared_result = cli.fetch_auth_token()
        tm.fail(cleared_result)

    def test_authentication_example_surfaces_missing_invalid_and_failed_login(
        self,
        tmp_path: Path,
    ) -> None:
        """Authentication example must handle no-session, invalid-token, and bad-login cases."""
        token_path = tmp_path / "auth_token.json"
        cli.settings.update_global(Cli={"token_file": str(token_path)})

        missing_token = Ex05Authentication.fetch_saved_token()
        tm.fail(missing_token)
        missing_validation = Ex05Authentication.validate_current_token()
        tm.fail(missing_validation)

        missing_logout = Ex05Authentication.logout()
        tm.fail(missing_logout)

        invalid_login = Ex05Authentication.login_to_service("", "")
        tm.fail(invalid_login)

        short_token_result = cli.save_auth_token("short-token")
        tm.ok(short_token_result)
        short_validation = Ex05Authentication.validate_current_token()
        tm.fail(short_validation)

        broken_token_path = tmp_path / "token-dir"
        broken_token_path.mkdir()
        cli.settings.update_global(Cli={"token_file": str(broken_token_path)})
        directory_logout = Ex05Authentication.logout()
        tm.fail(directory_logout)
        tm.that(
            broken_token_path.exists(),
            eq=True,
        )

    def test_authentication_example_surfaces_logout_unlink_failure(
        self,
        tmp_path: Path,
    ) -> None:
        """Authentication example must keep going when token removal raises an OS error."""
        token_path = tmp_path / "auth_token.json"
        token_path.write_text(
            '{"auth_token": "token-value-1234567890"}',
            encoding="utf-8",
        )
        cli.settings.update_global(Cli={"token_file": str(token_path)})

        def fail_unlink(self: Path, missing_ok: bool = False) -> None:
            _ = missing_ok
            if self == token_path:
                error_message = "denied"
                raise PermissionError(error_message)
            unexpected_message = f"unexpected unlink target: {self}"
            raise AssertionError(unexpected_message)

        with patch.object(Path, "unlink", new=fail_unlink):
            logout_result = Ex05Authentication.logout()
        tm.fail(logout_result)
        tm.that(
            token_path.exists(),
            eq=True,
        )

    def test_settings_example_surfaces_profile_and_override_branches(
        self,
        tmp_path: Path,
    ) -> None:
        """Settings example must cover alternate profiles and environment override failures."""
        production_profile = Ex06Settings.load_profile_settings(
            ec.DeploymentEnvironment.PRODUCTION,
        )
        tm.ok(production_profile)
        tm.that(
            production_profile.value.Cli.output_format,
            eq=ec.Cli.OutputFormats.JSON,
        )

        testing_settings = Ex06Settings.apply_environment_overrides(
            {
                "max_workers": 8,
                "enable_metrics": True,
                "temp_dir": str(tmp_path / "testing-cache"),
            },
            ec.DeploymentEnvironment.TESTING,
        )
        tm.that(
            testing_settings["max_workers"],
            eq=1,
        )
        tm.that(
            testing_settings["enable_metrics"],
            eq=False,
        )

        with pytest.raises(TypeError):
            Ex06Settings.apply_environment_overrides(
                {
                    "max_workers": "bad",
                    "enable_metrics": False,
                },
                ec.DeploymentEnvironment.PRODUCTION,
            )

    def test_complete_integration_example_persists_validated_workflow_data(
        self,
        tmp_path: Path,
    ) -> None:
        """Complete integration example must persist and reload real workflow data."""
        app = DataManagerCLI()
        app.data_file = tmp_path / "app_data.json"

        workflow_result = app.run_workflow()
        tm.ok(workflow_result)
        tm.that(
            app.data_file.exists(),
            eq=True,
        )

        load_result = app.load_data()
        tm.ok(load_result)
        tm.that(
            load_result.value["sample_key"],
            eq="sample_value",
        )

    def test_complete_integration_example_surfaces_load_and_save_failures(
        self,
        tmp_path: Path,
    ) -> None:
        """Complete integration example must fail honestly for missing, invalid, and unwritable data files."""
        app = DataManagerCLI()

        app.data_file = tmp_path / "missing-app-data.json"
        missing_load = app.load_data()
        tm.fail(missing_load)

        invalid_data_file = tmp_path / "invalid-app-data.json"
        invalid_data_file.write_text('["bad", "payload"]', encoding="utf-8")
        app.data_file = invalid_data_file
        invalid_load = app.load_data()
        tm.fail(invalid_load)

        broken_parent = tmp_path / "broken-parent"
        broken_parent.write_text("not-a-directory", encoding="utf-8")
        app.data_file = broken_parent / "app-data.json"
        save_result = app.save_data({"key": "value"})
        tm.fail(save_result)

    def test_complete_integration_example_surfaces_prompt_and_runtime_failures(
        self,
        tmp_path: Path,
    ) -> None:
        """Complete integration example must surface prompt and invalid-JSON failures through public APIs."""
        app = DataManagerCLI()

        invalid_json_file = tmp_path / "invalid-app-data.json"
        invalid_json_file.write_text("not json", encoding="utf-8")
        app.data_file = invalid_json_file
        invalid_load = app.load_data()
        tm.fail(invalid_load)

        def fail_prompt(
            _self: object,
            _message: str,
            default: str | None = None,
        ) -> r[str]:
            _ = default
            return r[str].fail("prompt failed")

        with patch.object(cli.__class__, "prompt", new=fail_prompt):
            first_prompt_failure = app.add_entry()
            tm.fail(first_prompt_failure)

            workflow_prompt_failure = app.run_workflow()
            tm.fail(
                workflow_prompt_failure,
            )
            tm.that(
                workflow_prompt_failure.error,
                has="Add entry failed",
            )

        prompt_calls: list[str] = []

        def fail_second_prompt(
            _self: object,
            _message: str,
            default: str | None = None,
        ) -> r[str]:
            if not prompt_calls:
                prompt_calls.append("first")
                return r[str].ok(default or "sample")
            return r[str].fail("prompt failed")

        with patch.object(cli.__class__, "prompt", new=fail_second_prompt):
            second_prompt_failure = app.add_entry()
        tm.fail(second_prompt_failure)

        def ok_prompt(
            _self: object,
            _message: str,
            default: str | None = None,
        ) -> r[str]:
            return r[str].ok(default or "sample")

        broken_parent = tmp_path / "workflow-parent"
        broken_parent.write_text("not-a-directory", encoding="utf-8")
        app.data_file = broken_parent / "workflow.json"
        with patch.object(cli.__class__, "prompt", new=ok_prompt):
            workflow_failure = app.run_workflow()
        tm.fail(workflow_failure)

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
