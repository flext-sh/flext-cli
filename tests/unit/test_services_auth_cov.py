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


import pytest

from flext_cli import settings
from flext_cli.services.auth import FlextCliAuth
from tests import c
from flext_tests import tm

from collections.abc import Iterator
from pathlib import Path

from tests import p


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
        tm.that(str(token_file), eq=settings.cli_token_file)
        return FlextCliAuth()

    # ── validate_credentials ──────────────────────────────────────────

    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"), c.Tests.AUTH_CRED_CASES
    )
    def test_validate_credentials_reports_success_per_case(
        self, auth: p.Cli.AuthService, username: str, password: str, *, expect_ok: bool
    ) -> None:
        """Verify that validate credentials reports success per case."""
        result = auth.validate_credentials(username, password)

        tm.that(result.success is expect_ok, eq=True)
        if expect_ok:
            tm.that(result.value, empty=False)
        else:
            tm.that(result.error, empty=False)

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
        """Verify that validate credentials failure names the missing field."""
        result = auth.validate_credentials(username, password)

        tm.fail(result)
        tm.that((result.error or ""), has=message_fragment)

    # ── save_auth_token / fetch_auth_token roundtrip ──────────────────

    def test_save_then_fetch_returns_persisted_token(
        self, auth: p.Cli.AuthService
    ) -> None:
        """Verify that save then fetch returns persisted token."""
        save_result = auth.save_auth_token("valid-token-abc123")

        tm.ok(save_result)

        fetch_result = auth.fetch_auth_token()

        tm.ok(fetch_result)
        tm.that(fetch_result.value, eq="valid-token-abc123")

    def test_save_overwrites_previous_token(self, auth: p.Cli.AuthService) -> None:
        """Verify that save overwrites previous token."""
        tm.ok(auth.save_auth_token("first-token"))
        tm.ok(auth.save_auth_token("second-token"))

        tm.that(auth.fetch_auth_token().value, eq="second-token")

    @pytest.mark.parametrize("token", ["", "   ", "\t\n"])
    def test_save_auth_token_rejects_blank_token(
        self, auth: p.Cli.AuthService, token: str
    ) -> None:
        """Verify that save auth token rejects blank token."""
        result = auth.save_auth_token(token)

        tm.fail(result)
        tm.that((result.error or "").lower(), has="token")

    def test_blank_save_does_not_create_token_file(
        self, auth: p.Cli.AuthService, token_file: Path
    ) -> None:
        """Verify that blank save does not create token file."""
        auth.save_auth_token("")

        tm.that(token_file.exists(), eq=False)

    def test_fetch_without_saved_token_fails(
        self, auth: p.Cli.AuthService, token_file: Path
    ) -> None:
        """Verify that fetch without saved token fails."""
        tm.that(token_file.exists(), eq=False)

        result = auth.fetch_auth_token()

        tm.fail(result)
        tm.that(result.error, empty=False)

    # ── authenticate ──────────────────────────────────────────────────

    def test_authenticate_with_direct_token_returns_and_persists_it(
        self, auth: p.Cli.AuthService
    ) -> None:
        """Verify that authenticate with direct token returns and persists it."""
        credentials = {c.Cli.DICT_KEY_AUTH_TOKEN: "direct-token-abc"}

        result = auth.authenticate(credentials)

        tm.ok(result)
        tm.that(result.value, eq="direct-token-abc")
        tm.that(auth.fetch_auth_token().value, eq="direct-token-abc")

    def test_authenticate_with_valid_credentials_generates_persisted_token(
        self, auth: p.Cli.AuthService
    ) -> None:
        """Verify that authenticate with valid credentials generates persisted token."""
        credentials = {
            c.Cli.DICT_KEY_USERNAME: "admin",
            c.Cli.DICT_KEY_USER_SECRET: "password123",
        }

        result = auth.authenticate(credentials)

        tm.ok(result)
        generated = result.value
        tm.that(generated, is_=str)
        tm.that(generated, empty=False)
        # The generated token is the one persisted and later fetchable.
        tm.that(auth.fetch_auth_token().value, eq=generated)

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
        self, auth: p.Cli.AuthService, credentials: dict[str, str]
    ) -> None:
        """Verify that authenticate rejects incomplete credentials."""
        result = auth.authenticate(credentials)

        tm.fail(result)
        tm.that(result.error, empty=False)

    def test_authenticate_failure_does_not_persist_token(
        self, auth: p.Cli.AuthService, token_file: Path
    ) -> None:
        """Verify that authenticate failure does not persist token."""
        auth.authenticate({})

        tm.that(token_file.exists(), eq=False)

    # ── clear_auth_tokens ─────────────────────────────────────────────

    def test_clear_removes_persisted_token_file(
        self, auth: p.Cli.AuthService, token_file: Path
    ) -> None:
        """Verify that clear removes persisted token file."""
        tm.ok(auth.save_auth_token("clear-me-token"))
        tm.that(token_file.exists(), eq=True)

        result = auth.clear_auth_tokens()

        tm.ok(result)
        tm.that(token_file.exists(), eq=False)

    def test_clear_is_idempotent_when_no_token_file(
        self, auth: p.Cli.AuthService, token_file: Path
    ) -> None:
        """Verify that clear is idempotent when no token file."""
        tm.that(token_file.exists(), eq=False)

        first = auth.clear_auth_tokens()
        second = auth.clear_auth_tokens()

        tm.ok(first)
        tm.ok(second)

    def test_fetch_after_clear_fails(self, auth: p.Cli.AuthService) -> None:
        """Verify that fetch after clear fails."""
        tm.ok(auth.save_auth_token("temp-token"))
        tm.ok(auth.clear_auth_tokens())

        tm.fail(auth.fetch_auth_token())


__all__: list[str] = ["TestsFlextCliServicesAuthCov"]
