"""FLEXT CLI Ecosystem Integration."""

from __future__ import annotations

from typing import ClassVar, override

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
          config_data: dict[str, object] = {}

          def execute(self) -> FlextResult[object]:
              # Project-specific implementation
              return FlextResult[None].ok({"executed": self.name})
    """

    # Generic fields that any project can extend
    config_data: ClassVar[dict[str, object]] = {}
    environment: str = "default"

    @override
    def execute(self) -> FlextResult[object]:
        """Execute generic command with automatic error handling."""
        # Generic implementation - projects override this
        return FlextResult[object].ok(
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

      # In client-a-oud-mig project:
      config = FlextCliConfigFactory.create_project_config(
          project_name="client-a-migration",
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
            ).value

        """
        # Set generic defaults that any project can use
        generic_defaults: dict[str, object] = {
            "project_name": project_name,
            "environment": "development",
            "debug": False,
        }

        # Merge with project-specific overrides
        final_config: dict[str, object] = {**generic_defaults, **overrides}

        return create_flext_cli_config(**final_config)


def setup_flext_cli_ecosystem(
    project_name: str,
    config: FlextCliConfig | None = None,
    **config_overrides: object,
) -> FlextResult[dict[str, object]]:
    """Set up CLI for ecosystem project following modern patterns.

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

            if not config_result.is_success:
                return FlextResult[dict[str, object]].fail(
                    f"Config creation failed: {config_result.error}",
                )

            config = config_result.value

        # Setup CLI with project-specific configuration
        setup_result = setup_flext_cli(config)
        if not setup_result.is_success:
            return FlextResult[dict[str, object]].fail(
                f"CLI setup failed: {setup_result.error}"
            )

        # config is guaranteed to be non-None at this point due to success check above

        return FlextResult[dict[str, object]].ok(
            {
                "project": project_name,
                "config": config.model_dump(),
                "setup": True,
            },
        )

    except Exception as e:
        return FlextResult[dict[str, object]].fail(f"Ecosystem CLI setup failed: {e}")


# Migration helpers for existing ecosystem projects
def migrate_to_modern_patterns(old_setup_function: str, project_name: str) -> str:
    """Generate migration code from old patterns to modern foundation patterns.

    This function helps ecosystem projects migrate from old CLI patterns to
    modern foundation patterns following docs/patterns/foundation-refactored.md.

    Args:
      old_setup_function: Name of existing setup function
      project_name: Project name for specific migration

    Returns:
      str: Migration code example

    """
    return f"""\
# MIGRATION: {project_name} - Old to Modern FlextCli Patterns
#
# OLD (Previous Pattern): 30+ lines of boilerplate
# def {old_setup_function}():
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

def {old_setup_function}_modern(**config_overrides):
    "Modern setup with railway-oriented programming following FlextCli patterns."
    return setup_flext_cli_ecosystem("{project_name}", **config_overrides)

# Usage in {project_name} project:
# result = {old_setup_function}_modern(debug=True, environment="prod")
# if result.is_success:
#     print("Setup completed successfully!")
#     context = result.value
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
#         return FlextResult[None].ok({{
#             "project": "{project_name}",
#             "field": self.project_specific_field,
#             "executed": True
#         }})
"""


__all__ = [
    "FlextCliConfigFactory",
    "FlextCliGenericCommand",
    "migrate_to_modern_patterns",
    "setup_flext_cli_ecosystem",
]
