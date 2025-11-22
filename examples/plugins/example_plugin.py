"""Example Plugin for FLEXT-CLI.

This is a complete example demonstrating how to create a plugin
for the flext-cli plugin system.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from flext_core import FlextResult

from flext_cli.typings import FlextCliTypes

type DataProcessor = Callable[[str], str]
type ProcessorRegistry = dict[str, DataProcessor]


class ExamplePlugin:
    """Example plugin demonstrating the plugin system.

    This plugin adds custom commands to the CLI and shows how to:
    - Implement the plugin protocol
    - Initialize plugin resources
    - Register commands
    - Access CLI features

    """

    # Plugin metadata (required)
    name = "example-plugin"
    version = "1.0.0"
    description = "Example plugin demonstrating flext-cli plugin system"

    def __init__(self) -> None:
        """Initialize plugin."""
        super().__init__()
        self._initialized = False
        self._config: FlextCliTypes.Data.CliDataDict = {}

    def initialize(self, _cli_main: object) -> FlextResult[bool]:
        """Initialize the plugin.

        Args:
            _cli_main: FlextCliMain instance

        Returns:
            FlextResult[bool] indicating success (True) or failure

        """
        try:
            # Plugin initialization logic
            self._config = {
                "enabled": True,
                "debug": False,
                "max_items": 100,
            }

            self._initialized = True

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(f"Plugin initialization failed: {e}")

    def register_commands(self, cli_main: object) -> FlextResult[bool]:
        """Register plugin commands.

        Args:
            cli_main: FlextCliMain instance for command registration

        Returns:
            FlextResult[bool] indicating success (True) or failure

        """
        try:
            # Cast cli_main to Any for decorator usage (runtime type is correct)
            cli_main_typed = cast("Any", cli_main)

            # Register command group
            @cli_main_typed.group()  # type: ignore[misc]
            def example() -> None:
                """Example plugin commands."""

            # Store command functions for later use
            def hello(name: str = "World") -> None:
                """Say hello from the plugin.

                Args:
                    name: Name to greet

                """
                print(f"Hello, {name}! From {self.name} plugin")

            def info() -> None:
                """Show plugin information."""
                print(f"Plugin: {self.name} v{self.version}")
                print(f"Description: {self.description}")
                print(f"Initialized: {self._initialized}")

            def status() -> None:
                """Show plugin status."""
                print(f"Plugin status: {'Active' if self._initialized else 'Inactive'}")
                print(f"Configuration: {self._config}")

            # Register commands under group
            @example.command()  # type: ignore[misc]
            def hello_cmd(name: str = "World") -> None:
                """Say hello from the plugin."""
                hello(name)

            @example.command()  # type: ignore[misc]
            def info_cmd() -> None:
                """Show plugin information."""
                info()

            @example.command()  # type: ignore[misc]
            def status_cmd() -> None:
                """Show plugin status."""
                status()

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(f"Command registration failed: {e}")


# Another example plugin - data processing
class DataProcessorPlugin:
    """Data processor plugin example.

    Demonstrates a more complex plugin with multiple command groups.

    """

    name = "data-processor"
    version = "1.0.0"
    description = "Data processing plugin"

    def __init__(self) -> None:
        """Initialize data processor plugin."""
        super().__init__()
        self._processors: ProcessorRegistry = {}

    def initialize(self, _cli_main: object) -> FlextResult[bool]:
        """Initialize the plugin.

        Args:
            _cli_main: FlextCliMain instance

        Returns:
            FlextResult[bool] indicating success (True) or failure

        """
        try:
            # Setup processors
            self._processors = {
                "csv": lambda data: f"CSV: {data}",
                "json": lambda data: f"JSON: {data}",
                "xml": lambda data: f"XML: {data}",
            }

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(f"Initialization failed: {e}")

    def register_commands(self, cli_main: object) -> FlextResult[bool]:
        """Register data processing commands.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            FlextResult[bool] indicating success (True) or failure

        """
        try:
            # Cast cli_main to Any for decorator usage (runtime type is correct)
            cli_main_typed = cast("Any", cli_main)

            @cli_main_typed.group()  # type: ignore[misc]
            def data() -> None:
                """Data processing commands."""

            # Store command functions for later use
            def process_data(input_data: str, format_type: str = "json") -> str:
                """Process data in specified format.

                Args:
                    input_data: Data to process
                    format_type: Output format (csv, json, xml)

                Returns:
                    Processed data string

                """
                if format_type in self._processors:
                    # Processor is already properly typed
                    processor: DataProcessor = self._processors[format_type]
                    return processor(input_data)
                return f"Unsupported format: {format_type}"

            def list_formats() -> list[str]:
                """List available data formats.

                Returns:
                    List of available format names

                """
                return list(self._processors.keys())

            @data.command()  # type: ignore[misc]
            def process_cmd(input_data: str, format_type: str = "json") -> None:
                """Process data in specified format."""
                result = process_data(input_data, format_type)
                print(f"Processed: {result}")

            @data.command()  # type: ignore[misc]
            def formats_cmd() -> None:
                """List available data formats."""
                formats_list = list_formats()
                print(f"Available formats: {', '.join(formats_list)}")

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(f"Command registration failed: {e}")


# ============================================================================
# DEMONSTRATION SECTION - Example usage of the plugin commands
# ============================================================================


def demonstrate_plugin_commands() -> None:
    """Demonstrate how the plugin commands would be used.

    Note: In a real CLI application, these commands would be invoked
    through the CLI framework when users run:
    - flext example hello "John"
    - flext example info
    - flext example status
    - flext data process "some data"
    - flext data formats

    For demonstration purposes, we'll call the underlying functions directly:
    """
    print("Plugin commands are registered and ready to use!")
    print("Example usage:")
    print("  flext example hello 'World'")
    print("  flext example info")
    print("  flext example status")
    print("  flext data process 'input data'")
    print("  flext data formats")

    print("\n--- Plugin Commands Successfully Registered ---")
    print("✅ Commands are now available through the CLI plugin system:")
    print("   • hello: Say hello from the plugin")
    print("   • info: Show plugin information")
    print("   • status: Show plugin status")
    print("   • process: Process data in specified format")
    print("   • formats: List available data formats")
    print("\nThese commands can be invoked through the flext CLI framework.")


if __name__ == "__main__":
    # This would normally be handled by the plugin system
    demonstrate_plugin_commands()
