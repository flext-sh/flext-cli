"""Authentication - Using flext-cli for Auth in YOUR CLI Application.

WHEN TO USE THIS:
- Building CLI tools that need authentication
- Managing API tokens and credentials
- Need to persist auth tokens securely
- Implementing login/logout functionality
- Building tools that call authenticated APIs

FLEXT-CLI PROVIDES:
- save_auth_token() - Save token to secure location
- get_auth_token() - Retrieve saved token
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

from flext_core import r

from flext_cli import FlextCli, m, t

cli = FlextCli()


def login_to_service(username: str, password: str) -> bool:
    """Login and save token in YOUR CLI application."""
    credentials: t.ContainerMapping = {
        "username": username,
        "password": password,
    }
    auth_result = cli.authenticate({k: str(v) for k, v in credentials.items()})
    if auth_result.is_failure:
        cli.print(f"❌ Login failed: {auth_result.error}", style="bold red")
        return False
    cli.print("✅ Login successful!", style="green")
    cli.print(f"   Token saved to: {cli.config.token_file}", style="cyan")
    return True


def get_saved_token() -> r[str]:
    """Retrieve saved auth token in YOUR CLI. Returns r[str]; no None."""
    token_result = cli.get_auth_token()
    if token_result.is_failure:
        cli.print(f"⚠️  Not authenticated: {token_result.error}", style="yellow")
        return r[str].fail(token_result.error or "Not authenticated")
    return r[str].ok(token_result.value)


def call_authenticated_api(endpoint: str) -> r[t.StrMapping]:
    """Make authenticated API call in YOUR tool. Returns r[dict]; no None."""
    token_result = cli.get_auth_token()
    if token_result.is_failure:
        cli.print("❌ Authentication required. Please login first.", style="bold red")
        return r[t.StrMapping].fail("Authentication required")
    token = token_result.value
    try:
        cli.print(f"📡 Calling {endpoint}...", style="cyan")
        cli.print(f"   Using token: {token[:20]}...", style="white")
        cli.print("✅ API call successful", style="green")
        return r[t.StrMapping].ok({"status": "success"})
    except Exception as e:
        cli.print(f"❌ API call failed: {e}", style="bold red")
        return r[t.StrMapping].fail(str(e))


def validate_current_token() -> bool:
    """Validate saved token in YOUR application."""
    token_result = cli.get_auth_token()
    if token_result.is_failure:
        cli.print("⚠️  No token found", style="yellow")
        return False
    token = token_result.value
    if len(token) < 20:
        cli.print("❌ Invalid token format", style="bold red")
        return False
    cli.print("✅ Token is valid", style="green")
    cli.print(f"   Token: {token[:30]}...", style="cyan")
    return True


def refresh_token_if_needed() -> None:
    """Auto-refresh token in YOUR long-running CLI."""
    if not validate_current_token():
        cli.print("🔄 Token refresh required...", style="yellow")
        new_token = secrets.token_urlsafe(32)
        save_result = cli.save_auth_token(new_token)
        if save_result.is_success:
            cli.print("✅ Token refreshed successfully", style="green")


def validate_user_credentials(username: str, password: str) -> bool:
    """Validate credentials in YOUR auth system."""
    validate_result = cli.validate_credentials(username, password)
    if validate_result.is_failure:
        cli.print(f"❌ {validate_result.error}", style="bold red")
        return False
    cli.print(f"✅ Credentials valid for user: {username}", style="green")
    return True


def show_session_info() -> None:
    """Display current session info in YOUR CLI."""
    token_result = cli.get_auth_token()
    if token_result.is_failure:
        cli.print("❌ Not authenticated", style="bold red")
        return
    token = token_result.value
    token_file_str = cli.config.token_file or ""
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
                "%Y-%m-%d %H:%M:%S", time.localtime(token_file_path.stat().st_mtime)
            )
            if token_file_path.exists()
            else "N/A",
        }
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
    token_file_str = cli.config.token_file or ""
    token_file_path = Path(token_file_str)
    if not token_file_path.exists():
        cli.print("⚠️  No active session", style="yellow")
        return
    try:
        token_file_path.unlink()
        cli.print("✅ Logged out successfully", style="green")
        cli.print(f"   Token removed from: {token_file_path}", style="cyan")
    except Exception as e:
        cli.print(f"❌ Logout failed: {e}", style="bold red")


def complete_auth_workflow() -> bool:
    """Complete authentication workflow for YOUR application."""
    cli.print("🔐 Authentication Workflow", style="bold cyan")
    cli.print("\n1. Checking existing authentication...", style="cyan")
    token_result = cli.get_auth_token()
    if token_result.is_success:
        cli.print("   ✅ Already authenticated", style="green")
        return True
    cli.print("\n2. Generating new authentication token...", style="cyan")
    new_token = secrets.token_urlsafe(32)
    cli.print("\n3. Saving authentication token...", style="cyan")
    save_result = cli.save_auth_token(new_token)
    if save_result.is_failure:
        cli.print(f"   ❌ Failed: {save_result.error}", style="bold red")
        return False
    cli.print("   ✅ Token saved successfully", style="green")
    cli.print("\n4. Verifying authentication...", style="cyan")
    verify_result = cli.get_auth_token()
    if verify_result.is_success:
        cli.print("   ✅ Authentication complete!", style="green")
        return True
    cli.print("   ❌ Verification failed", style="bold red")
    return False


def main() -> None:
    """Examples of using authentication in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Authentication Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Login Flow (save token):", style="bold cyan")
    username = os.getenv("USER", "demo_user")
    password = secrets.token_urlsafe(16)
    login_ok = login_to_service(username, password)
    cli.print(
        f"   Login result: {('OK' if login_ok else 'Failed')}",
        style="green" if login_ok else "red",
    )
    cli.print("\n2. Token Retrieval (for API calls):", style="bold cyan")
    token_result = get_saved_token()
    if token_result.is_success:
        cli.print(f"   Retrieved token: {token_result.value[:30]}...", style="green")
    else:
        cli.print("   No token available", style="yellow")
    cli.print("\n3. Authenticated API Call:", style="bold cyan")
    api_result = call_authenticated_api("https://api.example.com/data")
    if api_result.is_success:
        cli.print(f"   API returned: {api_result.value}", style="green")
    cli.print("\n4. Token Validation:", style="bold cyan")
    valid = validate_current_token()
    cli.print(f"   Token valid: {valid}", style="green" if valid else "yellow")
    cli.print("\n5. Session Information:", style="bold cyan")
    show_session_info()
    cli.print("\n6. Complete Auth Workflow:", style="bold cyan")
    workflow_ok = complete_auth_workflow()
    cli.print(
        f"   Workflow result: {('OK' if workflow_ok else 'Failed')}",
        style="green" if workflow_ok else "red",
    )
    cli.print("\n7. Logout (clear token):", style="bold cyan")
    logout()
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Authentication Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Login: Use cli.authenticate() to save tokens", style="white")
    cli.print(
        "  • API Calls: Use cli.get_auth_token() to retrieve tokens", style="white"
    )
    cli.print(
        "  • Validation: Use cli.validate_credentials() for user input", style="white"
    )
    cli.print("  • Logout: Delete token file at cli.config.token_file", style="white")


if __name__ == "__main__":
    main()
