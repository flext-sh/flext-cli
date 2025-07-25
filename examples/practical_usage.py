#!/usr/bin/env python3
"""Practical usage examples for FlextCli library.

These examples demonstrate real-world usage patterns for massive code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import (
    FlextCliBuilder,
    flext_cli_create_builder,
    flext_cli_format_output,
    flext_cli_validate_inputs,
)
from flext_core import FlextResult


def example_1_simple_cli() -> None:
    """Example 1: Ultra-simple CLI creation."""
    # Zero-boilerplate CLI with just commands

    # Create and run CLI in one line (without actually running to avoid sys.exit)
    # result = flext_cli_quick_commands(commands, name="simple-app")
    # In a real scenario, this would create and run the CLI


def example_2_web_service_cli() -> None:
    """Example 2: Web service management CLI."""
    # Create CLI with web validation
    cli = (flext_cli_create_builder("webservice", version="2.1.0")
           .set_validator(url="url", email="email", port=lambda x: 1 <= int(x) <= 65535)
           .set_formatter("json")
           .add_global_flag("--verbose", "Enable verbose logging"))

    def deploy_service(url: str, port: str, REDACTED_LDAP_BIND_PASSWORD_email: str) -> FlextResult[dict[str, str]]:
        """Deploy web service with validation."""
        # Validate all inputs using consolidated validator
        validation_data = {"url": url, "email": REDACTED_LDAP_BIND_PASSWORD_email, "port": port}
        validation_result = cli.validate_data(validation_data)

        if not validation_result.success:
            return FlextResult.fail(f"Validation failed: {validation_result.error}")

        # Simulate deployment
        deployment_info = {
            "service": "deployed",
            "url": url,
            "port": port,
            "REDACTED_LDAP_BIND_PASSWORD": REDACTED_LDAP_BIND_PASSWORD_email,
            "status": "active",
        }

        return FlextResult.ok(deployment_info)

    def check_health(endpoint: str = "http://localhost:8080/health") -> FlextResult[dict[str, str]]:
        """Check service health."""
        return FlextResult.ok({
            "endpoint": endpoint,
            "status": "healthy",
            "response_time": "45ms",
        })

    # Add commands with fluent interface
    cli.add_command("deploy", deploy_service, "Deploy web service")
    cli.add_command("health", check_health, "Check service health")

    # Test commands directly (in real usage, cli.run() would handle this)
    deploy_result = deploy_service("https://api.example.com", "8080", "REDACTED_LDAP_BIND_PASSWORD@example.com")
    if deploy_result.success:
        flext_cli_format_output(deploy_result.unwrap(), "json")
    else:
        pass


def example_3_database_management() -> None:
    """Example 3: Database management with comprehensive validation."""
    # Create validator with database-specific patterns
    db_validator = flext_cli_validate_inputs(
        host="domain",
        port=lambda x: 1024 <= int(x) <= 65535,
        database=lambda x: len(str(x)) >= 3,
        username="username",
        ssl_cert="file_path",
    )

    cli = (FlextCliBuilder("dbmanager", "3.0.0", "Database Management Tool")
           .set_formatter("table")
           .add_config_file_support("db.yaml"))

    # Set custom validator
    cli._validator = db_validator

    def connect_database(host: str, port: str, database: str, username: str) -> FlextResult[dict[str, str]]:
        """Connect to database with validation."""
        connection_data = {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
        }

        validation_result = cli.validate_data(connection_data)
        if not validation_result.success:
            return FlextResult.fail(validation_result.error)

        return FlextResult.ok({
            "connection": "established",
            "host": host,
            "database": database,
            "user": username,
            "ssl": "enabled",
        })

    def list_tables() -> FlextResult[list[dict[str, str]]]:
        """List database tables."""
        return FlextResult.ok([
            {"table": "users", "rows": "1,245", "size": "2.1MB"},
            {"table": "orders", "rows": "5,678", "size": "8.9MB"},
            {"table": "products", "rows": "3,421", "size": "5.2MB"},
        ])

    def backup_database(target_path: str) -> FlextResult[dict[str, str]]:
        """Create database backup."""
        return FlextResult.ok({
            "backup": "completed",
            "target": target_path,
            "size": "125.8MB",
            "duration": "2.3s",
        })

    # Add commands
    cli.add_command("connect", connect_database, "Connect to database")
    cli.add_command("tables", list_tables, "List all tables")
    cli.add_command("backup", backup_database, "Create database backup")

    # Demonstrate usage
    connect_result = connect_database("db.example.com", "5432", "production", "dbREDACTED_LDAP_BIND_PASSWORD")
    if connect_result.success:

        # Test table listing
        tables_result = list_tables()
        if tables_result.success:
            # Format as table
            formatter = cli._get_formatter()
            formatter.table(tables_result.unwrap(), "Database Tables")
    else:
        pass


def example_4_advanced_features() -> None:
    """Example 4: Advanced features demonstration."""
    # Create CLI with all advanced features
    cli = (FlextCliBuilder("advanced-app", "4.0.0", "Advanced CLI Demo")
           .set_validator(email="email", jwt="jwt", ipv6="ipv6")
           .set_formatter("rich")
           .add_global_flag("--debug", "Debug mode")
           .add_global_flag("--dry-run", "Dry run mode"))

    # Add middleware
    def audit_middleware(data: dict[str, Any]) -> dict[str, Any]:
        """Add audit information to all commands."""
        data["audit"] = {
            "timestamp": "2025-07-25T10:30:00Z",
            "user": "current_user",
            "session": "abc123",
        }
        return data

    cli.add_middleware(audit_middleware)

    # Set custom error handler
    def custom_error_handler(exc: Exception) -> str:
        return f"🚨 Custom error handler: {exc}"

    cli.set_error_handler(custom_error_handler)

    def process_user_data(email: str, token: str, ipv6_addr: str) -> FlextResult[dict[str, Any]]:
        """Process user data with comprehensive validation."""
        user_data = {"email": email, "jwt": token, "ipv6": ipv6_addr}

        validation_result = cli.validate_data(user_data)
        if not validation_result.success:
            return FlextResult.fail(validation_result.error)

        # Simulate processing
        result = {
            "processed": True,
            "email": email,
            "token_valid": True,
            "ipv6_valid": True,
            "processing_time": "150ms",
        }

        return FlextResult.ok(result)

    def generate_report(format_type: str = "rich") -> FlextResult[str]:
        """Generate formatted report."""
        report_data = {
            "system": {
                "cpu_usage": "45%",
                "memory": "2.1GB/8GB",
                "disk": "120GB/500GB",
            },
            "services": [
                {"name": "web-server", "status": "running", "uptime": "5d 3h"},
                {"name": "database", "status": "running", "uptime": "12d 8h"},
                {"name": "cache", "status": "stopped", "uptime": "0h"},
            ],
        }

        # Use different formatting based on request
        if format_type == "tree":
            formatter = cli._get_formatter()
            result = formatter.format_tree(report_data, "System Report")
        elif format_type == "json":
            result = flext_cli_format_output(report_data, "json").unwrap()
        else:
            result = flext_cli_format_output(report_data, "rich").unwrap()

        return FlextResult.ok(result)

    # Add commands
    cli.add_command("process", process_user_data, "Process user data")
    cli.add_command("report", generate_report, "Generate system report")

    # Demonstrate usage

    # Test with valid data
    valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    valid_ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    process_result = process_user_data("user@example.com", valid_jwt, valid_ipv6)
    if process_result.success:

        # Generate different report formats
        tree_report = generate_report("tree")
        if tree_report.success:
            pass
    else:
        pass


def example_5_input_collection() -> None:
    """Example 5: Interactive input collection."""
    # This example shows how the input system would work
    # (In practice, this would require actual user interaction)

    cli = FlextCliBuilder("interactive-app")

    # Define input schema

    def create_user_interactive() -> FlextResult[dict[str, Any]]:
        """Create user with interactive input (simulated)."""
        # In real usage, this would collect interactive input
        # For demo, we'll simulate the collected data
        collected_data = {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30,
            "subscribe": True,
            "plan": "premium",
        }

        # Validate collected data
        validator = flext_cli_validate_inputs(email="email")
        validation_result = validator.validate_dict({"email": collected_data["email"]})

        if not validation_result.success:
            return FlextResult.fail(validation_result.error)

        return FlextResult.ok({
            "user_created": True,
            "user_id": "user_12345",
            **collected_data,
        })

    cli.add_command("create-user", create_user_interactive, "Create user interactively")

    # Demonstrate
    result = create_user_interactive()
    if result.success:
        flext_cli_format_output(result.unwrap(), "yaml")


def main() -> None:
    """Run all examples."""
    try:
        example_1_simple_cli()

        example_2_web_service_cli()

        example_3_database_management()

        example_4_advanced_features()

        example_5_input_collection()


    except Exception:
        pass


if __name__ == "__main__":
    main()
