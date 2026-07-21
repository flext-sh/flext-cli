"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from examples import DataManagerCLI
from flext_tests import r, tm

from flext_cli import cli
from tests import p


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

    def test_complete_integration_example_surfaces_prompt_and_runtime_failures(
        self, tmp_path: Path
    ) -> None:
        """Complete integration example must surface prompt and invalid-JSON failures through public APIs."""
        app = DataManagerCLI()

        invalid_json_file = tmp_path / "invalid-app-data.json"
        invalid_json_file.write_text("not json", encoding="utf-8")
        app.data_file = invalid_json_file
        invalid_load = app.load_data()
        tm.fail(invalid_load)

        def fail_prompt(
            _self: object, _message: str, default: str | None = None
        ) -> p.Result[str]:
            _ = default
            return r[str].fail("prompt failed")

        with patch.object(cli.__class__, "prompt", new=fail_prompt):
            first_prompt_failure = app.add_entry()
            tm.fail(first_prompt_failure)

            workflow_prompt_failure = app.run_workflow()
            tm.fail(workflow_prompt_failure)
            tm.that(workflow_prompt_failure.error, has="Add entry failed")

        prompt_calls: list[str] = []

        def fail_second_prompt(
            _self: object, _message: str, default: str | None = None
        ) -> p.Result[str]:
            if not prompt_calls:
                prompt_calls.append("first")
                return r[str].ok(default or "sample")
            return r[str].fail("prompt failed")

        with patch.object(cli.__class__, "prompt", new=fail_second_prompt):
            second_prompt_failure = app.add_entry()
        tm.fail(second_prompt_failure)

        def ok_prompt(
            _self: object, _message: str, default: str | None = None
        ) -> p.Result[str]:
            return r[str].ok(default or "sample")

        broken_parent = tmp_path / "workflow-parent"
        broken_parent.write_text("not-a-directory", encoding="utf-8")
        app.data_file = broken_parent / "workflow.json"
        with patch.object(cli.__class__, "prompt", new=ok_prompt):
            workflow_failure = app.run_workflow()
        tm.fail(workflow_failure)


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
