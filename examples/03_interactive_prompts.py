"""Interactive Prompts - Using flext-cli for User Input in YOUR Code.

WHEN TO USE THIS:
- Building interactive CLI applications
- Need user confirmation before actions
- Collecting configuration data from users
- Building setup wizards or config tools
- Need password/secret input (masked)
- Want type-validated numeric input
- Need choice prompts with validation

FLEXT-CLI PROVIDES:
- prompts.prompt() - Text input with validation
- prompts.prompt_password() - Masked password input
- prompts.confirm() - Yes/No confirmation prompts
- prompts.prompt_choice() - Multiple choice selection
- Rich Prompt.ask() - Advanced prompts with built-in validation
- Rich Confirm.ask() - Boolean confirmations with defaults
- Rich IntPrompt/FloatPrompt - Type-safe numeric input
- FlextCore.Result error handling - No try/except needed

HOW TO USE IN YOUR CLI:
Replace input() calls with FlextCliPrompts for better UX and error handling
Use Rich Prompt.ask() for advanced validation and type safety

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextCore

from flext_cli import FlextCli, FlextCliPrompts
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()
prompts = FlextCliPrompts()


# ============================================================================
# PATTERN 1: Text input in YOUR CLI application
# ============================================================================


def get_user_configuration() -> str | None:
    """Collect configuration from user in YOUR app."""
    cli.formatters.print("Setting up your application...", style="cyan")

    # Instead of: project_name = input("Project name: ")
    name_result = prompts.prompt("Project name:", default="my-project")

    if name_result.is_success:
        project_name = name_result.unwrap()
        cli.formatters.print(f"✅ Project: {project_name}", style="green")
        return project_name
    cli.formatters.print(f"Error: {name_result.error}", style="bold red")
    return None


# ============================================================================
# PATTERN 2: Password input in YOUR authentication flow
# ============================================================================


def authenticate_user() -> bool:
    """Secure password collection in YOUR app."""
    # Instead of: password = input("Password: ")  # Shows password in terminal!
    password_result = prompts.prompt_password("Enter password:")

    if password_result.is_failure:
        cli.formatters.print(f"Error: {password_result.error}", style="bold red")
        return False

    password = password_result.unwrap()

    # Your validation logic
    if len(password) < 8:
        cli.formatters.print(
            "❌ Password must be at least 8 characters", style="bold red"
        )
        return False

    cli.formatters.print("✅ Password accepted", style="green")
    return True


# ============================================================================
# PATTERN 3: Confirmation prompts before destructive actions
# ============================================================================


def delete_database(database_name: str) -> None:
    """Confirm before destructive operations in YOUR app."""
    # Instead of: confirm = input(f"Delete {database_name}? (y/n): ")
    confirm_result = prompts.confirm(
        f"⚠️  Delete database '{database_name}'? This cannot be undone!",
        default=False,  # Safe default
    )

    if confirm_result.is_failure:
        cli.formatters.print(f"Error: {confirm_result.error}", style="bold red")
        return

    if confirm_result.unwrap():
        cli.formatters.print(f"🗑️  Deleting {database_name}...", style="yellow")
        # Your deletion logic here
        cli.formatters.print("✅ Database deleted", style="green")
    else:
        cli.formatters.print("❌ Operation cancelled", style="cyan")


# ============================================================================
# PATTERN 4: Choice selection in YOUR menu system
# ============================================================================


def select_environment() -> str | None:
    """Environment selection in YOUR deployment tool."""
    environments = ["development", "staging", "production"]

    # Instead of: env = input("Select env (1-3): ")
    choice_result = prompts.prompt_choice(
        "Select deployment environment:", choices=environments
    )

    if choice_result.is_failure:
        cli.formatters.print(f"Error: {choice_result.error}", style="bold red")
        return None

    selected = choice_result.unwrap()
    cli.formatters.print(f"🚀 Deploying to: {selected}", style="green")

    # Show warning for production
    if selected == "production":
        confirm = prompts.confirm("⚠️  Deploy to production?", default=False)
        if confirm.is_success and confirm.unwrap():
            return selected
        return None

    return selected


# ============================================================================
# PATTERN 5: Multi-step wizard in YOUR setup tool
# ============================================================================


def database_setup_wizard() -> dict[str, str | int | bool | float] | None:
    """Multi-step configuration wizard for YOUR application."""
    cli.formatters.print("📝 Database Setup Wizard", style="bold cyan")

    config: dict[str, str | int | bool | float] = {}

    # Step 1: Host
    host_result = prompts.prompt("Database host:", default="localhost")
    if host_result.is_failure:
        return None
    config["host"] = host_result.unwrap()

    # Step 2: Port
    port_result = prompts.prompt("Port:", default="5432")
    if port_result.is_failure:
        return None
    config["port"] = int(port_result.unwrap())

    # Step 3: Database name
    db_result = prompts.prompt("Database name:")
    if db_result.is_failure:
        return None
    config["database"] = db_result.unwrap()

    # Step 4: Password (masked)
    pwd_result = prompts.prompt_password("Database password:")
    if pwd_result.is_failure:
        return None
    config["password"] = pwd_result.unwrap()

    # Step 5: Confirm
    cli.formatters.print("\n📋 Review configuration:", style="yellow")
    display_config = {k: v for k, v in config.items() if k != "password"}
    display_config["password"] = "********"

    # Cast to CliDataDict for type safety
    table_data = cast("FlextCliTypes.Data.CliDataDict", display_config)
    table_result = cli.create_table(
        data=table_data,
        headers=["Setting", "Value"],
        title="Database Configuration",
    )
    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())

    confirm = prompts.confirm("Save this configuration?", default=True)
    if confirm.is_success and confirm.unwrap():
        cli.formatters.print("✅ Configuration saved!", style="green")
        return config

    cli.formatters.print("❌ Setup cancelled", style="yellow")
    return None


# ============================================================================
# PATTERN 6: Input validation with FlextCore.Result in YOUR CLI
# ============================================================================


def validate_email_input() -> str | None:
    """Email validation pattern for YOUR user input."""

    def is_valid_email(email: str) -> FlextCore.Result[str]:
        """Your validation function."""
        if not email or "@" not in email or "." not in email:
            return FlextCore.Result[str].fail("Invalid email format")
        return FlextCore.Result[str].ok(email)

    # Get input and validate
    email_result = prompts.prompt("Enter email address:")

    # Validate manually (FlextCore.Result doesn't have and_then in flext-core)
    if email_result.is_failure:
        cli.formatters.print(
            f"❌ Prompt failed: {email_result.error}", style="bold red"
        )
        return None

    email = email_result.unwrap()
    validated = is_valid_email(email)

    if validated.is_success:
        cli.formatters.print(f"✅ Valid email: {validated.unwrap()}", style="green")
        return validated.unwrap()
    cli.formatters.print(f"❌ {validated.error}", style="bold red")
    return None


# ============================================================================
# PATTERN 7: FlextCli prompts with custom validation
# ============================================================================


def flext_prompt_with_validation() -> int | None:
    """Use FlextCli prompts with custom validation logic."""
    cli.formatters.print("\n📝 FlextCli Prompts with Custom Validation", style="cyan")

    # Text prompt with default
    name_result = prompts.prompt("Enter your name", default="Anonymous")
    if name_result.is_success:
        name = name_result.unwrap()
        cli.formatters.print(f"✅ Name: {name}", style="green")
    else:
        cli.formatters.print(f"❌ Error: {name_result.error}", style="red")
        return None

    # Prompt with choices - automatic validation!
    env_result = prompts.prompt_choice(
        "Select environment",
        choices=["dev", "staging", "prod"],
        default="dev",
    )
    if env_result.is_success:
        environment = env_result.unwrap()
        cli.formatters.print(f"✅ Environment: {environment}", style="green")
    else:
        cli.formatters.print(f"❌ Error: {env_result.error}", style="red")
        return None

    # Prompt with custom validation using FlextCore.Result
    def validate_port(value: str) -> FlextCore.Result[int]:
        """Validate port number using FlextCore.Result pattern."""
        try:
            port = int(value)
            if not 1024 <= port <= 65535:
                return FlextCore.Result[int].fail("Port must be between 1024 and 65535")
            return FlextCore.Result[int].ok(port)
        except ValueError:
            return FlextCore.Result[int].fail("Port must be a valid number")

    port_result = prompts.prompt("Enter port number", default="8080")
    if port_result.is_success:
        port_input = port_result.unwrap()
        validation = validate_port(port_input)
        if validation.is_success:
            validated_port = validation.unwrap()
            cli.formatters.print(f"✅ Port: {validated_port}", style="green")
            return validated_port
        cli.formatters.print(f"❌ {validation.error}", style="bold red")
        return None
    cli.formatters.print(f"❌ Error: {port_result.error}", style="red")
    return None


# ============================================================================
# PATTERN 8: FlextCli confirmation prompts
# ============================================================================


def flext_confirm_prompts() -> bool:
    """Use FlextCli confirm() for boolean confirmations."""
    cli.formatters.print("\n🔘 Boolean Confirmations", style="cyan")

    # Simple confirmation with default=True
    proceed_result = prompts.confirm("Would you like to proceed?", default=True)

    if proceed_result.is_success and proceed_result.unwrap():
        cli.formatters.print("✅ Proceeding with operation", style="green")
    else:
        cli.formatters.print("❌ Operation cancelled", style="yellow")

    # Confirmation for destructive action with default=False
    delete_result = prompts.confirm(
        "⚠️  Delete all data? This cannot be undone!", default=False
    )

    if delete_result.is_success and delete_result.unwrap():
        cli.formatters.print("🗑️  Deleting all data...", style="red")
        return True
    cli.formatters.print("✅ Data preserved", style="green")
    return False


# ============================================================================
# PATTERN 9: FlextCli numeric input with validation
# ============================================================================


def flext_numeric_prompts() -> dict[str, int | float]:
    """Use FlextCli prompts with numeric validation."""
    cli.formatters.print("\n🔢 Type-Safe Numeric Input", style="cyan")

    # Integer prompt with validation
    def validate_int(
        value: str, min_val: int | None = None, max_val: int | None = None
    ) -> FlextCore.Result[int]:
        """Validate and convert to integer."""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return FlextCore.Result[int].fail(f"Value must be >= {min_val}")
            if max_val is not None and num > max_val:
                return FlextCore.Result[int].fail(f"Value must be <= {max_val}")
            return FlextCore.Result[int].ok(num)
        except ValueError:
            return FlextCore.Result[int].fail("Value must be a valid integer")

    # Initialize variables at function scope
    workers = 4
    cpu_limit = 2.5
    percentage = 50

    # Get worker count
    workers_result = prompts.prompt("Number of worker processes", default="4")
    if workers_result.is_success:
        workers_validation = validate_int(
            workers_result.unwrap(), min_val=1, max_val=32
        )
        if workers_validation.is_success:
            workers = workers_validation.unwrap()
            cli.formatters.print(
                f"✅ Workers: {workers} (type: {type(workers).__name__})", style="green"
            )

    # Get CPU limit (float)
    def validate_float(value: str) -> FlextCore.Result[float]:
        """Validate and convert to float."""
        try:
            return FlextCore.Result[float].ok(float(value))
        except ValueError:
            return FlextCore.Result[float].fail("Value must be a valid number")

    cpu_result = prompts.prompt("CPU limit (cores)", default="2.5")
    if cpu_result.is_success:
        cpu_validation = validate_float(cpu_result.unwrap())
        if cpu_validation.is_success:
            cpu_limit = cpu_validation.unwrap()
            cli.formatters.print(
                f"✅ CPU Limit: {cpu_limit} (type: {type(cpu_limit).__name__})",
                style="green",
            )

    # Percentage with range validation
    percentage_result = prompts.prompt("Enter percentage (0-100)", default="50")
    if percentage_result.is_success:
        pct_validation = validate_int(
            percentage_result.unwrap(), min_val=0, max_val=100
        )
        if pct_validation.is_success:
            percentage = pct_validation.unwrap()
            cli.formatters.print(f"✅ Percentage: {percentage}%", style="green")
            return {
                "workers": workers,
                "cpu_limit": cpu_limit,
                "percentage": percentage,
            }

    return {}


# ============================================================================
# PATTERN 10: Complete FlextCli configuration wizard
# ============================================================================


def flext_configuration_wizard() -> dict[str, str | int | bool | float] | None:
    """Complete configuration wizard using FlextCli prompts."""
    cli.formatters.print("\n⚙️  Application Configuration Wizard", style="bold cyan")

    config: dict[str, str | int | bool | float] = {}

    # Application name
    name_result = prompts.prompt("Application name", default="my-app")
    if name_result.is_failure:
        return None
    config["app_name"] = name_result.unwrap()

    # Environment with validation
    env_result = prompts.prompt_choice(
        "Environment",
        choices=["development", "staging", "production"],
        default="development",
    )
    if env_result.is_failure:
        return None
    config["environment"] = env_result.unwrap()

    # Port (type-safe integer)
    def validate_port(value: str) -> FlextCore.Result[int]:
        try:
            port = int(value)
            if not 1024 <= port <= 65535:
                return FlextCore.Result[int].fail("Port must be between 1024-65535")
            return FlextCore.Result[int].ok(port)
        except ValueError:
            return FlextCore.Result[int].fail("Port must be a number")

    port_result = prompts.prompt("Port number", default="8080")
    if port_result.is_success:
        port_validation = validate_port(port_result.unwrap())
        if port_validation.is_success:
            config["port"] = port_validation.unwrap()

    # CPU limit (type-safe float)
    cpu_result = prompts.prompt("CPU limit (cores)", default="1.0")
    if cpu_result.is_success:
        try:
            config["cpu_limit"] = float(cpu_result.unwrap())
        except ValueError:
            cli.formatters.print("Using default CPU limit: 1.0", style="yellow")
            config["cpu_limit"] = 1.0

    # Enable features (boolean)
    cache_result = prompts.confirm("Enable caching?", default=True)
    if cache_result.is_success:
        config["enable_cache"] = cache_result.unwrap()

    auth_result = prompts.confirm("Enable authentication?", default=True)
    if auth_result.is_success:
        config["enable_auth"] = auth_result.unwrap()

    # Display configuration
    cli.formatters.print("\n📋 Configuration Summary:", style="yellow")

    # Cast to CliDataDict for type safety
    config_data = cast("FlextCliTypes.Data.CliDataDict", config)
    table_result = cli.create_table(
        data=config_data,
        headers=["Setting", "Value"],
        title="Application Configuration",
    )

    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())

    # Final confirmation
    save_result = prompts.confirm("Save this configuration?", default=True)

    if save_result.is_success and save_result.unwrap():
        cli.formatters.print("✅ Configuration saved!", style="bold green")
        return config

    cli.formatters.print("❌ Configuration discarded", style="yellow")
    return None


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using prompts in YOUR code."""
    cli.formatters.print("=" * 70, style="bold blue")
    cli.formatters.print("  Interactive Prompts Library Usage", style="bold white")
    cli.formatters.print("=" * 70, style="bold blue")

    # Example 1: Text input
    cli.formatters.print("\n1. Text Input (setup configuration):", style="bold cyan")
    get_user_configuration()

    # Example 2: Password input
    cli.formatters.print("\n2. Password Input (secure auth):", style="bold cyan")
    authenticate_user()

    # Example 3: Confirmation prompt
    cli.formatters.print(
        "\n3. Confirmation Prompt (destructive action):", style="bold cyan"
    )
    delete_database("test_database")

    # Example 4: Choice selection
    cli.formatters.print("\n4. Choice Selection (environment):", style="bold cyan")
    select_environment()

    # Example 5: Multi-step wizard
    cli.formatters.print("\n5. Multi-Step Wizard (database setup):", style="bold cyan")
    database_setup_wizard()

    # Example 6: Input validation
    cli.formatters.print("\n6. Input Validation (email):", style="bold cyan")
    validate_email_input()

    # Example 7: FlextCli prompts with validation
    cli.formatters.print(
        "\n7. FlextCli Prompts (custom validation):", style="bold cyan"
    )
    flext_prompt_with_validation()

    # Example 8: FlextCli confirmations
    cli.formatters.print("\n8. FlextCli Confirm (boolean prompts):", style="bold cyan")
    flext_confirm_prompts()

    # Example 9: FlextCli numeric prompts
    cli.formatters.print(
        "\n9. FlextCli Numeric Prompts (type-safe):", style="bold cyan"
    )
    flext_numeric_prompts()

    # Example 10: FlextCli configuration wizard
    cli.formatters.print("\n10. FlextCli Configuration Wizard:", style="bold cyan")
    flext_configuration_wizard()

    cli.formatters.print("\n" + "=" * 70, style="bold blue")
    cli.formatters.print("  ✅ Prompt Examples Complete", style="bold green")
    cli.formatters.print("=" * 70, style="bold blue")

    # Integration guide
    cli.formatters.print("\n💡 Integration Tips:", style="bold cyan")
    cli.formatters.print(
        "  • Replace input() with prompts.prompt() for better UX", style="white"
    )
    cli.formatters.print(
        "  • Use prompts.prompt_password() for secrets (masked input)", style="white"
    )
    cli.formatters.print(
        "  • Add prompts.confirm() before destructive operations", style="white"
    )
    cli.formatters.print(
        "  • Use prompts.prompt_choice() for validated selections", style="white"
    )
    cli.formatters.print(
        "  • Combine with FlextCore.Result for robust validation", style="white"
    )
    cli.formatters.print(
        "  • All methods return FlextCore.Result - no try/except needed", style="white"
    )
    cli.formatters.print(
        "  • NEVER import rich/click directly - use FlextCli wrappers!", style="white"
    )


if __name__ == "__main__":
    main()
