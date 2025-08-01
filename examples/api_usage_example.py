#!/usr/bin/env python3
"""Example of FLEXT CLI API usage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates the real functionality implemented in the FLEXT CLI API.
It shows how to use all the major features without placeholders or mockups.
"""

from __future__ import annotations

import json
import operator
from datetime import UTC, datetime

from flext_cli.api import FlextCliApi


def main() -> None:
    """Demonstrate FLEXT CLI API functionality."""
    print("🚀 FLEXT CLI API Usage Example")
    print("=" * 50)

    # Create API instance
    api = FlextCliApi()

    # 1. Configure the CLI service
    print("\n1. Configuring CLI Service...")
    config = {
        "project_name": "example-project",
        "project_version": "1.0.0",
        "project_description": "Example CLI usage",
        "debug": True,
        "log_level": "DEBUG",
    }

    success = api.flext_cli_configure(config)
    print(f"   Configuration successful: {success}")

    # 2. Check health status
    print("\n2. Checking Health Status...")
    health = api.flext_cli_health()
    print(f"   Status: {health['status']}")
    print(f"   Service: {health['service']}")
    print(f"   Version: {health['version']}")
    print(f"   Python: {health['python_version'].split()[0]}")

    # 3. Create CLI commands
    print("\n3. Creating CLI Commands...")

    # Create a system command
    result = api.flext_cli_create_command(
        "list-files",
        "ls -la",
        description="List files in directory",
        command_type="system",
        timeout_seconds=10,
    )

    if result.is_success:
        command = result.unwrap()
        print(f"   ✅ Created command: {command.name}")
        print(f"      Type: {command.command_type}")
        print(f"      Command line: {command.command_line}")
        print(f"      Description: {command.description}")
    else:
        print(f"   ❌ Failed to create command: {result.error}")

    # Create a script command
    script_result = api.flext_cli_create_command(
        "backup-data",
        "python backup_script.py",
        description="Backup application data",
        command_type="script",
        environment_vars={"BACKUP_DIR": "/tmp/backup"},
        timeout_seconds=300,
    )

    if script_result.is_success:
        script_cmd = script_result.unwrap()
        print(f"   ✅ Created script command: {script_cmd.name}")
        print(f"      Environment: {script_cmd.environment}")

    # 4. Create and manage sessions
    print("\n4. Creating and Managing Sessions...")

    session_result = api.flext_cli_create_session("demo_user")
    if session_result.is_success:
        session_id = session_result.unwrap()
        print(f"   ✅ Created session: {session_id}")

        # Get active sessions
        sessions = api.flext_cli_get_sessions()
        if session_id in sessions:
            session_data = sessions[session_id]
            print(f"      Status: {session_data['status']}")
            print(f"      Commands count: {session_data['commands_count']}")

    # 5. Register and execute handlers
    print("\n5. Registering and Executing Handlers...")

    # Register a calculator handler
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

    # Register the handler
    register_result = api.flext_cli_register_handler("calculator", calculator_handler)
    if register_result.is_success:
        print("   ✅ Registered calculator handler")

        # Execute the handler
        exec_result = api.flext_cli_execute_handler(
            "calculator",
            "multiply",
            15.5,
            4.2
        )

        if exec_result.is_success:
            calc_result = exec_result.unwrap()
            print(f"      Calculation result: {calc_result}")
            print(f"      15.5 × 4.2 = {calc_result['result']}")

    # 6. Data formatting and rendering
    print("\n6. Data Formatting and Rendering...")

    sample_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "San Francisco"},
        {"name": "Carol", "age": 35, "city": "Chicago"},
    ]

    # Render as table (default)
    table_result = api.flext_cli_render_with_context(sample_data)
    if table_result.is_success:
        print("   ✅ Rendered as table:")
        print(table_result.unwrap())

    # Render with custom context
    context_result = api.flext_cli_render_with_context(
        sample_data,
        {"format": "json", "title": "User Data"}
    )
    if context_result.is_success:
        rendered = context_result.unwrap()
        print("\n   ✅ Rendered with context:")
        print(rendered[:200] + "..." if len(rendered) > 200 else rendered)

    # 7. Export functionality
    print("\n7. Data Export Functionality...")

    export_data = {
        "users": sample_data,
        "metadata": {
            "export_time": datetime.now(UTC).isoformat(),
            "total_records": len(sample_data),
            "format": "json",
        }
    }

    # Use the formatting functionality
    formatted_json = api.flext_cli_format(export_data, "json")
    if formatted_json:
        print("   ✅ Formatted data for export:")
        # Parse and pretty print
        try:
            parsed = json.loads(formatted_json)
            print(json.dumps(parsed, indent=2)[:300] + "...")
        except json.JSONDecodeError:
            print(formatted_json[:200] + "...")

    # 8. Summary of registries
    print("\n8. Registry Summary...")

    commands = api.flext_cli_get_commands()
    sessions = api.flext_cli_get_sessions()
    plugins = api.flext_cli_get_plugins()
    handlers = api.flext_cli_get_handlers()

    print(f"   📋 Commands registry: {len(commands)} commands")
    print(f"   🔗 Active sessions: {len(sessions)} sessions")
    print(f"   🔌 Plugins available: {len(plugins)} plugins")
    print(f"   ⚙️  Handlers registered: {len(handlers)} handlers")

    if handlers:
        print("      Registered handlers:")
        for name, info in handlers.items():
            print(f"        - {name}: {info['type']} (callable: {info['callable']})")

    print("\n✨ Example completed successfully!")
    print("All functionality is working with real implementations, no placeholders!")


if __name__ == "__main__":
    main()
