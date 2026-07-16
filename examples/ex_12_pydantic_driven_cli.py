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

import secrets

from examples import c, m, t, u
from flext_cli import cli
from flext_core import p, r

# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): the example enters
# the railway as one validated model and retains that object through services.
# mro-wkii.17.26 (codex): source example rules from c and generate credentials.


def _report_step_success[T](value: T, message: str) -> T:
    """Emit a success message while preserving the pipeline value."""
    cli.print(message, style=c.Cli.MessageStyles.GREEN)
    return value


def _finish_database_config(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> p.Examples.AdvancedDatabaseConfig:
    """Emit the final success summary and preserve the validated settings."""
    u.display_success_summary("Database configuration")
    return settings


def create_database_config_from_cli() -> p.Result[p.Examples.AdvancedDatabaseConfig]:
    """Create validated DatabaseConfig using Railway Pattern with Pydantic."""
    cli.print(
        "\n🗄️  Database Configuration with Railway Pattern:",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    cli_args = m.Examples.AdvancedDatabaseConfig(
        host="db.example.com",
        port=c.EXAMPLE_DEFAULT_DB_PORT,
        name="production_db",
        username="example_user",
        password=secrets.token_urlsafe(c.EXAMPLE_MIN_PASSWORD_LENGTH),
        ssl_enabled=True,
        connection_pool=c.EXAMPLE_DATABASE_DEMO_CONNECTION_POOL,
    )
    return (
        r[p.Examples.AdvancedDatabaseConfig]
        .ok(cli_args)
        .map(
            lambda settings: _report_step_success(
                settings, "✅ Required fields validated"
            )
        )
        .map(
            lambda settings: _report_step_success(
                settings, "✅ Pydantic validation passed"
            )
        )
        .flat_map(validate_business_rules)
        .map(
            lambda settings: _report_step_success(
                settings, "✅ Business rules validated"
            )
        )
        .flat_map(perform_connection_test)
        .map(
            lambda settings: _report_step_success(settings, "✅ Connection test passed")
        )
        .map(_finish_database_config)
    )


def validate_required_fields(
    data: t.MappingKV[str, t.JsonPayloadCollectionValue],
) -> p.Result[t.JsonMapping]:
    """Validate that all required fields are present."""
    required = list(c.EXAMPLE_DATABASE_REQUIRED_FIELDS)
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        return r[t.JsonMapping].fail(f"Missing required fields: {missing}")
    normalized_data = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
        u.normalize_to_json_value(data)
    )
    return r[t.JsonMapping].ok(normalized_data)


def convert_and_validate_with_pydantic(
    data: t.JsonMapping,
) -> p.Result[p.Examples.AdvancedDatabaseConfig]:
    """Convert raw data to validated Pydantic model."""
    try:
        return r[p.Examples.AdvancedDatabaseConfig].ok(
            m.Examples.AdvancedDatabaseConfig.model_validate(data)
        )
    except c.ValidationError as error:
        return r[p.Examples.AdvancedDatabaseConfig].fail(
            f"Pydantic validation failed: {error}"
        )


def validate_business_rules(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> p.Result[p.Examples.AdvancedDatabaseConfig]:
    """Apply custom business rules to validated database configuration."""
    if settings.ssl_enabled and settings.port == c.EXAMPLE_DEFAULT_DB_PORT:
        settings = settings.model_copy(update={"port": c.EXAMPLE_SSL_DB_PORT})
    if (
        settings.connection_pool > c.EXAMPLE_LOCALHOST_CONNECTION_POOL_LIMIT
        and settings.host == c.EXAMPLE_DEFAULT_HOST
    ):
        return r[p.Examples.AdvancedDatabaseConfig].fail(
            "Localhost cannot handle large connection pools"
        )
    return r[p.Examples.AdvancedDatabaseConfig].ok(settings)


def perform_connection_test(
    settings: m.Examples.AdvancedDatabaseConfig,
) -> p.Result[p.Examples.AdvancedDatabaseConfig]:
    """Simulate database connection test."""
    if "fail" in settings.host:
        return r[p.Examples.AdvancedDatabaseConfig].fail("Connection test failed")
    return r[p.Examples.AdvancedDatabaseConfig].ok(settings)
