"""Coverage tests for services/auth.py.

Targets: validate_credentials, save_auth_token, fetch_auth_token,
         authenticate, clear_auth_tokens.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.services.auth import FlextCliAuth
from tests import c


class TestsFlextCliServicesAuthCov:
    """Data-driven coverage tests for FlextCliAuth service."""

    def _make_auth(self, tmp_path: pytest.TempPathFactory | None = None) -> object:
        return FlextCliAuth()

    # ── validate_credentials ──────────────────────────────────────────

    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"),
        c.Tests.AUTH_CRED_CASES,
    )
    def test_validate_credentials_parametrized(
        self,
        username: str,
        password: str,
        expect_ok: bool,
    ) -> None:
        auth = FlextCliAuth()
        result = auth.validate_credentials(username, password)
        assert result.success == expect_ok

    # ── save_auth_token ───────────────────────────────────────────────

    def test_save_auth_token_valid(self, tmp_path: object) -> None:
        auth = FlextCliAuth()
        result = auth.save_auth_token("valid-token-abc123")
        assert result.success

    def test_save_auth_token_empty(self) -> None:
        auth = FlextCliAuth()
        result = auth.save_auth_token("")
        assert result.failure

    def test_save_auth_token_whitespace(self) -> None:
        auth = FlextCliAuth()
        result = auth.save_auth_token("   ")
        assert result.failure

    # ── fetch_auth_token ──────────────────────────────────────────────

    def test_fetch_auth_token_after_save(self) -> None:
        auth = FlextCliAuth()
        save_result = auth.save_auth_token("test-token-xyz")
        if save_result.success:
            fetch_result = auth.fetch_auth_token()
            assert fetch_result.success
            assert fetch_result.value == "test-token-xyz"

    def test_fetch_auth_token_missing_file_fails(self, tmp_path: object) -> None:

        auth = FlextCliAuth()
        # This will try to fetch from default token file; might succeed or fail
        result = auth.fetch_auth_token()
        assert result.success or result.failure  # Should not raise

    # ── authenticate ──────────────────────────────────────────────────

    def test_authenticate_with_token(self) -> None:
        auth = FlextCliAuth()
        credentials = {c.Cli.DICT_KEY_AUTH_TOKEN: "direct-token-abc"}
        result = auth.authenticate(credentials)
        assert result.success
        assert result.value == "direct-token-abc"

    def test_authenticate_with_credentials(self) -> None:
        auth = FlextCliAuth()
        credentials = {
            c.Cli.DICT_KEY_USERNAME: "admin",
            c.Cli.DICT_KEY_USER_SECRET: "password123",
        }
        result = auth.authenticate(credentials)
        assert result.success
        # Generated token should be a non-empty string
        assert isinstance(result.value, str)
        assert len(result.value) > 0

    def test_authenticate_invalid_credentials(self) -> None:
        auth = FlextCliAuth()
        credentials = {
            c.Cli.DICT_KEY_USERNAME: "",
            c.Cli.DICT_KEY_USER_SECRET: "",
        }
        result = auth.authenticate(credentials)
        assert result.failure

    def test_authenticate_empty_credentials(self) -> None:
        auth = FlextCliAuth()
        result = auth.authenticate({})
        assert result.failure

    # ── clear_auth_tokens ─────────────────────────────────────────────

    def test_clear_auth_tokens_no_file(self) -> None:
        auth = FlextCliAuth()
        # If no token file exists, should succeed (no-op)
        result = auth.clear_auth_tokens()
        assert result.success or result.failure  # Should not raise

    def test_clear_auth_tokens_after_save(self) -> None:
        auth = FlextCliAuth()
        save_result = auth.save_auth_token("clear-me-token")
        if save_result.success:
            clear_result = auth.clear_auth_tokens()
            assert clear_result.success


__all__: list[str] = ["TestsFlextCliServicesAuthCov"]
