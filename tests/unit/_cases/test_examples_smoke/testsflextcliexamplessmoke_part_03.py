"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from examples import Ex05Authentication, Ex06Settings, c as ec
from flext_tests import tm

from flext_cli import cli, settings


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

    def test_authentication_example_surfaces_missing_invalid_and_failed_login(
        self, tmp_path: Path
    ) -> None:
        """Authentication example must handle no-session, invalid-token, and bad-login cases."""
        token_path = tmp_path / "auth_token.json"
        settings.cli_token_file = str(token_path)

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
        settings.cli_token_file = str(broken_token_path)
        directory_logout = Ex05Authentication.logout()
        tm.fail(directory_logout)
        tm.that(broken_token_path.exists(), eq=True)

    def test_authentication_example_surfaces_logout_unlink_failure(
        self, tmp_path: Path
    ) -> None:
        """Authentication example must keep going when token removal raises an OS error."""
        token_dir = tmp_path / "locked-token-dir"
        token_dir.mkdir()
        token_path = token_dir / "auth_token.json"
        token_path.write_text(
            '{"auth_token": "token-value-1234567890"}', encoding="utf-8"
        )
        settings.cli_token_file = str(token_path)

        # NOTE (multi-agent): real OS-level failure, no patching — a read-only
        # directory makes ``unlink`` raise PermissionError through the public
        # logout flow; permissions are restored for tmp_path cleanup.
        token_dir.chmod(0o555)
        try:
            logout_result = Ex05Authentication.logout()
        finally:
            token_dir.chmod(0o755)
        tm.fail(logout_result)
        tm.that(token_path.exists(), eq=True)

    def test_settings_example_surfaces_profile_and_override_branches(
        self, tmp_path: Path
    ) -> None:
        """Settings example must cover alternate profiles and environment override failures."""
        production_profile = Ex06Settings.load_profile_settings(
            ec.DeploymentEnvironment.PRODUCTION
        )
        tm.ok(production_profile)
        tm.that(
            production_profile.value.cli_output_format, eq=ec.Cli.OutputFormats.JSON
        )

        testing_settings = Ex06Settings.apply_environment_overrides(
            {
                "max_workers": 8,
                "enable_metrics": True,
                "temp_dir": str(tmp_path / "testing-cache"),
            },
            ec.DeploymentEnvironment.TESTING,
        )
        tm.that(testing_settings["max_workers"], eq=1)
        tm.that(testing_settings["enable_metrics"], eq=False)

        with pytest.raises(TypeError):
            Ex06Settings.apply_environment_overrides(
                {"max_workers": "bad", "enable_metrics": False},
                ec.DeploymentEnvironment.PRODUCTION,
            )


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
