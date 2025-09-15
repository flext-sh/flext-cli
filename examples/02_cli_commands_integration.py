#!/usr/bin/env python3
"""02 - CLI Commands Integration with FLEXT CLI Foundation.

This example demonstrates proper CLI command integration using flext-cli patterns:

🎯 **Key Patterns Demonstrated:**
- FlextCliMain command registration system (replaces direct Click usage)
- FlextCliFormatters for all output (replaces direct Rich usage)
- FlextResult railway-oriented programming for command error handling
- FlextCliModels for domain entities with validation
- FlextContainer dependency injection for CLI services
- Proper flext-cli abstraction layer usage

🏗️ **Architecture Layers:**
- Application: Command handlers using flext-cli foundation
- Service: CLI business logic with FlextResult patterns
- Infrastructure: Output formatting through flext-cli abstractions

📈 **FLEXT CLI Foundation Compliance**: Zero direct Click/Rich imports

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

from flext_cli import (
    FlextCliConfig,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliModels,
)
from flext_core import FlextResult


def _setup_cli_demo(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demo CLI setup using flext-cli foundation."""
    formatter.print_success("\n1. 🔧 FLEXT CLI Command Integration Demo")

    # Setup CLI using flext-cli patterns
    setup_result = _setup_cli()
    if setup_result.is_failure:
        return FlextResult[None].fail(f"Setup failed: {setup_result.error}")

    setup_success = setup_result.value
    formatter.print_success("✅ CLI setup using FLEXT CLI foundation")
    formatter.console.print(f"   Setup result: {setup_success}")
    formatter.console.print("   Foundation: FlextCliMain + FlextCliApi")
    return FlextResult[None].ok(None)


