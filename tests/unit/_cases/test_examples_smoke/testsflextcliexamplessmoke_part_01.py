"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from examples import (
    ExamplesFlextCliGettingStarted,
)
from examples.ex_02_output_formatting import export_report
from examples.ex_04_file_operations import (
    load_deployment_config,
    load_user_preferences,
    save_deployment_config,
    save_user_preferences,
    validate_and_import_data,
)
from flext_tests import tm


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


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
