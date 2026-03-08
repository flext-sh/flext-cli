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
- FlextResult error handling - No try/except needed

HOW TO USE IN YOUR CLI:
Replace input() calls with FlextCliPrompts for better UX and error handling
Use Rich Prompt.ask() for advanced validation and type safety

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from models import AppWizardConfig, DatabaseWizardConfig, NumericPromptResult

from flext_cli import FlextCli, FlextCliPrompts, r

cli = FlextCli()
prompts = FlextCliPrompts()


def get_user_configuration() -> r[str]:
    """Collect configuration from user in YOUR app."""
    cli.print("Setting up your application...", style="cyan")
    name_result = prompts.prompt("Project name:", default="my-project")
    if name_result.is_success:
        project_name = name_result.value
        cli.print(f"✅ Project: {project_name}", style="green")
        return r[str].ok(project_name)
    cli.print(f"Error: {name_result.error}", style="bold red")
    return r[str].fail(name_result.error or "Failed to get configuration")


def authenticate_user() -> bool:
    """Secure password collection in YOUR app."""
    password_result = prompts.prompt_password("Enter password:")
    if password_result.is_failure:
        cli.print(f"Error: {password_result.error}", style="bold red")
        return False
    password = password_result.value
    if len(password) < 8:
        cli.print("❌ Password must be at least 8 characters", style="bold red")
        return False
    cli.print("✅ Password accepted", style="green")
    return True


def delete_database(database_name: str) -> None:
    """Confirm before destructive operations in YOUR app."""
    confirm_result = prompts.confirm(
        f"⚠️  Delete database '{database_name}'? This cannot be undone!", default=False
    )
    if confirm_result.is_failure:
        cli.print(f"Error: {confirm_result.error}", style="bold red")
        return
    if confirm_result.value:
        cli.print(f"🗑️  Deleting {database_name}...", style="yellow")
        cli.print("✅ Database deleted", style="green")
    else:
        cli.print("❌ Operation cancelled", style="cyan")


def select_environment() -> r[str]:
    """Environment selection in YOUR deployment tool."""
    environments = ["development", "staging", "production"]
    choice_result = prompts.prompt_choice(
        "Select deployment environment:", choices=environments
    )
    if choice_result.is_failure:
        cli.print(f"Error: {choice_result.error}", style="bold red")
        return r[str].fail(choice_result.error or "Failed to select environment")
    selected = choice_result.value
    cli.print(f"🚀 Deploying to: {selected}", style="green")
    if selected == "production":
        confirm = prompts.confirm("⚠️  Deploy to production?", default=False)
        if confirm.is_success and confirm.value:
            return r[str].ok(selected)
        return r[str].fail("Production deployment cancelled by user")
    return r[str].ok(selected)


def database_setup_wizard() -> r[DatabaseWizardConfig]:
    """Multi-step configuration wizard for YOUR application."""
    cli.print("📝 Database Setup Wizard", style="bold cyan")
    host_result = prompts.prompt("Database host:", default="localhost")
    if host_result.is_failure:
        return r[DatabaseWizardConfig].fail(host_result.error or "Failed to get host")
    host = host_result.value
    port_result = prompts.prompt("Port:", default="5432")
    if port_result.is_failure:
        return r[DatabaseWizardConfig].fail(port_result.error or "Failed to get port")
    try:
        port = int(port_result.value)
    except ValueError:
        return r[DatabaseWizardConfig].fail("Port must be a number")
    db_result = prompts.prompt("Database name:")
    if db_result.is_failure:
        return r[DatabaseWizardConfig].fail(
            db_result.error or "Failed to get database name"
        )
    database = db_result.value
    pwd_result = prompts.prompt_password("Database password:")
    if pwd_result.is_failure:
        return r[DatabaseWizardConfig].fail(
            pwd_result.error or "Failed to get password"
        )
    password = pwd_result.value
    cli.print("\n📋 Review configuration:", style="yellow")
    display_data = [
        {"Setting": "host", "Value": host},
        {"Setting": "port", "Value": str(port)},
        {"Setting": "database", "Value": database},
        {"Setting": "password", "Value": "********"},
    ]
    cli.show_table(
        display_data, headers=["Setting", "Value"], title="Database Configuration"
    )
    confirm = prompts.confirm("Save this configuration?", default=True)
    if confirm.is_success and confirm.value:
        cli.print("✅ Configuration saved!", style="green")
        return r[DatabaseWizardConfig].ok(
            DatabaseWizardConfig(
                host=host, port=port, database=database, password=password
            )
        )
    cli.print("❌ Setup cancelled", style="yellow")
    return r[DatabaseWizardConfig].fail("Setup cancelled by user")


