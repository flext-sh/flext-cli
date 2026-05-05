"""Settings - Using flext-cli for Settings Management in YOUR CLI.

WHEN TO USE THIS:
- Building CLI tools with configurable settings
- Need to manage environment-specific configs
- Want to load settings from environment variables
- Building tools with user preferences
- Need settings validation

FLEXT-CLI PROVIDES:
- cli - Settings management class
- cli.settings - Direct access to current settings
- Environment variable loading (FLEXT_*)
- Built-in validation with r
- Profile-based settings

HOW TO USE IN YOUR CLI:
Access settings through cli.settings and customize for YOUR application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from examples import c, m, t, u
from flext_cli import cli, p
from flext_core import r


class Ex06Settings:
    """Public settings example for flext-cli consumers."""

    @staticmethod
    def show_cli_settings() -> p.Cli.Settings:
        """Access flext-cli settings in YOUR application."""
        cli.print("📋 Current Settings:", style=c.Cli.MessageStyles.BOLD_CYAN)
        cli.print(
            f"   Debug Mode: {cli.settings.debug}", style=c.Cli.MessageStyles.CYAN
        )
        cli.print(
            f"   Log Level: {cli.settings.cli_log_level}",
            style=c.Cli.MessageStyles.CYAN,
        )
        cli.print(
            f"   Output Format: {cli.settings.output_format}",
            style=c.Cli.MessageStyles.CYAN,
        )
        cli.print(
            f"   App Name: {cli.settings.app_name}",
            style=c.Cli.MessageStyles.CYAN,
        )
        return cli.settings

    @staticmethod
    def show_settings_locations() -> m.Cli.DisplayData:
        """Display settings file locations for YOUR application."""
        home_dir = Path.home()
        token_file_path = u.Cli.auth_token_file_path(cli.settings.token_file)
        display_payload = u.to_json_dict({
            "Home Directory": str(home_dir),
            "Settings Directory": str(home_dir / c.Cli.PATH_FLEXT_DIR_NAME),
            "Token File": str(token_file_path),
            "Token Exists": "Yes" if token_file_path.exists() else "No",
        })
        u.display_config_table(
            config_data=display_payload,
            headers=("Location", "Path"),
        )
        return display_payload

    @staticmethod
    def load_profile_settings(
        profile_name: c.DeploymentEnvironment = c.EXAMPLE_DEFAULT_ENVIRONMENT,
    ) -> p.Result[p.Cli.Settings]:
        """Load profile-specific settings in YOUR tool."""
        cli.print(
            f"📋 Loading profile: {profile_name.value}",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        match profile_name:
            case c.DeploymentEnvironment.PRODUCTION:
                debug = False
                output_format = c.Cli.OutputFormats.JSON
            case c.DeploymentEnvironment.TESTING:
                debug = True
                output_format = c.Cli.OutputFormats.TABLE
            case _:
                debug = profile_name == c.DeploymentEnvironment.DEVELOPMENT
                output_format = c.Cli.OutputFormats.TABLE
        profile_config = cli.settings.clone(
            debug=debug,
            output_format=output_format,
        )
        cli.print(
            f"✅ Profile '{profile_name.value}' loaded successfully",
            style=c.Cli.MessageStyles.GREEN,
        )
        u.display_config_table(
            config_data=u.to_json_dict({
                "Profile": profile_name.value,
                "Debug": str(profile_config.debug),
                "Output": profile_config.output_format,
                "App Name": profile_config.app_name,
            })
        )
        return r[p.Cli.Settings].ok(profile_config)

    @classmethod
    def load_application_settings(cls) -> p.Result[t.MappingKV[str, t.JsonValue]]:
        """Load, validate, and derive application settings from the canonical model."""
        cli.print(
            "\n⚙️  Loading Application Settings:",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        settings_obj = m.Examples.AppSettingsAdvanced()
        cli.print("✅ Settings model created", style=c.Cli.MessageStyles.GREEN)
        validate_result = settings_obj.validate_to_mapping()
        if validate_result.failure:
            return r[t.MappingKV[str, t.JsonValue]].fail(
                validate_result.error or c.EXAMPLE_ERR_FAILED_LOAD_CONFIG,
            )
        cli.print("✅ Settings validated", style=c.Cli.MessageStyles.GREEN)
        try:
            overridden_data = cls.apply_environment_overrides(
                validate_result.value,
                settings_obj.environment,
            )
        except (TypeError, ValueError) as exc:
            return r[t.MappingKV[str, t.JsonValue]].fail(str(exc))
        cli.print("✅ Environment overrides applied", style=c.Cli.MessageStyles.GREEN)
        final_data = cls.initialize_services(overridden_data)
        cli.print("✅ Services initialized", style=c.Cli.MessageStyles.GREEN)
        cli.print(
            "🎉 Application settings loaded successfully!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )
        return r[t.MappingKV[str, t.JsonValue]].ok(final_data)

    @staticmethod
    def apply_environment_overrides(
        settings: t.MappingKV[str, t.JsonValue],
        environment: c.DeploymentEnvironment,
    ) -> t.MappingKV[str, t.JsonValue]:
        """Apply environment-specific settings overrides."""
        result = dict(settings)
        match environment:
            case c.DeploymentEnvironment.PRODUCTION:
                max_workers_value = result.get(
                    "max_workers",
                    c.EXAMPLE_DEFAULT_MAX_WORKERS,
                )
                if isinstance(max_workers_value, bool) or not isinstance(
                    max_workers_value,
                    int,
                ):
                    raise TypeError(c.EXAMPLE_ERR_MAX_WORKERS_MUST_BE_INTEGER)
                result["max_workers"] = min(
                    max_workers_value,
                    c.EXAMPLE_PRODUCTION_MAX_WORKERS_CAP,
                )
                result["enable_metrics"] = True
            case c.DeploymentEnvironment.TESTING:
                result["max_workers"] = c.EXAMPLE_TESTING_MAX_WORKERS
                result["enable_metrics"] = False
            case _:
                pass
        return result

    @staticmethod
    def initialize_services(
        settings: t.MappingKV[str, t.JsonValue],
    ) -> t.MappingKV[str, t.JsonValue]:
        """Initialize services based on validated settings."""
        result = dict(settings)
        result["services_initialized"] = True
        result["initialized_at"] = c.EXAMPLE_DEFAULT_INITIALIZED_AT
        return result
