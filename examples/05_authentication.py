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
- FlextResult error handling - No try/except needed

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

from flext_cli import FlextCli, m, r, t

cli = FlextCli()


# ============================================================================
# PATTERN 1: API token management in YOUR CLI tool
# ============================================================================


def login_to_service(username: str, password: str) -> bool:
    """Login and save token in YOUR CLI application."""
    # Your API authentication logic
    credentials: dict[str, t.JsonValue] = {
        "username": username,
        "password": password,
    }

    # Instead of manually managing tokens:
    # token = authenticate_with_api(username, password)
    # with open(TOKEN_FILE, 'w') as f:
    #     f.write(token)

    # Convert Mapping to dict[str, str] for authenticate
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


# ============================================================================
# PATTERN 2: Authenticated API calls in YOUR integration tool
# ============================================================================


def call_authenticated_api(endpoint: str) -> r[dict[str, str]]:
    """Make authenticated API call in YOUR tool. Returns r[dict]; no None."""
    token_result = cli.get_auth_token()

    if token_result.is_failure:
        cli.print("❌ Authentication required. Please login first.", style="bold red")
        return r[dict[str, str]].fail("Authentication required")

    token = token_result.value

    try:
        cli.print(f"📡 Calling {endpoint}...", style="cyan")
        cli.print(f"   Using token: {token[:20]}...", style="white")
        cli.print("✅ API call successful", style="green")
        return r[dict[str, str]].ok({"status": "success"})
    except Exception as e:
        cli.print(f"❌ API call failed: {e}", style="bold red")
        return r[dict[str, str]].fail(str(e))


# ============================================================================
# PATTERN 3: Token validation and refresh in YOUR CLI
# ============================================================================


def validate_current_token() -> bool:
    """Validate saved token in YOUR application."""
    token_result = cli.get_auth_token()

    if token_result.is_failure:
        cli.print("⚠️  No token found", style="yellow")
        return False

    token = token_result.value

    # Your token validation logic
    if len(token) < 20:  # Simple validation
        cli.print("❌ Invalid token format", style="bold red")
        return False

    cli.print("✅ Token is valid", style="green")
    cli.print(f"   Token: {token[:30]}...", style="cyan")
    return True


def refresh_token_if_needed() -> None:
    """Auto-refresh token in YOUR long-running CLI."""
    if not validate_current_token():
        cli.print("🔄 Token refresh required...", style="yellow")
        # Your token refresh logic
        new_token = secrets.token_urlsafe(32)
        save_result = cli.save_auth_token(new_token)
        if save_result.is_success:
            cli.print("✅ Token refreshed successfully", style="green")


# ============================================================================
# PATTERN 4: Credential validation in YOUR login flow
# ============================================================================


def validate_user_credentials(username: str, password: str) -> bool:
    """Validate credentials in YOUR auth system."""
    # Instead of manual validation:
    # if not username or not password:
    #     raise ValueError("Invalid credentials")

    validate_result = cli.validate_credentials(username, password)

    if validate_result.is_failure:
        cli.print(f"❌ {validate_result.error}", style="bold red")
        return False

    cli.print(f"✅ Credentials valid for user: {username}", style="green")
    return True


# ============================================================================
# PATTERN 5: Session management in YOUR CLI application
# ============================================================================


def show_session_info() -> None:
    """Display current session info in YOUR CLI."""
    # Check if authenticated
    token_result = cli.get_auth_token()

    if token_result.is_failure:
        cli.print("❌ Not authenticated", style="bold red")
        return

    token = token_result.value
    token_file = Path(cli.config.token_file)

    # Gather session data as Pydantic-backed display
    session_data = m.Cli.DisplayData(
        data={
            "User": os.getenv("USER", "unknown"),
            "Token File": str(token_file),
            "Token Length": f"{len(token)} chars",
            "File Size": (
                f"{token_file.stat().st_size} bytes" if token_file.exists() else "N/A"
            ),
            "Modified": (
                time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(token_file.stat().st_mtime),
                )
                if token_file.exists()
                else "N/A"
            ),
        },
    )

    cli.show_table(
        session_data.data,
        headers=["Property", "Value"],
        title="🔐 Current Session",
    )


