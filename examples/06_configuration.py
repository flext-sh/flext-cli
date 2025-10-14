"""Configuration - Using flext-cli for Config Management in YOUR CLI.

WHEN TO USE THIS:
- Building CLI tools with configurable settings
- Need to manage environment-specific configs
- Want to load settings from environment variables
- Building tools with user preferences
- Need configuration validation

FLEXT-CLI PROVIDES:
- FlextCliConfig - Configuration management class
- cli.config - Access to current config settings
- Environment variable loading (FLEXT_*)
- Built-in validation with FlextCore.Result
- Profile-based configuration

HOW TO USE IN YOUR CLI:
Access config settings through cli.config and customize for YOUR application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from flext_cli import FlextCli, FlextCliConfig
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()


# ============================================================================
# PATTERN 1: Access built-in config in YOUR CLI
# ============================================================================


def get_cli_settings() -> FlextCliConfig:
    """Access flext-cli config settings in YOUR application."""
    config = cli.config

    # Instead of manually reading env vars:
    # debug = os.getenv('DEBUG', 'false').lower() == 'true'
    # log_level = os.getenv('LOG_LEVEL', 'INFO')

    cli.print("📋 Current Configuration:", style="bold cyan")
    cli.print(f"   Debug Mode: {config.debug}", style="cyan")
    cli.print(f"   Log Level: {config.log_level}", style="cyan")
    cli.print(f"   Environment: {config.environment}", style="cyan")
    cli.print(f"   Profile: {config.profile}", style="cyan")

    return config


# ============================================================================
# PATTERN 2: Environment-based config in YOUR deployment tool
# ============================================================================


def load_environment_config() -> dict[str, str]:
    """Load environment-specific config in YOUR tool."""
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

    settings = {
        "API URL": api_url,
        "Max Retries": str(max_retries),
        "Environment": environment,
    }

    # Display config
    settings_data = cast("FlextCliTypes.Data.CliDataDict", settings)
    table_result = cli.create_table(
        data=settings_data,
        headers=["Setting", "Value"],
        title=f"🌍 {environment.capitalize()} Configuration",
    )

    if table_result.is_success:
        cli.print_table(table_result.unwrap())

    return settings


# ============================================================================
# PATTERN 3: Custom config class for YOUR application
# ============================================================================


class MyAppConfig:
    """Custom configuration for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize custom configuration with environment variables."""
        super().__init__()
        # Inherit from flext-cli config
        self.base_config = cli.config

        # Add your custom settings
        self.app_name = os.getenv("APP_NAME", "my-cli-tool")
        self.api_key = os.getenv("API_KEY", "")
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))

    def validate(self) -> bool:
        """Validate YOUR app configuration."""
        if not self.api_key:
            cli.print("❌ API_KEY not configured", style="bold red")
            return False

        if self.max_workers < 1:
            cli.print("❌ MAX_WORKERS must be >= 1", style="bold red")
            return False

        cli.print("✅ Configuration valid", style="green")
        return True

    def display(self) -> None:
        """Display YOUR app configuration."""
        config_data: FlextCliTypes.Data.CliDataDict = cast(
            "FlextCliTypes.Data.CliDataDict",
            {
                "App Name": self.app_name,
                "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                "Max Workers": str(self.max_workers),
                "Timeout": f"{self.timeout}s",
                "Debug": str(self.base_config.debug),
                "Profile": self.base_config.profile,
            },
        )

        table_result = cli.create_table(
            data=config_data,
            headers=["Setting", "Value"],
            title="⚙️  Application Configuration",
        )

        if table_result.is_success:
            # cli.create_table returns Rich Table, use print_table
            cli.print_table(table_result.unwrap())


# ============================================================================
# PATTERN 4: Config file locations in YOUR tool
# ============================================================================


def show_config_locations() -> dict[str, str]:
    """Display config file locations for YOUR application."""
    config = cli.config

    # Get standard locations
    home_dir = Path.home()
    config_dir = home_dir / ".flext"
    token_file = Path(config.token_file)

    locations = {
        "Home Directory": str(home_dir),
        "Config Directory": str(config_dir),
        "Token File": str(token_file),
        "Token Exists": "Yes" if token_file.exists() else "No",
    }

    # Display as table
    locations_data = cast("FlextCliTypes.Data.CliDataDict", locations)
    table_result = cli.create_table(
        data=locations_data,
        headers=["Location", "Path"],
        title="📂 Configuration Locations",
    )

    if table_result.is_success:
        cli.print_table(table_result.unwrap())

    return locations


# ============================================================================
# PATTERN 5: Profile-based config in YOUR multi-env tool
# ============================================================================


def load_profile_config(profile_name: str = "default") -> FlextCliConfig | None:
    """Load profile-specific config in YOUR tool."""
    cli.print(f"📋 Loading profile: {profile_name}", style="bold cyan")

    # You can create different FlextCliConfig instances for different profiles
    profile_config = FlextCliConfig(
        profile=profile_name,
        debug=profile_name == "development",
        output_format="json" if profile_name == "production" else "table",
    )

    # Validate profile config
    validate_result = profile_config.validate_business_rules()

    if validate_result.is_failure:
        cli.print(
            f"❌ Profile validation failed: {validate_result.error}", style="bold red"
        )
        return None

    cli.print(f"✅ Profile '{profile_name}' loaded successfully", style="green")

    # Display profile settings
    profile_data: FlextCliTypes.Data.CliDataDict = cast(
        "FlextCliTypes.Data.CliDataDict",
        {
            "Profile": profile_config.profile,
            "Debug": str(profile_config.debug),
            "Output": profile_config.output_format,
            "Environment": profile_config.environment,
        },
    )

    table_result = cli.create_table(
        data=profile_data,
        headers=["Setting", "Value"],
        title=f"🎯 Profile: {profile_name}",
    )

    if table_result.is_success:
        cli.print_table(table_result.unwrap())

    return profile_config


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

    # Display current values
    cli.print("\n📊 Current Environment Variables:", style="yellow")
    for key, value in env_vars.items():
        cli.print(f"   {key}={value}", style="cyan")

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
    validate_result = config.validate_business_rules()

    if validate_result.is_failure:
        cli.print(
            f"   ❌ Base config invalid: {validate_result.error}", style="bold red"
        )
        return False

    cli.print("   ✅ Base config valid", style="green")

    # Step 2: Validate custom settings
    cli.print("\n2. Validating custom settings...", style="cyan")
    app_config = MyAppConfig()

    if not app_config.validate():
        cli.print("   ❌ Custom config invalid", style="bold red")
        return False

    cli.print("   ✅ Custom config valid", style="green")

    # Step 3: Display complete config
    cli.print("\n3. Configuration summary:", style="cyan")
    app_config.display()

    cli.print("\n✅ All configuration validated successfully!", style="bold green")
    return True


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
    get_cli_settings()

    # Example 2: Environment-based config
    cli.print("\n2. Environment Config (deployment settings):", style="bold cyan")
    load_environment_config()

    # Example 3: Custom config class
    cli.print("\n3. Custom Config Class (app-specific):", style="bold cyan")
    app_config = MyAppConfig()
    app_config.validate()
    app_config.display()

    # Example 4: Config locations
    cli.print("\n4. Config Locations (file paths):", style="bold cyan")
    show_config_locations()

    # Example 5: Profile-based config
    cli.print("\n5. Profile-Based Config (multi-environment):", style="bold cyan")
    load_profile_config("production")

    # Example 6: Environment variables
    cli.print("\n6. Environment Variables (configuration guide):", style="bold cyan")
    show_environment_variables()

    # Example 7: Config validation
    cli.print("\n7. Config Validation (startup check):", style="bold cyan")
    validate_app_config()

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Configuration Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Access config: Use cli.config for built-in settings", style="white")
    cli.print("  • Custom config: Extend FlextCliConfig for your app", style="white")
    cli.print("  • Validation: Use config.validate_business_rules()", style="white")
    cli.print("  • Environment: Use FLEXT_* env vars for configuration", style="white")


if __name__ == "__main__":
    main()
