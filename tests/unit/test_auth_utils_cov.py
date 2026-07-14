"""Behavioral tests for the ``u.Cli`` auth helpers.

Contract under test (``flext_cli._utilities.auth.FlextCliUtilitiesAuth``):
- ``auth_token_file_path`` — resolve a token file path, defaulting to the
  canonical ``~/.flext/auth_token.json`` when no usable path is supplied.
- ``auth_validate_credentials`` — return a successful ``r[bool]`` only when
  both username and password carry non-blank content.
- ``auth_extract_token`` — return the token string from a JSON mapping, failing
  for non-mappings and for payloads without a usable token.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests import c
from tests import u
from flext_tests import tm

from tests import t



class TestsFlextCliAuthUtilsCov:
    """Behavioral contract for the ``u.Cli`` authentication helpers."""

    # ── auth_token_file_path ──────────────────────────────────────────

    @staticmethod
    def _canonical_default() -> Path:
        return Path.home() / ".flext" / "auth_token.json"

    @pytest.mark.parametrize("token_file", [None, "", "   ", "\t\n"])
    def test_token_file_path_defaults_to_canonical_when_blank(
        self, token_file: str | None
    ) -> None:
        # Arrange / Act
        path = u.Cli.auth_token_file_path(token_file)

        # Assert — blank/absent input yields the documented default location
        tm.that(path, eq=self._canonical_default())

    @pytest.mark.parametrize(
        "token_file",
        ["/tmp/my_token.json", "relative/token.json", "/var/lib/flext/t.json"],
    )
    def test_token_file_path_honours_explicit_path(self, token_file: str) -> None:
        # Act
        path = u.Cli.auth_token_file_path(token_file)

        # Assert — a non-blank path is returned verbatim as a Path
        tm.that(path, eq=Path(token_file))

    def test_token_file_path_is_deterministic(self) -> None:
        # Invariant: same input always maps to the same path
        first = u.Cli.auth_token_file_path(None)
        second = u.Cli.auth_token_file_path(None)
        tm.that(first, eq=second)

    # ── auth_validate_credentials ─────────────────────────────────────

    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"), c.Tests.AUTH_CRED_CASES
    )
    def test_validate_credentials_success_reflects_non_blank_fields(
        self, username: str, password: str, expect_ok: bool
    ) -> None:
        # Act
        result = u.Cli.auth_validate_credentials(username, password)

        # Assert — success iff both fields are non-blank
        assert result.success is expect_ok
        assert result.failure is (not expect_ok)
        if expect_ok:
            tm.that(result.unwrap(), eq=True)

    def test_validate_credentials_reports_empty_username(self) -> None:
        result = u.Cli.auth_validate_credentials("", "secret123")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="Username")

    def test_validate_credentials_reports_empty_password(self) -> None:
        result = u.Cli.auth_validate_credentials("admin", "   ")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="Password")

    # ── auth_extract_token ────────────────────────────────────────────

    def test_extract_token_returns_token_from_mapping(self) -> None:
        # Arrange
        payload: dict[str, t.JsonValue] = {c.Cli.DICT_KEY_AUTH_TOKEN: "my-secret-token"}

        # Act
        result = u.Cli.auth_extract_token(payload)

        # Assert — the exact token value is delivered on success
        tm.ok(result)
        tm.that(result.unwrap(), eq="my-secret-token")

    @pytest.mark.parametrize(
        "payload", [{"user": "admin"}, {c.Cli.DICT_KEY_AUTH_TOKEN: ""}]
    )
    def test_extract_token_fails_when_no_usable_token(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Act
        result = u.Cli.auth_extract_token(payload)

        # Assert — missing or empty token is a typed failure, not a value
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error.lower(), has="token")

    @pytest.mark.parametrize("payload", ["not-a-mapping", ["token", "value"], 42, None])
    def test_extract_token_rejects_non_mapping_payload(
        self, payload: t.JsonValue
    ) -> None:
        # Act
        result = u.Cli.auth_extract_token(payload)

        # Assert — only mappings are accepted; anything else fails with mapping msg
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error.lower(), has="mapping")

    def test_extract_token_success_chains_through_map(self) -> None:
        # Behavioral: a successful result composes with r[T] combinators
        payload: dict[str, t.JsonValue] = {c.Cli.DICT_KEY_AUTH_TOKEN: "abc"}
        length = u.Cli.auth_extract_token(payload).map(len)
        tm.ok(length)
        tm.that(length.unwrap(), eq=3)


__all__: list[str] = ["TestsFlextCliAuthUtilsCov"]
