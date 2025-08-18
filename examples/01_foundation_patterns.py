#!/usr/bin/env python3
"""01 - FLEXT-CLI Foundation Patterns.

This example demonstrates the core foundation patterns of flext-cli built on flext-core:

Key Patterns Demonstrated:
- FlextResult[T] railway-oriented programming for CLI error handling
- FlextModel integration with Pydantic for type-safe CLI models
- FlextContainer dependency injection for CLI services
- Foundation CLI entities (CLICommand, CLISession, CLIPlugin)
- Basic CLI configuration and setup patterns

Architecture Layers:
- Foundation: flext-core (FlextResult, FlextModel, FlextContainer)
- Domain: CLI entities with validation and business rules
- Infrastructure: Configuration and basic service patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextResult, get_flext_container
from rich.console import Console

from flext_cli import (
    CLIConfig,
    FlextCliCommand,
    FlextCliSession,
    FlextCliSessionState,
    get_cli_config,
    setup_cli,
)


def demonstrate_foundation_patterns() -> FlextResult[None]:
    """Demonstrate the foundation patterns of flext-cli."""
    console = Console()
    console.print("[bold blue]FLEXT-CLI Foundation Patterns Demo[/bold blue]")

    # 1. FlextResult Pattern for CLI Operations
    console.print("\n[green]1. FlextResult Pattern[/green]")
    setup_result = setup_cli()
    if setup_result.failure:
        return FlextResult.fail(f"Setup failed: {setup_result.error}")

    console.print("✅ CLI setup using FlextResult pattern")

    # 2. FlextModel-based Configuration
    console.print("\n[green]2. FlextModel Configuration[/green]")
    config = get_cli_config()
    console.print(f"✅ Config profile: {config.profile}")
    console.print(f"✅ Debug mode: {config.debug}")
    console.print(f"✅ Output format: {config.output.format}")

    # 3. FlextContainer Dependency Injection
    console.print("\n[green]3. FlextContainer DI Pattern[/green]")
    container = get_flext_container()

    # Register CLI services in the container
    container.register("console", console)
    container.register("config", config)

    # Retrieve services from container using FlextResult
    console_result = container.get("console")
    if console_result.success:
        console.print("✅ Console service retrieved from container")

    # 4. CLI Domain Entities with Validation
    console.print("\n[green]4. CLI Domain Entities[/green]")

    # Create CLI command using domain factory
    command_result = create_sample_command()
    if command_result.failure:
        return FlextResult.fail(f"Command creation failed: {command_result.error}")

    command = command_result.unwrap()
    console.print(f"✅ CLI Command: {command.name}")
    console.print(f"✅ Command status: {command.command_status}")

    # Create CLI session with state management
    session_result = create_sample_session(config)
    if session_result.failure:
        return FlextResult.fail(f"Session creation failed: {session_result.error}")

    session = session_result.unwrap()
    console.print(f"✅ CLI Session: {session.session_id}")
    console.print(f"✅ Session state: {session.session_state}")

    # 5. Domain Business Rules Validation
    console.print("\n[green]5. Domain Business Rules[/green]")

    # Validate command using business rules
    validation_result = command.validate_domain_rules()
    if validation_result.success:
        console.print("✅ Command passes domain validation")
    else:
        console.print(f"❌ Command validation failed: {validation_result.error}")

    # Demonstrate command execution lifecycle
    executed_command = command.start_execution()
    console.print(f"✅ Command execution started: {executed_command.command_status}")

    return FlextResult.ok(None)


def create_sample_command() -> FlextResult[FlextCliCommand]:
    """Create a sample CLI command using domain patterns."""
    try:
        # Create command with validation (factory pattern available but not used in this simple example)
        command = FlextCliCommand(
            name="demo-command",
            command_line="echo 'Hello FLEXT CLI'",
            description="Demonstration command for foundation patterns",
            working_directory=Path.cwd(),
        )

        return FlextResult.ok(command)

    except Exception as e:
        return FlextResult.fail(f"Failed to create command: {e}")


def create_sample_session(config: CLIConfig) -> FlextResult[FlextCliSession]:
    """Create a sample CLI session with configuration."""
    try:
        session = FlextCliSession(
            session_id="demo-session-001",
            session_state=FlextCliSessionState.ACTIVE,
            start_time=datetime.now(UTC),
            workspace_path=Path.cwd(),
            profile=config.profile,
        )

        return FlextResult.ok(session)

    except Exception as e:
        return FlextResult.fail(f"Failed to create session: {e}")


def main() -> None:
    """Main demonstration function."""
    console = Console()

    try:
        result = demonstrate_foundation_patterns()

        if result.success:
            console.print("\n[bold green]✅ Foundation patterns demonstration completed successfully![/bold green]")
        else:
            console.print(f"\n[bold red]❌ Demo failed: {result.error}[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")


if __name__ == "__main__":
    main()
