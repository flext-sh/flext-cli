"""Pydantic-Driven CLI - Auto-Generate CLI from Models.

Shows how to build type-safe CLIs using Pydantic 2 models with ZERO manual parameter definition.

WHEN TO USE:
- Building type-safe CLIs with built-in validation
- Want auto-generated CLI parameters from data models
- Need consistent validation between API and CLI
- Building complex CLIs with many parameters
- Want IDE autocomplete and type checking

FLEXT-CLI PROVIDES:
- CliModelConverter - Pydantic → CLI parameter conversion
- FlextCliCommonParams - Auto-generated common CLI params
- Complete type conversion: Pydantic Field → Click Option
- Automatic validation, defaults, help text from Pydantic

HOW TO USE IN YOUR CLI:
Define Pydantic models, auto-generate CLI parameters - NO manual Click decorators!

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextCore
from pydantic import BaseModel, Field, field_validator

from flext_cli import FlextCli
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()


# ============================================================================
# PATTERN 1: Define Pydantic model - becomes CLI automatically
# ============================================================================


class DeployConfig(BaseModel):
    """Deployment configuration - auto-generates CLI parameters.

    Each Pydantic Field becomes a CLI option automatically:
    - Field description → --help text
    - Field default → option default value
    - Field type → CLI parameter type
    - Field validators → CLI validation
    """

    environment: str = Field(
        default="development", description="Deployment environment (dev/staging/prod)"
    )

    workers: int = Field(
        default=4, ge=1, le=32, description="Number of worker processes"
    )

    enable_cache: bool = Field(default=True, description="Enable application cache")

    timeout: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment - works in CLI too."""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            msg = f"Must be one of: {', '.join(valid_envs)}"
            raise ValueError(msg)
        return v


# ============================================================================
# PATTERN 2: Auto-generate CLI parameters from Pydantic model
# ============================================================================


def demonstrate_auto_cli_generation() -> None:
    """Show auto-generated CLI parameters from Pydantic model."""
    cli.print("\n🔧 Auto-Generated CLI Parameters:", style="bold cyan")

    # Extract CLI parameters from Pydantic model
    params_result = FlextCliModels.CliModelConverter.model_to_cli_params(DeployConfig)

    if params_result.is_success:
        params = params_result.unwrap()

        cli.print(
            f"✅ Generated {len(params)} CLI parameters from DeployConfig:",
            style="green",
        )

        for param in params:
            cli.print(
                f"   --{param['name']:<20} {param['help']:<50} (type: {param['click_type']}, default: {param['default']})",
                style="cyan",
            )

    # Show what the CLI would look like
    cli.print("\n📝 Example CLI usage:", style="bold cyan")
    cli.print(
        "   python app.py deploy --environment production --workers 8 --enable-cache",
        style="white",
    )


# ============================================================================
# PATTERN 3: CLI args → validated Pydantic model instance
# ============================================================================


def execute_deploy_from_cli(cli_args: dict[str, str | int | bool]) -> None:
    """Convert CLI arguments to validated Pydantic model instance."""
    cli.print("\n🚀 Deploying with CLI Arguments:", style="bold cyan")

    try:
        # Pydantic automatically validates ALL constraints
        # DeployConfig constructor handles type conversion and validation
        config = DeployConfig(**cli_args)

        cli.print("✅ Valid configuration:", style="green")

        # Display validated config
        config_dict = config.model_dump()
        # Cast to expected type for table creation
        table_result = cli.create_table(
            data=config_dict,
            headers=["Parameter", "Value"],
            title="Validated Deploy Config",
        )

        if table_result.is_success:
            cli.print_table(table_result.unwrap())

        # Use validated config in your application
        deploy_result = deploy_application(config)

        if deploy_result.is_success:
            cli.print(
                f"✅ Deployment successful to {config.environment}!", style="bold green"
            )

    except Exception as e:
        cli.print(f"❌ Validation failed: {e}", style="bold red")


def deploy_application(config: DeployConfig) -> FlextCore.Result[str]:
    """Deploy application with validated config."""
    # Your deployment logic here - config is already validated!
    return FlextCore.Result[str].ok(f"Deployed to {config.environment}")


# ============================================================================
# PATTERN 4: Common CLI parameters (auto-generated from FlextCliConfig)
# ============================================================================


