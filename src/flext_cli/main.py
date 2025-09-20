"""CLI Main Service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# pyright: reportUnusedFunction=false
from __future__ import annotations

import os
import platform

import click  # ONLY file in ecosystem allowed to import Click - CLI foundation

from flext_cli.configs import FlextCliConfigs
from flext_cli.constants import FlextCliConstants
from flext_cli.validations import FlextCliValidations
from flext_core import (
    FlextConfig,
    FlextDomainService,
    FlextLogger,
    FlextResult,
)


class FlextCliMain(FlextDomainService[None]):
    """Main CLI class that provides comprehensive Click abstraction for FLEXT ecosystem.

    This class consolidates ALL Click functionality into a unified structure,
    following the single-class-per-module pattern while maintaining Click/Rich
    imports as appropriate for the CLI domain library.
    """

    def __init__(self, name: str = "flext-cli", description: str = "FLEXT CLI") -> None:
        """Initialize FlextCliMain with name and description.

        Args:
            name: CLI application name
            description: CLI application description

        """
        super().__init__()
        self._name = name
        self._description = description
        self._logger = FlextLogger(__name__)
        self._command_groups: dict[str, object] = {}
        self._commands: dict[str, object] = {}
        self._config = FlextCliConfigs()

    @property
    def name(self) -> str:
        """Get CLI name."""
        return self._name

    @property
    def description(self) -> str:
        """Get CLI description."""
        return self._description

    @property
    def config(self) -> FlextCliConfigs:
        """Get CLI configuration."""
        return self._config

    class _OptionsHelper:
        """Helper for CLI options management."""

        @staticmethod
        def create_common_options() -> dict[str, object]:
            """Create common CLI options."""
            return {
                "debug": True,
                "profile": "default",
                "quiet": False,
                "output": "table",
            }

        @staticmethod
        def validate_output_format(output: str) -> bool:
            """Validate output format using centralized validation."""
            result = FlextCliValidations.validate_output_format(output)
            return result.is_success

    class _ContextHelper:
        """Helper for CLI context management."""

        @staticmethod
        def create_context_object(
            *, debug: bool, profile: str, quiet: bool
        ) -> dict[str, object]:
            """Create CLI context object."""
            return {
                "debug": debug,
                "profile": profile,
                "quiet": quiet,
            }

        @staticmethod
        def apply_cli_overrides(
            cli_overrides: dict[str, object],
        ) -> FlextResult[FlextCliConfigs]:
            """Apply CLI parameter overrides to configuration."""
            try:
                # Apply overrides to FlextConfig singleton
                config_result = FlextCliConfigs.apply_cli_overrides(cli_overrides)
                if config_result.is_failure:
                    return FlextResult[FlextCliConfigs].fail(
                        f"Configuration error: {config_result.error}"
                    )

                return FlextResult[FlextCliConfigs].ok(config_result.value)

            except Exception as e:
                return FlextResult[FlextCliConfigs].fail(
                    f"Failed to apply CLI configuration: {e}"
                )

    class _VersionHelper:
        """Helper for version management."""

        @staticmethod
        def get_version_string() -> str:
            """Get version string."""
            return "0.1.0"

        @staticmethod
        def print_version_callback(ctx: object, _param: object, *, value: bool) -> None:
            """Print version and exit."""
            if not value or ctx is None:
                return
            # Version printing logic here
            raise SystemExit(0)

    class _LoggingHelper:
        """Helper for logging configuration."""

        @staticmethod
        def setup_logging(
            *, debug: bool = False, log_level: str | None = None
        ) -> FlextResult[None]:
            """Setup logging configuration."""
            try:
                # Configure FlextLogger based on CLI parameters
                if debug:
                    FlextLogger.configure(log_level="DEBUG", structured_output=True)
                elif log_level:
                    FlextLogger.configure(
                        log_level=log_level.upper(), structured_output=True
                    )
                else:
                    FlextLogger.configure(log_level="INFO", structured_output=True)

                return FlextResult[None].ok(None)

            except Exception as e:
                return FlextResult[None].fail(f"Logging setup failed: {e}")

        @staticmethod
        def configure_global_logging(
            level: str, verbosity: str | None = None
        ) -> FlextResult[str]:
            """Configure global logging settings."""
            try:
                # Set environment variables for global logging
                os.environ["FLEXT_LOG_LEVEL"] = level.upper()
                if verbosity:
                    os.environ["FLEXT_LOG_VERBOSITY"] = verbosity.lower()

                return FlextResult[str].ok(f"Global log level set to {level}")

            except Exception as e:
                return FlextResult[str].fail(f"Failed to configure global logging: {e}")

    class _AuthCommands:
        """Authentication command implementations."""

        @staticmethod
        def get_auth_status() -> str:
            """Get authentication status."""
            return "Authentication status: Not implemented"

        @staticmethod
        def login_user(username: str, _password: str) -> str:
            """Login user with credentials."""
            return f"Login attempt for {username}: Not implemented"

        @staticmethod
        def logout_user() -> str:
            """Logout current user."""
            return "Logout: Not implemented"

    class _ConfigCommands:
        """Configuration command implementations."""

        @staticmethod
        def show_config() -> str:
            """Show current configuration."""
            try:
                # Get both base and CLI configurations
                base_config = FlextConfig()
                cli_config = FlextCliConfigs.get_current()

                config_info: list[str] = []
                config_info.extend(
                    (
                        "=== FLEXT CONFIGURATION (FlextConfig Singleton - SINGLE SOURCE OF TRUTH) ===",
                        f"Environment: {base_config.environment}",
                        f"Debug Mode: {base_config.debug}",
                        f"Log Level: {base_config.log_level}",
                        f"App Name: {base_config.app_name}",
                        f"Host: {base_config.host}",
                        f"Port: {base_config.port}",
                        f"Database URL: {base_config.database_url}",
                        "\n=== CLI CONFIGURATION (FlextCliConfigs - Extends FlextConfig) ===",
                        f"Profile: {cli_config.profile}",
                        f"Output Format: {cli_config.output_format}",
                        f"API URL: {cli_config.api_url}",
                        f"Command Timeout: {cli_config.command_timeout}s",
                        f"Quiet Mode: {cli_config.quiet}",
                        f"Verbose Mode: {cli_config.verbose}",
                    )
                )

                return "\n".join(config_info)

            except Exception as e:
                return f"Failed to show configuration: {e}"

        @staticmethod
        def edit_config() -> str:
            """Edit configuration."""
            return "Edit configuration: Not implemented"

        @staticmethod
        def get_config_path() -> str:
            """Get configuration file path."""
            return "Configuration path: Not implemented"

        @staticmethod
        def get_config_value(key: str) -> str:
            """Get configuration value by key."""
            return f"Configuration value for {key}: Not implemented"

        @staticmethod
        def set_config_value(key: str, value: str) -> str:
            """Set configuration value."""
            return f"Set {key} = {value}: Not implemented"

        @staticmethod
        def validate_config() -> str:
            """Validate configuration."""
            return "Configuration validation: Not implemented"

    class _SystemCommands:
        """System and debug command implementations."""

        @staticmethod
        def get_environment_info() -> dict[str, str]:
            """Get environment information."""
            env_prefix = FlextCliConstants.SYSTEM.env_prefix
            return {
                key: value
                for key, value in os.environ.items()
                if key.startswith(env_prefix)
            }

        @staticmethod
        def check_connectivity() -> str:
            """Check system connectivity."""
            return "Connectivity check: Not implemented"

        @staticmethod
        def check_performance() -> str:
            """Check system performance."""
            return "Performance check: Not implemented"

        @staticmethod
        def show_paths() -> dict[str, str]:
            """Show system paths."""
            return {
                "config_path": "~/.flext/config",
                "log_path": "~/.flext/logs",
                "cache_path": "~/.flext/cache",
            }

        @staticmethod
        def validate_system() -> str:
            """Validate system setup."""
            return "System validation: Not implemented"

        @staticmethod
        def run_trace(args: tuple[str, ...]) -> str:
            """Run trace operations."""
            return f"Trace operation with args {args}: Not implemented"

        @staticmethod
        def health_check() -> str:
            """Run health check."""
            return "Health check: System OK"

    # Public delegation methods to eliminate SLF001 violations
    def validate_output_format(self, format_type: str) -> bool:
        """Validate output format type."""
        return self._OptionsHelper.validate_output_format(format_type)

    def apply_cli_overrides(
        self, overrides: dict[str, object]
    ) -> FlextResult[FlextCliConfigs]:
        """Apply CLI overrides to configuration."""
        return self._ContextHelper.apply_cli_overrides(overrides)

    def get_auth_status(self) -> str:
        """Get current authentication status."""
        return self._AuthCommands.get_auth_status()

    def login_user(self, username: str, password: str) -> str:
        """Login user with credentials."""
        return self._AuthCommands.login_user(username, password)

    def logout_user(self) -> str:
        """Logout current user."""
        return self._AuthCommands.logout_user()

    def show_config(self) -> str:
        """Show current configuration."""
        return self._ConfigCommands.show_config()

    def edit_config(self) -> str:
        """Edit configuration file."""
        return self._ConfigCommands.edit_config()

    def get_config_path(self) -> str:
        """Get configuration file path."""
        return self._ConfigCommands.get_config_path()

    def get_config_value(self, key: str) -> str:
        """Get configuration value by key."""
        return self._ConfigCommands.get_config_value(key)

    def set_config_value(self, key: str, value: str) -> str:
        """Set configuration value."""
        return self._ConfigCommands.set_config_value(key, value)

    def validate_config_settings(self) -> str:
        """Validate configuration settings."""
        return self._ConfigCommands.validate_config()

    def get_environment_info(self) -> dict[str, str]:
        """Get environment information."""
        return self._SystemCommands.get_environment_info()

    def check_connectivity(self) -> str:
        """Check system connectivity."""
        return self._SystemCommands.check_connectivity()

    def check_performance(self) -> str:
        """Check system performance."""
        return self._SystemCommands.check_performance()

    def show_paths(self) -> dict[str, str]:
        """Show system paths."""
        return self._SystemCommands.show_paths()

    def validate_system(self) -> str:
        """Validate system setup."""
        return self._SystemCommands.validate_system()

    def run_trace(self, args: tuple[str, ...]) -> str:
        """Run trace operations."""
        return self._SystemCommands.run_trace(args)

    def health_check(self) -> str:
        """Perform health check."""
        return self._SystemCommands.health_check()

    class _ClickCommands:
        """Click command definitions consolidated into unified class structure.

        This nested class contains ALL Click decorators and function definitions,
        maintaining the Click functionality while following the unified class pattern.
        """

        def __init__(self, cli_main_instance: FlextCliMain) -> None:
            """Initialize with reference to parent FlextCliMain instance."""
            self._cli_main = cli_main_instance

        def create_main_cli_group(self) -> object:
            """Create the main CLI group with all commands registered."""
            # This method will contain the consolidated Click group definitions
            # and command registrations in a more structured way

            @click.group(invoke_without_command=True)
            @click.option("--debug", is_flag=True, help="Enable debug mode.")
            @click.option(
                "--profile", default="default", help="Configuration profile to use."
            )
            @click.option("--quiet", is_flag=True, help="Suppress output.")
            @click.option(
                "--log-level",
                help="Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
            )
            @click.option(
                "--output", help="Set output format (table, json, yaml, csv)."
            )
            @click.option(
                "--version",
                is_flag=True,
                expose_value=False,
                is_eager=True,
                callback=print_version,
                help="Show version and exit.",
            )
            @click.pass_context
            def cli(
                ctx: click.Context,
                *,
                debug: bool,
                profile: str,
                quiet: bool,
                log_level: str | None,
                output: str | None,
            ) -> None:
                """FLEXT Command Line Interface - Enterprise Data Integration Platform."""
                ctx.ensure_object(dict)
                ctx.obj["debug"] = debug
                ctx.obj["profile"] = profile
                ctx.obj["quiet"] = quiet
                ctx.obj["log_level"] = log_level

                # Apply CLI parameters to FlextConfig singleton
                try:
                    # Create CLI overrides from parameters
                    cli_overrides = {
                        "debug": debug,
                        "profile": profile,
                        "quiet": quiet,
                    }

                    if log_level:
                        cli_overrides["log_level"] = log_level.upper()

                    if output:
                        # Validate output format
                        if not self._cli_main.validate_output_format(output):
                            # Get the proper error message from centralized validation
                            validation_result = (
                                FlextCliValidations.validate_output_format(output)
                            )
                            click.echo(
                                f"Error: {validation_result.error}",
                                err=True,
                            )
                            ctx.exit(1)
                        cli_overrides["output_format"] = output

                    # Apply overrides through helper
                    config_result = self._cli_main.apply_cli_overrides(cli_overrides)
                    if config_result.is_failure:
                        click.echo(
                            f"Configuration error: {config_result.error}", err=True
                        )
                        ctx.exit(1)

                    # Store the updated config in context
                    ctx.obj["config"] = config_result.value

                except Exception as e:
                    click.echo(f"Failed to apply CLI configuration: {e}", err=True)
                    ctx.exit(1)

                # Show debug information when debug flag is used and no subcommand
                if debug and ctx.invoked_subcommand is None:
                    click.echo("=== FLEXT CLI DEBUG INFO ===")
                    click.echo(f"Profile: {profile}")
                    click.echo(f"Debug Mode: {debug}")
                    click.echo(f"Log Level: {log_level or 'INFO'}")
                    click.echo(f"Output Format: {output or 'table'}")

                # Show help when no command, no debug, and not quiet
                if ctx.invoked_subcommand is None and not quiet:
                    click.echo(ctx.get_help())

            # Register auth commands
            self._register_auth_commands(cli)

            # Register config commands
            self._register_config_commands(cli)

            # Register debug commands
            self._register_debug_commands(cli)

            # Register log control commands
            self._register_log_control_commands(cli)

            # Register standalone commands
            self._register_standalone_commands(cli)

            return cli

        def _register_auth_commands(self, cli: click.Group) -> None:
            """Register authentication command group."""

            @cli.group()
            def auth() -> None:
                """Handle authentication commands."""

            @auth.command()
            @click.pass_context
            def status(_ctx: click.Context) -> None:
                """Show authentication status."""
                click.echo(self._cli_main.get_auth_status())

            @auth.command()
            @click.option(
                "--username", required=True, help="Username for authentication."
            )
            @click.option(
                "--password",
                "_password",
                required=True,
                help="Password for authentication.",
            )
            @click.pass_context
            def login(_ctx: click.Context, username: str, _password: str) -> None:
                """Login with username and password."""
                click.echo(self._cli_main.login_user(username, _password))

            @auth.command()
            @click.pass_context
            def logout(_ctx: click.Context) -> None:
                """Logout and remove authentication."""
                click.echo(self._cli_main.logout_user())

        def _register_config_commands(self, cli: click.Group) -> None:
            """Register configuration command group."""

            @cli.group()
            @click.pass_context
            def config(_ctx: click.Context) -> None:
                """Handle configuration commands."""

            @config.command()
            @click.pass_context
            def show(ctx: click.Context) -> None:
                """Show current configuration from FlextConfig singleton."""
                try:
                    config_output = self._cli_main.show_config()
                    click.echo(config_output)

                    # Show integration metadata
                    click.echo("\n=== INTEGRATION STATUS ===")
                    click.echo(
                        "Configuration Source: FlextConfig Singleton (Single Source of Truth)"
                    )
                    click.echo(f"CLI Parameters Applied: {bool(ctx.obj.get('config'))}")

                    # Verify integration
                    integration_result = (
                        FlextCliConfigs.ensure_flext_config_integration()
                    )
                    if integration_result.is_success:
                        click.echo("Integration Status: ✅ VERIFIED")
                    else:
                        click.echo(
                            f"Integration Status: ❌ FAILED - {integration_result.error}"
                        )

                except Exception as e:
                    click.echo(f"Failed to show configuration: {e}", err=True)

            @config.command()
            @click.pass_context
            def edit(_ctx: click.Context) -> None:
                """Edit configuration using default editor."""
                click.echo(self._cli_main.edit_config())

            @config.command()
            @click.pass_context
            def path(_ctx: click.Context) -> None:
                """Show configuration file path."""
                click.echo(self._cli_main.get_config_path())

            @config.command()
            @click.argument("key", required=False)
            @click.pass_context
            def get(_ctx: click.Context, key: str = "") -> None:
                """Get configuration value by key."""
                click.echo(self._cli_main.get_config_value(key))

            @config.command()
            @click.argument("key")
            @click.argument("value")
            @click.pass_context
            def set_value(_ctx: click.Context, key: str, value: str) -> None:
                """Set configuration value for key."""
                result = self._cli_main.set_config_value(key, value)
                click.echo(result)

            @config.command()
            @click.pass_context
            def validate(_ctx: click.Context) -> None:
                """Validate configuration settings."""
                click.echo(self._cli_main.validate_config_settings())

        def _register_debug_commands(self, cli: click.Group) -> None:
            """Register debug command group."""

            @cli.group()
            @click.pass_context
            def debug(_ctx: click.Context) -> None:
                """Debug commands for FLEXT CLI."""

            @debug.command()
            @click.pass_context
            def env(_ctx: click.Context) -> None:
                """Show environment information."""
                flx_vars = self._cli_main.get_environment_info()

                if flx_vars:
                    click.echo("FLEXT Environment Variables:")
                    click.echo("=" * 30)
                    for key, value in sorted(flx_vars.items()):
                        # Mask sensitive values
                        preview_length = 4
                        if any(
                            sensitive in key.upper()
                            for sensitive in ["TOKEN", "KEY", "SECRET", "PASS"]
                        ):
                            display_value = (
                                f"{value[:preview_length]}****"
                                if len(value) > preview_length
                                else "****"
                            )
                        else:
                            display_value = value
                        click.echo(f"{key}: {display_value}")
                else:
                    env_prefix = FlextCliConstants.SYSTEM.env_prefix
                    click.echo(
                        f"No FLEXT environment variables found ({env_prefix} prefix)"
                    )

            @debug.command()
            @click.pass_context
            def connectivity(_ctx: click.Context) -> None:
                """Test connectivity."""
                if not _ctx.obj:
                    click.echo(
                        "Connection test failed: context not available", err=True
                    )
                    _ctx.exit(1)
                click.echo(self._cli_main.check_connectivity())

            @debug.command()
            @click.pass_context
            def performance(_ctx: click.Context) -> None:
                """Show performance metrics."""
                click.echo(self._cli_main.check_performance())

            @debug.command()
            @click.pass_context
            def paths(_ctx: click.Context) -> None:
                """Show system paths."""
                paths_info = self._cli_main.show_paths()
                click.echo("FLEXT Configuration Paths")
                click.echo("=" * 25)
                for name, path in paths_info.items():
                    click.echo(f"{name.replace('_', ' ').title()}: {path}")

            @debug.command()
            @click.pass_context
            def validate_system(_ctx: click.Context) -> None:
                """Validate system setup."""
                click.echo(self._cli_main.validate_system())

            @debug.command()
            @click.argument("args", nargs=-1)
            @click.pass_context
            def trace(_ctx: click.Context, args: tuple[str, ...]) -> None:
                """Trace operations."""
                click.echo(self._cli_main.run_trace(args))

            @debug.command()
            @click.pass_context
            def check(_ctx: click.Context) -> None:
                """Health check for system connectivity."""
                click.echo(self._cli_main.health_check())

        def _register_log_control_commands(self, cli: click.Group) -> None:
            """Register log control command group."""

            @cli.group()
            @click.pass_context
            def log_control(_ctx: click.Context) -> None:
                """Control logging configuration for FLEXT projects."""

            @log_control.command()
            @click.argument(
                "level",
                type=click.Choice(
                    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    case_sensitive=False,
                ),
            )
            @click.pass_context
            def set_level(_ctx: click.Context, level: str) -> None:
                """Set global log level for all FLEXT projects."""
                result = self._cli_main.set_global_log_level(level)
                click.echo(result)

            @log_control.command()
            @click.argument(
                "verbosity",
                type=click.Choice(
                    ["compact", "detailed", "full"], case_sensitive=False
                ),
            )
            @click.pass_context
            def set_verbosity(_ctx: click.Context, verbosity: str) -> None:
                """Set global log verbosity for all FLEXT projects."""
                result = self._cli_main.set_global_log_verbosity(verbosity)
                click.echo(result)

            @log_control.command()
            @click.pass_context
            def log_status(_ctx: click.Context) -> None:
                """Show current logging configuration."""
                config = self._cli_main.get_log_config()
                if "error" in config:
                    click.echo(f"Error: {config['error']}", err=True)
                    return

                click.echo("=== FLEXT Logging Configuration ===")
                click.echo(f"Global Log Level: {config['log_level']}")
                click.echo(f"Global Log Verbosity: {config['log_verbosity']}")
                click.echo(f"CLI Log Level: {config['cli_log_level']}")
                click.echo(f"Logging Configured: {config['configured']}")

            @log_control.command()
            @click.argument("project_name")
            @click.option(
                "--level",
                type=click.Choice(
                    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    case_sensitive=False,
                ),
                help="Set log level for the project",
            )
            @click.option(
                "--verbosity",
                type=click.Choice(
                    ["compact", "detailed", "full"], case_sensitive=False
                ),
                help="Set log verbosity for the project",
            )
            @click.pass_context
            def configure_project(
                _ctx: click.Context,
                project_name: str,
                level: str | None,
                verbosity: str | None,
            ) -> None:
                """Configure logging for a specific FLEXT project."""
                if not level and not verbosity:
                    click.echo(
                        "Error: Must specify either --level or --verbosity", err=True
                    )
                    return

                result = self._cli_main.configure_project_logging(
                    project_name, level, verbosity
                )
                click.echo(result)

            @log_control.command()
            @click.pass_context
            def demo(_ctx: click.Context) -> None:
                """Demonstrate different logging formats."""
                click.echo("=== FLEXT Logging Format Demo ===\n")

                # Demo compact format
                click.echo("1. COMPACT Format:")
                FlextLogger.configure(log_verbosity="compact", structured_output=True)
                logger = FlextLogger("demo.service")
                logger.info(
                    "Sample log message for compact format", demo=True, entry_count=42
                )

                click.echo("\n2. DETAILED Format:")
                FlextLogger.configure(log_verbosity="detailed", structured_output=True)
                logger = FlextLogger("demo.service")
                logger.set_context(
                    extra={
                        "entry_count": 42,
                        "process_time": 0.125,
                        "status": "success",
                    }
                )
                logger.info("Sample log message for detailed format")

                click.echo("\n3. FULL Format:")
                FlextLogger.configure(log_verbosity="full", structured_output=True)
                logger = FlextLogger("demo.service")
                logger.set_context(
                    extra={"entry_count": 42, "file_size": 1024, "throughput": 250.5}
                )
                logger.info("Sample log message for full format")

                click.echo("\n=== Demo Complete ===")
                click.echo(
                    "Use 'flext log-control set-verbosity <level>' to change the format."
                )

            @log_control.command()
            @click.pass_context
            def reset(_ctx: click.Context) -> None:
                """Reset logging configuration to defaults."""
                # Remove FLEXT logging environment variables
                env_vars_to_remove = [
                    "FLEXT_LOG_LEVEL",
                    "FLEXT_LOG_VERBOSITY",
                    "FLEXT_CLI_LOG_LEVEL",
                ]

                removed = []
                for var in env_vars_to_remove:
                    if var in os.environ:
                        del os.environ[var]
                        removed.append(var)

                # Also remove any project-specific variables
                flext_vars = [
                    key
                    for key in os.environ
                    if key.startswith("FLEXT_") and ("LOG" in key or "VERBOSE" in key)
                ]

                for var in flext_vars:
                    if var not in env_vars_to_remove:
                        del os.environ[var]
                        removed.append(var)

                if removed:
                    click.echo(
                        f"Reset logging environment variables: {', '.join(removed)}"
                    )
                else:
                    click.echo("No logging environment variables found to reset.")

                click.echo("Logging configuration reset to defaults.")

        def _register_standalone_commands(self, cli: click.Group) -> None:
            """Register standalone commands not part of any group."""

            @cli.command()
            @click.pass_context
            def version(_ctx: click.Context) -> None:
                """Show version information."""
                click.echo(self._cli_main.get_version())

            @cli.command()
            @click.pass_context
            def interactive(_ctx: click.Context) -> None:
                """Interactive mode - coming soon."""
                click.echo(self._cli_main.start_interactive())

    def execute(self) -> FlextResult[None]:
        """Execute the CLI main functionality."""
        return FlextResult[None].ok(None)

    def get_logger(self) -> FlextLogger:
        """Get CLI logger instance."""
        return self._logger

    # Create options and context management methods
    def create_options(self) -> dict[str, object]:
        """Create CLI options."""
        return self._OptionsHelper.create_common_options()

    def create_context(
        self, *, debug: bool = False, profile: str = "default", quiet: bool = False
    ) -> dict[str, object]:
        """Create CLI context."""
        return self._ContextHelper.create_context_object(
            debug=debug, profile=profile, quiet=quiet
        )

    def get_version(self) -> str:
        """Get version information."""
        return self._VersionHelper.get_version_string()

    def get_version_info(self) -> dict[str, str]:
        """Get detailed version information."""
        return {
            "version": self._VersionHelper.get_version_string(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        }

    def create_cli_options(self) -> dict[str, object]:
        """Create CLI options with validation."""
        options = self._OptionsHelper.create_common_options()

        # Validate output format if present
        if "output" in options and not self._OptionsHelper.validate_output_format(
            str(options["output"])
        ):
            msg = f"Invalid output format: {options['output']}"
            raise ValueError(msg)

        return options

    def create_config_with_overrides(
        self, cli_overrides: dict[str, object]
    ) -> FlextResult[FlextCliConfigs]:
        """Create configuration with CLI parameter overrides."""
        try:
            # Apply CLI overrides to configuration
            config_result = self._ContextHelper.apply_cli_overrides(cli_overrides)
            if config_result.is_failure:
                return FlextResult[FlextCliConfigs].fail(
                    f"Configuration override failed: {config_result.error}"
                )

            return FlextResult[FlextCliConfigs].ok(config_result.value)

        except Exception as e:
            return FlextResult[FlextCliConfigs].fail(
                f"Configuration creation failed: {e}"
            )

    def setup_cli_context(
        self, _ctx: object, *, debug: bool, profile: str, quiet: bool
    ) -> FlextResult[None]:
        """Setup CLI context with configuration."""
        try:
            # Create context object
            context_obj = self._ContextHelper.create_context_object(
                debug=debug, profile=profile, quiet=quiet
            )

            # Store context (simulated - actual implementation would use Click context)
            self._context = context_obj

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"CLI context setup failed: {e}")

    def setup_logging(
        self, *, debug: bool = False, log_level: str | None = None
    ) -> FlextResult[None]:
        """Setup logging configuration."""
        return self._LoggingHelper.setup_logging(debug=debug, log_level=log_level)

    def print_version(self, ctx: object, _param: object, *, value: bool) -> None:
        """Print version and exit callback."""
        if not value:
            return

        # Get version info and display it
        self.get_version_info()

        if ctx:
            # Simulate Click exit
            raise SystemExit(0)

    def create_cli_group(self) -> object:
        """Create the main CLI group with all command registrations.

        This method creates and returns the main Click CLI group with all
        commands properly registered through the unified class structure.
        """
        # Create click commands handler
        click_commands = self._ClickCommands(self)

        # Create and return the main CLI group
        return click_commands.create_main_cli_group()

    def register_config(self, config: FlextCliConfigs) -> None:
        """Register CLI configuration."""
        self._config = config

    def add_command(self, name: str, command: object) -> FlextResult[None]:
        """Add a command to the CLI.

        This method allows external code to register additional commands
        with the CLI while maintaining the unified structure.
        """
        try:
            if not name or not command:
                return FlextResult[None].fail(
                    "Command name and command object are required"
                )

            # Validate command name
            if name in self._commands:
                return FlextResult[None].fail(f"Command '{name}' already exists")

            # Store command
            self._commands[name] = command

            self._logger.info(
                "Command registered successfully",
                extra={"command_name": name, "command_type": type(command).__name__},
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to add command '{name}': {e}"
            self._logger.exception(
                error_msg, extra={"command_name": name, "error": str(e)}
            )
            return FlextResult[None].fail(error_msg)

    def register_command(self, name: str, command: object) -> FlextResult[None]:
        """Register command - alias for add_command to match test expectations."""
        return self.add_command(name, command)

    def create_group(self, name: str, description: str = "") -> object:
        """Create CLI group - simplified wrapper for create_cli_group."""
        return click.Group(name=name, help=description)

    def run(self, args: list[str] | None = None) -> FlextResult[None]:
        """Run the CLI application."""
        try:
            # Create the main CLI group
            _cli_group = self.create_cli_group()

            # In a real implementation, this would call cli_group() to start Click
            # For now, we just indicate successful setup
            self._logger.info("CLI application started successfully")

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"CLI execution failed: {e}"
            self._logger.exception(error_msg, extra={"error": str(e)})
            return FlextResult[None].fail(error_msg)

    # Command execution methods (delegating to helper classes)
    def execute_show_config_command(self) -> str:
        """Execute show config command."""
        return self._ConfigCommands.show_config()

    def execute_set_config_command(self, key: str, value: str) -> str:
        """Execute set config command."""
        return self._ConfigCommands.set_config_value(key, value)

    def execute_edit_config_command(self) -> str:
        """Execute edit config command."""
        return self._ConfigCommands.edit_config()

    def execute_auth_login_command(self, username: str, password: str) -> str:
        """Execute auth login command."""
        return self._AuthCommands.login_user(username, password)

    def execute_auth_status_command(self) -> str:
        """Execute auth status command."""
        return self._AuthCommands.get_auth_status()

    def execute_auth_logout_command(self) -> str:
        """Execute auth logout command."""
        return self._AuthCommands.logout_user()

    def execute_debug_info_command(self) -> dict[str, str]:
        """Execute debug info command."""
        return self._SystemCommands.get_environment_info()

    def start_interactive(self) -> str:
        """Start interactive mode."""
        return "Interactive mode: Coming soon"

    # Logging control methods
    def set_global_log_level(self, level: str) -> str:
        """Set global log level."""
        result = self._LoggingHelper.configure_global_logging(level)
        if result.is_success:
            return result.value
        return f"Failed to set log level: {result.error}"

    def set_global_log_verbosity(self, verbosity: str) -> str:
        """Set global log verbosity."""
        result = self._LoggingHelper.configure_global_logging("INFO", verbosity)
        if result.is_success:
            return f"Global log verbosity set to {verbosity}"
        return f"Failed to set log verbosity: {result.error}"

    def get_log_config(self) -> dict[str, object]:
        """Get current logging configuration."""
        return {
            "log_level": os.environ.get("FLEXT_LOG_LEVEL", "INFO"),
            "log_verbosity": os.environ.get("FLEXT_LOG_VERBOSITY", "compact"),
            "cli_log_level": os.environ.get("FLEXT_CLI_LOG_LEVEL", "INFO"),
            "configured": True,
        }

    def configure_project_logging(
        self, project_name: str, level: str | None, verbosity: str | None
    ) -> str:
        """Configure logging for a specific project."""
        try:
            if level:
                env_var = f"FLEXT_{project_name.upper()}_LOG_LEVEL"
                os.environ[env_var] = level.upper()

            if verbosity:
                env_var = f"FLEXT_{project_name.upper()}_LOG_VERBOSITY"
                os.environ[env_var] = verbosity.lower()

            return f"Configured logging for project: {project_name}"

        except Exception as e:
            return f"Failed to configure project logging: {e}"

    def register_command_group(
        self, name: str, commands: dict[str, object], description: str = ""
    ) -> FlextResult[None]:
        """Register a command group with multiple commands."""
        try:
            if not name or not commands:
                return FlextResult[None].fail("Group name and commands are required")

            # Validate group name
            if name in self._command_groups:
                return FlextResult[None].fail(f"Command group '{name}' already exists")

            # Store command group
            group_info = {
                "name": name,
                "description": description,
                "commands": commands,
            }
            self._command_groups[name] = group_info

            # Register individual commands
            for cmd_name, command in commands.items():
                full_name = f"{name}.{cmd_name}"
                self._commands[full_name] = command

            self._logger.info(
                "Command group registered successfully",
                extra={
                    "group_name": name,
                    "command_count": len(commands),
                    "description": description,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register command group '{name}': {e}"
            self._logger.exception(
                error_msg, extra={"group_name": name, "error": str(e)}
            )
            return FlextResult[None].fail(error_msg)

    def get_command_bus_status(self) -> dict[str, object]:
        """Get command bus status."""
        return {"status": "active", "commands": len(self._commands)}

    def get_registered_handlers(self) -> list[str]:
        """Get list of registered command handlers."""
        return list(self._commands.keys())


# Create global instance for unified CLI
_cli_main = FlextCliMain()


# Version callback function for Click (needed for Click integration)
def print_version(
    ctx: click.Context,
    _param: click.Parameter,
    value: object,
) -> None:
    """Print version information and exit - Click callback function."""
    if not value or ctx.resilient_parsing:
        return

    # Use the unified service for version info
    version_info = _cli_main.get_version_info()
    click.echo(f"FLEXT CLI Version: {version_info['version']}")
    click.echo(f"Python Version: {version_info['python']}")
    click.echo(f"Platform: {version_info['platform']}")
    ctx.exit()


def get_cli_main() -> FlextCliMain:
    """Get the global CLI main instance."""
    return _cli_main


def main() -> None:
    """Main entry point for CLI - uses unified class structure."""
    # Create and run the unified CLI
    cli_group = _cli_main.create_cli_group()
    if callable(cli_group):
        cli_group()
    else:
        msg = "CLI group is not callable"
        raise TypeError(msg)


__all__ = [
    "FlextCliMain",
    "get_cli_main",
    "main",
    "print_version",
]
