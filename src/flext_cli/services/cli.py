"""FLEXT CLI - Typer/Click Abstraction Layer.

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
from typing import ClassVar, Self

from flext_core import r

from flext_cli import (
    FlextCliFileTools,
    FlextCliServiceBase,
    c,
)


class FlextCliCli(FlextCliServiceBase):
    """Unified Typer/Click abstraction marker for the FLEXT CLI ecosystem.

    Container and logger are provided by FlextMixins via MRO.
    """

    _instance: ClassVar[Self | None] = None

    @classmethod
    def get_instance(cls) -> Self:
        """Return the shared CLI facade instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _get_token_file_path(cls) -> Path:
        """Resolve the auth token path from settings with a safe default."""
        settings = cls.get_instance().settings
        token_file = settings.token_file
        if isinstance(token_file, str) and token_file.strip():
            return Path(token_file)
        return Path.home() / ".flext" / "auth_token.json"

    @classmethod
    def validate_credentials(cls, username: str, password: str) -> r[bool]:
        """Validate direct username/password credentials."""
        if not username.strip():
            return r[bool].fail("Username cannot be empty")
        if not password.strip():
            return r[bool].fail("Password cannot be empty")
        return r[bool].ok(True)

    @classmethod
    def save_auth_token(cls, token: str) -> r[bool]:
        """Persist an authentication token using the public file facade."""
        if not token.strip():
            return r[bool].fail("Token cannot be empty")
        return FlextCliFileTools.write_json_file(
            cls._get_token_file_path(),
            {c.Cli.DictKeys.TOKEN: token},
        )

    @classmethod
    def get_auth_token(cls) -> r[str]:
        """Load the persisted authentication token from the configured token file."""
        read_result = FlextCliFileTools.read_json_file(cls._get_token_file_path())
        if read_result.is_failure:
            return r[str].fail(read_result.error or "Failed to load auth token")
        payload = read_result.value
        if not isinstance(payload, Mapping):
            return r[str].fail("Token file must contain a mapping")
        token_value = payload.get(c.Cli.DictKeys.TOKEN)
        if not isinstance(token_value, str) or not token_value:
            return r[str].fail("Token file does not contain a valid token")
        return r[str].ok(token_value)

    @classmethod
    def authenticate(cls, credentials: Mapping[str, str]) -> r[str]:
        """Authenticate with a token or username/password and persist the token."""
        token_value = credentials.get(c.Cli.DictKeys.TOKEN)
        if isinstance(token_value, str) and token_value:
            save_result = cls.save_auth_token(token_value)
            if save_result.is_failure:
                return r[str].fail(save_result.error or "Failed to save token")
            return r[str].ok(token_value)
        username = credentials.get(c.Cli.DictKeys.USERNAME, "")
        password = credentials.get(c.Cli.DictKeys.PASSWORD, "")
        validation_result = cls.validate_credentials(username, password)
        if validation_result.is_failure:
            return r[str].fail(validation_result.error or "Invalid credentials")
        generated_token = secrets.token_urlsafe(32)
        save_result = cls.save_auth_token(generated_token)
        if save_result.is_failure:
            return r[str].fail(save_result.error or "Failed to save token")
        return r[str].ok(generated_token)

    @classmethod
    def clear_auth_tokens(cls) -> r[bool]:
        """Delete the configured authentication token file if present."""
        token_file = cls._get_token_file_path()
        if not token_file.exists():
            return r[bool].ok(True)
        return FlextCliFileTools.delete_file(token_file)


__all__ = ["FlextCliCli"]
