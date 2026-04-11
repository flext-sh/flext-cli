"""Interactive Prompts - Using flext-cli for User Input in YOUR Code.

WHEN TO USE THIS:
- Building interactive CLI applications
- Need user confirmation before actions
- Collecting configuration data from users
- Building setup wizards or config tools
- Need password/secret input (masked)
- Want type-validated numeric input
- Need choice cli with validation

FLEXT-CLI PROVIDES:
- cli.prompt() - Text input with validation
- cli.prompt_password() - Masked password input
- cli.confirm() - Yes/No confirmation cli
- cli.prompt_choice() - Multiple choice selection
- Rich Prompt.ask() - Advanced cli with built-in validation
- Rich Confirm.ask() - Boolean confirmations with defaults
- Rich IntPrompt/FloatPrompt - Type-safe numeric input
- r error handling - No try/except needed

HOW TO USE IN YOUR CLI:
Replace input() calls with FlextCliPrompts for better UX and error handling
Use Rich Prompt.ask() for advanced validation and type safety

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from examples import c, m
from flext_cli import cli
from flext_core import r

prompts = cli


def collect_user_configuration() -> r[str]:
    """Collect configuration from user in YOUR app."""
    cli.print("Setting up your application...", style=c.Cli.MessageStyles.CYAN)
    name_result = prompts.prompt("Project name:", default="my-project")
    if name_result.success:
        project_name = name_result.value
        cli.print(f"✅ Project: {project_name}", style=c.Cli.MessageStyles.GREEN)
        return r[str].ok(project_name)
    cli.print(f"Error: {name_result.error}", style=c.Cli.MessageStyles.BOLD_RED)
    return r[str].fail(
        name_result.error or c.EXAMPLE_ERR_FAILED_COLLECT_CONFIGURATION,
    )


def authenticate_user() -> bool:
    """Secure password collection in YOUR app."""
    password_result = prompts.prompt_password("Enter password:")
    if password_result.failure:
        cli.print(f"Error: {password_result.error}", style=c.Cli.MessageStyles.BOLD_RED)
        return False
    password = password_result.value
    if len(password) < c.EXAMPLE_MIN_PASSWORD_LENGTH:
        cli.print(
            "❌ Password must be at least 8 characters",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False
    cli.print("✅ Password accepted", style=c.Cli.MessageStyles.GREEN)
    return True


def delete_database(database_name: str) -> None:
    """Confirm before destructive operations in YOUR app."""
    confirm_result = prompts.confirm(
        f"⚠️  Delete database '{database_name}'? This cannot be undone!",
        default=False,
    )
    if confirm_result.failure:
        cli.print(f"Error: {confirm_result.error}", style=c.Cli.MessageStyles.BOLD_RED)
        return
    if confirm_result.value:
        cli.print(f"🗑️  Deleting {database_name}...", style=c.Cli.MessageStyles.YELLOW)
        cli.print("✅ Database deleted", style=c.Cli.MessageStyles.GREEN)
    else:
        cli.print("❌ Operation cancelled", style=c.Cli.MessageStyles.CYAN)


def select_environment() -> r[str]:
    """Environment selection in YOUR deployment tool."""
    environments = list(c.EXAMPLE_DEPLOYMENT_ENVIRONMENTS)
    choice_result = prompts.prompt_choice(
        "Select deployment environment:",
        choices=environments,
    )
    if choice_result.failure:
        cli.print(f"Error: {choice_result.error}", style=c.Cli.MessageStyles.BOLD_RED)
        return r[str].fail(
            choice_result.error or c.EXAMPLE_ERR_FAILED_SELECT_ENVIRONMENT,
        )
    selected = choice_result.value
    cli.print(f"🚀 Deploying to: {selected}", style=c.Cli.MessageStyles.GREEN)
    if selected == c.EXAMPLE_ENV_VALUE_PRODUCTION:
        confirm = prompts.confirm("⚠️  Deploy to production?", default=False)
        if confirm.success and confirm.value:
            return r[str].ok(selected)
        return r[str].fail(c.EXAMPLE_ERR_SETUP_CANCELLED)
    return r[str].ok(selected)


def database_setup_wizard() -> r[m.Examples.DatabaseWizardConfig]:
    """Multi-step configuration wizard for YOUR application."""
    cli.print("📝 Database Setup Wizard", style=c.Cli.MessageStyles.BOLD_CYAN)
    host_result = prompts.prompt("Database host:", default=c.EXAMPLE_DEFAULT_HOST)
    if host_result.failure:
        return r[m.Examples.DatabaseWizardConfig].fail(
            host_result.error or c.EXAMPLE_ERR_FAILED_COLLECT_HOST,
        )
    host = host_result.value
    port_result = prompts.prompt("Port:", default=str(c.EXAMPLE_DEFAULT_DB_PORT))
    if port_result.failure:
        return r[m.Examples.DatabaseWizardConfig].fail(
            port_result.error or c.EXAMPLE_ERR_FAILED_COLLECT_PORT,
        )
    try:
        port = int(port_result.value)
    except ValueError:
        return r[m.Examples.DatabaseWizardConfig].fail(c.EXAMPLE_ERR_PORT_NUMBER)
    db_result = prompts.prompt("Database name:")
    if db_result.failure:
        return r[m.Examples.DatabaseWizardConfig].fail(
            db_result.error or c.EXAMPLE_ERR_FAILED_GET_DATABASE_NAME,
        )
    database = db_result.value
    pwd_result = prompts.prompt_password("Database password:")
    if pwd_result.failure:
        return r[m.Examples.DatabaseWizardConfig].fail(
            pwd_result.error or c.EXAMPLE_ERR_FAILED_GET_PASSWORD,
        )
    password = pwd_result.value
    cli.print("\n📋 Review configuration:", style=c.Cli.MessageStyles.YELLOW)
    display_data = [
        {"Setting": "host", "Value": host},
        {"Setting": "port", "Value": str(port)},
        {"Setting": "database", "Value": database},
        {"Setting": "password", "Value": "********"},
    ]
    cli.show_table(
        display_data,
        headers=list(c.EXAMPLE_TABLE_HEADERS_SETTING_VALUE),
        title="Database Configuration",
    )
    confirm = prompts.confirm("Save this configuration?", default=True)
    if confirm.success and confirm.value:
        cli.print("✅ Configuration saved!", style=c.Cli.MessageStyles.GREEN)
        return r[m.Examples.DatabaseWizardConfig].ok(
            m.Examples.DatabaseWizardConfig(
                host=host,
                port=port,
                database=database,
                password=password,
            ),
        )
    cli.print("❌ Setup cancelled", style=c.Cli.MessageStyles.YELLOW)
    return r[m.Examples.DatabaseWizardConfig].fail(c.EXAMPLE_ERR_SETUP_CANCELLED)


def validate_email_input() -> r[str]:
    """Email validation pattern for YOUR user input."""

    def validate_email(email: str) -> r[str]:
        """Your validation function."""
        if not c.EXAMPLE_REGEX_EMAIL.fullmatch(email):
            return r[str].fail(c.EXAMPLE_ERR_INVALID_EMAIL_FORMAT)
        return r[str].ok(email)

    email_result = prompts.prompt("Enter email address:")
    if email_result.failure:
        cli.print(
            f"❌ Prompt failed: {email_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return r[str].fail(email_result.error or "Prompt failed")
    email = email_result.value
    validated = validate_email(email)
    if validated.success:
        cli.print(f"✅ Valid email: {validated.value}", style=c.Cli.MessageStyles.GREEN)
        return validated
    cli.print(f"❌ {validated.error}", style=c.Cli.MessageStyles.BOLD_RED)
    return validated


def flext_prompt_with_validation() -> r[int]:
    """Use cli cli with custom validation logic."""
    cli.print("\n📝 cli Prompts with Custom Validation", style=c.Cli.MessageStyles.CYAN)
    name_result = prompts.prompt("Enter your name", default="Anonymous")
    if name_result.success:
        name = name_result.value
        cli.print(f"✅ Name: {name}", style=c.Cli.MessageStyles.GREEN)
    else:
        cli.print(f"❌ Error: {name_result.error}", style=c.Cli.MessageStyles.RED)
        return r[int].fail(name_result.error or c.EXAMPLE_ERR_NAME_PROMPT_FAILED)
    env_result = prompts.prompt_choice(
        "Select environment",
        choices=list(c.EXAMPLE_DEPLOYMENT_ENVIRONMENTS_SHORT),
        default="dev",
    )
    if env_result.success:
        environment = env_result.value
        cli.print(f"✅ Environment: {environment}", style=c.Cli.MessageStyles.GREEN)
    else:
        cli.print(f"❌ Error: {env_result.error}", style=c.Cli.MessageStyles.RED)
        return r[int].fail(
            env_result.error or c.EXAMPLE_ERR_ENVIRONMENT_CHOICE_FAILED,
        )

    def validate_port(value: str) -> r[int]:
        """Validate port number using r pattern."""
        try:
            port = int(value)
            if not c.EXAMPLE_MIN_PORT <= port <= c.EXAMPLE_MAX_PORT:
                return r[int].fail(
                    c.EXAMPLE_ERR_PORT_RANGE_FMT.format(
                        min_port=c.EXAMPLE_MIN_PORT,
                        max_port=c.EXAMPLE_MAX_PORT,
                    ),
                )
            return r[int].ok(port)
        except ValueError:
            return r[int].fail(c.EXAMPLE_ERR_PORT_VALID_NUMBER)

    port_result = prompts.prompt(
        "Enter port number",
        default=str(c.EXAMPLE_DEFAULT_APP_PORT),
    )
    if port_result.success:
        port_input = port_result.value
        validation = validate_port(port_input)
        if validation.success:
            validated_port = validation.value
            cli.print(f"✅ Port: {validated_port}", style=c.Cli.MessageStyles.GREEN)
            return r[int].ok(validated_port)
        cli.print(f"❌ {validation.error}", style=c.Cli.MessageStyles.BOLD_RED)
        return validation
    cli.print(f"❌ Error: {port_result.error}", style=c.Cli.MessageStyles.RED)
    return r[int].fail(port_result.error or c.EXAMPLE_ERR_PORT_PROMPT_FAILED)


def flext_confirm_prompts() -> bool:
    """Use cli confirm() for boolean confirmations."""
    cli.print("\n🔘 Boolean Confirmations", style=c.Cli.MessageStyles.CYAN)
    proceed_result = prompts.confirm("Would you like to proceed?", default=True)
    if proceed_result.success and proceed_result.value:
        cli.print("✅ Proceeding with operation", style=c.Cli.MessageStyles.GREEN)
    else:
        cli.print("❌ Operation cancelled", style=c.Cli.MessageStyles.YELLOW)
    delete_result = prompts.confirm(
        "⚠️  Delete all data? This cannot be undone!",
        default=False,
    )
    if delete_result.success and delete_result.value:
        cli.print("🗑️  Deleting all data...", style=c.Cli.MessageStyles.RED)
        return True
    cli.print("✅ Data preserved", style=c.Cli.MessageStyles.GREEN)
    return False


def flext_numeric_prompts() -> r[m.Examples.NumericPromptResult]:
    """Use cli cli with numeric validation."""
    cli.print("\n🔢 Type-Safe Numeric Input", style=c.Cli.MessageStyles.CYAN)

    def validate_int(
        value: str,
        min_val: int | None = None,
        max_val: int | None = None,
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

    workers = c.EXAMPLE_DEFAULT_MAX_WORKERS
    cpu_limit = c.EXAMPLE_DEFAULT_CPU_LIMIT_PROMPTS
    percentage = c.EXAMPLE_DEFAULT_PERCENTAGE
    workers_result = prompts.prompt(
        "Number of worker processes",
        default=str(c.EXAMPLE_DEFAULT_MAX_WORKERS),
    )
    if workers_result.success:
        workers_validation = validate_int(
            workers_result.value,
            min_val=1,
            max_val=c.EXAMPLE_MAX_WORKERS,
        )
        if workers_validation.success:
            workers = workers_validation.value
            cli.print(
                f"✅ Workers: {workers} (type: {type(workers).__name__})",
                style=c.Cli.MessageStyles.GREEN,
            )
    cpu_result = prompts.prompt(
        "CPU limit (cores)",
        default=str(c.EXAMPLE_DEFAULT_CPU_LIMIT_PROMPTS),
    )
    if cpu_result.success:
        cpu_validation = validate_float(cpu_result.value)
        if cpu_validation.success:
            cpu_limit = cpu_validation.value
            cli.print(
                f"✅ CPU Limit: {cpu_limit} (type: {type(cpu_limit).__name__})",
                style=c.Cli.MessageStyles.GREEN,
            )
    percentage_result = prompts.prompt(
        "Enter percentage (0-100)",
        default=str(c.EXAMPLE_DEFAULT_PERCENTAGE),
    )
    if percentage_result.success:
        pct_validation = validate_int(percentage_result.value, min_val=0, max_val=100)
        if pct_validation.success:
            percentage = pct_validation.value
            cli.print(f"✅ Percentage: {percentage}%", style=c.Cli.MessageStyles.GREEN)
    return r[m.Examples.NumericPromptResult].ok(
        m.Examples.NumericPromptResult(
            workers=workers,
            cpu_limit=cpu_limit,
            percentage=percentage,
        ),
    )


def flext_configuration_wizard() -> r[m.Examples.AppWizardConfig]:
    """Complete configuration wizard using cli cli."""
    cli.print(
        "\n⚙️  Application Configuration Wizard", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    name_result = prompts.prompt(
        "Application name",
        default=c.EXAMPLE_DEFAULT_APP_NAME,
    )
    if name_result.failure:
        return r[m.Examples.AppWizardConfig].fail(
            name_result.error or "Failed to get application name",
        )
    app_name = name_result.value
    env_result = prompts.prompt_choice(
        "Environment",
        choices=list(c.EXAMPLE_DEPLOYMENT_ENVIRONMENTS),
        default=c.EXAMPLE_DEFAULT_ENVIRONMENT,
    )
    if env_result.failure:
        return r[m.Examples.AppWizardConfig].fail(
            env_result.error or "Failed to select environment",
        )
    environment = env_result.value

    def validate_port(value: str) -> r[int]:
        try:
            port = int(value)
            if not c.EXAMPLE_MIN_PORT <= port <= c.EXAMPLE_MAX_PORT:
                return r[int].fail(
                    c.EXAMPLE_ERR_PORT_RANGE_SHORT_FMT.format(
                        min_port=c.EXAMPLE_MIN_PORT,
                        max_port=c.EXAMPLE_MAX_PORT,
                    ),
                )
            return r[int].ok(port)
        except ValueError:
            return r[int].fail(c.EXAMPLE_ERR_PORT_NUMBER)

    port = c.EXAMPLE_DEFAULT_APP_PORT
    port_result = prompts.prompt("Port number", default=str(c.EXAMPLE_DEFAULT_APP_PORT))
    if port_result.success:
        port_validation = validate_port(port_result.value)
        if port_validation.success:
            port = port_validation.value
    cpu_limit = c.EXAMPLE_DEFAULT_CPU_LIMIT
    cpu_result = prompts.prompt(
        "CPU limit (cores)",
        default=str(c.EXAMPLE_DEFAULT_CPU_LIMIT),
    )
    if cpu_result.success:
        try:
            cpu_limit = float(cpu_result.value)
        except ValueError:
            cli.print(
                f"Using default CPU limit: {c.EXAMPLE_DEFAULT_CPU_LIMIT}",
                style=c.Cli.MessageStyles.YELLOW,
            )
    enable_cache = True
    cache_result = prompts.confirm("Enable caching?", default=True)
    if cache_result.success:
        enable_cache = cache_result.value
    enable_auth = True
    auth_result = prompts.confirm("Enable authentication?", default=True)
    if auth_result.success:
        enable_auth = auth_result.value
    cli.print("\n📋 Configuration Summary:", style=c.Cli.MessageStyles.YELLOW)
    summary = m.Examples.AppWizardConfig(
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
        display_rows,
        headers=list(c.EXAMPLE_TABLE_HEADERS_SETTING_VALUE),
        title="Application Configuration",
    )
    save_result = prompts.confirm("Save this configuration?", default=True)
    if save_result.success and save_result.value:
        cli.print("✅ Configuration saved!", style=c.Cli.MessageStyles.BOLD_GREEN)
        return r[m.Examples.AppWizardConfig].ok(summary)
    cli.print("❌ Configuration discarded", style=c.Cli.MessageStyles.YELLOW)
    return r[m.Examples.AppWizardConfig].fail(c.EXAMPLE_ERR_CONFIG_DISCARDED)


def main() -> None:
    """Examples of using cli in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Interactive Prompts Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n1. Text Input (setup configuration):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = collect_user_configuration()
    cli.print("\n2. Password Input (secure auth):", style=c.Cli.MessageStyles.BOLD_CYAN)
    _ = authenticate_user()
    cli.print(
        "\n3. Confirmation Prompt (destructive action):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    delete_database("test_database")
    cli.print(
        "\n4. Choice Selection (environment):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = select_environment()
    cli.print(
        "\n5. Multi-Step Wizard (database setup):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = database_setup_wizard()
    cli.print("\n6. Input Validation (email):", style=c.Cli.MessageStyles.BOLD_CYAN)
    _ = validate_email_input()
    cli.print(
        "\n7. cli Prompts (custom validation):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = flext_prompt_with_validation()
    cli.print("\n8. cli Confirm (boolean cli):", style=c.Cli.MessageStyles.BOLD_CYAN)
    _ = flext_confirm_prompts()
    cli.print(
        "\n9. cli Numeric Prompts (type-safe):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = flext_numeric_prompts()
    cli.print("\n10. cli Configuration Wizard:", style=c.Cli.MessageStyles.BOLD_CYAN)
    _ = flext_configuration_wizard()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  ✅ Prompt Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Replace input() with cli.prompt() for better UX",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Use cli.prompt_password() for secrets (masked input)",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Add cli.confirm() before destructive operations",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Use cli.prompt_choice() for validated selections",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Combine with r for robust validation", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • All methods return r - no try/except needed",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • NEVER import rich/click directly - use cli wrappers!",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()
