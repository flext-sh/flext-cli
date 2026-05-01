"""Coverage tests for _utilities/auth.py.

Targets: auth_token_file_path, auth_validate_credentials, auth_extract_token.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from tests import c


class TestsFlextCliAuthUtilsCov:
    """Coverage tests for FlextCliUtilitiesAuth."""

    # ── auth_token_file_path ──────────────────────────────────────────

    def test_auth_token_file_path_none(self) -> None:
        from pathlib import Path

        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        path = FlextCliUtilitiesAuth.auth_token_file_path(None)
        assert isinstance(path, Path)
        assert ".flext" in str(path)

    def test_auth_token_file_path_empty(self) -> None:
        from pathlib import Path

        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        path = FlextCliUtilitiesAuth.auth_token_file_path("")
        assert isinstance(path, Path)
        assert ".flext" in str(path)

    def test_auth_token_file_path_whitespace(self) -> None:
        from pathlib import Path

        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        path = FlextCliUtilitiesAuth.auth_token_file_path("   ")
        assert isinstance(path, Path)
        assert ".flext" in str(path)

    def test_auth_token_file_path_custom(self) -> None:
        from pathlib import Path

        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        path = FlextCliUtilitiesAuth.auth_token_file_path("/tmp/my_token.json")
        assert isinstance(path, Path)
        assert str(path) == "/tmp/my_token.json"

    # ── auth_validate_credentials ─────────────────────────────────────

    @pytest.mark.parametrize(
        ("username", "password", "expect_ok"),
        c.Tests.AUTH_CRED_CASES,
    )
    def test_auth_validate_credentials_parametrized(
        self,
        username: str,
        password: str,
        expect_ok: bool,
    ) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        result = FlextCliUtilitiesAuth.auth_validate_credentials(username, password)
        assert result.success == expect_ok

    # ── auth_extract_token ────────────────────────────────────────────

    def test_auth_extract_token_valid(self) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        payload = {c.Cli.DICT_KEY_AUTH_TOKEN: "my-secret-token"}
        result = FlextCliUtilitiesAuth.auth_extract_token(payload)
        assert result.success
        assert result.value == "my-secret-token"

    def test_auth_extract_token_missing_key(self) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        result = FlextCliUtilitiesAuth.auth_extract_token({"user": "admin"})
        assert result.failure

    def test_auth_extract_token_empty_token(self) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        result = FlextCliUtilitiesAuth.auth_extract_token({
            c.Cli.DICT_KEY_AUTH_TOKEN: ""
        })
        assert result.failure

    def test_auth_extract_token_not_mapping(self) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        result = FlextCliUtilitiesAuth.auth_extract_token("not-a-mapping")
        assert result.failure

    def test_auth_extract_token_list(self) -> None:
        from flext_cli._utilities.auth import FlextCliUtilitiesAuth

        result = FlextCliUtilitiesAuth.auth_extract_token(["token", "value"])
        assert result.failure


__all__: list[str] = ["TestsFlextCliAuthUtilsCov"]
