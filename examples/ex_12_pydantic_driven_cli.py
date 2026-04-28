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
from collections.abc import Mapping

from examples import c, m, t, u
from flext_cli import cli
from flext_core import p, r


def _report_step_success[T](value: T, message: str) -> T:
    """Emit a success message while preserving the pipeline value."""
    cli.print(message, style=c.Cli.MessageStyles.GREEN)
    return value


def _finish_database_config(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> m.Examples.AdvancedDatabaseConfig:
    """Emit the final success summary and preserve the validated settings."""
    u.display_success_summary("Database configuration")
    return settings


def demonstrate_auto_cli_generation() -> None:
    """Show auto-generated CLI parameters from Pydantic model."""
    cli.print(
        "\n🔧 Auto-Generated CLI Parameters:", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    fields = m.Examples.DeployConfig.model_fields
    cli.print(
        f"✅ Generated {len(fields)} CLI parameters from DeployConfig:",
        style=c.Cli.MessageStyles.GREEN,
    )
    for name, field_info in fields.items():
        field_type = field_info.annotation.__name__ if field_info.annotation else "str"
        description = field_info.description or ""
        default = field_info.default
        cli.print(
            f"   --{name:<20} {description:<50} (type: {field_type}, default: {default})",
            style=c.Cli.MessageStyles.CYAN,
        )
    cli.print("\n📝 Example CLI usage:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "   python app.py deploy --environment production --workers 8 --enable-cache",
        style=c.Cli.MessageStyles.WHITE,
    )


def execute_deploy_from_cli(settings: m.Examples.DeployConfig) -> None:
    """Convert validated Pydantic settings to deployment. Accepts DeployConfig only."""
    cli.print("\n🚀 Deploying with CLI Arguments:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print("✅ Valid configuration:", style=c.Cli.MessageStyles.GREEN)
    cli.show_table(
        settings.model_dump(),
        headers=["Parameter", "Value"],
        title="Validated Deploy Config",
    )
    deploy_result = deploy_application(settings)
    if deploy_result.success:
        cli.print(
            f"✅ Deployment successful to {settings.environment}!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )


def deploy_application(settings: m.Examples.DeployConfig) -> p.Result[str]:
    """Deploy application with validated settings."""
    return r[str].ok(f"Deployed to {settings.environment}")


def show_common_cli_params() -> None:
    """Show auto-generated common CLI parameters."""
    cli.print(
        "\n⚙️  Auto-Generated Common CLI Parameters:",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    cli.print(
        "These are AUTOMATICALLY available in ALL flext-cli commands:\n",
        style=c.Cli.MessageStyles.YELLOW,
    )
    common_params = {
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
        cli.print(
            f"   --{param.replace('_', '-'):<20} {description}",
            style=c.Cli.MessageStyles.CYAN,
        )


def demonstrate_nested_models() -> None:
    """Show CLI generation from nested Pydantic models."""
    cli.print("\n🏗️  Nested Model CLI Generation:", style=c.Cli.MessageStyles.BOLD_CYAN)
    db_fields = m.Examples.DatabaseConfig.model_fields
    cli.print("Database settings parameters:", style=c.Cli.MessageStyles.GREEN)
    for name, field_info in db_fields.items():
        description = field_info.description or ""
        cli.print(f"   --db-{name}: {description}", style=c.Cli.MessageStyles.CYAN)
    cli.print(
        "\n💡 Tip: Use prefixes for nested models:", style=c.Cli.MessageStyles.YELLOW
    )
    cli.print("   --database-host localhost", style=c.Cli.MessageStyles.WHITE)
    cli.print("   --database-port 5432", style=c.Cli.MessageStyles.WHITE)
    cli.print("   --database-name myapp", style=c.Cli.MessageStyles.WHITE)


def create_database_config_from_cli() -> p.Result[m.Examples.AdvancedDatabaseConfig]:
    """Create validated DatabaseConfig using Railway Pattern with Pydantic."""
    cli.print(
        "\n🗄️  Database Configuration with Railway Pattern:",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    cli_args = {
        "host": "db.example.com",
        "port": 5432,
        "name": "production_db",
        "username": "REDACTED_LDAP_BIND_PASSWORD",
        "password": "secure_password_123",
        "ssl_enabled": True,
        "connection_pool": 20,
    }
    return (
        validate_required_fields(cli_args)
        .map_error(
            lambda error: error or "Required field validation failed",
        )
        .map(
            lambda data: _report_step_success(data, "✅ Required fields validated"),
        )
        .flat_map(
            convert_and_validate_with_pydantic,
        )
        .map(
            lambda settings: _report_step_success(
                settings,
                "✅ Pydantic validation passed",
            ),
        )
        .flat_map(
            validate_business_rules,
        )
        .map(
            lambda settings: _report_step_success(
                settings,
                "✅ Business rules validated",
            ),
        )
        .flat_map(
            perform_connection_test,
        )
        .map(
            lambda settings: _report_step_success(
                settings,
                "✅ Connection test passed",
            ),
        )
        .map(
            _finish_database_config,
        )
    )


def validate_required_fields(
    data: Mapping[str, t.JsonPayloadCollectionValue],
) -> p.Result[t.JsonMapping]:
    """Validate that all required fields are present."""
    required = list(c.EXAMPLE_DATABASE_REQUIRED_FIELDS)
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        return r[t.JsonMapping].fail(
            f"Missing required fields: {missing}",
        )
    normalized_data = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
        u.normalize_to_json_value(data)
    )
    return r[t.JsonMapping].ok(normalized_data)


def convert_and_validate_with_pydantic(
    data: t.JsonMapping,
) -> p.Result[m.Examples.AdvancedDatabaseConfig]:
    """Convert raw data to validated Pydantic model."""
    try:
        return r[m.Examples.AdvancedDatabaseConfig].ok(
            m.Examples.AdvancedDatabaseConfig.model_validate(
                data,
            ),
        )
    except c.ValidationError as error:
        return r[m.Examples.AdvancedDatabaseConfig].fail(
            f"Pydantic validation failed: {error}",
        )


def validate_business_rules(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> p.Result[m.Examples.AdvancedDatabaseConfig]:
    """Apply custom business rules to validated database configuration."""
    if settings.ssl_enabled and settings.port == 5432:
        settings = settings.model_copy(update={"port": 5433})
    if settings.connection_pool > 50 and settings.host == "localhost":
        return r[m.Examples.AdvancedDatabaseConfig].fail(
            "Localhost cannot handle large connection pools",
        )
    return r[m.Examples.AdvancedDatabaseConfig].ok(settings)


def perform_connection_test(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> p.Result[m.Examples.AdvancedDatabaseConfig]:
    """Simulate database connection test."""
    time.sleep(0.1)
    if "fail" in settings.host:
        return r[m.Examples.AdvancedDatabaseConfig].fail("Connection test failed")
    return r[m.Examples.AdvancedDatabaseConfig].ok(settings)


def main() -> None:
    """Examples of Pydantic-driven CLI in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Pydantic-Driven CLI Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    demonstrate_auto_cli_generation()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    deploy_config = m.Examples.DeployConfig(
        environment="production",
        workers=8,
        enable_cache=True,
        timeout=60,
    )
    execute_deploy_from_cli(deploy_config)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    show_common_cli_params()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    demonstrate_nested_models()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n❌ Validation Demo - Invalid Environment:",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    try:
        _ = m.Examples.DeployConfig(
            environment="invalid_env",
            workers=4,
            enable_cache=True,
            timeout=30,
        )
    except c.ValidationError as error:
        cli.print(
            f"   Caught validation error: {error}", style=c.Cli.MessageStyles.YELLOW
        )
    cli.print(
        "\n6. Railway Pattern with Pydantic (complete workflow):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    db_config_result = create_database_config_from_cli()
    if db_config_result.success:
        final_config = db_config_result.value
        payload = final_config.model_dump(mode="json")
        u.display_config_table(config_data=m.Cli.DisplayData(data=payload))
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Pydantic CLI Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Define Pydantic models with m.Field() descriptions",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Use CliModelConverter.model_to_cli_params() to extract params",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Add field_validator() for custom validation",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Constraints (ge, le) become CLI validation automatically",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Model → CLI → validated instance = type-safe workflow!",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()
