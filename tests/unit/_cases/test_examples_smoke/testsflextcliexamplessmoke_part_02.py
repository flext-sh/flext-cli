"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import pytest
from examples import Ex05Authentication, Ex06Settings, c as ec, p as ep
from examples.ex_04_file_operations import (
    load_deployment_config,
    load_user_preferences,
    save_user_preferences,
    validate_and_import_data,
)

from flext_cli import cli, settings
from flext_tests import tm
from tests import c

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class TestsFlextCliExamplesSmoke:
    """Implementation part for TestsFlextCliExamplesSmoke."""

    @pytest.fixture(autouse=True)
    def _restore_token_file(self) -> Iterator[None]:
        """Restore the canonical token file setting after each example run."""
        original_token_file = settings.cli_token_file
        try:
            yield
        finally:
            settings.cli_token_file = original_token_file

    def test_file_operation_examples_surface_failure_paths(
        self, tmp_path: Path
    ) -> None:
        """File examples must report invalid filesystem and payload failures."""
        broken_config_root = tmp_path / "broken-config-root"
        broken_config_root.write_text("not-a-directory", encoding="utf-8")
        tm.that(save_user_preferences({"theme": "dark"}, broken_config_root), eq=False)

        missing_preferences = load_user_preferences(tmp_path / "missing-config")
        tm.fail(missing_preferences)

        invalid_preferences_dir = tmp_path / "invalid-preferences"
        invalid_preferences_dir.mkdir()
        (invalid_preferences_dir / "preferences.json").write_text(
            '["a", "b"]', encoding="utf-8"
        )
        invalid_preferences = load_user_preferences(invalid_preferences_dir)
        tm.fail(invalid_preferences)

        invalid_deployment_file = tmp_path / "invalid-deployment.yaml"
        invalid_deployment_file.write_text("- bad\n- config\n", encoding="utf-8")
        invalid_deployment = load_deployment_config(invalid_deployment_file)
        tm.fail(invalid_deployment)

        missing_import = validate_and_import_data(tmp_path / "missing-record.json")
        tm.fail(missing_import)

        incomplete_import_file = tmp_path / "incomplete-record.json"
        incomplete_import_file.write_text(
            '{"id": 1, "name": "Alice"}', encoding="utf-8"
        )
        incomplete_import = validate_and_import_data(incomplete_import_file)
        tm.fail(incomplete_import)

    def test_authentication_and_settings_examples(self, tmp_path: Path) -> None:
        """Auth and settings examples must work through settings and cli auth APIs."""
        settings.cli_token_file = str(tmp_path / "auth_token.json")

        shown_settings = Ex06Settings.show_cli_settings()
        tm.that(shown_settings, is_=ep.Cli.Settings)
        tm.that(shown_settings.cli_token_file, eq=settings.cli_token_file)

        login_result = Ex05Authentication.login_to_service("demo", "secret")
        tm.ok(login_result)

        token_result = Ex05Authentication.fetch_saved_token()
        tm.ok(token_result)
        tm.that(len(token_result.value) >= c.Tests.AUTH_TOKEN_MIN_LENGTH, eq=True)
        validation_result = Ex05Authentication.validate_current_token()
        tm.ok(validation_result)

        locations = Ex06Settings.show_settings_locations()
        tm.that(locations.data, is_=Mapping)
        tm.that(locations.data["Token Exists"], eq="Yes")

        profile_result = Ex06Settings.load_profile_settings(
            ec.DeploymentEnvironment.DEVELOPMENT
        )
        tm.ok(profile_result)
        tm.that(profile_result.value.debug, eq=True)
        tm.that(profile_result.value.cli_output_format, eq=ec.Cli.OutputFormats.TABLE)

        logout_result = Ex05Authentication.logout()
        tm.ok(logout_result)
        cleared_result = cli.fetch_auth_token()
        tm.fail(cleared_result)


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
