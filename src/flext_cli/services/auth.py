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

from flext_cli import (
    FlextCliFileTools,
    FlextCliServiceBase,
    c,
    m,
    p,
    r,
    t,
    u,
)


class FlextCliAuth(FlextCliServiceBase):
    """Unified Typer/Click abstraction marker for the FLEXT CLI ecosystem.

    Container and logger are provided by x via MRO.
    """

    def validate_credentials(self, username: str, password: str) -> p.Result[bool]:
        """Validate direct username/password credentials."""
        return u.Cli.auth_validate_credentials(username, password)

    def save_auth_token(self, token: str) -> p.Result[bool]:
        """Persist an authentication token using the public file facade."""
        if not token.strip():
            return r[bool].fail(
                c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(
                    field_name="token",
                ),
            )
        settings = self.settings
        token_file_path = u.Cli.auth_token_file_path(settings.token_file)
        return FlextCliFileTools.write_json_file(
            token_file_path,
            {c.Cli.DICT_KEY_AUTH_TOKEN: token},
        )

    def fetch_auth_token(self) -> p.Result[str]:
        """Load the persisted authentication token from the configured token file."""
        token_file_path = u.Cli.auth_token_file_path(self.settings.token_file)
        read_result = FlextCliFileTools.read_json_file(token_file_path)
        if read_result.failure:
            return r[str].fail(
                read_result.error
                or c.Cli.ERR_AUTH_LOAD_FAILED.format(error=c.Cli.ERR_UNKNOWN_ERROR),
            )
        return u.Cli.auth_extract_token(read_result.value)

    def authenticate(self, credentials: t.StrMapping) -> p.Result[str]:
        """Authenticate with a token or username/password and persist the token."""
        result: p.Result[str] | None = None
        try:
            credentials_payload = m.Cli.AuthCredentialsPayload.model_validate(
                credentials,
            )
        except c.ValidationError:
            result = r[str].fail(c.Cli.ERR_INVALID_CREDENTIALS)
        else:
            token_to_save = credentials_payload.token
            if not token_to_save:
                validation_result = self.validate_credentials(
                    credentials_payload.username,
                    credentials_payload.password,
                )
                if validation_result.failure:
                    result = r[str].fail(
                        validation_result.error or c.Cli.ERR_INVALID_CREDENTIALS,
                    )
                else:
                    token_to_save = secrets.token_urlsafe(32)
            if result is None and token_to_save:
                save_result = self.save_auth_token(token_to_save)
                result = (
                    r[str].fail(
                        save_result.error
                        or c.Cli.ERR_AUTH_SAVE_FAILED.format(
                            error=c.Cli.ERR_UNKNOWN_ERROR,
                        ),
                    )
                    if save_result.failure
                    else r[str].ok(token_to_save)
                )
        if result is None:
            result = r[str].fail(c.Cli.ERR_INVALID_CREDENTIALS)
        return result

    def clear_auth_tokens(self) -> p.Result[bool]:
        """Delete the configured authentication token file if present."""
        token_file = u.Cli.auth_token_file_path(self.settings.token_file)
        if not token_file.exists():
            return r[bool].ok(True)
        return u.Cli.files_delete(token_file)


__all__: t.MutableSequenceOf[str] = ["FlextCliAuth"]
