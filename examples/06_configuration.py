"""Configuration - Using flext-cli for Config Management in YOUR CLI.

WHEN TO USE THIS:
- Building CLI tools with configurable settings
- Need to manage environment-specific configs
- Want to load settings from environment variables
- Building tools with user preferences
- Need configuration validation

FLEXT-CLI PROVIDES:
- FlextCliSettings - Configuration management class
- cli.config - Access to current config settings
- Environment variable loading (FLEXT_*)
- Built-in validation with r
- Profile-based configuration

HOW TO USE IN YOUR CLI:
Access config settings through cli.config and customize for YOUR application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import time
from collections.abc import Mapping
from pathlib import Path

from example_utils import display_config_table
from models import AppConfigAdvanced, MyAppConfig

from flext_cli import FlextCli, FlextCliSettings, m, r, t, u

cli = FlextCli()


def get_cli_settings() -> FlextCliSettings:
    """Access flext-cli config settings in YOUR application."""
    config = cli.config

    # Instead of manually reading env vars:
    # debug = os.getenv('DEBUG', 'false').lower() == 'true'
    # log_level = os.getenv('LOG_LEVEL', 'INFO')

    cli.print("📋 Current Configuration:", style="bold cyan")
    cli.print(f"   Debug Mode: {config.debug}", style="cyan")
    cli.print(f"   Log Level: {config.cli_log_level}", style="cyan")
    cli.print(f"   Environment: {config.environment}", style="cyan")
    cli.print(f"   Profile: {config.profile}", style="cyan")

    return config


# ============================================================================
# PATTERN 2: Environment-based config in YOUR deployment tool
# ============================================================================


def load_environment_config() -> m.Cli.DisplayData:
    """Load environment-specific config in YOUR tool. Returns DisplayData model."""
    config = cli.config

    # Check which environment we're in
    environment = config.environment

    if environment == "production":
        cli.print("🚀 Production mode - using production settings", style="bold red")
        # Your production config
        api_url = "https://api.production.example.com"
        max_retries = 5
    elif environment == "staging":
        cli.print("🔧 Staging mode - using staging settings", style="bold yellow")
        # Your staging config
        api_url = "https://api.staging.example.com"
        max_retries = 3
    else:
        cli.print("💻 Development mode - using dev settings", style="bold cyan")
        # Your dev config
        api_url = "http://localhost:8000"
        max_retries = 1

    settings: dict[str, t.JsonValue] = {
        "API URL": api_url,
        "Max Retries": max_retries,
        "Environment": environment,
    }

    cli.print(f"🌍 {environment.capitalize()} Configuration", style="bold cyan")
    display_payload = m.Cli.DisplayData(data=settings)
    display_config_table(cli=cli, config_data=display_payload)

    return display_payload


# ============================================================================
# PATTERN 1: Access built-in config in YOUR CLI
# ============================================================================


def show_config_locations() -> m.Cli.DisplayData:
    """Display config file locations for YOUR application. Returns DisplayData model."""
    config = cli.config

    home_dir = Path.home()
    config_dir = home_dir / ".flext"
    token_file = Path(config.token_file)

    locations: dict[str, t.JsonValue] = {
        "Home Directory": str(home_dir),
        "Config Directory": str(config_dir),
        "Token File": str(token_file),
        "Token Exists": "Yes" if token_file.exists() else "No",
    }

    display_payload = m.Cli.DisplayData(data=locations)
    display_config_table(
        cli=cli,
        config_data=display_payload,
        headers=["Location", "Path"],
    )
    return display_payload


# ============================================================================
# PATTERN 5: Profile-based config in YOUR multi-env tool
# ============================================================================


def load_profile_config(profile_name: str = "default") -> r[FlextCliSettings]:
    """Load profile-specific config in YOUR tool. Returns r[FlextCliSettings]; no None."""
    cli.print(f"📋 Loading profile: {profile_name}", style="bold cyan")

    profile_config = FlextCliSettings(
        profile=profile_name,
        debug=profile_name == "development",
        output_format="json" if profile_name == "production" else "table",
    )

    validate_result = profile_config.validate_output_format_result(
        profile_config.output_format,
    )
    if validate_result.is_failure:
        cli.print(
            f"❌ Profile validation failed: {validate_result.error}",
            style="bold red",
        )
        return r[FlextCliSettings].fail(
            validate_result.error or "Profile validation failed"
        )

    cli.print(f"✅ Profile '{profile_name}' loaded successfully", style="green")

    profile_data: dict[str, t.JsonValue] = {
        "Profile": profile_config.profile,
        "Debug": str(profile_config.debug),
        "Output": profile_config.output_format,
        "Environment": profile_config.environment,
    }

    display_config_table(
        cli=cli,
        config_data=m.Cli.DisplayData(data=profile_data),
    )

    return r[FlextCliSettings].ok(profile_config)


# ============================================================================
# PATTERN 6: Environment variables guide for YOUR users
# ============================================================================


def show_environment_variables() -> None:
    """Display available environment variables for YOUR CLI."""
    cli.print("🌍 Environment Variables", style="bold cyan")

    # Built-in flext-cli env vars
    env_vars = {
        "FLEXT_DEBUG": os.getenv("FLEXT_DEBUG", "false"),
        "FLEXT_LOG_LEVEL": os.getenv("FLEXT_LOG_LEVEL", "INFO"),
        "FLEXT_ENVIRONMENT": os.getenv("FLEXT_ENVIRONMENT", "development"),
        "FLEXT_PROFILE": os.getenv("FLEXT_PROFILE", "default"),
        "FLEXT_OUTPUT_FORMAT": os.getenv("FLEXT_OUTPUT_FORMAT", "table"),
    }

    # Display current values using u.Cli.process
    cli.print("\n📊 Current Environment Variables:", style="yellow")

    def print_env(k: str, v: str) -> None:
        """Print single environment variable."""
        cli.print(f"   {k}={v}", style="cyan")

    _ = u.Cli.process_mapping(env_vars, processor=print_env)

    # Show how to set them
    cli.print("\n💡 How to set environment variables:", style="bold cyan")
    cli.print("   export FLEXT_DEBUG=true", style="white")
    cli.print("   export FLEXT_ENVIRONMENT=production", style="white")
    cli.print("   export FLEXT_LOG_LEVEL=DEBUG", style="white")


# ============================================================================
# PATTERN 7: Config validation workflow in YOUR application
# ============================================================================


def validate_app_config() -> bool:
    """Validate configuration in YOUR application startup."""
    cli.print("🔍 Validating Configuration...", style="bold cyan")

    # Step 1: Validate base config
    cli.print("\n1. Validating base configuration...", style="cyan")
    config = cli.config
    # validate_configuration is a model validator, not a callable method
    # Pydantic validation happens automatically, but we can validate output format
    validate_result = config.validate_output_format_result(config.output_format)
    if validate_result.is_failure:
        cli.print(
            f"   ❌ Base config invalid: {validate_result.error}",
            style="bold red",
        )
        return False
    cli.print("   ✅ Base config valid", style="green")

    # Step 2: Validate custom settings
    cli.print("\n2. Validating custom settings...", style="cyan")
    app_config = MyAppConfig()

    if not app_config.validate_config(cli):
        cli.print("   ❌ Custom config invalid", style="bold red")
        return False

    cli.print("   ✅ Custom config valid", style="green")

    # Step 3: Display complete config
    cli.print("\n3. Configuration summary:", style="cyan")
    app_config.display(cli)

    cli.print("\n✅ All configuration validated successfully!", style="bold green")
    return True


# ============================================================================
# PATTERN 6: Advanced Config with Environment Variables and Validation (Pydantic v2)
# ============================================================================


def load_application_config() -> r[t.ConfigurationMapping]:
    """Load and validate application configuration from environment."""
    cli.print("\n⚙️  Loading Application Configuration:", style="bold cyan")

    # Railway Pattern for config loading
    config_obj = AppConfigAdvanced()
    cli.print("✅ Config object created", style="green")

    # Step 2: Validate configuration
    validate_result = config_obj.validate_to_mapping()
    if validate_result.is_failure:
        return validate_result
    cli.print("✅ Configuration validated", style="green")

    config_data = validate_result.value

    # Step 3: Apply environment-specific overrides
    overridden_data = apply_environment_overrides(config_data)
    cli.print("✅ Environment overrides applied", style="green")

    # Step 4: Initialize dependent services
    final_data = initialize_services(overridden_data)
    cli.print("✅ Services initialized", style="green")

    result: r[t.ConfigurationMapping] = r[t.ConfigurationMapping].ok(final_data)

    if result.is_failure:
        cli.print(f"❌ Configuration failed: {result.error}", style="bold red")
        return result

    cli.print("🎉 Application configuration loaded successfully!", style="bold green")
    return result


def apply_environment_overrides(
    config: Mapping[str, t.ContainerValue],
) -> dict[str, t.ContainerValue]:
    """Apply environment-specific configuration overrides."""
    result: dict[str, t.ContainerValue] = dict(config)
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        max_workers_value = result.get("max_workers", 4)
        try:
            result["max_workers"] = min(int(str(max_workers_value)), 20)
        except (TypeError, ValueError):
            result["max_workers"] = 4
        result["enable_metrics"] = True
    elif env == "testing":
        result["max_workers"] = 1
        result["enable_metrics"] = False

    return result


def initialize_services(
    config: dict[str, t.ContainerValue],
) -> dict[str, t.ContainerValue]:
    """Initialize services based on configuration."""
    # In real code, this would initialize database connections, caches, etc.
    # For demo, just simulate initialization

    time.sleep(0.05)  # Simulate initialization time

    # Add initialization status to config
    config["services_initialized"] = True
    config["initialized_at"] = "2025-11-23T10:00:00Z"

    return config


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using configuration in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Configuration Management Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Access built-in config
    cli.print("\n1. Built-in Configuration (access settings):", style="bold cyan")
    _ = get_cli_settings()

    # Example 2: Environment-based config
    cli.print("\n2. Environment Config (deployment settings):", style="bold cyan")
    _ = load_environment_config()

    # Example 3: Custom config class
    cli.print("\n3. Custom Config Class (app-specific):", style="bold cyan")
    app_config = MyAppConfig()
    _ = app_config.validate_config(cli)
    app_config.display(cli)

    # Example 4: Config locations
    cli.print("\n4. Config Locations (file paths):", style="bold cyan")
    _ = show_config_locations()

    # Example 5: Profile-based config
    cli.print("\n5. Profile-Based Config (multi-environment):", style="bold cyan")
    _ = load_profile_config("production")

    # Example 6: Environment variables
    cli.print("\n6. Environment Variables (configuration guide):", style="bold cyan")
    show_environment_variables()

    # Example 7: Config validation
    cli.print("\n7. Config Validation (startup check):", style="bold cyan")
    _ = validate_app_config()

    # Example 8: Advanced config with env vars
    cli.print("\n8. Advanced Config with Environment Variables:", style="bold cyan")
    config_result = load_application_config()

    if config_result.is_success:
        final_config = config_result.value
        final_config_data: dict[str, t.JsonValue] = {
            k: str(v) for k, v in final_config.items()
        }
        cli.print("Final Application Configuration", style="bold cyan")
        display_config_table(
            cli=cli,
            config_data=m.Cli.DisplayData(data=final_config_data),
        )

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Configuration Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Access config: Use cli.config for built-in settings", style="white")
    cli.print("  • Custom config: Extend FlextCliSettings for your app", style="white")
    cli.print("  • Validation: Use config.validate_business_rules()", style="white")
    cli.print("  • Environment: Use FLEXT_* env vars for configuration", style="white")


if __name__ == "__main__":
    main()