def validate_email_input() -> r[str]:
    """Email validation pattern for YOUR user input."""

    def is_valid_email(email: str) -> r[str]:
        """Your validation function."""
        if not email or "@" not in email or "." not in email:
            return r[str].fail("Invalid email format")
        return r[str].ok(email)

    email_result = prompts.prompt("Enter email address:")
    if email_result.is_failure:
        cli.print(f"❌ Prompt failed: {email_result.error}", style="bold red")
        return r[str].fail(email_result.error or "Prompt failed")
    email = email_result.value
    validated = is_valid_email(email)
    if validated.is_success:
        cli.print(f"✅ Valid email: {validated.value}", style="green")
        return validated
    cli.print(f"❌ {validated.error}", style="bold red")
    return validated


def flext_prompt_with_validation() -> r[int]:
    """Use FlextCli prompts with custom validation logic."""
    cli.print("\n📝 FlextCli Prompts with Custom Validation", style="cyan")
    name_result = prompts.prompt("Enter your name", default="Anonymous")
    if name_result.is_success:
        name = name_result.value
        cli.print(f"✅ Name: {name}", style="green")
    else:
        cli.print(f"❌ Error: {name_result.error}", style="red")
        return r[int].fail(name_result.error or "Name prompt failed")
    env_result = prompts.prompt_choice(
        "Select environment", choices=["dev", "staging", "prod"], default="dev"
    )
    if env_result.is_success:
        environment = env_result.value
        cli.print(f"✅ Environment: {environment}", style="green")
    else:
        cli.print(f"❌ Error: {env_result.error}", style="red")
        return r[int].fail(env_result.error or "Environment choice failed")

    def validate_port(value: str) -> r[int]:
        """Validate port number using FlextResult pattern."""
        try:
            port = int(value)
            if not 1024 <= port <= 65535:
                return r[int].fail("Port must be between 1024 and 65535")
            return r[int].ok(port)
        except ValueError:
            return r[int].fail("Port must be a valid number")

    port_result = prompts.prompt("Enter port number", default="8080")
    if port_result.is_success:
        port_input = port_result.value
        validation = validate_port(port_input)
        if validation.is_success:
            validated_port = validation.value
            cli.print(f"✅ Port: {validated_port}", style="green")
            return r[int].ok(validated_port)
        cli.print(f"❌ {validation.error}", style="bold red")
        return validation
    cli.print(f"❌ Error: {port_result.error}", style="red")
    return r[int].fail(port_result.error or "Port prompt failed")


def flext_confirm_prompts() -> bool:
    """Use FlextCli confirm() for boolean confirmations."""
    cli.print("\n🔘 Boolean Confirmations", style="cyan")
    proceed_result = prompts.confirm("Would you like to proceed?", default=True)
    if proceed_result.is_success and proceed_result.value:
        cli.print("✅ Proceeding with operation", style="green")
    else:
        cli.print("❌ Operation cancelled", style="yellow")
    delete_result = prompts.confirm(
        "⚠️  Delete all data? This cannot be undone!", default=False
    )
    if delete_result.is_success and delete_result.value:
        cli.print("🗑️  Deleting all data...", style="red")
        return True
    cli.print("✅ Data preserved", style="green")
    return False


def flext_numeric_prompts() -> r[NumericPromptResult]:
    """Use FlextCli prompts with numeric validation."""
    cli.print("\n🔢 Type-Safe Numeric Input", style="cyan")

    def validate_int(
        value: str, min_val: int | None = None, max_val: int | None = None
    ) -> r[int]:
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return r[int].fail(f"Value must be >= {min_val}")
            if max_val is not None and num > max_val:
                return r[int].fail(f"Value must be <= {max_val}")
            return r[int].ok(num)
        except ValueError:
            return r[int].fail("Value must be a valid integer")

    def validate_float(value: str) -> r[float]:
        try:
            return r[float].ok(float(value))
        except ValueError:
            return r[float].fail("Value must be a valid number")

    workers = 4
    cpu_limit = 2.5
    percentage = 50
    workers_result = prompts.prompt("Number of worker processes", default="4")
    if workers_result.is_success:
        workers_validation = validate_int(workers_result.value, min_val=1, max_val=32)
        if workers_validation.is_success:
            workers = workers_validation.value
            cli.print(
                f"✅ Workers: {workers} (type: {type(workers).__name__})", style="green"
            )
    cpu_result = prompts.prompt("CPU limit (cores)", default="2.5")
    if cpu_result.is_success:
        cpu_validation = validate_float(cpu_result.value)
        if cpu_validation.is_success:
            cpu_limit = cpu_validation.value
            cli.print(
                f"✅ CPU Limit: {cpu_limit} (type: {type(cpu_limit).__name__})",
                style="green",
            )
    percentage_result = prompts.prompt("Enter percentage (0-100)", default="50")
    if percentage_result.is_success:
        pct_validation = validate_int(percentage_result.value, min_val=0, max_val=100)
        if pct_validation.is_success:
            percentage = pct_validation.value
            cli.print(f"✅ Percentage: {percentage}%", style="green")
    return r[NumericPromptResult].ok(
        NumericPromptResult(workers=workers, cpu_limit=cpu_limit, percentage=percentage)
    )


