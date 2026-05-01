"""Branch coverage tests for flext_cli.services.auth."""

from __future__ import annotations

from pathlib import Path

import pytest

import flext_cli.services.auth as auth_service_module
from flext_cli.services.auth import FlextCliAuth
from flext_core import r
from tests import c, t


class TestsFlextCliServicesAuthBranchCov:
    """Exercise remaining FlextCliAuth branches."""

    def test_authenticate_token_save_failure_returns_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = FlextCliAuth()
        monkeypatch.setattr(
            FlextCliAuth,
            "save_auth_token",
            lambda self, token: r[bool].fail("cannot-save"),
        )
        result = service.authenticate({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"})
        assert result.failure
        assert result.error == "cannot-save"

    def test_authenticate_generated_token_save_failure_returns_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = FlextCliAuth()
        monkeypatch.setattr(
            FlextCliAuth,
            "validate_credentials",
            lambda self, username, password: r[bool].ok(True),
        )
        monkeypatch.setattr(
            auth_service_module.secrets, "token_urlsafe", lambda size: "generated-token"
        )
        monkeypatch.setattr(
            FlextCliAuth,
            "save_auth_token",
            lambda self, token: r[bool].fail("cannot-save"),
        )
        result = service.authenticate({
            c.Cli.DICT_KEY_USERNAME: "user",
            c.Cli.DICT_KEY_USER_SECRET: "secret",
        })
        assert result.failure
        assert result.error == "cannot-save"

    def test_clear_auth_tokens_missing_file_returns_ok(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = FlextCliAuth()
        missing_path = Path("/tmp/flext-missing-token.json")
        monkeypatch.setattr(
            auth_service_module.u.Cli,
            "auth_token_file_path",
            lambda token_file: missing_path,
        )
        result = service.clear_auth_tokens()
        assert result.success
        assert result.value is True

    def test_fetch_auth_token_read_failure_without_error_uses_fallback(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = FlextCliAuth()
        token_path = Path("/tmp/flext-token.json")
        monkeypatch.setattr(
            auth_service_module.u.Cli,
            "auth_token_file_path",
            lambda token_file: token_path,
        )
        monkeypatch.setattr(
            auth_service_module.FlextCliFileTools,
            "read_json_file",
            lambda path: r[t.JsonMapping].fail(""),
        )
        result = service.fetch_auth_token()
        assert result.failure
        assert result.error == "Failed to load auth token"


__all__: list[str] = ["TestsFlextCliServicesAuthBranchCov"]
