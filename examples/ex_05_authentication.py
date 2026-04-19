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

import os
import secrets
import time
from pathlib import Path

from examples import c, m, t
from flext_cli import cli
from flext_core import p, r


def login_to_service(username: str, password: str) -> bool:
    """Login and save token in YOUR CLI application."""
    credentials: Mapping[str, t.Container] = {
        "username": username,
        "password": password,
    }
    auth_result = cli.authenticate({k: str(v) for k, v in credentials.items()})
    if auth_result.failure:
        cli.print(
            f"❌ Login failed: {auth_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return False
    settings = cli.settings
    cli.print("✅ Login successful!", style=c.Cli.MessageStyles.GREEN)
    cli.print(
        f"   Token saved to: {settings.token_file}", style=c.Cli.MessageStyles.CYAN
    )
    return True


def fetch_saved_token() -> p.Result[str]:
    """Retrieve saved auth token in YOUR CLI. Returns r[str]; no None."""
    token_result = cli.fetch_auth_token()
    if token_result.failure:
        cli.print(
            f"⚠️  Not authenticated: {token_result.error}",
            style=c.Cli.MessageStyles.YELLOW,
        )
        return r[str].fail(token_result.error or "Not authenticated")
    return r[str].ok(token_result.value)


def call_authenticated_api(endpoint: str) -> p.Result[t.StrMapping]:
    """Make authenticated API call in YOUR tool. Returns r[dict]; no None."""
    token_result = cli.fetch_auth_token()
    if token_result.failure:
        cli.print(
            "❌ Authentication required. Please login first.",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return r[t.StrMapping].fail("Authentication required")
    token = token_result.value
    try:
        cli.print(f"📡 Calling {endpoint}...", style=c.Cli.MessageStyles.CYAN)
        cli.print(f"   Using token: {token[:20]}...", style=c.Cli.MessageStyles.WHITE)
        cli.print("✅ API call successful", style=c.Cli.MessageStyles.GREEN)
        return r[t.StrMapping].ok({"status": "success"})
    except Exception as e:
        cli.print(f"❌ API call failed: {e}", style=c.Cli.MessageStyles.BOLD_RED)
        return r[t.StrMapping].fail(str(e))


def validate_current_token() -> bool:
    """Validate saved token in YOUR application."""
    token_result = cli.fetch_auth_token()
    if token_result.failure:
        cli.print("⚠️  No token found", style=c.Cli.MessageStyles.YELLOW)
        return False
    token = token_result.value
    if len(token) < 20:
        cli.print("❌ Invalid token format", style=c.Cli.MessageStyles.BOLD_RED)
        return False
    cli.print("✅ Token is valid", style=c.Cli.MessageStyles.GREEN)
    cli.print(f"   Token: {token[:30]}...", style=c.Cli.MessageStyles.CYAN)
    return True


def refresh_token_if_needed() -> None:
    """Auto-refresh token in YOUR long-running CLI."""
    if not validate_current_token():
        cli.print("🔄 Token refresh required...", style=c.Cli.MessageStyles.YELLOW)
        new_token = secrets.token_urlsafe(32)
        save_result = cli.save_auth_token(new_token)
        if save_result.success:
            cli.print(
                "✅ Token refreshed successfully", style=c.Cli.MessageStyles.GREEN
            )


def validate_user_credentials(username: str, password: str) -> bool:
    """Validate credentials in YOUR auth system."""
    validate_result = cli.validate_credentials(username, password)
    if validate_result.failure:
        cli.print(f"❌ {validate_result.error}", style=c.Cli.MessageStyles.BOLD_RED)
        return False
    cli.print(
        f"✅ Credentials valid for user: {username}", style=c.Cli.MessageStyles.GREEN
    )
    return True


def show_session_info() -> None:
    """Display current session info in YOUR CLI."""
    token_result = cli.fetch_auth_token()
    if token_result.failure:
        cli.print("❌ Not authenticated", style=c.Cli.MessageStyles.BOLD_RED)
        return
    token = token_result.value
    token_file_str = cli.settings.token_file or ""
    token_file_path = Path(token_file_str)
    session_data = m.Cli.DisplayData(
        data={
            "User": os.getenv("USER", "unknown"),
            "Token File": str(token_file_path),
            "Token Length": f"{len(token)} chars",
            "File Size": f"{token_file_path.stat().st_size} bytes"
            if token_file_path.exists()
            else "N/A",
            "Modified": time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(token_file_path.stat().st_mtime),
            )
            if token_file_path.exists()
            else "N/A",
        },
    )
    table_data: t.StrMapping
    if isinstance(session_data.data, dict):
        table_data = {str(key): str(value) for key, value in session_data.data.items()}
    else:
        table_data = {"Session": "Unavailable"}
    cli.show_table(
        table_data,
        headers=["Property", "Value"],
        title="🔐 Current Session",
    )


def logout() -> None:
    """Logout and clear token in YOUR CLI."""
    token_file_str = cli.settings.token_file or ""
    token_file_path = Path(token_file_str)
    if not token_file_path.exists():
        cli.print("⚠️  No active session", style=c.Cli.MessageStyles.YELLOW)
        return
    try:
        token_file_path.unlink()
        cli.print("✅ Logged out successfully", style=c.Cli.MessageStyles.GREEN)
        cli.print(
            f"   Token removed from: {token_file_path}", style=c.Cli.MessageStyles.CYAN
        )
    except Exception as e:
        cli.print(f"❌ Logout failed: {e}", style=c.Cli.MessageStyles.BOLD_RED)


def complete_auth_workflow() -> bool:
    """Complete authentication workflow for YOUR application."""
    cli.print("🔐 Authentication Workflow", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "\n1. Checking existing authentication...", style=c.Cli.MessageStyles.CYAN
    )
    token_result = cli.fetch_auth_token()
    if token_result.success:
        cli.print("   ✅ Already authenticated", style=c.Cli.MessageStyles.GREEN)
        return True
    cli.print(
        "\n2. Generating new authentication token...", style=c.Cli.MessageStyles.CYAN
    )
    new_token = secrets.token_urlsafe(32)
    cli.print("\n3. Saving authentication token...", style=c.Cli.MessageStyles.CYAN)
    save_result = cli.save_auth_token(new_token)
    if save_result.failure:
        cli.print(
            f"   ❌ Failed: {save_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return False
    cli.print("   ✅ Token saved successfully", style=c.Cli.MessageStyles.GREEN)
    cli.print("\n4. Verifying authentication...", style=c.Cli.MessageStyles.CYAN)
    verify_result = cli.fetch_auth_token()
    if verify_result.success:
        cli.print("   ✅ Authentication complete!", style=c.Cli.MessageStyles.GREEN)
        return True
    cli.print("   ❌ Verification failed", style=c.Cli.MessageStyles.BOLD_RED)
    return False


def main() -> None:
    """Examples of using authentication in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  Authentication Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n1. Login Flow (save token):", style=c.Cli.MessageStyles.BOLD_CYAN)
    username = os.getenv("USER", "demo_user")
    password = secrets.token_urlsafe(16)
    login_ok = login_to_service(username, password)
    cli.print(
        f"   Login result: {('OK' if login_ok else 'Failed')}",
        style=c.Cli.MessageStyles.GREEN if login_ok else c.Cli.MessageStyles.RED,
    )
    cli.print(
        "\n2. Token Retrieval (for API calls):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    token_result = fetch_saved_token()
    if token_result.success:
        cli.print(
            f"   Retrieved token: {token_result.value[:30]}...",
            style=c.Cli.MessageStyles.GREEN,
        )
    else:
        cli.print("   No token available", style=c.Cli.MessageStyles.YELLOW)
    cli.print("\n3. Authenticated API Call:", style=c.Cli.MessageStyles.BOLD_CYAN)
    api_result = call_authenticated_api("https://api.example.com/data")
    if api_result.success:
        cli.print(
            f"   API returned: {api_result.value}", style=c.Cli.MessageStyles.GREEN
        )
    cli.print("\n4. Token Validation:", style=c.Cli.MessageStyles.BOLD_CYAN)
    valid = validate_current_token()
    cli.print(
        f"   Token valid: {valid}",
        style=c.Cli.MessageStyles.GREEN if valid else c.Cli.MessageStyles.YELLOW,
    )
    cli.print("\n5. Session Information:", style=c.Cli.MessageStyles.BOLD_CYAN)
    show_session_info()
    cli.print("\n6. Complete Auth Workflow:", style=c.Cli.MessageStyles.BOLD_CYAN)
    workflow_ok = complete_auth_workflow()
    cli.print(
        f"   Workflow result: {('OK' if workflow_ok else 'Failed')}",
        style=c.Cli.MessageStyles.GREEN if workflow_ok else c.Cli.MessageStyles.RED,
    )
    cli.print("\n7. Logout (clear token):", style=c.Cli.MessageStyles.BOLD_CYAN)
    logout()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Authentication Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Login: Use cli.authenticate() to save tokens",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • API Calls: Use cli.fetch_auth_token() to retrieve tokens",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Validation: Use cli.validate_credentials() for user input",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Logout: Delete token file at cli.settings.token_file",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()