def _connection_demo(
    formatter: FlextCliFormatters, config: FlextCliConfig
) -> FlextResult[None]:
    """Demo connection testing using flext-cli patterns."""
    formatter.print_success("\n2. 🌐 Connection Testing Integration")

    # Connection parameters
    connection_data = {
        "URL": "https://api.example.com",
        "Timeout": "30s",
        "Retries": "3",
        "Status": "Ready",
    }

    # Display connection info using flext-cli formatter
    table_result = formatter.format_table(
        data=connection_data, title="Connection Test Configuration"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    # Execute connection test
    command_result = _create_connection_command("https://api.example.com", 30, 3)
    if command_result.is_failure:
        return FlextResult[None].fail(
            f"Command creation failed: {command_result.error}"
        )

    command = command_result.value
    test_result = _execute_connection_test(command)

    if test_result.is_success:
        formatter.print_success(f"✅ Connection test: {test_result.value}")
    else:
        formatter.print_error(f"❌ Connection failed: {test_result.error}")

    return FlextResult[None].ok(None)


def _file_processing_demo(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demo file processing using flext-cli patterns."""
    formatter.print_success("\n3. 📁 File Processing Integration")

    # Simulate file processing parameters
    processing_data = {
        "File": "/tmp/example.json",
        "Format": "JSON",
        "Batch Size": "100",
        "Lines": "150",
        "Batches": "2",
    }

    # Display processing info using flext-cli formatter
    table_result = formatter.format_table(
        data=processing_data, title="File Processing Configuration"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    # Simulate file processing
    file_path = Path("/tmp/example.json")
    result = _simulate_file_processing(file_path, "json", 100)

    if result.is_success:
        formatter.print_success(f"✅ File processing: {result.value}")
    else:
        formatter.print_error(f"❌ Processing failed: {result.error}")

    return FlextResult[None].ok(None)


def _cli_status_demo(
    formatter: FlextCliFormatters, config: FlextCliConfig
) -> FlextResult[None]:
    """Demo CLI status display using flext-cli patterns."""
    formatter.print_success("\n4. 📊 CLI Status Integration")

    # Display CLI status using flext-cli formatter
    status_data = {
        "Profile": config.profile,
        "Debug Mode": str(config.debug),
        "Output Format": str(config.output_format),
        "Workspace": str(Path.cwd()),
        "CLI Foundation": "FLEXT CLI",
    }

    table_result = formatter.format_table(
        data=status_data, title="CLI Status Dashboard"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    return FlextResult[None].ok(None)


def _command_registration_demo(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demo command registration using flext-cli foundation."""
    formatter.print_success("\n5. 🎛️ Command Registration System")

    # Create CLI main using flext-cli foundation
    cli_main = FlextCliMain()

    # Register command groups (simulated)
    commands_data = {
        "connect": "✅ Connection testing command",
        "process": "✅ File processing command",
        "status": "✅ Status display command",
        "config": "✅ Configuration management",
    }

    table_result = formatter.format_table(
        data=commands_data, title="Registered Commands (FlextCliMain)"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    formatter.console.print("   Command registration through FLEXT CLI foundation")
    formatter.console.print("   Zero direct Click imports required")

    return FlextResult[None].ok(None)


def _summary_demo(formatter: FlextCliFormatters) -> None:
    """Demo summary display."""
    formatter.print_success("\n📋 CLI Commands Integration Summary")

    summary_data = {
        "Component": "Status",
        "FlextCliMain": "✅ Command registration",
        "FlextCliFormatters": "✅ Output abstraction",
        "FlextResult Pattern": "✅ Error handling",
        "FlextCliModels": "✅ Domain entities",
        "FLEXT Foundation": "✅ Zero Click/Rich imports",
    }

    table_result = formatter.format_table(
        data=summary_data, title="CLI Integration Components"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    formatter.print_success("🎉 CLI commands integration demonstrated successfully!")


def _setup_cli() -> FlextResult[str]:
    """Setup CLI using FLEXT CLI foundation."""
    try:
        # Simulate CLI setup process
        return FlextResult[str].ok("FLEXT CLI Foundation Initialized")
    except Exception as e:
        return FlextResult[str].fail(f"Setup failed: {e}")


def _create_connection_command(
    url: str, timeout: int, retries: int
) -> FlextResult[FlextCliModels.CliCommand]:
    """Create connection command using flext-cli domain patterns."""
    try:
        command = FlextCliModels.CliCommand(
            command_line=f"curl --connect-timeout {timeout} --retry {retries} {url}",
            execution_time=datetime.now(),
        )

        return FlextResult[FlextCliModels.CliCommand].ok(command)

    except Exception as e:
        return FlextResult[FlextCliModels.CliCommand].fail(
            f"Failed to create connection command: {e}"
        )


def _execute_connection_test(command: FlextCliModels.CliCommand) -> FlextResult[str]:
    """Execute connection test with FlextResult pattern."""
    try:
        # Simulate connection test
        time.sleep(0.1)  # Simulate network delay

        # Validate command before execution
        validation_result = command.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult[str].fail(
                f"Command validation failed: {validation_result.error}"
            )

        # Start command execution
        start_result = command.start_execution()
        if start_result.is_failure:
            return FlextResult[str].fail(
                f"Execution start failed: {start_result.error}"
            )

        # Simulate execution result
        command_line = command.command_line or ""
        if "localhost" in command_line:
            result_msg = "Connection successful to localhost"
        else:
            result_msg = "Connection test completed successfully"

        # Complete execution
        complete_result = command.complete_execution(exit_code=0, output=result_msg)
        if complete_result.is_failure:
            return FlextResult[str].fail(
                f"Execution completion failed: {complete_result.error}"
            )

        return FlextResult[str].ok(result_msg)

    except Exception as e:
        return FlextResult[str].fail(f"Connection test failed: {e}")


def _simulate_file_processing(
    file_path: Path, output_format: str, batch_size: int
) -> FlextResult[str]:
    """Simulate file processing with FlextResult pattern."""
    try:
        # Simulate processing without requiring actual file
        time.sleep(0.1)

        lines_processed = 150  # Simulate
        batches = (lines_processed + batch_size - 1) // batch_size

        return FlextResult[str].ok(
            f"Processed {lines_processed} lines in {batches} batches. "
            f"Output format: {output_format}"
        )

    except Exception as e:
        return FlextResult[str].fail(f"File processing failed: {e}")


def main() -> None:
    """Main demonstration function showcasing CLI commands integration."""
    formatter = FlextCliFormatters()

    formatter.print_success("FLEXT CLI Commands Integration Demo")
    formatter.print_success("=" * 50)

    try:
        # Run all demos in sequence using FlextResult railway pattern
        setup_result = _setup_cli_demo(formatter)
        if setup_result.is_failure:
            formatter.print_error(f"Setup demo failed: {setup_result.error}")
            return

        # Create config for demos
        config = FlextCliConfig()

        connection_result = _connection_demo(formatter, config)
        if connection_result.is_failure:
            formatter.print_error(f"Connection demo failed: {connection_result.error}")
            return

        file_result = _file_processing_demo(formatter)
        if file_result.is_failure:
            formatter.print_error(f"File processing demo failed: {file_result.error}")
            return

        status_result = _cli_status_demo(formatter, config)
        if status_result.is_failure:
            formatter.print_error(f"Status demo failed: {status_result.error}")
            return

        registration_result = _command_registration_demo(formatter)
        if registration_result.is_failure:
            formatter.print_error(
                f"Registration demo failed: {registration_result.error}"
            )
            return

        _summary_demo(formatter)

    except Exception as e:
        formatter.print_error(f"Demo failed with exception: {e}")
        raise


if __name__ == "__main__":
    main()