def flext_configuration_wizard() -> r[AppWizardConfig]:
    """Complete configuration wizard using FlextCli prompts."""
    cli.print("\n⚙️  Application Configuration Wizard", style="bold cyan")
    name_result = prompts.prompt("Application name", default="my-app")
    if name_result.is_failure:
        return r[AppWizardConfig].fail(
            name_result.error or "Failed to get application name"
        )
    app_name = name_result.value
    env_result = prompts.prompt_choice(
        "Environment",
        choices=["development", "staging", "production"],
        default="development",
    )
    if env_result.is_failure:
        return r[AppWizardConfig].fail(
            env_result.error or "Failed to select environment"
        )
    environment = env_result.value

    def validate_port(value: str) -> r[int]:
        try:
            port = int(value)
            if not 1024 <= port <= 65535:
                return r[int].fail("Port must be between 1024-65535")
            return r[int].ok(port)
        except ValueError:
            return r[int].fail("Port must be a number")

    port = 8080
    port_result = prompts.prompt("Port number", default="8080")
    if port_result.is_success:
        port_validation = validate_port(port_result.value)
        if port_validation.is_success:
            port = port_validation.value
    cpu_limit = 1.0
    cpu_result = prompts.prompt("CPU limit (cores)", default="1.0")
    if cpu_result.is_success:
        try:
            cpu_limit = float(cpu_result.value)
        except ValueError:
            cli.print("Using default CPU limit: 1.0", style="yellow")
    enable_cache = True
    cache_result = prompts.confirm("Enable caching?", default=True)
    if cache_result.is_success:
        enable_cache = cache_result.value
    enable_auth = True
    auth_result = prompts.confirm("Enable authentication?", default=True)
    if auth_result.is_success:
        enable_auth = auth_result.value
    cli.print("\n📋 Configuration Summary:", style="yellow")
    summary = AppWizardConfig(
        app_name=app_name,
        environment=environment,
        port=port,
        cpu_limit=cpu_limit,
        enable_cache=enable_cache,
        enable_auth=enable_auth,
    )
    display_rows = [
        {"Setting": k, "Value": str(v)} for k, v in summary.model_dump().items()
    ]
    cli.show_table(
        display_rows, headers=["Setting", "Value"], title="Application Configuration"
    )
    save_result = prompts.confirm("Save this configuration?", default=True)
    if save_result.is_success and save_result.value:
        cli.print("✅ Configuration saved!", style="bold green")
        return r[AppWizardConfig].ok(summary)
    cli.print("❌ Configuration discarded", style="yellow")
    return r[AppWizardConfig].fail("Configuration discarded by user")


def main() -> None:
    """Examples of using prompts in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Interactive Prompts Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Text Input (setup configuration):", style="bold cyan")
    _ = get_user_configuration()
    cli.print("\n2. Password Input (secure auth):", style="bold cyan")
    _ = authenticate_user()
    cli.print("\n3. Confirmation Prompt (destructive action):", style="bold cyan")
    delete_database("test_database")
    cli.print("\n4. Choice Selection (environment):", style="bold cyan")
    _ = select_environment()
    cli.print("\n5. Multi-Step Wizard (database setup):", style="bold cyan")
    _ = database_setup_wizard()
    cli.print("\n6. Input Validation (email):", style="bold cyan")
    _ = validate_email_input()
    cli.print("\n7. FlextCli Prompts (custom validation):", style="bold cyan")
    _ = flext_prompt_with_validation()
    cli.print("\n8. FlextCli Confirm (boolean prompts):", style="bold cyan")
    _ = flext_confirm_prompts()
    cli.print("\n9. FlextCli Numeric Prompts (type-safe):", style="bold cyan")
    _ = flext_numeric_prompts()
    cli.print("\n10. FlextCli Configuration Wizard:", style="bold cyan")
    _ = flext_configuration_wizard()
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Prompt Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Replace input() with prompts.prompt() for better UX", style="white")
    cli.print(
        "  • Use prompts.prompt_password() for secrets (masked input)", style="white"
    )
    cli.print("  • Add prompts.confirm() before destructive operations", style="white")
    cli.print("  • Use prompts.prompt_choice() for validated selections", style="white")
    cli.print("  • Combine with FlextResult for robust validation", style="white")
    cli.print(
        "  • All methods return FlextResult - no try/except needed", style="white"
    )
    cli.print(
        "  • NEVER import rich/click directly - use FlextCli wrappers!", style="white"
    )


if __name__ == "__main__":
    main()
