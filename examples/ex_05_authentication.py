"""Authentication - Using flext-cli for Auth in YOUR CLI Application.

WHEN TO USE THIS:
- Building CLI tools that need authentication
- Managing API tokens and credentials
- Need to persist auth tokens securely
- Implementing login/logout functionality
- Building tools that call authenticated APIs

FLEXT-CLI PROVIDES:
- save_auth_token() - Save token to secure location
- fetch_auth_token() - Retrieve saved token
- validate_credentials() - Credential validation
- authenticate() - Full auth flow
- r error handling - No try/except needed

HOW TO USE IN YOUR CLI:
Add authentication to YOUR CLI tool using flext-cli's built-in auth functions

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import c, cli, u
from flext_core import p, r


class Ex05Authentication:
    """Public authentication example for flext-cli consumers."""

    @staticmethod
    def login_to_service(username: str, password: str) -> p.Result[bool]:
        """Login and save token in YOUR CLI application."""
        auth_result = cli.authenticate({
            "username": username,
            "password": password,
        })
        if auth_result.failure:
            cli.print(
                f"❌ Login failed: {auth_result.error}",
                style=c.Cli.MessageStyles.BOLD_RED,
            )
            return r[bool].fail(auth_result.error or "Login failed")
        token_file_path = u.Cli.auth_token_file_path(cli.settings.token_file)
        cli.print("✅ Login successful!", style=c.Cli.MessageStyles.GREEN)
        cli.print(
            f"   Token saved to: {token_file_path}",
            style=c.Cli.MessageStyles.CYAN,
        )
        return r[bool].ok(True)

    @staticmethod
    def fetch_saved_token() -> p.Result[str]:
        """Retrieve saved auth token in YOUR CLI."""
        token_result = cli.fetch_auth_token()
        if token_result.failure:
            cli.print(
                f"⚠️  Not authenticated: {token_result.error}",
                style=c.Cli.MessageStyles.YELLOW,
            )
            return r[str].fail(token_result.error or "Not authenticated")
        return r[str].ok(token_result.value)

    @staticmethod
    def validate_current_token() -> p.Result[bool]:
        """Validate the saved token and return the explicit outcome."""
        token_result = cli.fetch_auth_token()
        if token_result.failure:
            cli.print("⚠️  No token found", style=c.Cli.MessageStyles.YELLOW)
            return r[bool].fail(token_result.error or "No token found")
        token = token_result.value
        if len(token) < 20:
            cli.print("❌ Invalid token format", style=c.Cli.MessageStyles.BOLD_RED)
            return r[bool].fail("Invalid token format")
        token_file_path = u.Cli.auth_token_file_path(cli.settings.token_file)
        cli.print("✅ Token is valid", style=c.Cli.MessageStyles.GREEN)
        cli.print(f"   Token: {token[:30]}...", style=c.Cli.MessageStyles.CYAN)
        cli.print(
            f"   Token file: {token_file_path}",
            style=c.Cli.MessageStyles.CYAN,
        )
        return r[bool].ok(True)

    @staticmethod
    def logout() -> p.Result[bool]:
        """Logout and clear the saved token if a session exists."""
        token_file_path = u.Cli.auth_token_file_path(cli.settings.token_file)
        if not token_file_path.exists():
            cli.print("⚠️  No active session", style=c.Cli.MessageStyles.YELLOW)
            return r[bool].fail("No active session")
        try:
            token_file_path.unlink()
        except OSError as exc:
            cli.print(
                f"❌ Logout failed: {exc}",
                style=c.Cli.MessageStyles.BOLD_RED,
            )
            return r[bool].fail(str(exc))
        cli.print("✅ Logged out successfully", style=c.Cli.MessageStyles.GREEN)
        cli.print(
            f"   Token removed from: {token_file_path}",
            style=c.Cli.MessageStyles.CYAN,
        )
        return r[bool].ok(True)
