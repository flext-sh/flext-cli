"""Behavioral contract tests for services/auth.py (FlextCliAuth).

Exercises the public ``p.Cli.AuthService`` contract only: r[T] outcomes,
persisted-token roundtrips, generated-token invariants, and error paths.
The token file is isolated per test by pointing the canonical settings
singleton's ``cli_token_file`` at ``tmp_path`` and restoring the original
value afterwards — no shared/global state leaks between tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import settings
from flext_cli.services.auth import FlextCliAuth
from tests.constants import c

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from tests.protocols import p


class TestsFlextCliServicesAuthCov:
    """Behavioral tests for the FlextCliAuth authentication service."""

    @pytest.fixture
    def token_file(self, tmp_path: Path) -> Iterator[Path]:
        """Isolate the auth token file inside the test's tmp dir."""
        path = tmp_path / "auth_token.json"
        # NOTE (multi-agent): the auth service reads the module-level
        # ``settings`` object directly, so isolation must mutate that very
        # instance (update_global would only replace the class singleton,
        # which the service never re-reads); the original value is restored.
        original_token_file = settings.cli_token_file
        settings.cli_token_file = str(path)
        try:
            yield path
        finally:
            settings.cli_token_file = original_token_file

    @pytest.fixture
    def auth(self, token_file: Path) -> p.Cli.AuthService:
        """Fresh auth service bound to the isolated token file."""
        return FlextCliAuth()

    # ── validate_credentials ──────────────────────────────────────────

    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"),
        c.Tests.AUTH_CRED_CASES,
    )
    def test_validate_credentials_reports_success_per_case(
        self,
        auth: p.Cli.AuthService,
        username: str,
        password: str,
        expect_ok: bool,
    ) -> None:
        result = auth.validate_credentials(username, password)

        assert result.success is expect_ok
        if expect_ok:
            assert result.value is True
        else:
            assert result.error

    @pytest.mark.parametrize(
        ("username", "password", "message_fragment"),
        [
            ("", "secret", "Username"),
            ("   ", "secret", "Username"),
            ("admin", "", "Password"),
            ("admin", "   ", "Password"),
        ],
    )
    def test_validate_credentials_failure_names_the_missing_field(
        self,
        auth: p.Cli.AuthService,
        username: str,
        password: str,
        message_fragment: str,
    ) -> None:
        result = auth.validate_credentials(username, password)

        assert result.failure
        assert message_fragment in (result.error or "")

    # ── save_auth_token / fetch_auth_token roundtrip ──────────────────

    def test_save_then_fetch_returns_persisted_token(
        self,
        auth: p.Cli.AuthService,
    ) -> None:
        save_result = auth.save_auth_token("valid-token-abc123")

        assert save_result.success

        fetch_result = auth.fetch_auth_token()

        assert fetch_result.success
        assert fetch_result.value == "valid-token-abc123"

    def test_save_overwrites_previous_token(
        self,
        auth: p.Cli.AuthService,
    ) -> None:
        assert auth.save_auth_token("first-token").success
        assert auth.save_auth_token("second-token").success

        assert auth.fetch_auth_token().value == "second-token"

    @pytest.mark.parametrize("token", ["", "   ", "\t\n"])
    def test_save_auth_token_rejects_blank_token(
        self,
        auth: p.Cli.AuthService,
        token: str,
    ) -> None:
        result = auth.save_auth_token(token)

        assert result.failure
        assert "token" in (result.error or "").lower()

    def test_blank_save_does_not_create_token_file(
        self,
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        auth.save_auth_token("")

        assert not token_file.exists()

    def test_fetch_without_saved_token_fails(
        self,
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        assert not token_file.exists()

        result = auth.fetch_auth_token()

        assert result.failure
        assert result.error

    # ── authenticate ──────────────────────────────────────────────────

    def test_authenticate_with_direct_token_returns_and_persists_it(
        self,
        auth: p.Cli.AuthService,
    ) -> None:
        credentials = {c.Cli.DICT_KEY_AUTH_TOKEN: "direct-token-abc"}

        result = auth.authenticate(credentials)

        assert result.success
        assert result.value == "direct-token-abc"
        assert auth.fetch_auth_token().value == "direct-token-abc"

    def test_authenticate_with_valid_credentials_generates_persisted_token(
        self,
        auth: p.Cli.AuthService,
    ) -> None:
        credentials = {
            c.Cli.DICT_KEY_USERNAME: "admin",
            c.Cli.DICT_KEY_USER_SECRET: "password123",
        }

        result = auth.authenticate(credentials)

        assert result.success
        generated = result.value
        assert isinstance(generated, str)
        assert generated
        # The generated token is the one persisted and later fetchable.
        assert auth.fetch_auth_token().value == generated

    @pytest.mark.parametrize(
        "credentials",
        [
            {},
            {c.Cli.DICT_KEY_USERNAME: "", c.Cli.DICT_KEY_USER_SECRET: ""},
            {c.Cli.DICT_KEY_USERNAME: "admin", c.Cli.DICT_KEY_USER_SECRET: ""},
            {c.Cli.DICT_KEY_USERNAME: "   ", c.Cli.DICT_KEY_USER_SECRET: "pw"},
        ],
    )
    def test_authenticate_rejects_incomplete_credentials(
        self,
        auth: p.Cli.AuthService,
        credentials: dict[str, str],
    ) -> None:
        result = auth.authenticate(credentials)

        assert result.failure
        assert result.error

    def test_authenticate_failure_does_not_persist_token(
        self,
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        auth.authenticate({})

        assert not token_file.exists()

    # ── clear_auth_tokens ─────────────────────────────────────────────

    def test_clear_removes_persisted_token_file(
        self,
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        assert auth.save_auth_token("clear-me-token").success
        assert token_file.exists()

        result = auth.clear_auth_tokens()

        assert result.success
        assert not token_file.exists()

    def test_clear_is_idempotent_when_no_token_file(
        self,
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        assert not token_file.exists()

        first = auth.clear_auth_tokens()
        second = auth.clear_auth_tokens()

        assert first.success
        assert second.success

    def test_fetch_after_clear_fails(
        self,
        auth: p.Cli.AuthService,
    ) -> None:
        assert auth.save_auth_token("temp-token").success
        assert auth.clear_auth_tokens().success

        assert auth.fetch_auth_token().failure


__all__: list[str] = ["TestsFlextCliServicesAuthCov"]