def logout() -> None:
    """Logout and clear token in YOUR CLI."""
    token_file = Path(cli.config.token_file)

    if not token_file.exists():
        cli.print("⚠️  No active session", style="yellow")
        return

    try:
        token_file.unlink()
        cli.print("✅ Logged out successfully", style="green")
        cli.print(f"   Token removed from: {token_file}", style="cyan")
    except Exception as e:
        cli.print(f"❌ Logout failed: {e}", style="bold red")


# ============================================================================
# PATTERN 6: Multi-step auth workflow in YOUR CLI
# ============================================================================


def complete_auth_workflow() -> bool:
    """Complete authentication workflow for YOUR application."""
    cli.print("🔐 Authentication Workflow", style="bold cyan")

    # Step 1: Check existing auth
    cli.print("\n1. Checking existing authentication...", style="cyan")
    token_result = cli.get_auth_token()

    if token_result.is_success:
        cli.print("   ✅ Already authenticated", style="green")
        return True

    # Step 2: Generate new token (simulated auth)
    cli.print("\n2. Generating new authentication token...", style="cyan")
    new_token = secrets.token_urlsafe(32)

    # Step 3: Save token
    cli.print("\n3. Saving authentication token...", style="cyan")
    save_result = cli.save_auth_token(new_token)

    if save_result.is_failure:
        cli.print(f"   ❌ Failed: {save_result.error}", style="bold red")
        return False

    cli.print("   ✅ Token saved successfully", style="green")

    # Step 4: Verify
    cli.print("\n4. Verifying authentication...", style="cyan")
    verify_result = cli.get_auth_token()

    if verify_result.is_success:
        cli.print("   ✅ Authentication complete!", style="green")
        return True

    cli.print("   ❌ Verification failed", style="bold red")
    return False


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using authentication in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Authentication Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Login flow
    cli.print("\n1. Login Flow (save token):", style="bold cyan")
    username = os.getenv("USER", "demo_user")
    password = secrets.token_urlsafe(16)
    login_ok = login_to_service(username, password)
    cli.print(
        f"   Login result: {'OK' if login_ok else 'Failed'}",
        style="green" if login_ok else "red",
    )

    # Example 2: Get saved token
    cli.print("\n2. Token Retrieval (for API calls):", style="bold cyan")
    token_result = get_saved_token()
    if token_result.is_success:
        cli.print(f"   Retrieved token: {token_result.value[:30]}...", style="green")
    else:
        cli.print("   No token available", style="yellow")

    # Example 3: API call with token
    cli.print("\n3. Authenticated API Call:", style="bold cyan")
    api_result = call_authenticated_api("https://api.example.com/data")
    if api_result.is_success:
        cli.print(f"   API returned: {api_result.value}", style="green")

    # Example 4: Token validation
    cli.print("\n4. Token Validation:", style="bold cyan")
    valid = validate_current_token()
    cli.print(f"   Token valid: {valid}", style="green" if valid else "yellow")

    # Example 5: Session info
    cli.print("\n5. Session Information:", style="bold cyan")
    show_session_info()

    # Example 6: Complete workflow
    cli.print("\n6. Complete Auth Workflow:", style="bold cyan")
    workflow_ok = complete_auth_workflow()
    cli.print(
        f"   Workflow result: {'OK' if workflow_ok else 'Failed'}",
        style="green" if workflow_ok else "red",
    )

    # Example 7: Logout
    cli.print("\n7. Logout (clear token):", style="bold cyan")
    logout()

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Authentication Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Login: Use cli.authenticate() to save tokens", style="white")
    cli.print(
        "  • API Calls: Use cli.get_auth_token() to retrieve tokens",
        style="white",
    )
    cli.print(
        "  • Validation: Use cli.validate_credentials() for user input",
        style="white",
    )
    cli.print("  • Logout: Delete token file at cli.config.token_file", style="white")


if __name__ == "__main__":
    main()
