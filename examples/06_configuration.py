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
from pathlib import Path
from typing import cast

from example_utils import display_config_table

from flext_cli import FlextCli, FlextCliConfig, r, t, u

cli = FlextCli()


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
    cli.print(f"   Log Level: {config.cli_log_level}", style="cyan")
    cli.print(f"   Environment: {config.environment}", style="cyan")
    cli.print(f"   Profile: {config.profile}", style="cyan")

    return config


# ============================================================================
# PATTERN 2: Environment-based config in YOUR deployment tool
# ============================================================================


def load_environment_config() -> dict[str, str | int]:
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

    settings: dict[str, str | int] = {
        "API URL": api_url,
        "Max Retries": max_retries,
        "Environment": environment,
    }

    # Display config - convert to CliDataDict using u directly
    # Use u.transform for JSON conversion
    transform_result = u.transform(
        cast("dict[str, t.GeneralValueType]", settings),
        to_json=True,
    )
    settings_data = (
        transform_result.value
        if transform_result.is_success
        else cast("dict[str, t.GeneralValueType]", settings)
    )
    display_config_table(
        cli=cli,
        config_data=settings_data,
        title=f"🌍 {environment.capitalize()} Configuration",
    )

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
        config_data: t.Cli.Data.CliDataDict = {
            "App Name": self.app_name,
            "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
            "Max Workers": str(self.max_workers),
            "Timeout": f"{self.timeout}s",
            "Debug": str(self.base_config.debug),
            "Profile": self.base_config.profile,
        }

        table_result = cli.create_table(
            data=config_data,
            headers=["Setting", "Value"],
            title="⚙️  Application Configuration",
        )

        if table_result.is_success:
            # cli.create_table returns Rich Table, use print_table
            cli.print_table(table_result.value)


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

    # Display as table - convert to CliDataDict using u directly
    # Use u.transform for JSON conversion
    transform_result = u.transform(
        cast("dict[str, t.GeneralValueType]", locations),
        to_json=True,
    )
    locations_data = (
        transform_result.value
        if transform_result.is_success
        else cast("dict[str, t.GeneralValueType]", locations)
    )
    table_result = cli.create_table(
        data=locations_data,
        headers=["Location", "Path"],
        title="📂 Configuration Locations",
    )

    if table_result.is_success:
        cli.print_table(table_result.value)

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

    # Validate profile config (Pydantic validation happens automatically on init)
    # validate_configuration is a model validator, not a callable method
    validate_result = profile_config.validate_output_format_result(
        profile_config.output_format,
    )
    if validate_result.is_failure:
        cli.print(
            f"❌ Profile validation failed: {validate_result.error}",
            style="bold red",
        )
        return None

    cli.print(f"✅ Profile '{profile_name}' loaded successfully", style="green")

    # Display profile settings
    profile_data: t.Cli.Data.CliDataDict = {
        "Profile": profile_config.profile,
        "Debug": str(profile_config.debug),
        "Output": profile_config.output_format,
        "Environment": profile_config.environment,
    }

    display_config_table(
        cli=cli,
        config_data=profile_data,
        title=f"🎯 Profile: {profile_name}",
    )

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

    # Display current values using u.process
    cli.print("\n📊 Current Environment Variables:", style="yellow")

    def print_env(k: str, v: str) -> None:
        """Print single environment variable."""
        cli.print(f"   {k}={v}", style="cyan")

    u.process(env_vars, processor=print_env, on_error="skip")

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
# PATTERN 6: Advanced Config with Environment Variables and Validation
# ============================================================================


class AppConfig:
    """Advanced application configuration with env var integration."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables and defaults."""
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://localhost:5432/myapp",
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.api_key = os.getenv("API_KEY", "")
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.temp_dir = Path(
            os.getenv("TEMP_DIR", str(Path.home() / ".cache" / "myapp")),
        )

    def validate(self) -> r[dict[str, object]]:
        """Validate configuration with comprehensive checks."""
        errors = []

        # Validate database URL
        if not self.database_url.startswith(("postgresql://", "mysql://")):
            errors.append("DATABASE_URL must be a valid database URL")

        # Validate Redis URL
        if not self.redis_url.startswith("redis://"):
            errors.append("REDIS_URL must be a valid Redis URL")

        # Validate API key
        if not self.api_key and os.getenv("ENVIRONMENT") == "production":
            errors.append("API_KEY is required in production")

        # Validate workers
        if not 1 <= self.max_workers <= 100:
            errors.append("MAX_WORKERS must be between 1 and 100")

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")

        # Validate temp directory
        if not self.temp_dir.exists():
            try:
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create TEMP_DIR: {e}")
        elif not self.temp_dir.is_dir():
            errors.append("TEMP_DIR must be a directory")

        if errors:
            return r[dict[str, object]].fail("; ".join(errors))

        # Return validated config as dict
        return r[dict[str, object]].ok({
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "api_key": "***" if self.api_key else "",
            "max_workers": self.max_workers,
            "enable_metrics": self.enable_metrics,
            "log_level": self.log_level,
            "temp_dir": str(self.temp_dir),
        })


def load_application_config() -> r[dict[str, object]]:
    """Load and validate application configuration from environment."""
    cli.print("\n⚙️  Loading Application Configuration:", style="bold cyan")

    # Railway Pattern for config loading
    config_obj = AppConfig()
    cli.print("✅ Config object created", style="green")

    # Step 2: Validate configuration
    validate_result = config_obj.validate()
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

    result: r[dict[str, object]] = r[dict[str, object]].ok(final_data)

    if result.is_failure:
        cli.print(f"❌ Configuration failed: {result.error}", style="bold red")
        return result

    cli.print("🎉 Application configuration loaded successfully!", style="bold green")
    return result


def apply_environment_overrides(config: dict[str, object]) -> dict[str, object]:
    """Apply environment-specific configuration overrides."""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        # Production overrides
        max_workers_value = config.get("max_workers", 4)
        # Type narrowing: ensure int before conversion
        if isinstance(max_workers_value, int):
            config["max_workers"] = min(max_workers_value, 20)  # Limit workers in prod
        elif isinstance(max_workers_value, str):
            config["max_workers"] = min(int(max_workers_value), 20)
        else:
            config["max_workers"] = 4
        config["enable_metrics"] = True  # Always enable metrics in prod
    elif env == "testing":
        # Testing overrides
        config["max_workers"] = 1  # Single worker for tests
        config["enable_metrics"] = False  # Disable metrics during tests

    return config


def initialize_services(config: dict[str, object]) -> dict[str, object]:
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

    # Example 8: Advanced config with env vars
    cli.print("\n8. Advanced Config with Environment Variables:", style="bold cyan")
    config_result = load_application_config()

    if config_result.is_success:
        final_config = config_result.value
        # Display final config - convert to CliDataDict
        # Use u.transform for JSON conversion
        transform_result = u.transform(
            cast("dict[str, t.GeneralValueType]", final_config),
            to_json=True,
        )
        final_config_data = (
            transform_result.value
            if transform_result.is_success
            else cast("dict[str, t.GeneralValueType]", final_config)
        )
        display_config_table(
            cli=cli,
            config_data=final_config_data,
            title="Final Application Configuration",
        )

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
