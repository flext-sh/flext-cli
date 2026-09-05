"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from examples import DataManagerCLI

from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliExamplesSmoke:
    """Implementation part for TestsFlextCliExamplesSmoke."""

    def test_complete_integration_example_persists_validated_workflow_data(
        self, tmp_path: Path
    ) -> None:
        """Complete integration example must persist and reload real workflow data."""
        app = DataManagerCLI()
        app.data_file = tmp_path / "app_data.json"

        workflow_result = app.run_workflow()
        tm.ok(workflow_result)
        tm.that(app.data_file.exists(), eq=True)

        load_result = app.load_data()
        tm.ok(load_result)
        tm.that(load_result.value["sample_key"], eq="sample_value")

    def test_complete_integration_example_surfaces_load_and_save_failures(
        self, tmp_path: Path
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

    def test_complete_integration_example_surfaces_runtime_failures(
        self, tmp_path: Path
    ) -> None:
        """Complete integration surfaces invalid JSON and publication failures."""
        app = DataManagerCLI()

        invalid_json_file = tmp_path / "invalid-app-data.json"
        invalid_json_file.write_text("not json", encoding="utf-8")
        app.data_file = invalid_json_file
        invalid_load = app.load_data()
        tm.fail(invalid_load)

        broken_parent = tmp_path / "workflow-parent"
        broken_parent.write_text("not-a-directory", encoding="utf-8")
        app.data_file = broken_parent / "workflow.json"
        workflow_failure = app.run_workflow()
        tm.fail(workflow_failure)


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
