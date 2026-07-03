"""Branch coverage tests for flext_cli.services.auth."""

from __future__ import annotations

from pathlib import Path

from flext_tests import tm

from flext_cli import cli
from tests.constants import c


class TestsFlextCliServicesAuthBranchCov:
    """Exercise remaining FlextCliAuth branches through real behavior flows."""

    def test_authenticate_token_save_failure_returns_error(
        self, tmp_path: Path
    ) -> None:
        service = type(cli)()
        old_token_file = service.settings.Cli.token_file
        token_dir = tmp_path / "token-dir"
        token_dir.mkdir()
        service.settings.update_global(Cli={"token_file": str(token_dir)})
        try:
            result = service.authenticate({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"})
        finally:
            service.settings.update_global(Cli={"token_file": old_token_file})
        tm.fail(result)
        tm.that(result.error, has="json_write:")

    def test_authenticate_generated_token_save_failure_returns_error(
        self,
        tmp_path: Path,
    ) -> None:
        service = type(cli)()
        old_token_file = service.settings.Cli.token_file
        token_dir = tmp_path / "generated-token-dir"
        token_dir.mkdir()
        service.settings.update_global(Cli={"token_file": str(token_dir)})
        try:
            result = service.authenticate({
                c.Cli.DICT_KEY_USERNAME: "user",
                c.Cli.DICT_KEY_USER_SECRET: "secret",
            })
        finally:
            service.settings.update_global(Cli={"token_file": old_token_file})
        tm.fail(result)
        tm.that(result.error, has="json_write:")

    def test_clear_auth_tokens_missing_file_returns_ok(self, tmp_path: Path) -> None:
        service = type(cli)()
        old_token_file = service.settings.Cli.token_file
        missing_path = tmp_path / "missing-token.json"
        service.settings.update_global(Cli={"token_file": str(missing_path)})
        try:
            result = service.clear_auth_tokens()
        finally:
            service.settings.update_global(Cli={"token_file": old_token_file})
        tm.ok(result)
        tm.that(result.value, eq=True)

    def test_fetch_auth_token_read_failure_from_directory(self, tmp_path: Path) -> None:
        service = type(cli)()
        old_token_file = service.settings.Cli.token_file
        token_dir = tmp_path / "read-fail-dir"
        token_dir.mkdir()
        service.settings.update_global(Cli={"token_file": str(token_dir)})
        try:
            result = service.fetch_auth_token()
        finally:
            service.settings.update_global(Cli={"token_file": old_token_file})
        tm.fail(result)
        tm.that((result.error or "").lower(), has="load")


__all__: list[str] = ["TestsFlextCliServicesAuthBranchCov"]
