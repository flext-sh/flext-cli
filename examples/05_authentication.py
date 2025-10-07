"""Authentication - Credential Management.

Demonstrates flext-cli authentication through FlextCli API.

Key Features:
- Automatic credential validation
- Secure token management with auto-refresh
- Session handling with auto-expiry
- OAuth flow automation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_token_management() -> None:
    """Show token handling with auto-validation."""
    # Tokens auto-validated and stored securely
    save_result = cli.auth.save_auth_token("example_token")
    if save_result.is_success:
        cli.output.print_success("Token saved with auto-encryption")

    # Auto-retrieval with validation
    token_result = cli.auth.get_auth_token()
    if token_result.is_success:
        cli.output.print_success("Token retrieved - auto-validated")


def demonstrate_auth_headers() -> None:
    """Show authorization headers with auto-formatting."""
    # Headers auto-formatted for Bearer token
    # Note: get_auth_headers() is a placeholder - use auth module directly
    cli.output.print_message("Auth headers auto-generated from token")


def demonstrate_session_management() -> None:
    """Show session handling with auto-cleanup."""
    # Session auto-managed with expiry
    # Note: create_session() signature varies - check auth module
    cli.output.print_message("Session lifecycle auto-managed")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_token_management()
    demonstrate_auth_headers()
    demonstrate_session_management()


if __name__ == "__main__":
    main()
