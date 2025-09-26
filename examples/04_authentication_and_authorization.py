#!/usr/bin/env python3
"""04 - Authentication and Authorization Patterns.

This example demonstrates authentication and authorization patterns using flext-cli:

Key Patterns Demonstrated:
- Authentication token management (save, retrieve, validate)
- Authorization headers generation and usage
- Secure credential handling with environment variables
- API client authentication with flext patterns
- Role-based access control simulation
- Login/logout command patterns
- Session management and token refresh

Architecture Layers:
- Domain: Authentication entities and value objects
- Application: Auth command handlers and services
- Infrastructure: Token storage, HTTP clients, credential management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

from flext_cli import (
    FlextCliAuth,
    FlextCliConfig,
    FlextCliOutput,
    FlextCliService,
    FlextCliUtilities,
)
from flext_core import FlextConstants, FlextResult, FlextTypes

# from .example_utils import print_demo_completion


def demonstrate_basic_authentication() -> FlextResult[None]:
    """Demonstrate basic authentication patterns."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("[bold blue]Basic Authentication Patterns[/bold blue]")

    # 1. Save authentication token
    console.print("\n[green]1. Token Management[/green]")

    # Simulate receiving a token from login
    demo_token = "flx_demo_token_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    auth = FlextCliAuth()
    save_result = auth.save_auth_token(demo_token)
    if save_result.is_success:
        console.print("✅ Authentication token saved successfully")
        console.print(f"   Token prefix: {demo_token[:20]}...")
    else:
        console.print(f"❌ Failed to save token: {save_result.error}")
        return FlextResult[None].fail("Token save failed")

    # 2. Retrieve authentication headers
    console.print("\n[green]2. Authorization Headers[/green]")

    # get_auth_status returns FlextResult[FlextTypes.Core.Dict]
    headers_result = auth.get_auth_status()

    # Handle FlextResult type
    if hasattr(headers_result, "is_success") and hasattr(headers_result, "value"):
        if getattr(headers_result, "is_success"):
            headers: dict[str, object] = getattr(headers_result, "value") or {}
            headers_dict: dict[str, object] = {
                str(k): str(v) for k, v in headers.items()
            }
            console.print("✅ Authorization headers retrieved")
            console.print("   Headers structure:")
            for key, value in headers_dict.items():
                # Mask sensitive values
                max_display_length = 10
                display_value = (
                    str(value)[:max_display_length] + "..."
                    if len(str(value)) > max_display_length
                    else str(value)
                )
                console.print(f"     {key}: {display_value}")
        else:
            console.print(
                f"❌ Failed to retrieve headers: {getattr(headers_result, 'error', 'unknown')}"
            )
    else:
        # Handle case where headers_result might be a raw dict (backward compatibility)
        console.print("❌ Headers result is not a FlextResult type")

    return FlextResult[None].ok(None)


def demonstrate_api_authentication() -> FlextResult[None]:
    """Demonstrate API client authentication patterns."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]3. API Client Authentication[/green]")

    try:
        # Create authenticated API client
        api_client = FlextCliService()
        console.print("✅ FlextCliService initialized")

        # Simulate authenticated API call
        # Note: This is a demo - actual API endpoints would be real
        demo_endpoint = "/api/v1/user/profile"

        # Use FlextResult pattern for API calls
        profile_result = simulate_authenticated_request(api_client, demo_endpoint)

        if profile_result.is_success:
            profile_data: dict[str, object] = profile_result.value
            if profile_data:
                console.print("✅ Authenticated API request successful")
                console.print(f"   User: {profile_data.get('username', 'demo_user')}")
                console.print(f"   Role: {profile_data.get('role', 'user')}")
                permissions = profile_data.get("permissions", [])
                perm_count = len(permissions) if isinstance(permissions, list) else 0
                console.print(f"   Permissions: {perm_count} permissions")
            else:
                console.print("❌ Invalid profile data returned")
        else:
            console.print(f"❌ API request failed: {profile_result.error}")

    except Exception as e:
        return FlextResult[None].fail(f"API authentication demo failed: {e}")

    return FlextResult[None].ok(None)


@FlextCliUtilities.Decorators.require_auth()
def demonstrate_protected_operation() -> FlextResult[str]:
    """Demonstrate a protected operation requiring authentication."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]4. Protected Operations[/green]")

    # This function is decorated with @require_auth()
    # It will only execute if valid authentication is present

    console.print("✅ @require_auth() decorator passed - user is authenticated")

    # Simulate protected business operation
    operation_result = perform_protected_business_logic()

    if operation_result.is_success:
        result = operation_result.value
        console.print(f"✅ Protected operation completed: {result}")
        return FlextResult[str].ok(result)
    console.print(f"❌ Protected operation failed: {operation_result.error}")
    return FlextResult[str].fail(operation_result.error or "Operation failed")


