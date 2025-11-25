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

import time
from typing import cast

from example_utils import display_config_table, display_success_summary
from flext_core import FlextResult
from pydantic import BaseModel, Field, field_validator

from flext_cli import FlextCli, FlextCliModels, FlextCliTypes

cli = FlextCli()


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
        default="development",
        description="Deployment environment (dev/staging/prod)",
    )

    workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker processes",
    )

    enable_cache: bool = Field(default=True, description="Enable application cache")

    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
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
    cli.output.print_message("\n🔧 Auto-Generated CLI Parameters:", style="bold cyan")

    # Extract CLI parameters from Pydantic model
    params_result = FlextCliModels.CliModelConverter.model_to_cli_params(DeployConfig)

    if params_result.is_success:
        params = params_result.unwrap()

        cli.output.print_message(
            f"✅ Generated {len(params)} CLI parameters from DeployConfig:",
            style="green",
        )

        for param in params:
            cli.output.print_message(
                f"   --{param.name:<20} {param.help:<50} (type: {param.click_type}, default: {param.default})",
                style="cyan",
            )

    # Show what the CLI would look like
    cli.output.print_message("\n📝 Example CLI usage:", style="bold cyan")
    cli.output.print_message(
        "   python app.py deploy --environment production --workers 8 --enable-cache",
        style="white",
    )


# ============================================================================
# PATTERN 3: CLI args → validated Pydantic model instance
# ============================================================================


def execute_deploy_from_cli(cli_args: dict[str, str | int | bool]) -> None:
    """Convert CLI arguments to validated Pydantic model instance."""
    cli.output.print_message("\n🚀 Deploying with CLI Arguments:", style="bold cyan")

    try:
        # Cast to proper CLI data type for type safety
        typed_args = cast("FlextCliTypes.Data.CliDataDict", cli_args)

        # Pydantic automatically validates ALL constraints
        # DeployConfig constructor handles type conversion and validation
        # Cast JsonValue types to specific types expected by DeployConfig
        config = DeployConfig(
            environment=str(typed_args.get("environment", "development")),
            workers=int(str(typed_args.get("workers", 4))),
            enable_cache=bool(typed_args.get("enable_cache", True)),
            timeout=int(str(typed_args.get("timeout", 30))),
        )

        cli.output.print_message("✅ Valid configuration:", style="green")

        # Display validated config
        config_dict = config.model_dump()
        # Create table for displaying validated config
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
            cli.output.print_message(
                f"✅ Deployment successful to {config.environment}!",
                style="bold green",
            )

    except Exception as e:
        cli.output.print_message(f"❌ Validation failed: {e}", style="bold red")


def deploy_application(config: DeployConfig) -> FlextResult[str]:
    """Deploy application with validated config."""
    # Your deployment logic here - config is already validated!
    return FlextResult[str].ok(f"Deployed to {config.environment}")


# ============================================================================
# PATTERN 4: Common CLI parameters (auto-generated from FlextCliConfig)
# ============================================================================


