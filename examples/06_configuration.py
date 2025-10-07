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

from flext_cli import FlextCliConfig


def demonstrate_auto_configuration() -> None:
    """Show auto-configuration from environment."""
    # Config auto-loads from environment variables
    config = FlextCliConfig()

    print(f"Debug mode: {config.debug}")  # Auto-set from FLEXT_DEBUG
    print(f"Log level: {config.log_level}")  # Auto-set from FLEXT_LOG_LEVEL
    print(f"Environment: {config.environment}")  # Auto-detected


def demonstrate_auto_validation() -> None:
    """Show automatic validation with Pydantic."""
    # Validation happens automatically on init
    config = FlextCliConfig(
        debug=True,
        log_level="DEBUG",
        environment="development",
    )

    # Auto-validated against business rules
    validation = config.validate_business_rules()
    if validation.is_success:
        print("Config auto-validated")


def demonstrate_profile_auto_selection() -> None:
    """Show profile auto-selection based on environment."""
    # Development profile auto-selected in dev env
    dev_config = FlextCliConfig(environment="development")
    print(f"Dev debug: {dev_config.debug}")  # Auto-enabled

    # Production profile auto-selected in prod env
    prod_config = FlextCliConfig(environment="production")
    print(f"Prod debug: {prod_config.debug}")  # Auto-disabled


def main() -> None:
    """Run all demonstrations."""
    demonstrate_auto_configuration()
    demonstrate_auto_validation()
    demonstrate_profile_auto_selection()


if __name__ == "__main__":
    main()
