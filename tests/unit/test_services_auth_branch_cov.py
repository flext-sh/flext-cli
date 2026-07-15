"""Behavioral tests for the public FlextCli authentication contract.

Exercises the observable behavior of ``authenticate`` / ``save_auth_token`` /
``fetch_auth_token`` / ``clear_auth_tokens`` / ``validate_credentials`` through
the public ``FlextCli`` facade only: return values, ``r[T]`` success/failure
outcomes, error messages, and persistence round-trips. No private attributes,
internal collaborators, or line-coverage pokes are touched.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import FlextCli, cli, settings
from tests import c

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class TestsFlextCliServicesAuth:
    """Public authentication behavior of the FlextCli facade."""

    @pytest.fixture
    def service(self) -> Iterator[FlextCli]:
        """Fresh facade whose global token_file is restored after each test."""
        instance = type(cli)()
        # NOTE (multi-agent): flat cli_* settings (§2.6) — the auth service
        # reads the module-level ``settings`` object, so isolation mutates
        # that instance's ``cli_token_file`` and restores it afterwards.
        original_token_file = settings.cli_token_file
        try:
            yield instance
        finally:
            settings.cli_token_file = original_token_file

    @staticmethod
    def _point_token_file(path: Path) -> None:
        settings.cli_token_file = str(path)

    def test_authenticate_with_token_persists_and_round_trips(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "token.json")

        # Act
        authenticated = service.authenticate({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"})

        # Assert: the supplied token is returned and reloadable verbatim.
        tm.that(tm.ok(authenticated), eq="token-123")
        tm.that(tm.ok(service.fetch_auth_token()), eq="token-123")

    def test_authenticate_with_username_password_returns_reloadable_token(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "token.json")

        # Act
        authenticated = service.authenticate({
            c.Cli.DICT_KEY_USERNAME: "user",
            c.Cli.DICT_KEY_USER_SECRET: "secret",
        })

        # Assert: a non-empty token is generated and persisted for reload.
        generated = tm.ok(authenticated)
        tm.that(generated, is_=str)
        assert generated
        tm.that(tm.ok(service.fetch_auth_token()), eq=generated)

    @pytest.mark.parametrize(
        "credentials",
        [
            pytest.param({"unrelated": "value"}, id="unknown-keys"),
            pytest.param(
                {c.Cli.DICT_KEY_AUTH_TOKEN: "tok", "extra": "x"},
                id="token-plus-unknown-key",
            ),
        ],
    )
    def test_authenticate_rejects_malformed_credentials_payload(
        self, service: FlextCli, tmp_path: Path, credentials: dict[str, str]
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "token.json")

        # Act
        result = service.authenticate(credentials)

        # Assert: a payload violating the credentials schema is the invalid
        # credentials contract error.
        tm.fail(result)
        tm.that(result.error, eq=c.Cli.ERR_INVALID_CREDENTIALS)

    @pytest.mark.parametrize(
        ("credentials", "missing_field"),
        [
            pytest.param({}, "username", id="empty-payload"),
            pytest.param(
                {c.Cli.DICT_KEY_USERNAME: "user"}, "password", id="username-only"
            ),
            pytest.param(
                {c.Cli.DICT_KEY_USER_SECRET: "secret"}, "username", id="secret-only"
            ),
        ],
    )
    def test_authenticate_reports_missing_credential_field(
        self,
        service: FlextCli,
        tmp_path: Path,
        credentials: dict[str, str],
        missing_field: str,
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "token.json")

        # Act
        result = service.authenticate(credentials)

        # Assert: an empty required field fails naming that field.
        tm.fail(result)
        tm.that((result.error or "").lower(), has=missing_field)
        tm.that((result.error or "").lower(), has="empty")

    @pytest.mark.parametrize(
        "credentials",
        [
            pytest.param({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"}, id="token"),
            pytest.param(
                {c.Cli.DICT_KEY_USERNAME: "user", c.Cli.DICT_KEY_USER_SECRET: "secret"},
                id="username-password",
            ),
        ],
    )
    def test_authenticate_fails_when_token_cannot_be_persisted(
        self, service: FlextCli, tmp_path: Path, credentials: dict[str, str]
    ) -> None:
        # Arrange: point token_file at a directory so the write cannot succeed.
        token_dir = tmp_path / "token-as-dir"
        token_dir.mkdir()
        self._point_token_file(token_dir)

        # Act
        result = service.authenticate(credentials)

        # Assert: persistence failure surfaces as a write error, not success.
        tm.fail(result)
        tm.that(result.error, has="json_write failed:")

    def test_save_auth_token_rejects_blank_token(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "token.json")

        # Act
        result = service.save_auth_token("   ")

        # Assert: blank token is rejected with an empty-field message.
        tm.fail(result)
        tm.that(result.error, has="token")
        tm.that(result.error, has="empty")

    def test_validate_credentials_rejects_empty_password(
        self, service: FlextCli
    ) -> None:
        # Act
        result = service.validate_credentials("user", "")

        # Assert
        tm.fail(result)
        tm.that((result.error or "").lower(), has="password")

    def test_fetch_auth_token_fails_when_file_missing(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "missing-token.json")

        # Act
        result = service.fetch_auth_token()

        # Assert
        tm.fail(result)
        tm.that((result.error or "").lower(), has="load")

    def test_fetch_auth_token_fails_when_path_is_directory(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        token_dir = tmp_path / "read-as-dir"
        token_dir.mkdir()
        self._point_token_file(token_dir)

        # Act
        result = service.fetch_auth_token()

        # Assert
        tm.fail(result)
        tm.that((result.error or "").lower(), has="load")

    def test_clear_auth_tokens_is_ok_when_file_missing(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange
        self._point_token_file(tmp_path / "missing-token.json")

        # Act
        result = service.clear_auth_tokens()

        # Assert
        tm.ok(result)
        tm.that(result.value, eq=True)

    def test_clear_auth_tokens_removes_persisted_token_and_is_idempotent(
        self, service: FlextCli, tmp_path: Path
    ) -> None:
        # Arrange: persist a token first.
        self._point_token_file(tmp_path / "token.json")
        tm.ok(service.authenticate({c.Cli.DICT_KEY_AUTH_TOKEN: "token-123"}))

        # Act: clearing removes the token so it can no longer be fetched.
        first_clear = service.clear_auth_tokens()
        fetch_after_clear = service.fetch_auth_token()
        second_clear = service.clear_auth_tokens()

        # Assert
        tm.ok(first_clear)
        tm.that(first_clear.value, eq=True)
        tm.fail(fetch_after_clear)
        tm.ok(second_clear)
        tm.that(second_clear.value, eq=True)


__all__: list[str] = ["TestsFlextCliServicesAuth"]
