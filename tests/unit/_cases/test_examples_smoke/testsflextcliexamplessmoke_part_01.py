"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from examples import ExamplesFlextCliGettingStarted
from examples.ex_02_output_formatting import export_report
from examples.ex_04_file_operations import (
    load_deployment_config,
    load_user_preferences,
    save_deployment_config,
    save_user_preferences,
    validate_and_import_data,
)
from flext_tests import tm
from tests import m

from flext_cli import cli

if TYPE_CHECKING:
    from pathlib import Path

# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): file fixtures are
# validated models, serialized once at egress and validated once at ingress.


class TestsFlextCliExamplesSmoke:
    """Implementation part for TestsFlextCliExamplesSmoke."""

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
        tm.that(execute_result.value["app_name"], eq=settings_result.value.app_name)

        report_rows = (
            m.Tests.ReportRow(id=1, name="Alice", status="active"),
            m.Tests.ReportRow(id=2, name="Bob", status="inactive"),
        )
        report_result = export_report(
            tuple(row.model_dump(mode="json") for row in report_rows)
        )
        tm.ok(report_result)
        tm.that(report_result.value, has="Alice")
        tm.that(report_result.value, has="Bob")

    def test_file_operation_examples(self, tmp_path: Path) -> None:
        """File-oriented examples must use cli file APIs successfully."""
        config_dir = tmp_path / "settings"
        config_dir.mkdir()
        preferences = m.Tests.UserPreferences(theme="dark", notifications=True)

        tm.that(
            save_user_preferences(preferences.model_dump(mode="json"), config_dir),
            eq=True,
        )

        preferences_result = load_user_preferences(config_dir)
        tm.ok(preferences_result)
        loaded_preferences = m.Tests.UserPreferences.model_validate(
            preferences_result.value.content
        )
        tm.that(loaded_preferences, eq=preferences)

        deployment_file = tmp_path / "deployment.yaml"
        deployment_config = m.Tests.DeploymentConfig(environment="dev", replicas=2)
        tm.that(
            save_deployment_config(
                deployment_config.model_dump(mode="json"), deployment_file
            ),
            eq=True,
        )

        deployment_result = load_deployment_config(deployment_file)
        tm.ok(deployment_result)
        loaded_deployment = m.Tests.DeploymentConfig.model_validate(
            deployment_result.value.content
        )
        tm.that(loaded_deployment, eq=deployment_config)

        import_file = tmp_path / "record.json"
        record = m.Tests.ImportRecord(id=1, name="Alice", value="ok")
        write_result = cli.write_json_file(import_file, record.model_dump(mode="json"))
        tm.ok(write_result)
        validation_result = validate_and_import_data(import_file)
        tm.ok(validation_result)
        loaded_record = m.Tests.ImportRecord.model_validate(
            validation_result.value.content
        )
        tm.that(loaded_record, eq=record)


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
