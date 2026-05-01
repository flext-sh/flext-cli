"""Branch coverage tests for flext_cli.services.auth."""

from __future__ import annotations

from pathlib import Path

from flext_cli.services.auth import FlextCliAuth
from tests import c


class TestsFlextCliServicesAuthBranchCov:
    """Exercise remaining FlextCliAuth branches through real behavior flows."""

    def test_authenticate_token_save_failure_returns_error(
        self, tmp_path: Path
    ) -> None:
        service = FlextCliAuth()
        old_token_file = service.settings.token_file
        token_dir = tmp_path / "token-dir"
        token_dir.mkdir()
        service.settings.token_file = str(token_dir)
        try:
            result = service.authenticate({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"})
        finally:
            service.settings.token_file = old_token_file
        assert result.failure
        assert "json_write:" in (result.error or "")

    def test_authenticate_generated_token_save_failure_returns_error(
        self,
        tmp_path: Path,
    ) -> None:
        service = FlextCliAuth()
        old_token_file = service.settings.token_file
        token_dir = tmp_path / "generated-token-dir"
        token_dir.mkdir()
        service.settings.token_file = str(token_dir)
        try:
            result = service.authenticate({
                c.Cli.DICT_KEY_USERNAME: "user",
                c.Cli.DICT_KEY_USER_SECRET: "secret",
            })
        finally:
            service.settings.token_file = old_token_file
        assert result.failure
        assert "json_write:" in (result.error or "")

    def test_clear_auth_tokens_missing_file_returns_ok(self, tmp_path: Path) -> None:
        service = FlextCliAuth()
        old_token_file = service.settings.token_file
        missing_path = tmp_path / "missing-token.json"
        service.settings.token_file = str(missing_path)
        try:
            result = service.clear_auth_tokens()
        finally:
            service.settings.token_file = old_token_file
        assert result.success
        assert result.value is True

    def test_fetch_auth_token_read_failure_from_directory(self, tmp_path: Path) -> None:
        service = FlextCliAuth()
        old_token_file = service.settings.token_file
        token_dir = tmp_path / "read-fail-dir"
        token_dir.mkdir()
        service.settings.token_file = str(token_dir)
        try:
            result = service.fetch_auth_token()
        finally:
            service.settings.token_file = old_token_file
        assert result.failure
        assert "load" in (result.error or "").lower()


__all__: list[str] = ["TestsFlextCliServicesAuthBranchCov"]
