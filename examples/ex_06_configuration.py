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

from examples import m, t, u
from flext_cli import FlextCliSettings, cli
from flext_core import r


def get_cli_settings() -> FlextCliSettings:
    """Access flext-cli config settings in YOUR application."""
    cli.print("📋 Current Configuration:", style="bold cyan")
    cli.print(f"   Debug Mode: {cli.settings.debug}", style="cyan")
    cli.print(f"   Log Level: {cli.settings.cli_log_level}", style="cyan")
    cli.print(f"   Output Format: {cli.settings.output_format}", style="cyan")
    cli.print(f"   App Name: {cli.settings.app_name}", style="cyan")
    return cli.settings


def load_environment_config() -> m.Cli.DisplayData:
    """Load environment-specific config in YOUR tool. Returns DisplayData model."""
    cli_settings = cli.settings
    debug_mode = cli_settings.debug
    if debug_mode:
        cli.print("🔧 Debug mode - using development settings", style="bold yellow")
        api_url = "https://api.staging.example.com"
        max_retries = 3
    else:
        cli.print("💻 Normal mode - using production settings", style="bold cyan")
        api_url = "http://localhost:8000"
        max_retries = 1
    settings = m.Cli.DisplayData(
        data={
            "API URL": api_url,
            "Max Retries": max_retries,
            "Debug": str(debug_mode),
        },
    )
    cli.print(f"🌍 {cli_settings.app_name} Configuration", style="bold cyan")
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
    cli.print(f"📋 Loading profile: {profile_name}", style="bold cyan")
    profile_config = cli.settings.model_copy(
        update={
            "debug": profile_name == "development",
            "output_format": "json" if profile_name == "production" else "table",
        },
        deep=True,
    )
    validate_result = u.Cli.CliValidation.v_format(profile_config.output_format)
    if validate_result.is_failure:
        cli.print(
            f"❌ Profile validation failed: {validate_result.error}",
            style="bold red",
        )
        return r[FlextCliSettings].fail(
            validate_result.error or "Profile validation failed",
        )
    cli.print(f"✅ Profile '{profile_name}' loaded successfully", style="green")
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
    cli.print("🌍 Environment Variables", style="bold cyan")
    env_vars = {
        "FLEXT_DEBUG": os.getenv("FLEXT_DEBUG", "false"),
        "FLEXT_LOG_LEVEL": os.getenv("FLEXT_LOG_LEVEL", "INFO"),
        "FLEXT_ENVIRONMENT": os.getenv("FLEXT_ENVIRONMENT", "development"),
        "FLEXT_PROFILE": os.getenv("FLEXT_PROFILE", "default"),
        "FLEXT_OUTPUT_FORMAT": os.getenv("FLEXT_OUTPUT_FORMAT", "table"),
    }
    cli.print("\n📊 Current Environment Variables:", style="yellow")

    def print_env(k: str, v: str) -> None:
        """Print single environment variable."""
        cli.print(f"   {k}={v}", style="cyan")

    _ = u.Cli.process_mapping(env_vars, processor=print_env)
    cli.print("\n💡 How to set environment variables:", style="bold cyan")
    cli.print("   export FLEXT_DEBUG=true", style="white")
    cli.print("   export FLEXT_ENVIRONMENT=production", style="white")
    cli.print("   export FLEXT_LOG_LEVEL=DEBUG", style="white")


def validate_app_config() -> bool:
    """Validate configuration in YOUR application startup."""
    settings = cli.settings
    cli.print("🔍 Validating Configuration...", style="bold cyan")
    cli.print("\n1. Validating base configuration...", style="cyan")
    validate_result = u.Cli.CliValidation.v_format(settings.output_format)
    if validate_result.is_failure:
        cli.print(
            f"   ❌ Base config invalid: {validate_result.error}",
            style="bold red",
        )
        return False
    cli.print("   ✅ Base config valid", style="green")
    cli.print("\n2. Validating custom settings...", style="cyan")
    app_config = m.MyAppConfig()
    if not app_config.validate_config(cli):
        cli.print("   ❌ Custom config invalid", style="bold red")
        return False
    cli.print("   ✅ Custom config valid", style="green")
    cli.print("\n3. Configuration summary:", style="cyan")
    app_config.display(cli)
    cli.print("\n✅ All configuration validated successfully!", style="bold green")
    return True


def load_application_config() -> r[Mapping[str, t.Cli.JsonValue]]:
    """Load and validate application configuration from environment."""
    cli.print("\n⚙️  Loading Application Configuration:", style="bold cyan")
    config_obj = m.AppConfigAdvanced()
    cli.print("✅ Config t.NormalizedValue created", style="green")
    validate_result = config_obj.validate_to_mapping()
    if validate_result.is_failure:
        return validate_result
    cli.print("✅ Configuration validated", style="green")
    config_data = validate_result.value
    overridden_data = apply_environment_overrides(config_data)
    cli.print("✅ Environment overrides applied", style="green")
    final_data = initialize_services(overridden_data)
    cli.print("✅ Services initialized", style="green")
    result: r[Mapping[str, t.Cli.JsonValue]] = r[Mapping[str, t.Cli.JsonValue]].ok(
        final_data,
    )
    if result.is_failure:
        cli.print(f"❌ Configuration failed: {result.error}", style="bold red")
        return result
    cli.print("🎉 Application configuration loaded successfully!", style="bold green")
    return result


def apply_environment_overrides(
    config: t.ContainerMapping,
) -> t.MutableContainerMapping:
    """Apply environment-specific configuration overrides."""
    result: t.MutableContainerMapping = dict(config) if isinstance(config, dict) else {}
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
    config: t.ContainerMapping,
) -> t.MutableContainerMapping:
    """Initialize services based on configuration."""
    time.sleep(0.05)
    result: t.MutableContainerMapping = dict(config) if isinstance(config, dict) else {}
    result["services_initialized"] = True
    result["initialized_at"] = "2025-11-23T10:00:00Z"
    return result


def main() -> None:
    """Examples of using configuration in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Configuration Management Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Built-in Configuration (access settings):", style="bold cyan")
    _ = get_cli_settings()
    cli.print("\n2. Environment Config (deployment settings):", style="bold cyan")
    _ = load_environment_config()
    cli.print("\n3. Custom Config Class (app-specific):", style="bold cyan")
    app_config = m.MyAppConfig()
    _ = app_config.validate_config(cli)
    app_config.display(cli)
    cli.print("\n4. Config Locations (file paths):", style="bold cyan")
    _ = show_config_locations()
    cli.print("\n5. Profile-Based Config (multi-environment):", style="bold cyan")
    _ = load_profile_config("production")
    cli.print("\n6. Environment Variables (configuration guide):", style="bold cyan")
    show_environment_variables()
    cli.print("\n7. Config Validation (startup check):", style="bold cyan")
    _ = validate_app_config()
    cli.print("\n8. Advanced Config with Environment Variables:", style="bold cyan")
    config_result = load_application_config()
    if config_result.is_success:
        final_config = config_result.value
        final_config_data = {k: str(v) for k, v in final_config.items()}
        cli.print("Final Application Configuration", style="bold cyan")
        u.display_config_table(
            config_data=m.Cli.DisplayData(data=final_config_data),
        )
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Configuration Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print(
        "  • Access config: Use cli.settings for built-in settings", style="white"
    )
    cli.print("  • Custom config: Extend cli for your app", style="white")
    cli.print("  • Validation: Use config.validate_business_rules()", style="white")
    cli.print("  • Environment: Use FLEXT_* env vars for configuration", style="white")


if __name__ == "__main__":
    main()
