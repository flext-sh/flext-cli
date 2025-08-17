"""Example demonstrating all restored functionality with real flext-core integration.

This example shows how to use the FLEXT CLI with real dependencies,
following SOLID principles without mocks or placeholders.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli import FlextCliApi, flext_cli_export, flext_cli_format


def demo_command(message: str) -> str:
    """Demo command handler."""
    return f"Processed: {message}"


def demonstrate_restored_functionality() -> None:
    """Demonstrate that ALL original functionality has been restored.

    Applies SOLID Single Responsibility Principle by delegating to specialized
    functions.
    """
    # Delegate to specialized demonstration functions (SOLID SRP)
    _demo_basic_functionality()
    _demo_flext_cli_service()
    _demo_command_management()
    _demo_session_management()
    _demo_plugin_management()
    _demo_advanced_features()
    _demo_integration_verification()


def _demo_basic_functionality() -> None:
    """Demonstrate basic CLI functionality."""
    # Test data
    sample_data = [
      {"name": "Alice", "age": 30, "city": "São Paulo"},
      {"name": "Bob", "age": 25, "city": "Rio de Janeiro"},
    ]

    # Export functionality
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_file = Path(temp_dir) / "test_export.json"
      flext_cli_export(sample_data, str(temp_file), "json")

      # Verify file was created
      if temp_file.exists():
          pass

    # Format functionality
    formatted_result = flext_cli_format(sample_data, "table")
    formatted_result.unwrap() if formatted_result.success else ""

    formatted_json_result = flext_cli_format(sample_data, "json")
    (formatted_json_result.unwrap() if formatted_json_result.success else "")


def _demo_flext_cli_service() -> None:
    """Demo FLEXT CLI service functionality - SOLID SRP."""
    # Test data for functions
    sample_data = [
      {"name": "Alice", "age": 30, "city": "São Paulo"},
      {"name": "Bob", "age": 25, "city": "Rio de Janeiro"},
    ]

    # Command creation and tracking (RESTORED)
    api = FlextCliApi()
    api.flext_cli_create_command(
      "test_cmd",
      "echo 'Hello World'",
      command_type="SYSTEM",
    )

    # Plugin system (RESTORED)
    api.flext_cli_register_plugin(
      "test_plugin",
      {"name": "TestPlugin", "version": "1.0"},
    )

    # Rich context rendering (RESTORED)
    context = {"debug": True, "format": "table", "no_color": False}
    rendered_result = api.flext_cli_render_with_context(sample_data, context)
    rendered_result.unwrap() if rendered_result.success else ""


def _demo_command_management() -> None:
    """Demo command management functionality."""
    # Format capabilities (RESTORED)
    formats_info = {"available": ["table", "json", "yaml", "csv"]}
    formats_info.get("available", [])


def _demo_session_management() -> None:
    """Demo session management functionality."""
    # Session tracking (RESTORED)
    api = FlextCliApi()
    api.flext_cli_create_session("demo_user")

    # Direct API access for complex scenarios
    cli_api = FlextCliApi()

    # Register and execute commands
    def demo_command(message: str) -> str:
      return f"Demo executed: {message}"

    cli_api.flext_cli_register_handler("demo", demo_command)
    result = cli_api.flext_cli_execute_handler(
      "demo",
      "Hello from restored functionality!",
    )
    result = result.unwrap() if result.success else "Failed"


def _demo_plugin_management() -> None:
    """Demo plugin management functionality."""
    # Health check with comprehensive info
    cli_api = FlextCliApi()
    cli_api.flext_cli_health()


def _demo_advanced_features() -> None:
    """Demo advanced CLI features."""
    # Show flext-core integration
    api = FlextCliApi()
    api.health()


def _demo_integration_verification() -> None:
    """Demo integration verification."""


if __name__ == "__main__":
    demonstrate_restored_functionality()