def show_common_cli_params() -> None:
    """Show auto-generated common CLI parameters."""
    cli.output.print_message(
        "\n⚙️  Auto-Generated Common CLI Parameters:", style="bold cyan"
    )
    cli.output.print_message(
        "These are AUTOMATICALLY available in ALL flext-cli commands:\n",
        style="yellow",
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
        cli.output.print_message(
            f"   --{param.replace('_', '-'):<20} {description}", style="cyan"
        )


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
    cli.output.print_message("\n🏗️  Nested Model CLI Generation:", style="bold cyan")

    # Extract parameters from nested model
    db_params_result = FlextCliModels.CliModelConverter.model_to_cli_params(
        DatabaseConfig,
    )

    if db_params_result.is_success:
        db_params = db_params_result.unwrap()

        cli.output.print_message("Database config parameters:", style="green")
        for param in db_params:
            cli.output.print_message(
                f"   --db-{param.name}: {param.help}", style="cyan"
            )

    # In real usage, you'd flatten nested models or use prefixes
    cli.output.print_message(
        "\n💡 Tip: Use prefixes for nested models:", style="yellow"
    )
    cli.output.print_message("   --database-host localhost", style="white")
    cli.output.print_message("   --database-port 5432", style="white")
    cli.output.print_message("   --database-name myapp", style="white")


# ============================================================================
# PATTERN 7: FlextResult + Pydantic Integration (Railway Pattern)
# ============================================================================


class AdvancedDatabaseConfig(BaseModel):
    """Database configuration with advanced validation."""

    host: str = Field(description="Database host", default="localhost")
    port: int = Field(description="Database port", ge=1024, le=65535, default=5432)
    name: str = Field(description="Database name", min_length=1)
    username: str = Field(description="Database username", min_length=1)
    password: str = Field(description="Database password", min_length=8)
    ssl_enabled: bool = Field(description="Enable SSL", default=True)
    connection_pool: int = Field(
        description="Connection pool size", ge=1, le=100, default=10
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is reachable (example validation)."""
        # In real code, you might check DNS resolution or connectivity
        if not v or "." not in v:
            msg = "Host must be a valid hostname or IP"
            raise ValueError(msg)
        return v


def create_database_config_from_cli() -> FlextResult[AdvancedDatabaseConfig]:
    """Create validated DatabaseConfig using Railway Pattern with Pydantic."""
    cli.output.print_message(
        "\n🗄️  Database Configuration with Railway Pattern:", style="bold cyan"
    )

    # Simulate CLI argument collection (normally from Click decorators)
    cli_args = {
        "host": "db.example.com",
        "port": 5432,
        "name": "production_db",
        "username": "REDACTED_LDAP_BIND_PASSWORD",
        "password": "secure_password_123",
        "ssl_enabled": True,
        "connection_pool": 20,
    }

    # Railway Pattern: Chain validation steps
    result: FlextResult[AdvancedDatabaseConfig] = (
        FlextResult[dict[str, object]]
        .ok(cast("dict[str, object]", cli_args))
        # Step 1: Validate required fields
        .map(validate_required_fields)
        .map(
            lambda data: (
                cli.output.print_message("✅ Required fields validated", style="green"),
                data,
            )[1]
        )
        # Step 2: Type conversion and Pydantic validation
        .and_then(convert_and_validate_with_pydantic)
        .map(
            lambda config: (
                cli.output.print_message(
                    "✅ Pydantic validation passed", style="green"
                ),
                config,
            )[1]
        )
        # Step 3: Business logic validation
        .map(validate_business_rules)
        .map(
            lambda config: (
                cli.output.print_message("✅ Business rules validated", style="green"),
                config,
            )[1]
        )
        # Step 4: Connection test (simulated)
        .map(perform_connection_test)
        .map(
            lambda config: (
                cli.output.print_message("✅ Connection test passed", style="green"),
                config,
            )[1]
        )
    )

    if result.is_failure:
        cli.output.print_message(
            f"❌ Configuration failed: {result.error}", style="bold red"
        )
        return result

    config = result.unwrap()
    display_success_summary(cli, "Database configuration")
    return FlextResult[AdvancedDatabaseConfig].ok(config)


def validate_required_fields(data: dict[str, object]) -> dict[str, object]:
    """Validate that all required fields are present."""
    required = ["host", "name", "username", "password"]
    missing = [field for field in required if field not in data or not data[field]]

    if missing:
        msg = f"Missing required fields: {missing}"
        raise ValueError(msg)

    return data


def convert_and_validate_with_pydantic(
    data: dict[str, object],
) -> FlextResult[AdvancedDatabaseConfig]:
    """Convert raw data to validated Pydantic model."""
    try:
        # Pydantic handles type conversion and validation automatically
        config = AdvancedDatabaseConfig(**data)
        return FlextResult[AdvancedDatabaseConfig].ok(config)
    except Exception as e:
        return FlextResult[AdvancedDatabaseConfig].fail(
            f"Pydantic validation failed: {e}"
        )


def validate_business_rules(config: AdvancedDatabaseConfig) -> AdvancedDatabaseConfig:
    """Apply custom business logic validation."""
    # Example business rules
    if config.ssl_enabled and config.port == 5432:
        # SSL should use different port in production
        config.port = 5433  # Force SSL port

    if config.connection_pool > 50 and config.host == "localhost":
        msg = "Localhost cannot handle large connection pools"
        raise ValueError(msg)

    return config


def perform_connection_test(config: AdvancedDatabaseConfig) -> AdvancedDatabaseConfig:
    """Simulate database connection test."""
    # In real code, this would attempt an actual connection
    # For demo, just simulate success

    time.sleep(0.1)  # Simulate network delay

    # Simulate connection failure for demo
    if "fail" in config.host:
        msg = "Connection test failed"
        raise ConnectionError(msg)

    return config


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of Pydantic-driven CLI in YOUR code."""
    cli.output.print_message("=" * 70, style="bold blue")
    cli.output.print_message("  Pydantic-Driven CLI Library Usage", style="bold white")
    cli.output.print_message("=" * 70, style="bold blue")

    # Example 1: Auto-generate CLI params
    demonstrate_auto_cli_generation()

    # Example 2: Execute with CLI args (simulated)
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    test_args: dict[str, str | int | bool] = {
        "environment": "production",
        "workers": 8,
        "enable_cache": True,
        "timeout": 60,
    }
    # test_args is already properly typed for the function
    execute_deploy_from_cli(test_args)

    # Example 3: Show common CLI params
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    show_common_cli_params()

    # Example 4: Nested models
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    demonstrate_nested_models()

    # Example 5: Validation demonstration
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message(
        "\n❌ Validation Demo - Invalid Environment:", style="bold cyan"
    )

    # Intentional invalid args to demonstrate validation - use object for flexible testing

    # Use proper types for the invalid args to demonstrate validation
    invalid_args: dict[str, str | int | bool] = {
        "environment": "invalid_env",  # Will fail validation!
        "workers": 4,
        "enable_cache": True,
        "timeout": 30,
    }

    try:
        # Cast to proper CLI data type for type safety
        typed_invalid_args = cast("FlextCliTypes.Data.CliDataDict", invalid_args)

        # DeployConfig constructor handles type conversion and validation
        # Cast JsonValue types to specific types expected by DeployConfig
        DeployConfig(
            environment=str(typed_invalid_args.get("environment", "development")),
            workers=int(str(typed_invalid_args.get("workers", 4))),
            enable_cache=bool(typed_invalid_args.get("enable_cache", True)),
            timeout=int(str(typed_invalid_args.get("timeout", 30))),
        )
    except Exception as e:
        cli.output.print_message(f"   Caught validation error: {e}", style="yellow")

    # Example 6: Railway Pattern with Pydantic
    cli.output.print_message(
        "\n6. Railway Pattern with Pydantic (complete workflow):", style="bold cyan"
    )
    db_config_result = create_database_config_from_cli()

    if db_config_result.is_success:
        final_config = db_config_result.unwrap()
        # Display final validated config
        config_data = final_config.model_dump()
        display_config_table(
            cli=cli,
            config_data=config_data,
            title="Final Database Configuration",
        )

    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("  ✅ Pydantic CLI Examples Complete", style="bold green")
    cli.output.print_message("=" * 70, style="bold blue")

    # Integration guide
    cli.output.print_message("\n💡 Integration Tips:", style="bold cyan")
    cli.output.print_message(
        "  • Define Pydantic models with Field() descriptions", style="white"
    )
    cli.output.print_message(
        "  • Use CliModelConverter.model_to_cli_params() to extract params",
        style="white",
    )
    cli.output.print_message(
        "  • Add field_validator() for custom validation", style="white"
    )
    cli.output.print_message(
        "  • Constraints (ge, le) become CLI validation automatically",
        style="white",
    )
    cli.output.print_message(
        "  • Model → CLI → validated instance = type-safe workflow!",
        style="white",
    )


if __name__ == "__main__":
    main()
