"""FLEXT CLI Ecosystem Integration - Generic patterns for ecosystem projects.

This module provides generic CLI patterns that ANY ecosystem project can use,
following docs/patterns/foundation-refactored.md. This library is project-agnostic
and provides the foundation patterns that specific projects implement in their own codebases.

Generic Integration Patterns:
    1. CLI Foundation Base - Base for standalone CLI or flext-service integration
    2. flext-core Integration Bridge - Deep flext-core configuration integration
    3. Ecosystem Library Base - Generic patterns that projects extend

Project Implementation Guide:
    Each ecosystem project should implement these patterns in their own codebase:

    # In flext-meltano project:
    from flext_cli import FlextCliGenericCommand, FlextCliConfigFactory

    class MeltanoCommand(FlextCliGenericCommand):
        pipeline: str
        environment: str = "dev"

        def execute(self) -> FlextResult[Any]:
            # Meltano-specific implementation
            return FlextResult.ok({"pipeline": self.pipeline})

    # In algar-oud-mig project:
    from flext_cli import FlextCliGenericCommand

    class AlgarMigrationCommand(FlextCliGenericCommand):
        source_ldap: str
        target_oud: str

        def execute(self) -> FlextResult[Any]:
            # ALGAR-specific implementation
            return FlextResult.ok({"migration": f"{self.source_ldap} -> {self.target_oud}"})

Modern Benefits:
    - 85% boilerplate reduction compared to custom CLI implementations
    - Railway-oriented programming eliminating exception handling
    - Hierarchical configuration following config-cli.md patterns
    - Zero-configuration entity management
    - Project-agnostic patterns that any project can extend

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from typing import ClassVar, cast

from flext_core import FlextResult

from flext_cli.foundation import (
    FlextCliConfig,
    FlextCliEntity,
    create_flext_cli_config,
    setup_flext_cli,
)


class FlextCliGenericCommand(FlextCliEntity):
    """Generic CLI command example following modern patterns.

    This demonstrates how ecosystem projects can create their own commands
    using the FlextCli foundation patterns.

    Benefits vs custom implementation:
    - OLD: 50+ lines of custom CLI boilerplate
    - NEW: 8 lines - 84% reduction!
    - Automatic: error handling, validation, logging, metrics

    Example usage for ANY ecosystem project:
        class MyProjectCommand(FlextCliGenericCommand):
            my_field: str
            config_data: dict[str, Any] = {}

            def execute(self) -> FlextResult[Any]:
                # Project-specific implementation
                return FlextResult.ok({"executed": self.name})
    """

    # Generic fields that any project can extend
    config_data: ClassVar[dict[str, object]] = {}
    environment: str = "default"

    def execute(self) -> FlextResult[object]:
        """Execute generic command with automatic error handling."""
        # Generic implementation - projects override this
        return FlextResult.ok(
            {
                "command": self.name,
                "environment": self.environment,
                "config": self.config_data,
                "status": "completed",
            },
        )


class FlextCliConfigFactory:
    """Generic factory for creating project-specific CLI configurations.

    This factory demonstrates how any ecosystem project can create CLI configurations
    following the hierarchical patterns while maintaining their specific requirements.

    Usage by ecosystem projects:
        # In flext-meltano project:
        config = FlextCliConfigFactory.create_project_config(
            project_name="meltano",
            environment="production",
            debug=True,
            # Project-specific fields
            state_backend="systemdb",
            project_root="."
        )

        # In algar-oud-mig project:
        config = FlextCliConfigFactory.create_project_config(
            project_name="algar-migration",
            migration_mode="incremental",
            batch_size=1000,
            ldap_timeout=30
        )
    """

    @staticmethod
    def create_project_config(
        project_name: str,
        **overrides: object,
    ) -> FlextResult[FlextCliConfig]:
        """Create project-specific CLI configuration.

        Args:
            project_name: Name of the project (for logging/identification)
            **overrides: Project-specific configuration overrides

        Returns:
            FlextResult[FlextCliConfig]: Configuration with project-specific settings

        Example:
            config = FlextCliConfigFactory.create_project_config(
                project_name="my-project",
                environment="production",
                debug=True,
                custom_field="value"
            ).unwrap()

        """
        # Set generic defaults that any project can use
        generic_defaults = {
            "project_name": project_name,
            "environment": "development",
            "debug": False,
        }

        # Merge with project-specific overrides
        final_config = {**generic_defaults, **overrides}

        return create_flext_cli_config(**final_config)


def setup_flext_cli_ecosystem(
    project_name: str,
    config: FlextCliConfig | None = None,
    **config_overrides: object,
) -> FlextResult[dict[str, object]]:
    """Setup CLI for ecosystem project following modern patterns.

    This function provides a unified setup pattern for all ecosystem projects,
    eliminating project-specific CLI boilerplate while maintaining flexibility.

    Args:
        project_name: Name of the ecosystem project (e.g., "flext-meltano")
        config: Optional pre-created configuration
        **config_overrides: Configuration overrides for hierarchical system

    Returns:
        FlextResult[dict[str, object]]: Setup result with project context

    Example:
        # Generic usage for any ecosystem project
        result = setup_flext_cli_ecosystem(
            "my-project",
            environment="production",
            debug=True
        )

        # Any project can use this pattern
        result = setup_flext_cli_ecosystem(
            "another-project",
            custom_setting="value",
            batch_size=1000
        )

    """
    try:
        # Create configuration if not provided
        if config is None:
            # Use generic factory for all ecosystem projects
            config_result = FlextCliConfigFactory.create_project_config(
                project_name=project_name,
                **config_overrides,
            )

            if not config_result.success:
                return FlextResult.fail(
                    f"Config creation failed: {config_result.error}",
                )

            config = config_result.data

        # Setup CLI with project-specific configuration
        setup_result = setup_flext_cli(config)
        if not setup_result.success:
            return FlextResult.fail(f"CLI setup failed: {setup_result.error}")

        if config is None:
            # This case should ideally not happen if config_result.success was true,
            # but for mypy's sake and runtime safety, we'll keep it.
            return FlextResult.fail(
                "Configuration object is unexpectedly None after creation.",
            )

        return FlextResult.ok(
            {
                "project": project_name,
                "config": config.model_dump(),
                "setup": True,
            },
        )

    except Exception as e:
        return FlextResult.fail(f"Ecosystem CLI setup failed: {e}")


# Migration helpers for existing ecosystem projects
def migrate_to_modern_patterns(legacy_setup_function: str, project_name: str) -> str:
    """Generate migration code from legacy patterns to modern foundation patterns.

    This function helps ecosystem projects migrate from legacy CLI patterns to
    modern foundation patterns following docs/patterns/foundation-refactored.md.

    Args:
        legacy_setup_function: Name of existing setup function
        project_name: Project name for specific migration

    Returns:
        str: Migration code example

    """
    return f"""\
