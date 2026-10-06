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
from flext_tests import tm

from flext_cli import settings
from flext_cli.services.auth import FlextCliAuth
from tests import c

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from tests import p, t


class TestsFlextCliServicesAuthCov:
    """Behavioral tests for the FlextCliAuth authentication service."""

    @staticmethod
    @pytest.fixture
    def token_file(tmp_path: Path) -> Iterator[Path]:
        """Isolate the auth token file inside the test's tmp dir.

        Yields:
            Each ``Path``.

        """
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

    @staticmethod
    @pytest.fixture
    def auth(token_file: Path) -> p.Cli.AuthService:
        """Fresh auth service bound to the isolated token file.

        Returns:
            The resulting ``p.Cli.AuthService``.

        """
        tm.that(str(token_file), eq=settings.cli_token_file)
        return FlextCliAuth()

    # ── validate_credentials ──────────────────────────────────────────

    @staticmethod
    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"),
        c.Tests.AUTH_CRED_CASES,
    )
    def test_validate_credentials_reports_success_per_case(
        auth: p.Cli.AuthService,
        username: str,
        password: str,
        *,
        expect_ok: bool,
    ) -> None:
        """Verify that validate credentials reports success per case."""
        result = auth.validate_credentials(username, password)

        tm.that(result.success is expect_ok, eq=True)
        if expect_ok:
            tm.that(result.value, empty=False)
        else:
            tm.that(result.error, empty=False)

    @staticmethod
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

    @staticmethod
    def test_save_then_fetch_returns_persisted_token(
        auth: p.Cli.AuthService,
    ) -> None:
        """Verify that save then fetch returns persisted token."""
        save_result = auth.save_auth_token("valid-token-abc123")

        tm.ok(save_result)

        fetch_result = auth.fetch_auth_token()

        tm.ok(fetch_result)
        tm.that(fetch_result.value, eq="valid-token-abc123")

    @staticmethod
    def test_save_overwrites_previous_token(auth: p.Cli.AuthService) -> None:
        """Verify that save overwrites previous token."""
        tm.ok(auth.save_auth_token("first-token"))
        tm.ok(auth.save_auth_token("second-token"))

        tm.that(auth.fetch_auth_token().value, eq="second-token")

    @staticmethod
    @pytest.mark.parametrize("token", ["", "   ", "\t\n"])
    def test_save_auth_token_rejects_blank_token(
        auth: p.Cli.AuthService,
        token: str,
    ) -> None:
        """Verify that save auth token rejects blank token."""
        result = auth.save_auth_token(token)

        tm.fail(result)
        tm.that((result.error or "").lower(), has="token")

    @staticmethod
    def test_blank_save_does_not_create_token_file(
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        """Verify that blank save does not create token file."""
        auth.save_auth_token("")

        tm.that(token_file.exists(), eq=False)

    @staticmethod
    def test_fetch_without_saved_token_fails(
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        """Verify that fetch without saved token fails."""
        tm.that(token_file.exists(), eq=False)

        result = auth.fetch_auth_token()

        tm.fail(result)
        tm.that(result.error, empty=False)

    # ── authenticate ──────────────────────────────────────────────────

    @staticmethod
    def test_authenticate_with_direct_token_returns_and_persists_it(
        auth: p.Cli.AuthService,
    ) -> None:
        """Verify that authenticate with direct token returns and persists it."""
        credentials = {c.Cli.DICT_KEY_TOKEN: "t" + "2" * 12}

        result = auth.authenticate(credentials)

        tm.ok(result)
        tm.that(result.value, eq="t" + "2" * 12)
        tm.that(auth.fetch_auth_token().value, eq="t" + "2" * 12)

    @staticmethod
    def test_authenticate_with_valid_credentials_generates_persisted_token(
        auth: p.Cli.AuthService,
    ) -> None:
        """Verify that authenticate with valid credentials generates persisted token."""
        credentials = {
            c.Cli.DICT_KEY_USERNAME: "admin",
            c.Cli.DICT_KEY_PASSWORD: f"pw-{len('admin')}-auth",
        }

        result = auth.authenticate(credentials)

        tm.ok(result)
        generated = result.value
        tm.that(generated, is_=str)
        tm.that(generated, empty=False)
        # The generated token is the one persisted and later fetchable.
        tm.that(auth.fetch_auth_token().value, eq=generated)

    @staticmethod
    @pytest.mark.parametrize(
        "credentials",
        [
            {},
            {c.Cli.DICT_KEY_USERNAME: "", c.Cli.DICT_KEY_PASSWORD: ""},
            {c.Cli.DICT_KEY_USERNAME: "admin", c.Cli.DICT_KEY_PASSWORD: ""},
            {c.Cli.DICT_KEY_USERNAME: "   ", c.Cli.DICT_KEY_PASSWORD: "pw"},
        ],
    )
    def test_authenticate_rejects_incomplete_credentials(
        auth: p.Cli.AuthService,
        credentials: t.MappingKV[str, str],
    ) -> None:
        """Verify that authenticate rejects incomplete credentials."""
        result = auth.authenticate(credentials)

        tm.fail(result)
        tm.that(result.error, empty=False)

    @staticmethod
    def test_authenticate_failure_does_not_persist_token(
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        """Verify that authenticate failure does not persist token."""
        auth.authenticate({})

        tm.that(token_file.exists(), eq=False)

    # ── clear_auth_tokens ─────────────────────────────────────────────

    @staticmethod
    def test_clear_removes_persisted_token_file(
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        """Verify that clear removes persisted token file."""
        tm.ok(auth.save_auth_token("clear-me-token"))
        tm.that(token_file.exists(), eq=True)

        result = auth.clear_auth_tokens()

        tm.ok(result)
        tm.that(token_file.exists(), eq=False)

    @staticmethod
    def test_clear_is_idempotent_when_no_token_file(
        auth: p.Cli.AuthService,
        token_file: Path,
    ) -> None:
        """Verify that clear is idempotent when no token file."""
        tm.that(token_file.exists(), eq=False)

        first = auth.clear_auth_tokens()
        second = auth.clear_auth_tokens()

        tm.ok(first)
        tm.ok(second)

    @staticmethod
    def test_fetch_after_clear_fails(auth: p.Cli.AuthService) -> None:
        """Verify that fetch after clear fails."""
        tm.ok(auth.save_auth_token("temp-token"))
        tm.ok(auth.clear_auth_tokens())

        tm.fail(auth.fetch_auth_token())
