"""Pydantic-Driven CLI - Auto-Generate CLI from Models.

Shows how to build type-safe CLIs using Pydantic 2 models with ZERO manual
parameter definition.

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

from flext_core import r

from examples import (
    AdvancedDatabaseConfig,
    DatabaseConfig,
    DeployConfig,
    display_config_table,
    display_success_summary,
)
from flext_cli import cli, m, t


def demonstrate_auto_cli_generation() -> None:
    """Show auto-generated CLI parameters from Pydantic model."""
    cli.print("\n🔧 Auto-Generated CLI Parameters:", style="bold cyan")
    fields = DeployConfig.model_fields
    cli.print(
        f"✅ Generated {len(fields)} CLI parameters from DeployConfig:",
        style="green",
    )
    for name, field_info in fields.items():
        field_type = field_info.annotation.__name__ if field_info.annotation else "str"
        description = field_info.description or ""
        default = field_info.default
        cli.print(
            f"   --{name:<20} {description:<50} (type: {field_type}, default: {default})",
            style="cyan",
        )
    cli.print("\n📝 Example CLI usage:", style="bold cyan")
    cli.print(
        "   python app.py deploy --environment production --workers 8 --enable-cache",
        style="white",
    )


def execute_deploy_from_cli(config: DeployConfig) -> None:
    """Convert validated Pydantic config to deployment. Accepts DeployConfig only."""
    cli.print("\n🚀 Deploying with CLI Arguments:", style="bold cyan")
    cli.print("✅ Valid configuration:", style="green")
    cli.show_table(
        config.model_dump(),
        headers=["Parameter", "Value"],
        title="Validated Deploy Config",
    )
    deploy_result = deploy_application(config)
    if deploy_result.is_success:
        cli.print(
            f"✅ Deployment successful to {config.environment}!",
            style="bold green",
        )


def deploy_application(config: DeployConfig) -> r[str]:
    """Deploy application with validated config."""
    return r[str].ok(f"Deployed to {config.environment}")


def show_common_cli_params() -> None:
    """Show auto-generated common CLI parameters."""
    cli.print("\n⚙️  Auto-Generated Common CLI Parameters:", style="bold cyan")
    cli.print(
        "These are AUTOMATICALLY available in ALL flext-cli commands:\n",
        style="yellow",
    )
    common_params: t.ContainerMapping = {
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


def demonstrate_nested_models() -> None:
    """Show CLI generation from nested Pydantic models."""
    cli.print("\n🏗️  Nested Model CLI Generation:", style="bold cyan")
    db_fields = DatabaseConfig.model_fields
    cli.print("Database config parameters:", style="green")
    for name, field_info in db_fields.items():
        description = field_info.description or ""
        cli.print(f"   --db-{name}: {description}", style="cyan")
    cli.print("\n💡 Tip: Use prefixes for nested models:", style="yellow")
    cli.print("   --database-host localhost", style="white")
    cli.print("   --database-port 5432", style="white")
    cli.print("   --database-name myapp", style="white")


def create_database_config_from_cli() -> r[AdvancedDatabaseConfig]:
    """Create validated DatabaseConfig using Railway Pattern with Pydantic."""
    cli.print("\n🗄️  Database Configuration with Railway Pattern:", style="bold cyan")
    cli_args: t.ContainerMapping = {
        "host": "db.example.com",
        "port": 5432,
        "name": "production_db",
        "username": "REDACTED_LDAP_BIND_PASSWORD",
        "password": "secure_password_123",
        "ssl_enabled": True,
        "connection_pool": 20,
    }
    validated_data = validate_required_fields(cli_args)
    cli.print("✅ Required fields validated", style="green")
    pydantic_result = convert_and_validate_with_pydantic(validated_data)
    if pydantic_result.is_failure:
        return pydantic_result
    cli.print("✅ Pydantic validation passed", style="green")
    config = pydantic_result.value
    final_config = validate_business_rules(config)
    cli.print("✅ Business rules validated", style="green")
    tested_config = perform_connection_test(final_config)
    cli.print("✅ Connection test passed", style="green")
    display_success_summary(cli, "Database configuration")
    return r[AdvancedDatabaseConfig].ok(tested_config)


def validate_required_fields(
    data: t.ContainerMapping,
) -> t.ContainerMapping:
    """Validate that all required fields are present."""
    required = ["host", "name", "username", "password"]
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        msg = f"Missing required fields: {missing}"
        raise ValueError(msg)
    return data


def convert_and_validate_with_pydantic(
    data: t.ContainerMapping,
) -> r[AdvancedDatabaseConfig]:
    """Convert raw data to validated Pydantic model."""
    try:
        host = str(data.get("host", "localhost"))
        port_value = data.get("port", 5432)
        port = int(port_value) if isinstance(port_value, (str, int)) else 5432
        name = str(data.get("name", ""))
        username = str(data.get("username", ""))
        password = str(data.get("password", ""))
        ssl_value = data.get("ssl_enabled", True)
        ssl_enabled = bool(ssl_value)
        pool_value = data.get("connection_pool", 10)
        connection_pool = int(pool_value) if isinstance(pool_value, (str, int)) else 10
        config = AdvancedDatabaseConfig(
            host=host,
            port=port,
            name=name,
            username=username,
            password=password,
            ssl_enabled=ssl_enabled,
            connection_pool=connection_pool,
        )
        return r[AdvancedDatabaseConfig].ok(config)
    except Exception as e:
        return r[AdvancedDatabaseConfig].fail(f"Pydantic validation failed: {e}")


def validate_business_rules(config: AdvancedDatabaseConfig) -> AdvancedDatabaseConfig:
    """Apply custom business logic validation; returns new instance (no mutation)."""
    if config.ssl_enabled and config.port == 5432:
        config = config.model_copy(update={"port": 5433})
    if config.connection_pool > 50 and config.host == "localhost":
        msg = "Localhost cannot handle large connection pools"
        raise ValueError(msg)
    return config


def perform_connection_test(config: AdvancedDatabaseConfig) -> AdvancedDatabaseConfig:
    """Simulate database connection test."""
    time.sleep(0.1)
    if "fail" in config.host:
        msg = "Connection test failed"
        raise ConnectionError(msg)
    return config


def main() -> None:
    """Examples of Pydantic-driven CLI in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Pydantic-Driven CLI Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    demonstrate_auto_cli_generation()
    cli.print("\n" + "=" * 70, style="bold blue")
    deploy_config = DeployConfig(
        environment="production",
        workers=8,
        enable_cache=True,
        timeout=60,
    )
    execute_deploy_from_cli(deploy_config)
    cli.print("\n" + "=" * 70, style="bold blue")
    show_common_cli_params()
    cli.print("\n" + "=" * 70, style="bold blue")
    demonstrate_nested_models()
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("\n❌ Validation Demo - Invalid Environment:", style="bold cyan")
    try:
        _ = DeployConfig(
            environment="invalid_env",
            workers=4,
            enable_cache=True,
            timeout=30,
        )
    except Exception as e:
        cli.print(f"   Caught validation error: {e}", style="yellow")
    cli.print(
        "\n6. Railway Pattern with Pydantic (complete workflow):",
        style="bold cyan",
    )
    db_config_result = create_database_config_from_cli()
    if db_config_result.is_success:
        final_config = db_config_result.value
        payload = final_config.model_dump(mode="json")
        display_config_table(cli=cli, config_data=m.Cli.DisplayData(data=payload))
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Pydantic CLI Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Define Pydantic models with Field() descriptions", style="white")
    cli.print(
        "  • Use CliModelConverter.model_to_cli_params() to extract params",
        style="white",
    )
    cli.print("  • Add field_validator() for custom validation", style="white")
    cli.print(
        "  • Constraints (ge, le) become CLI validation automatically",
        style="white",
    )
    cli.print(
        "  • Model → CLI → validated instance = type-safe workflow!",
        style="white",
    )


if __name__ == "__main__":
    main()
