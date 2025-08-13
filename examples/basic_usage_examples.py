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

Run Examples:
    python examples/basic_usage_examples.py

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from pathlib import Path

# Import FlextCli library - everything from root namespace
from flext_cli import (
    FlextCliHelper,
    FlextCliMixin,
    flext_cli_auto_config,
    flext_cli_auto_validate,
    flext_cli_batch_execute,
    flext_cli_create_table,
    flext_cli_handle_exceptions,
    flext_cli_load_file,
    flext_cli_output_data,
    flext_cli_quick_setup,
    flext_cli_require_confirmation,
    flext_cli_save_file,
    flext_cli_validate_all,
)
from flext_core import FlextResult


def example_1_zero_boilerplate_setup() -> None:
    """Example 1: Zero-boilerplate CLI setup with intelligent defaults."""
    print("=" * 60)
    print("EXAMPLE 1: Zero-Boilerplate CLI Setup")
    print("=" * 60)

    # Single function call sets up entire CLI environment
    config = {
        "profile": "development",
        "debug": True,
        "output_format": "json",
        "commands": ["auth", "config", "debug"],
    }

    setup_result = flext_cli_quick_setup(config)
    if setup_result.success:
        cli_context = setup_result.data
        print("✅ CLI setup successful!")
        print(f"   Profile: {cli_context['config']['profile']}")
        print(f"   Debug: {cli_context['config']['debug']}")
        print(f"   Session ID: {cli_context['session_id']}")
        print(f"   Initialized: {cli_context['initialized']}")
    else:
        print(f"❌ Setup failed: {setup_result.error}")

    print()


def example_2_batch_validation() -> None:
    """Example 2: Batch validation with FlextResult integration."""
    print("=" * 60)
    print("EXAMPLE 2: Batch Validation with FlextResult")
    print("=" * 60)

    # Validate multiple inputs in single function call
    validations = {
        "user_email": ("john.doe@company.com", "email"),
        "api_endpoint": ("https://api.flext.sh/v1", "url"),
        "project_name": ("my-project<>file?.txt", "filename"),
    }

    result = flext_cli_validate_all(validations)

    if result.success:
        print("✅ All validations successful!")
        for key, validated_value in result.data.items():
            print(f"   {key}: {validated_value}")
    else:
        print(f"❌ Validation failed: {result.error}")

    print()


def example_3_helper_integration() -> None:
    """Example 3: FlextCliHelper with modern FlextResult patterns."""
    print("=" * 60)
    print("EXAMPLE 3: FlextCliHelper with FlextResult Integration")
    print("=" * 60)

    helper = FlextCliHelper()

    # Modern email validation with detailed error reporting
    email_result = helper.flext_cli_validate_email("user@example.com")
    if email_result.success:
        print(f"✅ Valid email: {email_result.data}")
    else:
        print(f"❌ Email validation failed: {email_result.error}")

    # URL validation with protocol checking
    url_result = helper.flext_cli_validate_url("https://secure.api.flext.sh")
    if url_result.success:
        print(f"✅ Valid URL: {url_result.data}")
    else:
        print(f"❌ URL validation failed: {url_result.error}")

    # Filename sanitization for safe filesystem usage
    filename_result = helper.flext_cli_sanitize_filename("report<>file?.pdf")
    if filename_result.success:
        print(f"✅ Sanitized filename: {filename_result.data}")
    else:
        print(f"❌ Filename sanitization failed: {filename_result.error}")

    print()


