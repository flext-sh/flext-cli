#!/usr/bin/env python3
"""Basic FLEXT CLI Library Usage Example.

This example demonstrates the core functionality of the FLEXT CLI library,
showing how to use the library to build CLI applications with proper
configuration, context management, and result handling.

Key features demonstrated:
- Configuration management with CLIConfig
- CLI context creation and management
- Helper utilities for common CLI operations
- Click parameter types integration
- Service result handling patterns

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult
from rich import Console

import flext_cli


def demonstrate_configuration() -> None:
    """Demonstrate configuration management."""
    console = Console()
    console.print("[bold blue]1. Configuration Management[/bold blue]")
    config = flext_cli.get_config()
    console.print(f"   API URL: {config.api_url}")
    console.print(f"   Output Format: {config.output_format}")
    console.print(f"   Debug Mode: {config.debug}")
    console.print()


def demonstrate_settings() -> None:
    """Demonstrate environment settings."""
    console = Console()
    console.print("[bold blue]2. Environment Settings[/bold blue]")
    settings = flext_cli.get_settings()
    console.print(f"   Project: {settings.project_name}")
    console.print(f"   Version: {settings.project_version}")
    console.print(f"   Log Level: {settings.log_level}")
    console.print()


def demonstrate_context_management() -> None:
    """Demonstrate CLI context management."""
    console = Console()
    console.print("[bold blue]3. CLI Context Management[/bold blue]")

    # Create default context
    default_context = flext_cli.CLIContext()
    console.print(f"   Default profile: {default_context.profile}")
    console.print(f"   Output format: {default_context.output_format}")


def demonstrate_utilities() -> None:
    """Demonstrate helper utilities."""
    console = Console()
    console.print("[bold blue]4. Helper Utilities[/bold blue]")
    helper = flext_cli.CLIHelper()

    # Validation examples
    test_url = "https://api.example.com"
    is_valid_url = helper.validate_url(test_url)
    console.print(f"   URL '{test_url}' is valid: {is_valid_url}")


def demonstrate_advanced_helpers() -> None:
    """Demonstrate advanced helper utilities following SOLID principles."""
    console = Console()
    console.print("[bold blue]5. Advanced Helper Examples[/bold blue]")
    helper = flext_cli.CLIHelper()

    # Email validation
    test_email = "user@example.com"
    is_valid_email = helper.validate_email(test_email)
    console.print(f"   Email '{test_email}' is valid: {is_valid_email}")

    # File size formatting
    file_size = 1024 * 1024 * 5  # 5MB
    formatted_size = helper.format_size(file_size)
    console.print(f"   Formatted size: {formatted_size}")

    # Text truncation
    long_text = "This is a very long text that needs to be truncated for display"
    truncated = helper.truncate_text(long_text, max_length=30)
    console.print(f"   Truncated text: {truncated}")
    console.print()


def demonstrate_debug_context() -> None:
    """Demonstrate debug context."""
    console = Console()
    debug_context = flext_cli.CLIContext(
        profile="development",
        output_format="json",
        debug=True,
        verbose=True,
    )
    console.print(f"   Debug profile: {debug_context.profile}")
    console.print(f"   Debug format: {debug_context.output_format}")
    console.print()


def main() -> None:
    """Demonstrate basic FLEXT CLI library usage."""
    console = Console()
    console.print("[bold green]🚀 FLEXT CLI Library Basic Usage Example[/bold green]\n")

    # Break down into smaller functions following SOLID principles
    demonstrate_configuration()
    demonstrate_settings()
    demonstrate_context_management()
    demonstrate_debug_context()
    demonstrate_utilities()
    demonstrate_advanced_helpers()

    # 5. Click Parameter Types
    console.print("[bold blue]5. Click Parameter Types Integration[/bold blue]")

    # Demonstrate type validation
    positive_int_type = flext_cli.PositiveInt
    console.print(f"   PositiveInt type name: {positive_int_type.name}")

    url_type = flext_cli.URL
    console.print(f"   URL type name: {url_type.name}")

    # Path types
    console.print(
        f"   ExistingFile allows existing files: {flext_cli.ExistingFile.exists}",
    )
    console.print(f"   NewFile allows new files: {not flext_cli.NewFile.exists}")
    console.print()

    # 6. CLI Setup
    console.print("[bold blue]6. CLI Setup[/bold blue]")
    setup_result = flext_cli.setup_cli()
    if setup_result.success:
        console.print("   ✅ CLI setup completed successfully")
    else:
        console.print(f"   ❌ CLI setup failed: {setup_result.error}")
    console.print()

    # 7. Service Result Handling Pattern
    console.print("[bold blue]7. Service Result Handling[/bold blue]")

    @flext_cli.handle_service_result
    def example_service_operation() -> str:
        """Return a simple result from a service operation."""
        return "Operation completed successfully"

    @flext_cli.handle_service_result
    def example_service_with_result() -> str:
        """Return a FlextResult from a service operation."""
        return FlextResult.ok("Service result data")

    # Test the decorators
    result1 = example_service_operation()
    console.print(f"   Simple result: {result1}")

    result2 = example_service_with_result()
    console.print(f"   FlextResult data: {result2}")
    console.print()

    console.print("[bold green]✨ Basic usage example completed![/bold green]")


if __name__ == "__main__":
    main()
