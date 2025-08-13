#!/usr/bin/env python3
"""Example of FLEXT CLI API usage.

This example demonstrates the real functionality implemented in the FLEXT CLI API.
It shows how to use all the major features without placeholders or mockups.

REFACTORED: Applied Single Responsibility Principle (SRP) from SOLID.
Each function now has a single, focused responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import operator
import tempfile
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from flext_cli.api import FlextCliApi

if TYPE_CHECKING:
    from flext_cli.domain.entities import CLICommand

# Constants
PREVIEW_LENGTH_LIMIT = 200


class FlextCliDemoRunner:
    """Demo runner following SOLID principles for reduced complexity."""

    def __init__(self) -> None:
        """Initialize demo runner with API instance."""
        self.api = FlextCliApi()

    def configure_service(self) -> bool:
        """Configure the CLI service with demo settings."""
        print("\n1. Configuring CLI Service...")
        config = {
            "project_name": "example-project",
            "project_version": "1.0.0",
            "project_description": "Example CLI usage",
            "debug": True,
            "log_level": "DEBUG",
        }

        success = self.api.flext_cli_configure(config)
        print(f"   Configuration successful: {success}")
        return success

    def check_health_status(self) -> dict[str, object]:
        """Check and display health status."""
        print("\n2. Checking Health Status...")
        health = self.api.flext_cli_health()
        print(f"   Status: {health['status']}")
        print(f"   Service: {health['service']}")
        print(f"   Version: {health['version']}")
        python_version = health["python_version"]
        if isinstance(python_version, str):
            print(f"   Python: {python_version.split()[0]}")
        else:
            print(f"   Python: {python_version}")
        return health

    def create_demo_commands(self) -> tuple[bool, bool]:
        """Create demonstration CLI commands."""
        print("\n3. Creating CLI Commands...")

        # Create system command
        result = self.api.flext_cli_create_command(
            "list-files",
            "ls -la",
            description="List files in directory",
            command_type="system",
            timeout_seconds=10,
        )

        system_success = False
        if result.success:
            command = cast("CLICommand", result.data)  # Cast to proper type
            print(f"   ✅ Created command: {command.name}")
            print(f"      Type: {command.command_type}")
            print(f"      Command line: {command.command_line}")
            print(f"      Description: {command.description}")
            system_success = True
        else:
            print(f"   ❌ Failed to create command: {result.error}")

        # Create script command using secure temporary directory

        secure_backup_dir = tempfile.mkdtemp(prefix="backup_")

        script_result = self.api.flext_cli_create_command(
            "backup-data",
            "python backup_script.py",
            description="Backup application data",
            command_type="script",
            environment_vars={"BACKUP_DIR": secure_backup_dir},
            timeout_seconds=300,
        )

        script_success = False
        if script_result.success:
            script_cmd = cast("CLICommand", script_result.data)  # Cast to proper type
            print(f"   ✅ Created script command: {script_cmd.name}")
            print(f"      Environment: {script_cmd.environment}")
            script_success = True

        return system_success, script_success

    def manage_sessions(self) -> str | None:
        """Create and manage demo sessions."""
        print("\n4. Creating and Managing Sessions...")

        session_result = self.api.flext_cli_create_session("demo_user")
        if session_result.success:
            session_id = session_result.unwrap()
            print(f"   ✅ Created session: {session_id}")

            # Get active sessions
            sessions = self.api.flext_cli_get_sessions()
            if session_id in sessions:
                session_data = sessions[session_id]
                print(f"      Status: {session_data['status']}")
                print(f"      Commands count: {session_data['commands_count']}")

            return session_id
        return None

    def _create_calculator_handler(self) -> callable:
        """Create calculator handler function."""

        def calculator_handler(operation: str, a: float, b: float) -> dict[str, object]:
            """Simple calculator handler."""
            operations = {
                "add": operator.add,
                "subtract": operator.sub,
                "multiply": operator.mul,
                "divide": lambda x, y: x / y if y != 0 else None,
            }

            if operation not in operations:
                return {"error": f"Unknown operation: {operation}"}

            result = operations[operation](a, b)
            return {
                "operation": operation,
                "operands": [a, b],
                "result": result,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return calculator_handler

    def register_and_execute_handlers(self) -> bool:
        """Register and execute demonstration handlers."""
        print("\n5. Registering and Executing Handlers...")

        calculator_handler = self._create_calculator_handler()

        # Register the handler
        register_result = self.api.flext_cli_register_handler(
            "calculator", calculator_handler,
        )
        if register_result.success:
            print("   ✅ Registered calculator handler")

            # Execute the handler
            exec_result = self.api.flext_cli_execute_handler(
                "calculator", "multiply", 15.5, 4.2,
            )

            if exec_result.success:
                calc_result = exec_result.unwrap()
                print(f"      Calculation result: {calc_result}")
                print(f"      15.5 * 4.2 = {calc_result['result']}")
                return True

        return False

    def _get_sample_data(self) -> list[dict[str, object]]:
        """Get sample data for demonstrations."""
        return [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "San Francisco"},
            {"name": "Carol", "age": 35, "city": "Chicago"},
        ]

    def demonstrate_formatting(self) -> bool:
        """Demonstrate data formatting and rendering capabilities."""
        print("\n6. Data Formatting and Rendering...")

        sample_data = self._get_sample_data()

        # Render as table (default)
        table_result = self.api.flext_cli_render_with_context(sample_data)
        if table_result.success:
            print("   ✅ Rendered as table:")
            print(table_result.unwrap())

            # Render with custom context
            context_result = self.api.flext_cli_render_with_context(
                sample_data, {"format": "json", "title": "User Data"},
            )
            if context_result.success:
                rendered = context_result.unwrap()
                print("\n   ✅ Rendered with context:")
                preview = (
                    rendered[:PREVIEW_LENGTH_LIMIT] + "..."
                    if len(rendered) > PREVIEW_LENGTH_LIMIT
                    else rendered
                )
                print(preview)
                return True

        return False

    def demonstrate_export(self) -> bool:
        """Demonstrate data export functionality."""
        print("\n7. Data Export Functionality...")

        sample_data = self._get_sample_data()
        export_data = {
            "users": sample_data,
            "metadata": {
                "export_time": datetime.now(UTC).isoformat(),
                "total_records": len(sample_data),
                "format": "json",
            },
        }

        # Use the formatting functionality
        formatted_json = self.api.flext_cli_format(export_data, "json")
        if formatted_json:
            print("   ✅ Formatted data for export:")
            # Parse and pretty print
            try:
                parsed = json.loads(formatted_json)
                print(json.dumps(parsed, indent=2)[:300] + "...")
                return True
            except json.JSONDecodeError:
                print(formatted_json[:200] + "...")
                return True

        return False

    def show_registry_summary(self) -> None:
        """Show summary of all registries."""
        print("\n8. Registry Summary...")

        commands = self.api.flext_cli_get_commands()
        sessions = self.api.flext_cli_get_sessions()
        plugins = self.api.flext_cli_get_plugins()
        handlers = self.api.flext_cli_get_handlers()

        print(f"   📋 Commands registry: {len(commands)} commands")
        print(f"   🔗 Active sessions: {len(sessions)} sessions")
        print(f"   🔌 Plugins available: {len(plugins)} plugins")
        print(f"   ⚙️  Handlers registered: {len(handlers)} handlers")

        if handlers:
            print("      Registered handlers:")
            for name, info in handlers.items():
                print(
                    f"        - {name}: {info['type']} (callable: {info['callable']})",
                )

    def run_complete_demo(self) -> bool:
        """Run the complete demonstration workflow."""
        print("🚀 FLEXT CLI API Usage Example")
        print("=" * 50)

        # Execute all demo steps
        success_flags = [
            self.configure_service(),
            bool(self.check_health_status()),
            any(self.create_demo_commands()),
            self.manage_sessions() is not None,
            self.register_and_execute_handlers(),
            self.demonstrate_formatting(),
            self.demonstrate_export(),
        ]

        self.show_registry_summary()

        success = all(success_flags)
        if success:
            print("\n✨ Example completed successfully!")
            print(
                "All functionality is working with real implementations, "
                "no placeholders!",
            )
        else:
            print("\n⚠️  Some demo steps failed. Check the output above.")

        return success


def main() -> None:
    """Run FLEXT CLI API demonstration using SOLID principles."""
    demo_runner = FlextCliDemoRunner()
    demo_runner.run_complete_demo()


if __name__ == "__main__":
    main()