def example_4_mixin_class_usage() -> None:
    """Example 4: Using FlextCli mixins for boilerplate reduction."""
    print("=" * 60)
    print("EXAMPLE 4: FlextCli Mixins for Boilerplate Reduction")
    print("=" * 60)

    class MyCliCommand(FlextCliMixin):
        """Example CLI command using FlextCli mixins."""

        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name

        def execute(self, email: str, config_path: str) -> FlextResult[str]:
            """Execute command with automatic validation and progress."""
            # Automatic input validation via mixin
            validation_result = self.flext_cli_validate_inputs(
                {"email": (email, "email"), "config": (config_path, "path")},
            )

            if not validation_result.success:
                return FlextResult.fail(f"Validation failed: {validation_result.error}")

            validated_data = validation_result.data

            # Rich console output via mixin
            self.flext_cli_print_info(f"Executing {self.name} command...")
            self.flext_cli_print_info(f"Email: {validated_data['email']}")
            self.flext_cli_print_info(f"Config: {validated_data['config']}")

            # Simulate progress tracking
            items = ["step1", "step2", "step3", "step4"]
            for _item in self.flext_cli_track_progress(items, "Processing steps"):
                # Simulate work
                import time

                time.sleep(0.1)

            self.flext_cli_print_success(f"Command {self.name} completed successfully!")
            return FlextResult.ok(f"Command {self.name} executed with validated inputs")

    # Use the command
    command = MyCliCommand("data-sync")
    result = command.execute("user@example.com", str(Path.cwd() / "temp"))

    if result.success:
        print(f"✅ Command result: {result.data}")
    else:
        print(f"❌ Command failed: {result.error}")

    print()


@flext_cli_auto_validate(email="email", url="url")
@flext_cli_handle_exceptions("API operation failed")
@flext_cli_require_confirmation("Send API request")
def example_5_decorators(email: str, url: str) -> FlextResult[str]:
    """Example 5: FlextCli decorators for automatic functionality."""
    # This function automatically:
    # 1. Validates email and url parameters
    # 2. Requires user confirmation before execution
    # 3. Handles any exceptions and converts to FlextResult

    return FlextResult.ok(f"API request sent to {url} for {email}")


def example_5_decorator_usage() -> None:
    """Example 5: Using FlextCli decorators."""
    print("=" * 60)
    print("EXAMPLE 5: FlextCli Decorators for Automatic Functionality")
    print("=" * 60)

    print("Calling function with decorators (requires confirmation)...")

    # Note: In real usage, user would be prompted for confirmation
    # For demo, we'll show what the decorated function would do
    try:
        result = example_5_decorators("user@example.com", "https://api.flext.sh")
        if result.success:
            print(f"✅ Decorated function result: {result.data}")
        else:
            print(f"❌ Decorated function failed: {result.error}")
    except Exception as e:
        print(f"❌ Exception in decorated function: {e}")

    print()


def example_6_file_operations() -> None:
    """Example 6: File operations with automatic format detection."""
    print("=" * 60)
    print("EXAMPLE 6: File Operations with Auto-Format Detection")
    print("=" * 60)

    # Sample data to save
    sample_data = {
        "project": "flext-cli-demo",
        "version": "1.0.0",
        "features": ["validation", "mixins", "decorators"],
        "config": {"debug": True, "output_format": "json"},
    }

    # Save in different formats (format auto-detected from extension)
    temp_dir = Path.cwd() / "temp" / "flext_cli_examples"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # JSON format
    json_file = temp_dir / "config.json"
    json_result = flext_cli_save_file(sample_data, json_file)
    if json_result.success:
        print(f"✅ Saved JSON config: {json_file}")
    else:
        print(f"❌ JSON save failed: {json_result.error}")

    # YAML format
    yaml_file = temp_dir / "config.yml"
    yaml_result = flext_cli_save_file(sample_data, yaml_file)
    if yaml_result.success:
        print(f"✅ Saved YAML config: {yaml_file}")
    else:
        print(f"❌ YAML save failed: {yaml_result.error}")

    # Load back and verify
    if json_result.success:
        load_result = flext_cli_load_file(json_file)
        if load_result.success:
            print(f"✅ Loaded JSON data: {load_result.data['project']}")
        else:
            print(f"❌ JSON load failed: {load_result.error}")

    print()


