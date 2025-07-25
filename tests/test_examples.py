"""Practical examples demonstrating FlextCli library usage.

Complete examples showing the power of the FlextCli library:
- Zero-boilerplate CLI creation
- Advanced validation patterns
- Multiple output formats
- Interactive input collection
- Real-world use cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import patch

from flext_cli import (
    FlextCliBuilder,
    FlextCliFormatter,
    FlextCliInput,
    flext_cli_create_builder,
    flext_cli_format_output,
    flext_cli_quick_commands,
    flext_cli_validate_inputs,
)
from flext_core import FlextResult


class TestBasicExamples:
    """Basic usage examples for FlextCli library."""

    def test_minimal_cli_example(self) -> None:
        """Example: Create minimal CLI with zero boilerplate."""
        # Create CLI builder
        cli = flext_cli_create_builder("myapp", version="1.0.0")

        # Add simple command
        def hello() -> str:
            return "Hello, World!"

        cli.add_command("hello", hello, help="Say hello")

        # Verify setup
        assert cli.name == "myapp"
        assert "hello" in cli._commands
        assert cli._commands["hello"].help == "Say hello"

    def test_quick_commands_example(self) -> None:
        """Example: Ultra-fast CLI from command dictionary."""
        commands = {
            "version": lambda: "myapp v1.0.0",
            "status": lambda: "All systems operational",
            "help": lambda: "Available commands: version, status, help",
        }

        # This would normally run the CLI, but we'll test the structure
        with patch("flext_cli.core.builder.FlextCliBuilder.run") as mock_run:
            mock_run.return_value = FlextResult.ok(None)
            result = flext_cli_quick_commands(commands, name="quickapp")
            assert result.success

    def test_validation_patterns_example(self) -> None:
        """Example: Input validation with built-in patterns."""
        # Create validator with multiple patterns
        validator = flext_cli_validate_inputs(
            email="email",
            url="url",
            port=lambda x: 1 <= int(x) <= 65535,
            username="username",
        )

        # Test validations
        result = validator.validate("email", "user@example.com")
        assert result.success

        result = validator.validate("port", "8080")
        assert result.success

        result = validator.validate("username", "valid_user123")
        assert result.success

    def test_output_formatting_example(self) -> None:
        """Example: Format data in multiple styles."""
        data = {
            "name": "Alice Johnson",
            "role": "Developer",
            "projects": ["API", "Dashboard", "Mobile App"],
            "active": True,
        }

        # JSON format
        result = flext_cli_format_output(data, "json")
        assert result.success
        json_output = result.unwrap()
        assert "Alice Johnson" in json_output
        assert "Developer" in json_output

        # YAML format
        result = flext_cli_format_output(data, "yaml")
        assert result.success
        yaml_output = result.unwrap()
        assert "name: Alice Johnson" in yaml_output

        # Table format for list data
        table_data = [
            {"name": "Alice", "role": "Developer"},
            {"name": "Bob", "role": "Designer"},
        ]
        result = flext_cli_format_output(table_data, "table")
        assert result.success
        table_output = result.unwrap()
        assert "Alice" in table_output
        assert "|" in table_output


class TestAdvancedExamples:
    """Advanced usage examples demonstrating complex scenarios."""

    def test_user_management_cli_example(self) -> None:
        """Example: User management CLI with validation and formatting."""
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
        result = create_user("alice123", "alice@example.com", "admin")
        assert result.success
        user_data = result.unwrap()
        assert user_data["username"] == "alice123"
        assert user_data["role"] == "admin"

    def test_configuration_tool_example(self) -> None:
        """Example: Configuration management tool with interactive input."""
        cli = FlextCliBuilder(name="config-tool", description="Configuration Manager")

        def configure_database():
            """Interactive database configuration."""
            input_collector = FlextCliInput()

            # Define configuration schema
            schema = {
                "host": {
                    "type": str,
                    "prompt": "Database host",
                    "default": "localhost",
                    "validator": "url",
                },
                "port": {
                    "type": int,
                    "prompt": "Database port",
                    "default": 5432,
                    "min_value": 1,
                    "max_value": 65535,
                },
                "database": {
                    "type": str,
                    "prompt": "Database name",
                    "required": True,
                },
                "username": {
                    "type": str,
                    "prompt": "Username",
                    "validator": "username",
                },
                "password": {
                    "type": str,
                    "prompt": "Password",
                    "password": True,
                    "confirm": True,
                },
                "ssl_enabled": {
                    "type": bool,
                    "prompt": "Enable SSL?",
                    "default": True,
                },
            }

            # Mock the interactive collection for testing
            with patch.object(input_collector, "collect_dict") as mock_collect:
                mock_collect.return_value = {
                    "host": "https://db.example.com",
                    "port": 5432,
                    "database": "myapp",
                    "username": "dbuser",
                    "password": "secret123",
                    "ssl_enabled": True,
                }

                config = input_collector.collect_dict(schema)

                # Format as YAML for configuration file
                formatter = FlextCliFormatter(style="yaml")
                config_yaml = formatter.format(config, "Database Configuration")

                return FlextResult.ok({
                    "config": config,
                    "yaml": config_yaml,
                })

        cli.add_command("db", configure_database, help="Configure database")

        # Test the configuration
        result = configure_database()
        assert result.success
        data = result.unwrap()
        assert data["config"]["host"] == "https://db.example.com"
        assert "Database Configuration" in data["yaml"]

    def test_api_testing_tool_example(self) -> None:
        """Example: API testing tool with multiple output formats."""
        cli = FlextCliBuilder(name="api-test", description="API Testing Tool")

        # Set up web-related validation
        cli.set_validator(
            url="url",
            method=lambda x: x.upper() in ["GET", "POST", "PUT", "DELETE"],
            timeout=lambda x: 1 <= int(x) <= 300,
        )

        def test_api(url: str, method: str = "GET", timeout: int = 30):
            """Test API endpoint."""
            # Validate inputs
            validation_result = cli.validate_data({
                "url": url,
                "method": method,
                "timeout": timeout,
            })

            if not validation_result.success:
                return FlextResult.fail(validation_result.error)

            # Mock API response for testing
            mock_response = {
                "request": {
                    "url": url,
                    "method": method.upper(),
                    "timeout": timeout,
                },
                "response": {
                    "status_code": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Server": "nginx/1.18",
                    },
                    "body": {"message": "API is working", "timestamp": "2025-01-15T10:30:00Z"},
                    "response_time_ms": 145,
                },
                "test_result": {
                    "success": True,
                    "assertions_passed": 3,
                    "assertions_failed": 0,
                },
            }

            return FlextResult.ok(mock_response)

        cli.add_command("test", test_api, help="Test API endpoint")
        cli.add_option("--url", command_name="test", required=True, help="API URL")
        cli.add_option("--method", command_name="test", default="GET", help="HTTP method")
        cli.add_option("--timeout", command_name="test", type=int, default=30, help="Request timeout")

        # Test with valid inputs
        result = test_api("https://api.example.com/users", "GET", 15)
        assert result.success

        response_data = result.unwrap()
        assert response_data["request"]["url"] == "https://api.example.com/users"
        assert response_data["response"]["status_code"] == 200
        assert response_data["test_result"]["success"] is True

    def test_deployment_tool_example(self) -> None:
        """Example: Deployment tool with environment validation."""
        cli = FlextCliBuilder(name="deploy", description="Deployment Tool")

        # Custom validation for deployment environments
        def validate_environment(env: str) -> bool:
            return env in ["development", "staging", "production"]

        def validate_version(version: str) -> bool:
            import re
            # Semantic version pattern
            pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
            return bool(re.match(pattern, version))

        cli.set_validator(
            environment=validate_environment,
            version=validate_version,
            service="slug",  # Built-in slug pattern
        )

        def deploy_service(service: str, version: str, environment: str):
            """Deploy service to environment."""
            # Validation happens automatically in CLI wrapper

            deployment_plan = {
                "service": service,
                "version": version,
                "environment": environment,
                "timestamp": "2025-01-15T10:30:00Z",
                "steps": [
                    {"step": 1, "action": "validate_version", "status": "completed"},
                    {"step": 2, "action": "build_image", "status": "completed"},
                    {"step": 3, "action": "push_registry", "status": "completed"},
                    {"step": 4, "action": "update_deployment", "status": "in_progress"},
                    {"step": 5, "action": "health_check", "status": "pending"},
                ],
                "estimated_completion": "2025-01-15T10:35:00Z",
            }

            return FlextResult.ok(deployment_plan)

        cli.add_command("deploy", deploy_service, help="Deploy service")
        cli.add_option("--service", command_name="deploy", required=True, help="Service name")
        cli.add_option("--version", command_name="deploy", required=True, help="Version to deploy")
        cli.add_option("--environment", command_name="deploy", required=True, help="Target environment")

        # Test deployment
        result = deploy_service("user-api", "1.2.3", "staging")
        assert result.success

        plan = result.unwrap()
        assert plan["service"] == "user-api"
        assert plan["version"] == "1.2.3"
        assert plan["environment"] == "staging"
        assert len(plan["steps"]) == 5


class TestRealWorldScenarios:
    """Real-world scenarios showing practical FlextCli usage."""

    def test_database_migration_tool(self) -> None:
        """Example: Database migration management tool."""
        cli = FlextCliBuilder(name="migrate", description="Database Migration Tool")

        # Database connection validation
        cli.set_validator(
            connection_string=lambda x: "://" in x and len(x) > 10,
            migration_name="slug",
        )

        def create_migration(name: str, description: str = ""):
            """Create new database migration."""
            import uuid
            from datetime import datetime

            migration_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{migration_id}_{name}.sql"

            migration_data = {
                "id": migration_id,
                "name": name,
                "description": description,
                "filename": filename,
                "created_at": datetime.now().isoformat(),
                "applied": False,
                "rollback_available": True,
                "sql_preview": f"-- Migration: {name}\n-- Description: {description}\n\n-- Add your SQL here\n",
            }

            return FlextResult.ok(migration_data)

        def list_migrations():
            """List all migrations with status."""
            migrations = [
                {"id": "abc12345", "name": "create-users-table", "applied": True, "date": "2025-01-10"},
                {"id": "def67890", "name": "add-user-roles", "applied": True, "date": "2025-01-12"},
                {"id": "ghi13579", "name": "create-projects-table", "applied": False, "date": "2025-01-15"},
            ]

            return FlextResult.ok(migrations)

        cli.add_command("create", create_migration, help="Create new migration")
        cli.add_option("--name", command_name="create", required=True, help="Migration name")
        cli.add_option("--description", command_name="create", help="Migration description")

        cli.add_command("list", list_migrations, help="List all migrations")

        # Test migration creation
        result = create_migration("add-user-indexes", "Add database indexes for user queries")
        assert result.success

        migration = result.unwrap()
        assert migration["name"] == "add-user-indexes"
        assert "add-user-indexes" in migration["filename"]
        assert migration["applied"] is False

        # Test migration listing
        result = list_migrations()
        assert result.success

        migrations = result.unwrap()
        assert len(migrations) == 3
        assert migrations[0]["applied"] is True
        assert migrations[2]["applied"] is False

    def test_log_analysis_tool(self) -> None:
        """Example: Log analysis and monitoring tool."""
        cli = FlextCliBuilder(name="loganalyzer", description="Log Analysis Tool")

        def analyze_logs(log_level: str = "INFO", time_range: str = "24h"):
            """Analyze application logs."""
            # Mock log analysis results
            analysis_results = {
                "summary": {
                    "total_entries": 15420,
                    "time_range": time_range,
                    "log_level_filter": log_level,
                    "analysis_duration_ms": 1250,
                },
                "log_levels": {
                    "ERROR": 23,
                    "WARN": 156,
                    "INFO": 12890,
                    "DEBUG": 2351,
                },
                "top_errors": [
                    {"message": "Database connection timeout", "count": 12, "last_seen": "2025-01-15T09:45:00Z"},
                    {"message": "Invalid user credentials", "count": 8, "last_seen": "2025-01-15T10:15:00Z"},
                    {"message": "External API rate limit exceeded", "count": 3, "last_seen": "2025-01-15T08:30:00Z"},
                ],
                "performance_metrics": {
                    "avg_response_time_ms": 245,
                    "slowest_endpoint": "/api/reports/generate",
                    "fastest_endpoint": "/api/health",
                    "requests_per_second": 125.5,
                },
                "recommendations": [
                    "Consider increasing database connection pool size",
                    "Implement retry logic for external API calls",
                    "Add caching for report generation endpoint",
                ],
            }

            return FlextResult.ok(analysis_results)

        def export_report(format: str = "json", output_file: str = ""):
            """Export analysis report."""
            # Mock export data
            report_data = {
                "export_info": {
                    "format": format,
                    "output_file": output_file or f"log_report.{format}",
                    "generated_at": "2025-01-15T10:30:00Z",
                    "file_size_kb": 245,
                },
                "status": "completed",
            }

            return FlextResult.ok(report_data)

        cli.add_command("analyze", analyze_logs, help="Analyze application logs")
        cli.add_option("--log-level", command_name="analyze", default="INFO", help="Minimum log level")
        cli.add_option("--time-range", command_name="analyze", default="24h", help="Time range to analyze")

        cli.add_command("export", export_report, help="Export analysis report")
        cli.add_option("--format", command_name="export", default="json", help="Export format")
        cli.add_option("--output-file", command_name="export", help="Output file path")

        # Test log analysis
        result = analyze_logs("ERROR", "12h")
        assert result.success

        analysis = result.unwrap()
        assert analysis["summary"]["log_level_filter"] == "ERROR"
        assert analysis["summary"]["time_range"] == "12h"
        assert len(analysis["top_errors"]) == 3
        assert "recommendations" in analysis

        # Test report export
        result = export_report("yaml", "error_report.yaml")
        assert result.success

        export_info = result.unwrap()
        assert export_info["export_info"]["format"] == "yaml"
        assert export_info["export_info"]["output_file"] == "error_report.yaml"
        assert export_info["status"] == "completed"

    def test_system_monitoring_dashboard(self) -> None:
        """Example: System monitoring and alerting tool."""
        cli = FlextCliBuilder(name="monitor", description="System Monitoring Tool")

        def system_status():
            """Get comprehensive system status."""
            status_data = {
                "timestamp": "2025-01-15T10:30:00Z",
                "overall_health": "healthy",
                "services": {
                    "web_server": {"status": "running", "cpu": 15.5, "memory": 512, "uptime": "5d 12h"},
                    "database": {"status": "running", "cpu": 8.2, "memory": 1024, "uptime": "12d 3h"},
                    "redis": {"status": "running", "cpu": 2.1, "memory": 128, "uptime": "12d 3h"},
                    "worker_queue": {"status": "degraded", "cpu": 45.8, "memory": 756, "uptime": "2d 15h"},
                },
                "system_metrics": {
                    "cpu_usage": 18.5,
                    "memory_usage": 62.3,
                    "disk_usage": 45.8,
                    "network_io": {"in": "125 MB/s", "out": "89 MB/s"},
                },
                "alerts": [
                    {"level": "warning", "service": "worker_queue", "message": "High CPU usage detected"},
                    {"level": "info", "service": "database", "message": "Connection pool at 80% capacity"},
                ],
            }

            return FlextResult.ok(status_data)

        def health_check(service: str = ""):
            """Run health check on specific service or all services."""
            if service:
                health_data = {
                    "service": service,
                    "status": "healthy",
                    "checks": [
                        {"name": "connectivity", "status": "pass", "duration_ms": 5},
                        {"name": "response_time", "status": "pass", "duration_ms": 120},
                        {"name": "resource_usage", "status": "pass", "duration_ms": 15},
                    ],
                    "overall_duration_ms": 140,
                }
            else:
                health_data = {
                    "overall_status": "degraded",
                    "services_checked": 4,
                    "services_healthy": 3,
                    "services_degraded": 1,
                    "services_down": 0,
                    "total_duration_ms": 450,
                }

            return FlextResult.ok(health_data)

        cli.add_command("status", system_status, help="Show system status")
        cli.add_command("health", health_check, help="Run health checks")
        cli.add_option("--service", command_name="health", help="Specific service to check")

        # Test system status
        result = system_status()
        assert result.success

        status = result.unwrap()
        assert status["overall_health"] == "healthy"
        assert len(status["services"]) == 4
        assert status["services"]["worker_queue"]["status"] == "degraded"
        assert len(status["alerts"]) == 2

        # Test service-specific health check
        result = health_check("database")
        assert result.success

        health = result.unwrap()
        assert health["service"] == "database"
        assert health["status"] == "healthy"
        assert len(health["checks"]) == 3

        # Test overall health check
        result = health_check()
        assert result.success

        overall_health = result.unwrap()
        assert overall_health["overall_status"] == "degraded"
        assert overall_health["services_healthy"] == 3
        assert overall_health["services_degraded"] == 1