def demonstrate_role_based_access() -> FlextResult[None]:
    """Demonstrate role-based access control patterns."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]5. Role-Based Access Control[/green]")

    # Simulate different user roles and permissions
    demo_roles: list[FlextTypes.Core.Dict] = [
        {
            "name": "REDACTED_LDAP_BIND_PASSWORD",
            "permissions": ["read", "write", "delete", "manage_users", "system_config"],
        },
        {"name": "operator", "permissions": ["read", "write", "deploy", "monitor"]},
        {"name": "viewer", "permissions": ["read", "monitor"]},
    ]

    # Create permissions table using flext-cli formatter
    permissions_data: dict[str, object] = {}

    for role in demo_roles:
        permissions = role["permissions"]
        if isinstance(permissions, list):
            # Convert to list of strings for safe iteration
            perm_strings: list[str] = [str(item) for item in permissions]
            permissions_str = ", ".join(perm_strings)
            access_level = (
                "Full"
                if "delete" in permissions
                else "Limited"
                if "write" in permissions
                else "Read-Only"
            )
        else:
            permissions_str = "Invalid permissions data"
            access_level = "Unknown"

        role_name = str(role["name"])
        permissions_data[role_name] = f"{permissions_str} ({access_level})"

    # Format and display table using flext-cli
    table_result = formatter.format_table(
        data=permissions_data, title="Role-Based Permissions Matrix"
    )
    if table_result.is_success:
        console.print(table_result.value)

    # Simulate permission checking
    current_user_role = "operator"  # Simulated
    required_permission = "deploy"

    check_result = check_permission(current_user_role, required_permission, demo_roles)
    if check_result.is_success:
        console.print(
            f"✅ Permission check passed: {current_user_role} can {required_permission}"
        )
    else:
        console.print(f"❌ Permission denied: {check_result.error}")

    return FlextResult[None].ok(None)


def demonstrate_session_management() -> FlextResult[None]:
    """Demonstrate session management patterns."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]6. Session Management[/green]")

    # Simulate session data
    now = datetime.now(UTC)
    session_data: FlextTypes.Core.Dict = {
        "session_id": f"sess_{now.strftime('%Y%m%d_%H%M%S')}",
        "user_id": "demo_user_123",
        "created_at": now,
        "expires_at": now + timedelta(hours=8),
        "last_activity": now,
        "permissions": ["read", "write", "deploy"],
        "ip_address": FlextConstants.Platform.LOOPBACK_IP,
        "user_agent": "flext-cli/1.0.0",
    }

    console.print("✅ Session created with the following details:")
    console.print(f"   Session ID: {session_data['session_id']}")
    console.print(f"   User ID: {session_data['user_id']}")
    created_at = session_data["created_at"]
    expires_at = session_data["expires_at"]
    if isinstance(created_at, datetime) and isinstance(expires_at, datetime):
        console.print(f"   Created: {created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        console.print(f"   Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    else:
        console.print("   Created: Session data formatted incorrectly")
        console.print("   Expires: Session data formatted incorrectly")

    # Check session validity
    validity_result = validate_session(session_data)
    if validity_result.is_success:
        console.print("✅ Session is valid and active")

        # Simulate session refresh
        refresh_result = refresh_session(session_data)
        if refresh_result.is_success:
            refreshed_session: dict[str, object] = refresh_result.value
            console.print("✅ Session refreshed successfully")
            if refreshed_session:
                expires_at = refreshed_session.get("expires_at")
                if expires_at and isinstance(expires_at, datetime):
                    console.print(
                        f"   New expiry: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    )
                else:
                    console.print("   New expiry: Updated successfully")
    else:
        console.print(f"❌ Session validation failed: {validity_result.error}")

    return FlextResult[None].ok(None)


def demonstrate_secure_configuration() -> FlextResult[None]:
    """Demonstrate secure configuration and credential management."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]7. Secure Configuration Management[/green]")

    # Get CLI configuration
    FlextCliConfig.MainConfig()
    console.print("✅ CLI configuration loaded")

    # Demonstrate environment variable usage for sensitive data
    console.print("\n📋 Environment Variables for Security:")

    secure_env_vars = [
        ("FLEXT_API_TOKEN", "API authentication token"),
        ("FLEXT_API_BASE_URL", "Base URL for FLEXT API"),
        ("FLEXT_CLI_PROFILE", "CLI profile (dev/staging/prod)"),
        ("FLEXT_LOG_LEVEL", "Logging level for debugging"),
        ("FLEXT_TIMEOUT", "Request timeout configuration"),
    ]

    env_data: dict[str, object] = {}
    for var_name, purpose in secure_env_vars:
        value = os.environ.get(var_name)
        status = "✅ Set" if value else "⚠️ Not set"
        env_data[var_name] = f"{purpose} ({status})"

    # Format and display table using flext-cli
    table_result = formatter.format_table(
        data=env_data, title="Secure Environment Variables"
    )
    if table_result.is_success:
        console.print(table_result.value)

    # Demonstrate secure credential patterns
    console.print("\n🔒 Secure Credential Patterns:")
    console.print("   • Never hardcode credentials in source code")
    console.print("   • Use environment variables for sensitive configuration")
    console.print("   • Implement token rotation and expiration")
    console.print("   • Use secure storage for persistent tokens")
    console.print("   • Validate and sanitize all credential inputs")

    return FlextResult[None].ok(None)


def simulate_authenticated_request(
    _client: FlextCliService, endpoint: str
) -> FlextResult[FlextTypes.Core.Dict]:
    """Simulate an authenticated API request."""
    try:
        # In a real implementation, this would make an actual HTTP request
        # For demo purposes, we simulate a successful response

        # Simulate different responses based on endpoint
        if "profile" in endpoint:
            response_data = {
                "username": "demo_user",
                "email": "demo@example.com",
                "role": "operator",
                "permissions": ["read", "write", "deploy", "monitor"],
                "last_login": datetime.now(UTC).isoformat(),
                "active": True,
            }
        elif "health" in endpoint:
            response_data = {
                "status": "healthy",
                "version": "1.0.0",
                "uptime": "24h 15m",
                "authenticated": True,
            }
        else:
            response_data = {
                "message": "Authenticated request successful",
                "endpoint": endpoint,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return FlextResult[FlextTypes.Core.Dict].ok(dict(response_data))

    except Exception as e:
        return FlextResult[FlextTypes.Core.Dict].fail(f"API request failed: {e}")


def perform_protected_business_logic() -> FlextResult[str]:
    """Simulate protected business operation."""
    try:
        # Simulate some business logic that requires authentication
        operations = [
            "Deploying service configuration",
            "Updating security policies",
            "Accessing sensitive data",
            "Modifying system settings",
        ]

        # For demo, just return a success message
        selected_operation = operations[0]  # Deploy operation

        return FlextResult[str].ok(f"Successfully executed: {selected_operation}")

    except Exception as e:
        return FlextResult[str].fail(f"Business operation failed: {e}")


def check_permission(
    user_role: str, required_permission: str, roles_config: list[FlextTypes.Core.Dict]
) -> FlextResult[bool]:
    """Check if user role has required permission."""
    try:
        # Find user role configuration
        role_config = None
        for role in roles_config:
            if role["name"] == user_role:
                role_config = role
                break

        if not role_config:
            return FlextResult[bool].fail(f"Role '{user_role}' not found")

        # Check if role has required permission
        permissions = role_config["permissions"]
        if isinstance(permissions, list) and required_permission in permissions:
            is_authorized = True
            return FlextResult[bool].ok(is_authorized)
        return FlextResult[bool].fail(
            f"Role '{user_role}' lacks permission '{required_permission}'"
        )

    except Exception as e:
        return FlextResult[bool].fail(f"Permission check failed: {e}")


def validate_session(session_data: FlextTypes.Core.Dict) -> FlextResult[bool]:
    """Validate session data and expiration."""
    try:
        current_time = datetime.now(UTC)
        expires_at = session_data.get("expires_at")

        if not expires_at:
            return FlextResult[bool].fail("Session has no expiration time")

        if isinstance(expires_at, datetime) and current_time > expires_at:
            return FlextResult[bool].fail("Session has expired")

        # Check if session is too old (example: max 24 hours)
        created_at = session_data.get("created_at")
        if isinstance(created_at, datetime) and (current_time - created_at) > timedelta(
            days=1
        ):
            return FlextResult[bool].fail("Session is too old")

        is_valid = True
        return FlextResult[bool].ok(is_valid)

    except Exception as e:
        return FlextResult[bool].fail(f"Session validation error: {e}")


def refresh_session(
    session_data: FlextTypes.Core.Dict,
) -> FlextResult[FlextTypes.Core.Dict]:
    """Refresh session with new expiration time."""
    try:
        current_time = datetime.now(UTC)

        # Create refreshed session data
        refreshed_session = session_data.copy()
        refreshed_session.update({
            "expires_at": current_time + timedelta(hours=8),
            "last_activity": current_time,
            "refreshed_at": current_time,
        })

        return FlextResult[FlextTypes.Core.Dict].ok(refreshed_session)

    except Exception as e:
        return FlextResult[FlextTypes.Core.Dict].fail(f"Session refresh failed: {e}")


def main() -> None:
    """Main demonstration function."""
    formatter = FlextCliOutput()
    console = formatter.console

    formatter.print_success("04 - Authentication and Authorization Patterns")
    formatter.print_success("=" * 50)
    console.print(
        "[yellow]Comprehensive demonstration of flext-cli authentication patterns:[/yellow]"
    )
    console.print("🔐 Token management and secure storage")
    console.print("🛡️ Authorization headers and API authentication")
    console.print("🔒 Protected operations with @require_auth() decorator")
    console.print("👥 Role-based access control (RBAC)")
    console.print("⏰ Session management and token refresh")
    console.print("🔑 Secure configuration and credential handling")
    console.print("🌐 API client authentication patterns")
    console.print()

    try:
        # Run all authentication demonstrations
        auth_result = demonstrate_basic_authentication()
        if auth_result.is_failure:
            console.print(f"[red]Basic auth demo failed: {auth_result.error}[/red]")

        api_result = demonstrate_api_authentication()
        if api_result.is_failure:
            console.print(f"[red]API auth demo failed: {api_result.error}[/red]")

        protected_result = demonstrate_protected_operation()
        if isinstance(protected_result, FlextResult) and protected_result.is_failure:
            console.print(
                f"[red]Protected operation demo failed: {protected_result.error}[/red]"
            )
        elif not isinstance(protected_result, FlextResult):
            console.print(
                "[red]Protected operation failed - authentication required[/red]"
            )

        rbac_result = demonstrate_role_based_access()
        if rbac_result.is_failure:
            console.print(f"[red]RBAC demo failed: {rbac_result.error}[/red]")

        session_result = demonstrate_session_management()
        if session_result.is_failure:
            console.print(
                f"[red]Session management demo failed: {session_result.error}[/red]"
            )

        config_result = demonstrate_secure_configuration()
        if config_result.is_failure:
            console.print(
                f"[red]Secure configuration demo failed: {config_result.error}[/red]"
            )

        # Final summary using shared utility
        features = [
            "🔐 Token-based authentication with save_auth_token()",
            "🛡️ Authorization headers via get_auth_headers()",
            "🔒 Protected operations using @require_auth() decorator",
            "👥 Role-based permissions and access control",
            "⏰ Session lifecycle management and validation",
            "🔑 Environment-based secure configuration",
            "🌐 FlextCliService authentication patterns",
        ]

        console.print(
            "[bold green]✅ Authentication and Authorization Demo completed![/bold green]"
        )
        console.print("[bold blue]Features demonstrated:[/bold blue]")
        for feature in features:
            console.print(f"  • {feature}")

    except Exception as e:
        console.print(f"[bold red]❌ Authentication demo error: {e}[/bold red]")


if __name__ == "__main__":
    main()
