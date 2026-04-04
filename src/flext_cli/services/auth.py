"""FLEXT CLI - Auth Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Typer/Click.
All CLI framework functionality is exposed through this unified interface.

Implementation: Uses Typer as the backend framework. Since Typer is built on Click,
it generates Click-compatible commands internally.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from pathlib import Path

from flext_cli import (
    FlextCliFileTools,
    FlextCliServiceBase,
    c,
    t,
)
from flext_core import r


class FlextCliAuth(FlextCliServiceBase):
    """Unified Typer/Click abstraction marker for the FLEXT CLI ecosystem.

    Container and logger are provided by FlextMixins via MRO.
    """

    def _get_token_file_path(self) -> Path:
        """Resolve the auth token path from settings with a safe default."""
        token_file = self.settings.token_file
        if isinstance(token_file, str) and token_file.strip():
            return Path(token_file)
        return Path.home() / ".flext" / "auth_token.json"

    def validate_credentials(self, username: str, password: str) -> r[bool]:
        """Validate direct username/password credentials."""
        if not username.strip():
            return r[bool].fail("Username cannot be empty")
        if not password.strip():
            return r[bool].fail("Password cannot be empty")
        return r.ok(True)

    def save_auth_token(self, token: str) -> r[bool]:
        """Persist an authentication token using the public file facade."""
        if not token.strip():
            return r[bool].fail("Token cannot be empty")
        return FlextCliFileTools.write_json_file(
            self._get_token_file_path(),
            {c.Cli.DictKeys.TOKEN: token},
        )

    def get_auth_token(self) -> r[str]:
        """Load the persisted authentication token from the configured token file."""
        read_result = FlextCliFileTools.read_json_file(self._get_token_file_path())
        if read_result.is_failure:
            return r[str].fail(read_result.error or "Failed to load auth token")
        payload = read_result.value
        if not isinstance(payload, Mapping):
            return r[str].fail("Token file must contain a mapping")
        token_value = payload.get(c.Cli.DictKeys.TOKEN)
        if not isinstance(token_value, str) or not token_value:
            return r[str].fail("Token file does not contain a valid token")
        return r.ok(token_value)

    def authenticate(self, credentials: t.StrMapping) -> r[str]:
        """Authenticate with a token or username/password and persist the token."""
        token_value = credentials.get(c.Cli.DictKeys.TOKEN)
        if isinstance(token_value, str) and token_value:
            save_result = self.save_auth_token(token_value)
            if save_result.is_failure:
                return r[str].fail(save_result.error or "Failed to save token")
            return r.ok(token_value)
        username = credentials.get(c.Cli.DictKeys.USERNAME, "")
        password = credentials.get(c.Cli.DictKeys.PASSWORD, "")
        validation_result = self.validate_credentials(username, password)
        if validation_result.is_failure:
            return r[str].fail(validation_result.error or "Invalid credentials")
        generated_token = secrets.token_urlsafe(32)
        save_result = self.save_auth_token(generated_token)
        if save_result.is_failure:
            return r[str].fail(save_result.error or "Failed to save token")
        return r.ok(generated_token)

    def clear_auth_tokens(self) -> r[bool]:
        """Delete the configured authentication token file if present."""
        token_file = self._get_token_file_path()
        if not token_file.exists():
            return r.ok(True)
        return FlextCliFileTools.delete_file(token_file)


__all__ = ["FlextCliAuth"]