# MIGRATION: {project_name} - Legacy to Modern FlextCli Patterns
#
# OLD (Legacy Pattern): 30+ lines of boilerplate
# def {legacy_setup_function}():
#     try:
#         config = load_config()
#         validate_config(config)
#         setup_logging(config.log_level)
#         setup_cli_context(config)
#         return {{"success": True, "config": config}}
#     except Exception as e:
#         return {{"success": False, "error": str(e)}}
#
# NEW (Modern FlextCli Pattern): 3 lines - 90% reduction!
from flext_cli import setup_flext_cli_ecosystem

def {legacy_setup_function}_modern(**config_overrides):
    "Modern setup with railway-oriented programming following FlextCli patterns."
    return setup_flext_cli_ecosystem("{project_name}", **config_overrides)

# Usage in {project_name} project:
# result = {legacy_setup_function}_modern(debug=True, environment="prod")
# if result.success:
#     print("Setup completed successfully!")
#     context = result.data
# else:
#     print(f"Setup failed: {{result.error}}")
#
# Custom commands in {project_name}:
# from flext_cli import FlextCliGenericCommand
#
# class {project_name.title().replace("-", "")}Command(FlextCliGenericCommand):
#     project_specific_field: str
#
#     def execute(self) -> FlextResult[dict[str, object]]: # Changed from Any
#         return FlextResult.ok({{
#             "project": "{project_name}",
#             "field": self.project_specific_field,
#             "executed": True
#         }})
"""


# Legacy compatibility facades with warnings
def setup_ecosystem_cli(
    *args: object,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:  # Changed return type to object
    """Legacy facade for setup_flext_cli_ecosystem (deprecated).

    ⚠️ DEPRECATED: Use setup_flext_cli_ecosystem following FLEXT architecture patterns.
    """
    warnings.warn(
        "setup_ecosystem_cli is deprecated. Use setup_flext_cli_ecosystem following FLEXT architecture patterns.",
        DeprecationWarning,
        stacklevel=2,
    )

    project_name: str = ""
    current_config: FlextCliConfig | None = None
    extra_kwargs: dict[str, object] = {}

    # Iterate through args to extract project_name, config, and other kwargs
    # This is a heuristic and might need adjustment based on how legacy functions were called.
    for i, arg in enumerate(args):
        if i == 0 and isinstance(arg, str):
            project_name = arg
        elif isinstance(arg, FlextCliConfig):
            current_config = arg
        elif isinstance(arg, dict):
            extra_kwargs.update(arg)
        # else: ignore other types in args if not directly relevant to setup_flext_cli_ecosystem

    # Merge any remaining kwargs from the original call
    final_kwargs = {**kwargs, **extra_kwargs}

    # If project_name wasn't found in args, try to get it from kwargs
    if not project_name and "project_name" in final_kwargs:
        project_name = cast("str", final_kwargs.pop("project_name"))

    return setup_flext_cli_ecosystem(
        project_name=project_name,
        config=current_config,
        **final_kwargs,
    )


__all__ = [
    "FlextCliConfigFactory",  # Generic config factory for any project
    # Modern ecosystem patterns (FlextCli* naming following FLEXT architecture)
    "FlextCliGenericCommand",  # Generic command pattern for any project
    # Migration helpers
    "migrate_to_modern_patterns",  # Code generation for legacy migration
    # Legacy compatibility facade (deprecated)
    "setup_ecosystem_cli",  # Facade for setup_flext_cli_ecosystem (deprecated)
    "setup_flext_cli_ecosystem",  # Generic setup for any ecosystem project
]