def show_common_cli_params() -> None:
    """Show auto-generated common CLI parameters."""
    cli.print("\n⚙️  Auto-Generated Common CLI Parameters:", style="bold cyan")
    cli.print(
        "These are AUTOMATICALLY available in ALL flext-cli commands:\n", style="yellow"
    )

    # These come from FlextCliConfig Pydantic fields
    common_params: FlextCliTypes.Data.CliDataDict = {
        "verbose": "Enable verbose output (-v)",
        "quiet": "Suppress non-error output (-q)",
        "debug": "Enable debug mode (-d)",
        "trace": "Enable trace mode (-t)",
        "log_level": "Set log level: DEBUG, INFO, WARNING, ERROR (-L)",
        "log_format": "Set log format: compact, detailed, full",
        "output_format": "Set output format: table, json, yaml, csv (-o)",
        "no_color": "Disable colored output",
        "config_file": "Path to configuration file (-c)",
    }

    for param, description in common_params.items():
        cli.print(f"   --{param.replace('_', '-'):<20} {description}", style="cyan")


# ============================================================================
# PATTERN 5: Complex nested models → CLI
# ============================================================================


class DatabaseConfig(BaseModel):
    """Database configuration."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1024, le=65535, description="Database port")
    name: str = Field(description="Database name")


class AppConfig(BaseModel):
    """Complete application configuration with nested models."""

    app_name: str = Field(description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    database: DatabaseConfig = Field(description="Database configuration")
    debug: bool = Field(default=False, description="Enable debug mode")


def demonstrate_nested_models() -> None:
    """Show CLI generation from nested Pydantic models."""
    cli.print("\n🏗️  Nested Model CLI Generation:", style="bold cyan")

    # Extract parameters from nested model
    db_params_result = FlextCliModels.CliModelConverter.model_to_cli_params(
        DatabaseConfig
    )

    if db_params_result.is_success:
        db_params = db_params_result.unwrap()

        cli.print("Database config parameters:", style="green")
        for param in db_params:
            cli.print(f"   --db-{param['name']}: {param['help']}", style="cyan")

    # In real usage, you'd flatten nested models or use prefixes
    cli.print("\n💡 Tip: Use prefixes for nested models:", style="yellow")
    cli.print("   --database-host localhost", style="white")
    cli.print("   --database-port 5432", style="white")
    cli.print("   --database-name myapp", style="white")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of Pydantic-driven CLI in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Pydantic-Driven CLI Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Auto-generate CLI params
    demonstrate_auto_cli_generation()

    # Example 2: Execute with CLI args (simulated)
    cli.print("\n" + "=" * 70, style="bold blue")
    test_args: dict[str, str | int | bool] = {
        "environment": "production",
        "workers": 8,
        "enable_cache": True,
        "timeout": 60,
    }
    # test_args is already properly typed for the function
    execute_deploy_from_cli(test_args)

    # Example 3: Show common CLI params
    cli.print("\n" + "=" * 70, style="bold blue")
    show_common_cli_params()

    # Example 4: Nested models
    cli.print("\n" + "=" * 70, style="bold blue")
    demonstrate_nested_models()

    # Example 5: Validation demonstration
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("\n❌ Validation Demo - Invalid Environment:", style="bold cyan")

    # Intentional invalid args to demonstrate validation - use object for flexible testing

    # Use proper types for the invalid args to demonstrate validation
    invalid_args: dict[str, str | int | bool] = {
        "environment": "invalid_env",  # Will fail validation!
        "workers": 4,
        "enable_cache": True,
        "timeout": 30,
    }

    try:
        # DeployConfig constructor handles type conversion and validation
        DeployConfig(**invalid_args)
    except Exception as e:
        cli.print(f"   Caught validation error: {e}", style="yellow")

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Pydantic CLI Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Define Pydantic models with Field() descriptions", style="white")
    cli.print(
        "  • Use CliModelConverter.model_to_cli_params() to extract params",
        style="white",
    )
    cli.print("  • Add field_validator() for custom validation", style="white")
    cli.print(
        "  • Constraints (ge, le) become CLI validation automatically", style="white"
    )
    cli.print(
        "  • Model → CLI → validated instance = type-safe workflow!", style="white"
    )


if __name__ == "__main__":
    main()
