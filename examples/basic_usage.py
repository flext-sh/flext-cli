#!/usr/bin/env python3
"""Basic Usage Examples for FlextCli Library.

Demonstrates the power and simplicity of the FlextCli library
with zero-boilerplate CLI creation and massive code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_cli import (
    FlextCliBuilder,
    FlextResult,
    flext_cli_create_builder,
    flext_cli_format_output,
    flext_cli_validate_inputs,
)


def example_minimal_cli() -> None:
    """Example 1: Create minimal CLI with zero boilerplate."""
    # Create CLI builder
    cli = flext_cli_create_builder("myapp", version="1.0.0")

    # Add simple command
    def hello() -> str:
        return "Hello, World!"

    cli.add_command("hello", hello, help="Say hello")



def example_quick_commands() -> None:
    """Example 2: Ultra-fast CLI from command dictionary."""

    # Note: In real usage, this would call: flext_cli_quick_commands(commands)


def example_validation_patterns() -> None:
    """Example 3: Input validation with built-in patterns."""
    # Create validator with multiple patterns
    validator = flext_cli_validate_inputs(
        email="email",
        url="url",
        port=lambda x: 1 <= int(x) <= 65535,
        username="username",
    )

    # Test validations
    test_cases = [
        ("email", "user@example.com", True),
        ("email", "invalid-email", False),
        ("port", "8080", True),
        ("port", "99999", False),
        ("username", "valid_user123", True),
        ("username", "invalid-user!", False),
    ]

    for field, value, _expected in test_cases:
        validator.validate(field, value)


def example_output_formatting() -> None:
    """Example 4: Format data in multiple styles."""
    data = {
        "name": "Alice Johnson",
        "role": "Developer",
        "projects": ["API", "Dashboard", "Mobile App"],
        "active": True,
    }

    # Test different formats
    formats = ["json", "yaml", "table"]

    for format_type in formats:
        result = flext_cli_format_output(data, format_type)
        if result.success:
            pass
        else:
            pass


def example_user_management_cli() -> None:
    """Example 5: User management CLI with validation and formatting."""
    # Create CLI with custom settings
    cli = FlextCliBuilder(
        name="usermgr",
        version="2.0.0",
        description="User Management System",
    )

    # Set up validation for user data
    cli.set_validator(
        email="email",
        username="username",
        password="password",
    )

    # Set JSON output format
    cli.set_formatter("json")

    # User creation command
    def create_user(username: str, email: str, role: str = "user"):
        # Validate inputs
        validation_data = {"username": username, "email": email}
        result = cli.validate_data(validation_data)

        if not result.success:
            return FlextResult.fail(f"Validation failed: {result.error}")

        # Create user data
        user_data = {
            "id": 123,
            "username": username,
            "email": email,
            "role": role,
            "created": "2025-01-15T10:30:00Z",
            "active": True,
        }

        return FlextResult.ok(user_data)

    # Add command with options
    cli.add_command("create", create_user, help="Create new user")
    cli.add_option("--username", command_name="create", required=True, help="Username")
    cli.add_option("--email", command_name="create", required=True, help="Email address")
    cli.add_option("--role", command_name="create", default="user", help="User role")

    # Test the command function
    result = create_user("alice123", "alice@example.com", "REDACTED_LDAP_BIND_PASSWORD")
    if result.success:
        result.unwrap()
    else:
        pass


def example_configuration_tool() -> None:
    """Example 6: Configuration management tool with interactive input."""
    FlextCliBuilder(name="config-tool", description="Configuration Manager")

    # Simulate configuration data
    config_data = {
        "host": "https://db.example.com",
        "port": 5432,
        "database": "myapp",
        "username": "dbuser",
        "ssl_enabled": True,
    }

    # Format as YAML for configuration file
    result = flext_cli_format_output(config_data, "yaml")
    if result.success:
        pass
    else:
        pass


def example_fluent_builder_pattern() -> None:
    """Example 7: Fluent builder pattern for complex CLI setup."""
    # Chain multiple configuration calls
    (FlextCliBuilder(name="fluentapp", version="3.0.0")
           .set_validator(
               email="email",
               port=lambda x: 1 <= int(x) <= 65535,
           )
           .set_formatter("json")
           .add_command("start", lambda: "Starting service...", help="Start the service")
           .add_command("stop", lambda: "Stopping service...", help="Stop the service")
           .add_option("--port", command_name="start", type=int, default=8080)
           .add_option("--host", command_name="start", default="localhost"))



def main() -> int:
    """Run all examples to demonstrate FlextCli capabilities."""
    try:
        example_minimal_cli()
        example_quick_commands()
        example_validation_patterns()
        example_output_formatting()
        example_user_management_cli()
        example_configuration_tool()
        example_fluent_builder_pattern()


    except Exception:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
