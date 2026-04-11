"""Configuration - Using flext-cli for Config Management in YOUR CLI.

WHEN TO USE THIS:
- Building CLI tools with configurable settings
- Need to manage environment-specific configs
- Want to load settings from environment variables
- Building tools with user preferences
- Need configuration validation

FLEXT-CLI PROVIDES:
- cli - Configuration management class
- cli.settings - Direct access to current config settings
- Environment variable loading (FLEXT_*)
- Built-in validation with r
- Profile-based configuration

HOW TO USE IN YOUR CLI:
Access config settings through cli.settings and customize for YOUR application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import time
from collections.abc import Mapping
from pathlib import Path

from examples import c, m, t, u
from flext_cli import FlextCliSettings, cli
from flext_core import r


def show_cli_settings() -> FlextCliSettings:
    """Access flext-cli config settings in YOUR application."""
    cli.print("📋 Current Configuration:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(f"   Debug Mode: {cli.settings.debug}", style=c.Cli.MessageStyles.CYAN)
    cli.print(
        f"   Log Level: {cli.settings.cli_log_level}", style=c.Cli.MessageStyles.CYAN
    )
    cli.print(
        f"   Output Format: {cli.settings.output_format}",
        style=c.Cli.MessageStyles.CYAN,
    )
    cli.print(f"   App Name: {cli.settings.app_name}", style=c.Cli.MessageStyles.CYAN)
    return cli.settings


def load_environment_config() -> m.Cli.DisplayData:
    """Load environment-specific config in YOUR tool. Returns DisplayData model."""
    cli_settings = cli.settings
    debug_mode = cli_settings.debug
    if debug_mode:
        cli.print(
            "🔧 Debug mode - using development settings",
            style=c.Cli.MessageStyles.BOLD_YELLOW,
        )
        api_url = "https://api.staging.example.com"
        max_retries = 3
    else:
        cli.print(
            "💻 Normal mode - using production settings",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        api_url = "http://localhost:8000"
        max_retries = 1
    settings = m.Cli.DisplayData(
        data={
            "API URL": api_url,
            "Max Retries": max_retries,
            "Debug": str(debug_mode),
        },
    )
    cli.print(
        f"🌍 {cli_settings.app_name} Configuration", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    u.display_config_table(config_data=settings)
    return settings


def show_config_locations() -> m.Cli.DisplayData:
    """Display config file locations for YOUR application. Returns DisplayData model."""
    home_dir = Path.home()
    config_dir = home_dir / ".flext"
    token_file_str = cli.settings.token_file or ""
    token_file_path = Path(token_file_str)
    locations = {
        "Home Directory": str(home_dir),
        "Config Directory": str(config_dir),
        "Token File": str(token_file_path),
        "Token Exists": "Yes" if token_file_path.exists() else "No",
    }
    display_payload = m.Cli.DisplayData(data=locations)
    u.display_config_table(
        config_data=display_payload,
        headers=["Location", "Path"],
    )
    return display_payload


def load_profile_config(profile_name: str = "default") -> r[FlextCliSettings]:
    """Load profile-specific config in YOUR tool. Returns r[FlextCliSettings]."""
    cli.print(
        f"📋 Loading profile: {profile_name}", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    profile_config = cli.settings.model_copy(
        update={
            "debug": profile_name == "development",
            "output_format": c.Cli.OutputFormats.JSON
            if profile_name == "production"
            else c.Cli.OutputFormats.TABLE,
        },
        deep=True,
    )
    validate_result = u.Cli.validate_format(profile_config.output_format)
    if validate_result.failure:
        cli.print(
            f"❌ Profile validation failed: {validate_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return r[FlextCliSettings].fail(
            validate_result.error or "Profile validation failed",
        )
    cli.print(
        f"✅ Profile '{profile_name}' loaded successfully",
        style=c.Cli.MessageStyles.GREEN,
    )
    profile_data = {
        "Profile": profile_name,
        "Debug": str(profile_config.debug),
        "Output": profile_config.output_format,
        "App Name": profile_config.app_name,
    }
    u.display_config_table(config_data=m.Cli.DisplayData(data=profile_data))
    return r[FlextCliSettings].ok(profile_config)


def show_environment_variables() -> None:
    """Display available environment variables for YOUR CLI."""
    cli.print("🌍 Environment Variables", style=c.Cli.MessageStyles.BOLD_CYAN)
    env_vars = {
        "FLEXT_DEBUG": os.getenv("FLEXT_DEBUG", "false"),
        "FLEXT_LOG_LEVEL": os.getenv("FLEXT_LOG_LEVEL", "INFO"),
        "FLEXT_ENVIRONMENT": os.getenv("FLEXT_ENVIRONMENT", "development"),
        "FLEXT_PROFILE": os.getenv("FLEXT_PROFILE", "default"),
        "FLEXT_OUTPUT_FORMAT": os.getenv(
            "FLEXT_OUTPUT_FORMAT", c.Cli.OutputFormats.TABLE
        ),
    }
    cli.print("\n📊 Current Environment Variables:", style=c.Cli.MessageStyles.YELLOW)

    def print_env(k: str, v: str) -> None:
        """Print single environment variable."""
        cli.print(f"   {k}={v}", style=c.Cli.MessageStyles.CYAN)

    _ = u.Cli.process_mapping(env_vars, processor=print_env)
    cli.print(
        "\n💡 How to set environment variables:", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    cli.print("   export FLEXT_DEBUG=true", style=c.Cli.MessageStyles.WHITE)
    cli.print("   export FLEXT_ENVIRONMENT=production", style=c.Cli.MessageStyles.WHITE)
    cli.print("   export FLEXT_LOG_LEVEL=DEBUG", style=c.Cli.MessageStyles.WHITE)


def validate_app_config() -> bool:
    """Validate configuration in YOUR application startup."""
    settings = cli.settings
    cli.print("🔍 Validating Configuration...", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print("\n1. Validating base configuration...", style=c.Cli.MessageStyles.CYAN)
    validate_result = u.Cli.validate_format(settings.output_format)
    if validate_result.failure:
        cli.print(
            f"   ❌ Base config invalid: {validate_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False
    cli.print("   ✅ Base config valid", style=c.Cli.MessageStyles.GREEN)
    cli.print("\n2. Validating custom settings...", style=c.Cli.MessageStyles.CYAN)
    app_config = m.Examples.MyAppConfig()
    if not app_config.validate_config(cli):
        cli.print("   ❌ Custom config invalid", style=c.Cli.MessageStyles.BOLD_RED)
        return False
    cli.print("   ✅ Custom config valid", style=c.Cli.MessageStyles.GREEN)
    cli.print("\n3. Configuration summary:", style=c.Cli.MessageStyles.CYAN)
    app_config.display(cli)
    cli.print(
        "\n✅ All configuration validated successfully!",
        style=c.Cli.MessageStyles.BOLD_GREEN,
    )
    return True


def load_application_config() -> r[Mapping[str, t.Cli.JsonValue]]:
    """Load and validate application configuration from environment."""
    cli.print(
        "\n⚙️  Loading Application Configuration:", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    config_obj = m.Examples.AppConfigAdvanced()
    cli.print("✅ Configuration model created", style=c.Cli.MessageStyles.GREEN)
    validate_result = config_obj.validate_to_mapping()
    if validate_result.failure:
        return validate_result
    cli.print("✅ Configuration validated", style=c.Cli.MessageStyles.GREEN)
    config_data = validate_result.value
    overridden_data = apply_environment_overrides(config_data)
    cli.print("✅ Environment overrides applied", style=c.Cli.MessageStyles.GREEN)
    final_data = initialize_services(overridden_data)
    cli.print("✅ Services initialized", style=c.Cli.MessageStyles.GREEN)
    result = r[Mapping[str, t.Cli.JsonValue]].ok(final_data)
    if result.failure:
        cli.print(
            f"❌ Configuration failed: {result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return result
    cli.print(
        "🎉 Application configuration loaded successfully!",
        style=c.Cli.MessageStyles.BOLD_GREEN,
    )
    return result


def apply_environment_overrides(
    config: Mapping[str, t.Cli.JsonValue],
) -> Mapping[str, t.Cli.JsonValue]:
    """Apply environment-specific configuration overrides."""
    result: dict[str, t.Cli.JsonValue] = {
        str(key): value for key, value in config.items()
    }
    env = os.getenv("ENVIRONMENT", "development")
    if env == c.EXAMPLE_ENV_VALUE_PRODUCTION:
        max_workers_value = result.get("max_workers", 4)
        if isinstance(max_workers_value, bool) or not isinstance(
            max_workers_value,
            int,
        ):
            msg = c.EXAMPLE_ERR_MAX_WORKERS_MUST_BE_INTEGER
            raise ValueError(msg)
        result["max_workers"] = min(max_workers_value, 20)
        result["enable_metrics"] = True
    elif env == "testing":
        result["max_workers"] = 1
        result["enable_metrics"] = False
    return result


def initialize_services(
    config: Mapping[str, t.Cli.JsonValue],
) -> Mapping[str, t.Cli.JsonValue]:
    """Initialize services based on configuration."""
    time.sleep(0.05)
    result: dict[str, t.Cli.JsonValue] = {
        str(key): value for key, value in config.items()
    }
    result["services_initialized"] = True
    result["initialized_at"] = "2025-11-23T10:00:00Z"
    return result


def main() -> None:
    """Examples of using configuration in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Configuration Management Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n1. Built-in Configuration (access settings):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    _ = show_cli_settings()
    cli.print(
        "\n2. Environment Config (deployment settings):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    _ = load_environment_config()
    cli.print(
        "\n3. Custom Config Class (app-specific):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    app_config = m.Examples.MyAppConfig()
    _ = app_config.validate_config(cli)
    app_config.display(cli)
    cli.print(
        "\n4. Config Locations (file paths):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = show_config_locations()
    cli.print(
        "\n5. Profile-Based Config (multi-environment):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    _ = load_profile_config("production")
    cli.print(
        "\n6. Environment Variables (configuration guide):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    show_environment_variables()
    cli.print(
        "\n7. Config Validation (startup check):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    _ = validate_app_config()
    cli.print(
        "\n8. Advanced Config with Environment Variables:",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    config_result = load_application_config()
    if config_result.success:
        final_config = config_result.value
        final_config_data = {k: str(v) for k, v in final_config.items()}
        cli.print(
            "Final Application Configuration", style=c.Cli.MessageStyles.BOLD_CYAN
        )
        u.display_config_table(
            config_data=m.Cli.DisplayData(data=final_config_data),
        )
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Configuration Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Access config: Use cli.settings for built-in settings",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Custom config: Extend cli for your app", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • Validation: Use config.validate_business_rules()",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Environment: Use FLEXT_* env vars for configuration",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()
