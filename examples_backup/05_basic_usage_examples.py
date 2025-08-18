"""Basic Usage Examples for FLEXT CLI Library.

This module demonstrates basic usage patterns of the FLEXT CLI library,
showcasing how to use FlextCli classes and utilities for typical CLI operations
with massive boilerplate reduction.

Examples Include:
    - Zero-boilerplate CLI setup
    - FlextResult integration patterns
    - Validation and confirmation utilities
    - File operations with auto-format detection
    - Rich console integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import time
from pathlib import Path

from flext_core import FlextResult
from rich.console import Console

from flext_cli import (
    CLIValidationMixin,
    cli_create_table,
    cli_load_data_file,
    cli_quick_setup,
    cli_save_data_file,
    confirm_action,
    flext_cli_format,
    flext_cli_table,
    measure_time,
)


def example_1_zero_boilerplate_setup() -> None:
    """Example 1: Zero-boilerplate CLI setup with intelligent defaults."""
    # Single function call sets up entire CLI environment
    setup_result = cli_quick_setup(
        project_name="flext-demo",
        create_dirs=True,
        create_config=True,
        init_git=False
    )
    if setup_result.success:
        pass


def example_2_batch_validation() -> None:
    """Example 2: Batch validation with FlextResult integration."""
    # Use CLIHelper for validation
    # Using CLIHelper for validation would be done here

    # Validate multiple inputs individually
    validations = {
        "user_email": "john.doe@company.com",
        "api_endpoint": "https://api.flext.sh/v1",
        "project_name": "my-project",
    }

    # Simulate validation results
    validation_results = {}
    for key, value in validations.items():
        validation_results[key] = FlextResult.ok(value)

    if all(result.success for result in validation_results.values()):
        for _key, _result in validation_results.items():
            pass


def example_3_helper_integration() -> None:
    """Example 3: CLIHelper with modern FlextResult patterns."""
    # Using CLIHelper for validation would be done here

    # Helper instance created successfully
    # Note: CLIHelper provides various utility methods
    # Email validation example
    email = "user@example.com"
    if "@" in email and "." in email.split("@")[1]:
        email_result = FlextResult.ok(email)
    else:
        email_result = FlextResult.fail("Invalid email format")

    if email_result.success:
        pass

    # URL validation example
    url = "https://secure.api.flext.sh"
    if url.startswith(("http://", "https://")):
        url_result = FlextResult.ok(url)
    else:
        url_result = FlextResult.fail("Invalid URL format")

    if url_result.success:
        pass

    # Filename sanitization example
    filename = "report_file.pdf"  # Pre-sanitized for demo
    filename_result = FlextResult.ok(filename)
    if filename_result.success:
        pass


def example_4_mixin_class_usage() -> None:
    """Example 4: Using FlextCli mixins for boilerplate reduction."""

    class MyCliCommand(CLIValidationMixin):
        """Example CLI command using CLIValidationMixin."""

        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name
            self.console = Console()

        def execute(self, email: str, config_path: str) -> FlextResult[str]:
            """Execute command with validation and progress."""
            # Simple validation
            if not email or "@" not in email:
                return FlextResult.fail("Invalid email format")

            if not config_path or not Path(config_path).exists():
                return FlextResult.fail("Invalid config path")

            # Console output
            self.console.print(f"[blue]Executing {self.name} command...[/blue]")
            self.console.print(f"[green]Email: {email}[/green]")
            self.console.print(f"[green]Config: {config_path}[/green]")

            # Simulate progress tracking
            items = ["step1", "step2", "step3", "step4"]
            for _item in items:
                # Simulate work
                time.sleep(0.1)

            self.console.print(f"[green]Command {self.name} completed successfully![/green]")
            return FlextResult.ok(f"Command {self.name} executed with validated inputs")

    # Use the command
    command = MyCliCommand("data-sync")
    result = command.execute("user@example.com", str(Path.cwd() / "temp"))

    if result.success:
        pass


@confirm_action("Execute API operation?")
@measure_time(show_in_output=True)
def example_5_decorators(email: str, url: str) -> FlextResult[str]:
    """Example 5: CLI decorators for automatic functionality."""
    # This function uses available decorators:
    # 1. Requires user confirmation before execution
    # 2. Measures execution time
    # 3. Returns FlextResult

    # Simple validation
    if not email or "@" not in email:
        return FlextResult.fail("Invalid email format")

    if not url or not url.startswith(("http://", "https://")):
        return FlextResult.fail("Invalid URL format")

    return FlextResult.ok(f"API request sent to {url} for {email}")


def example_5_decorator_usage() -> None:
    """Example 5: Using CLI decorators."""
    # Note: In real usage, user would be prompted for confirmation
    # For demo, we'll show what the decorated function would do
    result = example_5_decorators("user@example.com", "https://api.flext.sh")
    if result and hasattr(result, "success") and result.success:
        pass


def example_6_file_operations() -> None:
    """Example 6: File operations with automatic format detection."""
    # Sample data to save
    sample_data = {
        "project": "flext-cli-demo",
        "version": "1.0.0",
        "features": ["validation", "mixins", "decorators"],
        "config": {"debug": True, "output_format": "json"},
    }

    # Save in different formats using available functions
    temp_dir = Path.cwd() / "temp" / "flext_cli_examples"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # JSON format
    json_file = temp_dir / "config.json"
    json_result = cli_save_data_file(sample_data, json_file)
    if json_result.success:
        pass

    # YAML format (using JSON for demo since YAML might not be available)
    yaml_file = temp_dir / "config.json"
    yaml_result = cli_save_data_file(sample_data, yaml_file)
    if yaml_result.success:
        pass

    # Load back and verify
    if json_result.success:
        load_result = cli_load_data_file(json_file)
        if load_result.success:
            pass


def example_7_output_formatting() -> None:
    """Example 7: Output formatting with multiple formats."""
    # Sample data for formatting
    data = [
        {"name": "Alice Johnson", "role": "Developer", "projects": 5},
        {"name": "Bob Smith", "role": "Designer", "projects": 3},
        {"name": "Carol Brown", "role": "Manager", "projects": 8},
        {"name": "David Wilson", "role": "DevOps", "projects": 4},
    ]

    # Create a nice table using available function
    table_result = cli_create_table(data, title="Team Members")
    console = Console()
    if table_result.success:
        console.print(table_result.unwrap())

    # Output in JSON format using available formatter
    json_result = flext_cli_format(data)
    if json_result.success:
        console.print("[blue]JSON Output:[/blue]")
        console.print(json_result.unwrap())

    # Output in table format using available function
    table_result2 = flext_cli_table(data)
    if table_result2.success:
        console.print("[blue]Table Output:[/blue]")
        console.print(table_result2.unwrap())


def example_8_batch_operations() -> None:
    """Example 8: Batch operations with progress tracking."""

    # Define batch operations
    def validate_config() -> FlextResult[str]:
        """Simulate config validation."""
        return FlextResult.ok("Configuration validated")

    def load_data() -> FlextResult[str]:
        """Simulate data loading."""
        time.sleep(0.2)  # Simulate work
        return FlextResult.ok("Data loaded successfully")

    def process_data() -> FlextResult[str]:
        """Simulate data processing."""
        time.sleep(0.3)  # Simulate work
        return FlextResult.ok("Data processed")

    def save_results() -> FlextResult[str]:
        """Simulate saving results."""
        return FlextResult.ok("Results saved")

    # Batch execute with progress
    operations = [
        ("validate_config", validate_config),
        ("load_data", load_data),
        ("process_data", process_data),
        ("save_results", save_results),
    ]

    # Execute operations sequentially (batch execute simulation)
    batch_results = {}
    console = Console()

    console.print("[blue]Processing pipeline...[/blue]")
    for name, operation in operations:
        try:
            result = operation()
            batch_results[name] = {"success": result.success, "data": result.data if result.success else result.error}
            if result.success:
                console.print(f"[green]✓ {name}: {result.data}[/green]")
            else:
                console.print(f"[red]✗ {name}: {result.error}[/red]")
                break  # stop_on_error=True
        except Exception as e:
            batch_results[name] = {"success": False, "error": str(e)}
            console.print(f"[red]✗ {name}: {e}[/red]")
            break

    # Check results
    if batch_results:
        for result_info in batch_results.values():
            if result_info.get("success"):
                pass


def example_9_auto_config_loading() -> None:
    """Example 9: Automatic configuration loading with hierarchy."""
    # Create sample config files
    temp_dir = Path.cwd() / "temp" / "flext_cli_examples"
    temp_dir.mkdir(parents=True, exist_ok=True)

    config_file = temp_dir / "flext-demo.yml"
    sample_config = {
        "api_url": "https://demo.api.flext.sh",
        "timeout": 30,
        "retry_count": 3,
        "features": {"auth": True, "caching": True, "debug": False},
    }

    # Save config file using available function
    save_result = cli_save_data_file(sample_config, config_file)
    if save_result.success:
        pass
    else:
        return

    # Load configuration using available function
    config_result = cli_load_data_file(config_file)

    if config_result.success:
        loaded_config = config_result.unwrap()
        console = Console()
        if isinstance(loaded_config, dict):
            console.print(f"[green]Configuration loaded: {loaded_config.get('service_name', 'N/A')}[/green]")
        else:
            console.print("[green]Configuration loaded successfully[/green]")


def main() -> None:
    """Run all examples."""
    # Run all examples
    example_1_zero_boilerplate_setup()
    example_2_batch_validation()
    example_3_helper_integration()
    example_4_mixin_class_usage()
    example_5_decorator_usage()
    example_6_file_operations()
    example_7_output_formatting()
    example_8_batch_operations()
    example_9_auto_config_loading()


if __name__ == "__main__":
    main()
