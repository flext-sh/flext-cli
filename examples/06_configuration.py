"""Configuration Management - Settings.

Demonstrates flext-cli configuration through FlextCli API.

Key Features:
- Auto-loading from environment variables
- Pydantic validation automatic
- Config propagation to services automatic
- Profile management auto-selected

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli, FlextCliConfig

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_auto_configuration() -> None:
    """Show auto-configuration from environment."""
    cli.formatters.print("\n⚙️  Auto-Configuration:", style="bold cyan")

    # Config auto-loads from environment variables
    config = FlextCliConfig()

    cli.formatters.print(f"✅ Debug mode: {config.debug}", style="green")
    cli.formatters.print(f"✅ Log level: {config.log_level}", style="green")
    cli.formatters.print(f"✅ Environment: {config.environment}", style="green")


def demonstrate_auto_validation() -> None:
    """Show automatic validation with Pydantic."""
    cli.formatters.print("\n✔️  Auto-Validation:", style="bold cyan")

    # Validation happens automatically on init
    config = FlextCliConfig(
        debug=True,
        log_level="DEBUG",
        environment="development",
    )

    # Auto-validated against business rules
    validation = config.validate_business_rules()
    if validation.is_success:
        cli.formatters.print("✅ Config auto-validated", style="green")


def demonstrate_profile_auto_selection() -> None:
    """Show profile auto-selection based on environment."""
    cli.formatters.print("\n🎯 Profile Auto-Selection:", style="bold cyan")

    # Development profile auto-selected in dev env
    dev_config = FlextCliConfig(environment="development")
    cli.formatters.print(f"✅ Dev debug: {dev_config.debug}", style="green")

    # Production profile auto-selected in prod env
    prod_config = FlextCliConfig(environment="production")
    cli.formatters.print(f"✅ Prod debug: {prod_config.debug}", style="green")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print(
        "  Configuration Management Examples", style="bold white on blue"
    )
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_auto_configuration()
    demonstrate_auto_validation()
    demonstrate_profile_auto_selection()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print(
        "  ✅ All configuration examples completed!", style="bold green"
    )
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
