"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from examples import (
    Ex05Authentication,
    Ex06Settings,
    c as ec,
)
from flext_tests import tm

from flext_cli import cli


class TestsFlextCliExamplesSmoke:
    """Implementation part for TestsFlextCliExamplesSmoke."""

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


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
