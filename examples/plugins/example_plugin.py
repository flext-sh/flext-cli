"""Example Plugin for FLEXT-CLI.

This is a complete example demonstrating how to create a plugin
for the flext-cli plugin system.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from flext_core import FlextCore

from flext_cli.typings import FlextCliTypes

# Type definitions for processor functions
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
        self._initialized = False
        self._config: FlextCliTypes.Data.CliDataDict = {}

    def initialize(self, _cli_main: object) -> FlextCore.Result[None]:
        """Initialize the plugin.

        Args:
            _cli_main: FlextCliMain instance

        Returns:
            FlextCore.Result[None] indicating success or failure

        """
        try:
            # Plugin initialization logic
            self._config = {
                "enabled": True,
                "debug": False,
                "max_items": 100,
            }

            self._initialized = True

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Plugin initialization failed: {e}")

    def register_commands(self, cli_main: object) -> FlextCore.Result[None]:
        """Register plugin commands.

        Args:
            cli_main: FlextCliMain instance for command registration

        Returns:
            FlextCore.Result[None] indicating success or failure

        """
        try:
            # Cast cli_main to Any for decorator usage (runtime type is correct)
            cli_main_typed = cast("Any", cli_main)

            # Register command group
            @cli_main_typed.group()
            def example() -> None:
                """Example plugin commands."""

            # Register commands under group
            @example.command()
            def hello(name: str = "World") -> None:
                """Say hello from the plugin.

                Args:
                    name: Name to greet

                """

            @example.command()
            def info() -> None:
                """Show plugin information."""

            @example.command()
            def status() -> None:
                """Show plugin status."""

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Command registration failed: {e}")


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
        self._processors: ProcessorRegistry = {}

    def initialize(self, _cli_main: object) -> FlextCore.Result[None]:
        """Initialize the plugin.

        Args:
            _cli_main: FlextCliMain instance

        Returns:
            FlextCore.Result[None]

        """
        try:
            # Setup processors
            self._processors = {
                "csv": lambda data: f"CSV: {data}",
                "json": lambda data: f"JSON: {data}",
                "xml": lambda data: f"XML: {data}",
            }

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Initialization failed: {e}")

    def register_commands(self, cli_main: object) -> FlextCore.Result[None]:
        """Register data processing commands.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            FlextCore.Result[None]

        """
        try:
            # Cast cli_main to Any for decorator usage (runtime type is correct)
            cli_main_typed = cast("Any", cli_main)

            @cli_main_typed.group()
            def data() -> None:
                """Data processing commands."""

            @data.command()
            def process(input_data: str, format_type: str = "json") -> None:
                """Process data in specified format.

                Args:
                    input_data: Data to process
                    format_type: Output format (csv, json, xml)

                """
                if format_type in self._processors:
                    # Processor is already properly typed
                    processor: DataProcessor = self._processors[format_type]
                    processor(input_data)

            @data.command()
            def formats() -> None:
                """List available data formats."""
                for _fmt in self._processors:
                    pass

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Command registration failed: {e}")
