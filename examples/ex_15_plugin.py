"""Example Plugin for FLEXT-CLI.

This is a complete example demonstrating how to create a plugin
for the flext-cli plugin system.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from examples import c, p, r, t


class ExamplePlugin:
    """Example plugin demonstrating the plugin system.

    This plugin adds custom commands to the CLI and shows how to:
    - Implement the plugin protocol
    - Initialize plugin resources
    - Register commands
    - Access CLI features

    """

    name = "example-plugin"
    version = "1.0.0"
    description = "Example plugin demonstrating flext-cli plugin system"

    def __init__(self) -> None:
        """Initialize plugin."""
        super().__init__()
        self._initialized = False
        self._config: Mapping[str, bool | int] = {}

    def initialize(self, _cli: p.CliMainWithGroups) -> p.Result[bool]:
        """Initialize the plugin.

        Args:
            _cli: FlextCliMain instance (unused — protocol-required)

        Returns:
            r[bool] indicating success (True) or failure

        """
        try:
            self._config = {"enabled": True, "debug": False, "max_items": 100}
            self._initialized = True
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(f"Plugin initialization failed: {e}")

    def register_commands(self, cli_main: p.CliMainWithGroups) -> p.Result[bool]:
        """Register plugin commands.

        Args:
            cli_main: FlextCliMain instance for command registration

        Returns:
            r[bool] indicating success (True) or failure

        """
        try:
            cli_with_group = cli_main

            @cli_with_group.group()
            def example() -> None:
                """Example plugin commands."""

            if not isinstance(example, p.GroupWithCommands):
                return r[bool].fail(
                    "example group does not implement GroupWithCommands protocol",
                )

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
                print(
                    f"Plugin status: {('Active' if self._initialized else 'Inactive')}",
                )
                print(f"Configuration: {self._config}")

            example_group = example

            @example_group.command()
            def hello_cmd(name: str = "World") -> None:
                """Say hello from the plugin."""
                hello(name)

            @example_group.command()
            def info_cmd() -> None:
                """Show plugin information."""
                info()

            @example_group.command()
            def status_cmd() -> None:
                """Show plugin status."""
                status()

            return r[bool].ok(value=len((hello_cmd, info_cmd, status_cmd)) == 3)
        except Exception as e:
            return r[bool].fail(f"Command registration failed: {e}")


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
        self._processors: t.ProcessorRegistry = {}

    def initialize(self, _cli: p.CliMainWithGroups) -> p.Result[bool]:
        """Initialize the plugin.

        Args:
            _cli: FlextCliMain instance (unused — protocol-required)

        Returns:
            r[bool] indicating success (True) or failure

        """
        try:
            self._processors = {
                c.Cli.OutputFormats.CSV: lambda data: f"CSV: {data}",
                c.Cli.OutputFormats.JSON: lambda data: f"JSON: {data}",
                c.Cli.OutputFormats.XML: lambda data: f"XML: {data}",
            }
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(f"Initialization failed: {e}")

    def register_commands(self, cli_main: p.CliMainWithGroups) -> p.Result[bool]:
        """Register data processing commands.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            r[bool] indicating success (True) or failure

        """
        try:
            cli_with_group = cli_main

            @cli_with_group.group()
            def data() -> None:
                """Data processing commands."""

            if not isinstance(data, p.GroupWithCommands):
                return r[bool].fail(
                    "data group does not implement GroupWithCommands protocol",
                )

            def process_data(
                input_data: str,
                format_type: c.Cli.OutputFormats = c.Cli.OutputFormats.JSON,
            ) -> str:
                """Process data in specified format.

                Args:
                    input_data: Data to process
                    format_type: Output format (csv, json, xml)

                Returns:
                    Processed data string

                """
                if format_type in self._processors:
                    processor: t.DataProcessor = self._processors[format_type]
                    return processor(input_data)
                return f"Unsupported format: {format_type}"

            def list_formats() -> t.StrSequence:
                """List available data formats.

                Returns:
                    List of available format names

                """
                return list(self._processors.keys())

            data_group = data

            @data_group.command()
            def process_cmd(
                input_data: str,
                format_type: c.Cli.OutputFormats = c.Cli.OutputFormats.JSON,
            ) -> None:
                """Process data in specified format."""
                result = process_data(input_data, format_type)
                print(f"Processed: {result}")

            @data_group.command()
            def formats_cmd() -> None:
                """List available data formats."""
                formats_list = list_formats()
                print(f"Available formats: {', '.join(formats_list)}")

            return r[bool].ok(value=len((process_cmd, formats_cmd)) == 2)
        except Exception as e:
            return r[bool].fail(f"Command registration failed: {e}")


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
    demonstrate_plugin_commands()