def example_7_output_formatting() -> None:
    """Example 7: Output formatting with multiple formats."""
    print("=" * 60)
    print("EXAMPLE 7: Output Formatting with Multiple Formats")
    print("=" * 60)

    # Sample data for formatting
    data = [
        {"name": "Alice Johnson", "role": "Developer", "projects": 5},
        {"name": "Bob Smith", "role": "Designer", "projects": 3},
        {"name": "Carol Brown", "role": "Manager", "projects": 8},
        {"name": "David Wilson", "role": "DevOps", "projects": 4},
    ]

    # Create a nice table
    table = flext_cli_create_table(data, title="Team Members")
    print("Rich Table Output:")
    from rich.console import Console

    console = Console()
    console.print(table)
    print()

    # Output in JSON format
    print("JSON Format Output:")
    json_result = flext_cli_output_data(data, "json")
    if not json_result.success:
        print(f"❌ JSON output failed: {json_result.error}")

    print()

    # Output in CSV format
    print("CSV Format Output:")
    csv_result = flext_cli_output_data(data, "csv")
    if not csv_result.success:
        print(f"❌ CSV output failed: {csv_result.error}")

    print()


def example_8_batch_operations() -> None:
    """Example 8: Batch operations with progress tracking."""
    print("=" * 60)
    print("EXAMPLE 8: Batch Operations with Progress Tracking")
    print("=" * 60)

    # Define batch operations
    def validate_config() -> FlextResult[str]:
        """Simulate config validation."""
        return FlextResult.ok("Configuration validated")

    def load_data() -> FlextResult[str]:
        """Simulate data loading."""
        import time

        time.sleep(0.2)  # Simulate work
        return FlextResult.ok("Data loaded successfully")

    def process_data() -> FlextResult[str]:
        """Simulate data processing."""
        import time

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

    batch_result = flext_cli_batch_execute(
        operations, stop_on_error=True, progress_description="Processing pipeline",
    )

    if batch_result.success:
        print("✅ All batch operations completed!")
        for operation_name, result_info in batch_result.data.items():
            if result_info["success"]:
                print(f"   ✅ {operation_name}: {result_info['data']}")
            else:
                print(f"   ❌ {operation_name}: {result_info['error']}")
    else:
        print(f"❌ Batch execution failed: {batch_result.error}")

    print()


def example_9_auto_config_loading() -> None:
    """Example 9: Automatic configuration loading with hierarchy."""
    print("=" * 60)
    print("EXAMPLE 9: Automatic Configuration Loading")
    print("=" * 60)

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

    # Save config file
    save_result = flext_cli_save_file(sample_config, config_file)
    if save_result.success:
        print(f"✅ Created demo config: {config_file}")
    else:
        print(f"❌ Config creation failed: {save_result.error}")
        return

    # Auto-load configuration
    config_result = flext_cli_auto_config("demo", [str(config_file)])

    if config_result.success:
        loaded_config = config_result.data
        print("✅ Configuration loaded successfully!")
        print(f"   Profile: {loaded_config['profile']}")
        print(f"   API URL: {loaded_config['api_url']}")
        print(f"   Timeout: {loaded_config['timeout']}")
        print(f"   Config Source: {loaded_config['config_source']}")
        print(f"   Loaded At: {loaded_config['loaded_at']}")
    else:
        print(f"❌ Config loading failed: {config_result.error}")

    print()


def main() -> None:
    """Run all examples."""
    print("FLEXT CLI Library - Basic Usage Examples")
    print("=" * 80)
    print()

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

    print("=" * 80)
    print("All examples completed! 🎉")
    print()
    print("Key Benefits Demonstrated:")
    print("  ✅ 85%+ boilerplate reduction")
    print("  ✅ FlextResult railway-oriented programming")
    print("  ✅ Type-safe validation with detailed errors")
    print("  ✅ Rich console integration with zero config")
    print("  ✅ Automatic format detection for files")
    print("  ✅ Progress tracking and batch operations")
    print("  ✅ Configuration management with hierarchy")
    print("  ✅ Decorator-based functionality injection")


if __name__ == "__main__":
    main()
