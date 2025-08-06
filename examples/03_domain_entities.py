#!/usr/bin/env python3
"""FLEXT CLI Library Domain Entities Example.

This example demonstrates how to use the domain entities provided by the
FLEXT CLI library for modeling CLI commands, sessions, and plugins in a
domain-driven design approach.

Key features demonstrated:
- CLI command lifecycle management
- CLI session tracking with command history
- CLI plugin management with dependencies
- Domain events for CLI operations
- Business rule validation
- Entity state transitions

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from uuid import uuid4

import flext_cli
from rich.console import Console
from rich.table import Table


def demonstrate_cli_commands() -> None:
    """Demonstrate CLI command entity usage."""
    console = Console()
    console.print("[bold blue]CLI Command Entity Demo[/bold blue]\n")

    # Note: CLI entities require an ID - in real usage, this would come from
    # your ID generation strategy or database
    str(uuid4())

    # Create a CLI command (would normally use a factory or repository)
    try:
        # For demonstration, we'll show the structure without full instantiation
        # since the entities require proper ID management from flext-core
        console.print("🔧 CLI Command Structure:")
        console.print("   - name: Command identifier")
        console.print("   - command_line: Actual command to execute")
        console.print(
            "   - command_type: system, pipeline, plugin, data, config, auth, "
            "monitoring"
        )
        console.print("   - arguments: Command arguments dictionary")
        console.print("   - options: Command options dictionary")
        console.print(
            "   - command_status: pending, running, completed, failed, cancelled"
        )
        console.print("   - exit_code: Process exit code")
        console.print("   - stdout/stderr: Command output")
        console.print(
            "   - execution timing: started_at, completed_at, duration_seconds"
        )
        console.print(
            "   - context: user_id, session_id, working_directory, environment"
        )
        console.print()

        # Show command types
        console.print("📋 Available Command Types:")
        for cmd_type in flext_cli.CommandType:
            console.print(f"   - {cmd_type.value}")
        console.print()

        # Show command statuses
        console.print("📊 Available Command Statuses:")
        for status in flext_cli.CommandStatus:
            console.print(f"   - {status.value}")
        console.print()

        console.print("✨ Command lifecycle methods:")
        console.print(
            "   - start_execution(): Set status to running, record start time"
        )
        console.print(
            "   - complete_execution(): Set final status, record completion, "
            "calculate duration"
        )
        console.print("   - cancel_execution(): Cancel command, record completion time")
        console.print("   - is_completed: Property to check if execution finished")
        console.print("   - successful: Property to check if completed successfully")
        console.print()

    except (RuntimeError, ValueError, TypeError) as e:
        console.print(
            f"[yellow]Note: Full entity instantiation requires ID management: "
            f"{e}[/yellow]"
        )
        console.print("In production, use proper entity factories or repositories.")
        console.print()


def demonstrate_cli_sessions() -> None:
    """Demonstrate CLI session entity usage."""
    console = Console()
    console.print("[bold blue]CLI Session Entity Demo[/bold blue]\n")

    console.print("🔧 CLI Session Structure:")
    console.print("   - session_id: Unique session identifier")
    console.print("   - user_id: Optional user identifier")
    console.print("   - started_at: Session start timestamp")
    console.print("   - last_activity: Last activity timestamp")
    console.print("   - working_directory: Session working directory")
    console.print("   - environment: Environment variables dictionary")
    console.print("   - commands_executed: List of command IDs")
    console.print("   - current_command: Currently executing command ID")
    console.print("   - active: Session active status")
    console.print()

    console.print("✨ Session management methods:")
    console.print("   - add_command(): Add command to session and update activity")
    console.print("   - end_session(): Deactivate session and clear current command")
    console.print()


def demonstrate_cli_plugins() -> None:
    """Demonstrate CLI plugin entity usage."""
    console = Console()
    console.print("[bold blue]CLI Plugin Entity Demo[/bold blue]\n")

    console.print("🔧 CLI Plugin Structure:")
    console.print("   - name: Plugin identifier")
    console.print("   - version: Plugin version")
    console.print("   - description: Plugin description")
    console.print("   - entry_point: Plugin entry point module.function")
    console.print("   - commands: List of commands provided by plugin")
    console.print("   - enabled: Plugin enabled status")
    console.print("   - installed: Plugin installation status")
    console.print("   - dependencies: List of plugin dependencies")
    console.print("   - author: Plugin author")
    console.print("   - license: Plugin license")
    console.print("   - repository_url: Plugin repository URL")
    console.print()

    console.print("✨ Plugin lifecycle methods:")
    console.print("   - enable(): Enable the plugin")
    console.print("   - disable(): Disable the plugin")
    console.print("   - install(): Mark plugin as installed")
    console.print("   - uninstall(): Uninstall and disable plugin")
    console.print()


def demonstrate_domain_events() -> None:
    """Demonstrate domain events for CLI operations."""
    console = Console()
    console.print("[bold blue]Domain Events Demo[/bold blue]\n")

    console.print("📨 Available Domain Events:")

    events_table = Table(title="CLI Domain Events")
    events_table.add_column("Event", style="cyan")
    events_table.add_column("Purpose", style="green")
    events_table.add_column("Key Fields", style="yellow")

    events_table.add_row(
        "CommandStartedEvent",
        "Raised when command starts execution",
        "command_id, command_name, session_id",
    )
    events_table.add_row(
        "CommandCompletedEvent",
        "Raised when command completes",
        "command_id, command_name, success",
    )
    events_table.add_row(
        "CommandCancelledEvent",
        "Raised when command is cancelled",
        "command_id, command_name",
    )
    events_table.add_row(
        "ConfigUpdatedEvent",
        "Raised when configuration is updated",
        "config_id, config_name",
    )
    events_table.add_row(
        "SessionStartedEvent",
        "Raised when CLI session starts",
        "session_id, user_id, working_directory",
    )
    events_table.add_row(
        "SessionEndedEvent",
        "Raised when CLI session ends",
        "session_id, user_id, commands_executed, duration_seconds",
    )
    events_table.add_row(
        "PluginInstalledEvent",
        "Raised when plugin is installed",
        "plugin_id, plugin_name",
    )
    events_table.add_row(
        "PluginUninstalledEvent",
        "Raised when plugin is uninstalled",
        "plugin_id, plugin_name",
    )

    console.print(events_table)
    console.print()

    console.print("💡 Events are FlextValueObjects that can be:")
    console.print("   - Published to event buses")
    console.print("   - Stored for audit trails")
    console.print("   - Used for integration with other systems")
    console.print("   - Processed by event handlers for side effects")
    console.print()


def demonstrate_business_rules() -> None:
    """Demonstrate business rule validation."""
    console = Console()
    console.print("[bold blue]Business Rules Validation Demo[/bold blue]\n")

    console.print("🔒 Entity Validation Rules:")
    console.print()

    console.print("📋 CLI Command Rules:")
    console.print("   - Command name cannot be empty")
    console.print("   - Command line cannot be empty")
    console.print("   - Duration must be positive when set")
    console.print()

    console.print("👥 CLI Session Rules:")
    console.print("   - Session ID cannot be empty")
    console.print("   - Last activity cannot be before session start")
    console.print("   - Current command must be in executed commands list")
    console.print()

    console.print("🔌 CLI Plugin Rules:")
    console.print("   - Plugin name cannot be empty")
    console.print("   - Entry point cannot be empty")
    console.print("   - Version cannot be empty")
    console.print()

    console.print("🎛️ CLI Context Rules:")
    console.print("   - Profile cannot be empty")
    console.print("   - Output format must be valid (table, json, yaml, csv, plain)")
    console.print("   - Cannot have both quiet and verbose modes enabled")
    console.print()

    console.print("💡 All entities implement validate_domain_rules() method")
    console.print("   This ensures business rules are enforced at the domain level")
    console.print()


def demonstrate_practical_usage() -> None:
    """Show practical usage patterns for the domain entities."""
    console = Console()
    console.print("[bold blue]Practical Usage Patterns[/bold blue]\n")

    console.print("🏗️ Typical Integration Patterns:")
    console.print()

    console.print("1. **Command Execution Service**:")
    console.print("   ```python")
    console.print("   # Create command entity")
    console.print(
        "   command = CLICommand(name='deploy', "
        "command_line='kubectl apply -f app.yaml')"
    )
    console.print("   command.start_execution()")
    console.print("   ")
    console.print("   # Execute actual command")
    console.print("   result = subprocess.run(command.command_line, ...)")
    console.print("   ")
    console.print("   # Complete execution")
    console.print(
        "   command.complete_execution(result.returncode, result.stdout, result.stderr)"
    )
    console.print("   ```")
    console.print()

    console.print("2. **Session Management**:")
    console.print("   ```python")
    console.print("   # Start session")
    console.print("   session = CLISession(session_id=generate_session_id())")
    console.print("   ")
    console.print("   # Track commands")
    console.print("   session.add_command(command.id)")
    console.print("   ")
    console.print("   # End session")
    console.print("   session.end_session()")
    console.print("   ```")
    console.print()

    console.print("3. **Plugin System**:")
    console.print("   ```python")
    console.print("   # Register plugin")
    console.print("   plugin = CLIPlugin(")
    console.print("       name='kubernetes-plugin',")
    console.print("       entry_point='k8s_plugin.main',")
    console.print("       commands=['deploy', 'scale', 'rollback']")
    console.print("   )")
    console.print("   plugin.install()")
    console.print("   plugin.enable()")
    console.print("   ```")
    console.print()

    console.print("4. **Event-Driven Architecture**:")
    console.print("   ```python")
    console.print("   # Publish events")
    console.print(
        "   event = CommandStartedEvent(command_id=command.id, "
        "command_name=command.name)"
    )
    console.print("   event_bus.publish(event)")
    console.print("   ```")
    console.print()


def main() -> None:
    """Run the domain entities demonstration."""
    console = Console()
    console.print(
        "[bold green]🏗️ FLEXT CLI Library Domain Entities Example[/bold green]\n"
    )

    demonstrate_cli_commands()
    demonstrate_cli_sessions()
    demonstrate_cli_plugins()
    demonstrate_domain_events()
    demonstrate_business_rules()
    demonstrate_practical_usage()

    console.print("[bold green]✨ Domain entities example completed![/bold green]")
    console.print("\n💡 These entities provide the foundation for building")
    console.print("   enterprise-grade CLI applications with proper domain modeling.")


if __name__ == "__main__":
    main()
