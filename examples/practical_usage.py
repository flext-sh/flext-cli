#!/usr/bin/env python3
"""Practical usage examples for FlextCli library.

These examples demonstrate real-world usage patterns for massive code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import (
    flext_cli_format,  # available format function
    flext_cli_table,  # available table function
    # Use actually available exports
    format_output,  # available formatter function
    setup_cli,  # available CLI setup function
)
from flext_core import ServiceResult as FlextResult

# Constants
MAX_PORT_NUMBER = 65535
MIN_PRIVILEGED_PORT = 1024
MIN_DATABASE_NAME_LENGTH = 3


def example_1_simple_cli() -> None:
    """Example 1: Ultra-simple CLI creation."""
    # Zero-boilerplate CLI with just commands

    # Create basic CLI setup using available functions
    from flext_cli import CLISettings

    settings = CLISettings(debug=True)
    setup_cli(settings)
    # This demonstrates the actual available API


def example_2_web_service_cli() -> None:
    """Example 2: Web service management CLI."""
    # Create CLI with configuration
    from flext_cli import CLIConfig, CLISettings

    CLIConfig(
        output_format="json",
        verbose=True,
        debug=True,
    )
    settings = CLISettings(debug=True, project_name="webservice")
    setup_cli(settings)

    def deploy_service(
        url: str,
        port: str,
        admin_email: str,
    ) -> FlextResult[dict[str, str]]:
        """Deploy web service with validation."""
        # Basic validation using available patterns
        if not url or not admin_email or not port:
            return FlextResult.fail("Missing required parameters")

        try:
            port_num = int(port)
            if not (1 <= port_num <= MAX_PORT_NUMBER):
                return FlextResult.fail(f"Port must be between 1 and {MAX_PORT_NUMBER}")
        except ValueError:
            return FlextResult.fail("Port must be a valid number")

        # Simulate deployment
        deployment_info = {
            "service": "deployed",
            "url": url,
            "port": port,
            "admin": admin_email,
            "status": "active",
        }

        return FlextResult.ok(deployment_info)

    def check_health(
        endpoint: str = "http://localhost:8080/health",
    ) -> FlextResult[dict[str, str]]:
        """Check service health."""
        return FlextResult.ok(
            {
                "endpoint": endpoint,
                "status": "healthy",
                "response_time": "45ms",
            },
        )

    # Commands would be added to actual CLI in practice
    # This demonstrates the service function patterns available

    # Test commands directly (in real usage, cli.run() would handle this)
    deploy_result = deploy_service(
        "https://api.example.com",
        "8080",
        "admin@example.com",
    )
    if deploy_result.success:
        format_output(deploy_result.unwrap(), "json")


def example_3_database_management() -> None:
    """Example 3: Database management with comprehensive validation."""
    # Create configuration for database management
    from flext_cli import CLIConfig, CLISettings

    CLIConfig(
        output_format="table",
        debug=True,
    )
    CLISettings(
        debug=True,
        project_name="dbmanager",
    )

    # Constants for validation
    MIN_HOST_LENGTH = 3
    MIN_USERNAME_LENGTH = 2

    def validate_db_params(
        host: str, port: str, database: str, username: str
    ) -> FlextResult[None]:
        """Validate database connection parameters."""
        if not host or len(host) < MIN_HOST_LENGTH:
            return FlextResult.fail(f"Host must be at least {MIN_HOST_LENGTH} characters")
        try:
            port_num = int(port)
            if not (MIN_PRIVILEGED_PORT <= port_num <= MAX_PORT_NUMBER):
                return FlextResult.fail(
                    f"Port must be between {MIN_PRIVILEGED_PORT} and {MAX_PORT_NUMBER}"
                )
        except ValueError:
            return FlextResult.fail("Port must be a valid number")
        if len(database) < MIN_DATABASE_NAME_LENGTH:
            return FlextResult.fail(
                f"Database name must be at least {MIN_DATABASE_NAME_LENGTH} characters"
            )
        if not username or len(username) < MIN_USERNAME_LENGTH:
            return FlextResult.fail(f"Username must be at least {MIN_USERNAME_LENGTH} characters")
        return FlextResult.ok(None)

    def connect_database(
        host: str,
        port: str,
        database: str,
        username: str,
    ) -> FlextResult[dict[str, str]]:
        """Connect to database with validation."""
        validation_result = validate_db_params(host, port, database, username)
        if not validation_result.success:
            return FlextResult.fail(validation_result.error)

        return FlextResult.ok(
            {
                "connection": "established",
                "host": host,
                "database": database,
                "user": username,
                "ssl": "enabled",
            },
        )

    def list_tables() -> FlextResult[list[dict[str, str]]]:
        """List database tables."""
        return FlextResult.ok(
            [
                {"table": "users", "rows": "1,245", "size": "2.1MB"},
                {"table": "orders", "rows": "5,678", "size": "8.9MB"},
                {"table": "products", "rows": "3,421", "size": "5.2MB"},
            ],
        )

    def backup_database(target_path: str) -> FlextResult[dict[str, str]]:
        """Create database backup."""
        return FlextResult.ok(
            {
                "backup": "completed",
                "target": target_path,
                "size": "125.8MB",
                "duration": "2.3s",
            },
        )

    # Functions demonstrate available patterns
    # In practice, these would be registered as CLI commands

    # Demonstrate usage
    connect_result = connect_database("db.example.com", "5432", "production", "dbadmin")
    if connect_result.success:
        # Test table listing
        tables_result = list_tables()
        if tables_result.success:
            # Format as table using available function
            table_data = tables_result.unwrap()
            flext_cli_table(table_data, "Database Tables", "grid")


def example_4_advanced_features() -> None:
    """Example 4: Advanced features demonstration."""
    # Create advanced CLI configuration
    from flext_cli import CLIConfig, CLISettings

    CLIConfig(
        output_format="rich",
        debug=True,
        verbose=True,
    )
    CLISettings(
        debug=True,
        project_name="advanced-app",
    )

    def validate_advanced_inputs(
        email: str, token: str, ipv6_addr: str
    ) -> FlextResult[None]:
        """Validate advanced input parameters."""
        import re

        # Constants for validation
        JWT_PARTS_COUNT = 3
        MIN_IPV6_LENGTH = 15

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return FlextResult.fail("Invalid email format")

        # Basic JWT validation (simplified)
        if not token or len(token.split(".")) != JWT_PARTS_COUNT:
            return FlextResult.fail("Invalid JWT token format")

        # Basic IPv6 validation (simplified)
        if ":" not in ipv6_addr or len(ipv6_addr) < MIN_IPV6_LENGTH:
            return FlextResult.fail("Invalid IPv6 address format")

        return FlextResult.ok(None)

    # Middleware and error handling patterns (would be implemented in actual CLI)
    def audit_middleware(data: dict[str, object]) -> dict[str, object]:
        """Add audit information to all commands."""
        data["audit"] = {
            "timestamp": "2025-07-25T10:30:00Z",
            "user": "current_user",
            "session": "abc123",
        }
        return data

    def custom_error_handler(exc: Exception) -> str:
        return f"🚨 Custom error handler: {exc}"

    def process_user_data(
        email: str,
        token: str,
        ipv6_addr: str,
    ) -> FlextResult[dict[str, object]]:
        """Process user data with comprehensive validation."""
        validation_result = validate_advanced_inputs(email, token, ipv6_addr)
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
        if format_type == "table":
            table_result = flext_cli_table(
                report_data.get("services", []), "System Report", "grid"
            )
            result = str(table_result.unwrap() if table_result.success else "No data")
        elif format_type == "json":
            result = str(format_output(report_data, "json"))
        else:
            format_result = flext_cli_format(report_data)
            result = str(format_result.unwrap() if format_result.success else "")

        return FlextResult.ok(result)

    # Functions demonstrate available patterns for CLI commands

    # Demonstrate usage

    # Test with valid data
    valid_jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    valid_ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    process_result = process_user_data("user@example.com", valid_jwt, valid_ipv6)
    if process_result.success:
        # Generate different report formats
        table_report = generate_report("table")
        if table_report.success:
            pass


def example_5_input_collection() -> None:
    """Example 5: Interactive input collection."""
    # This example shows how the input system would work
    # (In practice, this would require actual user interaction)

    # Interactive CLI configuration
    from flext_cli import CLISettings

    CLISettings(project_name="interactive-app")

    # Define input schema

    def create_user_interactive() -> FlextResult[dict[str, object]]:
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
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, collected_data["email"]):
            return FlextResult.fail("Invalid email format")

        return FlextResult.ok(
            {
                "user_created": True,
                "user_id": "user_12345",
                **collected_data,
            },
        )

    # Function demonstrates interactive input collection pattern

    # Demonstrate
    result = create_user_interactive()
    if result.success:
        format_output(result.unwrap(), "yaml")


def main() -> None:
    """Run all examples."""
    try:
        example_1_simple_cli()

        example_2_web_service_cli()

        example_3_database_management()

        example_4_advanced_features()

        example_5_input_collection()

    except (RuntimeError, ValueError, TypeError):
        pass


if __name__ == "__main__":
    main()
