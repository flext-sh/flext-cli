"""Tests for ecosystem_integration.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.ecosystem_integration import (
    FlextCliConfigFactory,
    FlextCliGenericCommand,
    migrate_to_modern_patterns,
    setup_flext_cli_ecosystem,
)
from flext_cli.foundation import FlextCliConfig


class TestFlextCliGenericCommand:
    """Test FlextCliGenericCommand class."""

    def test_create_generic_command(self) -> None:
        """Test creating a generic command."""
        command = FlextCliGenericCommand(
            id="test-id",
            name="test-command",
            description="Test command",
        )

        assert command.name == "test-command"
        assert command.description == "Test command"
        assert command.environment == "default"
        assert command.config_data == {}

    def test_create_command_with_environment(self) -> None:
        """Test creating command with custom environment."""
        command = FlextCliGenericCommand(
            id="test-id",
            name="prod-command",
            description="Production command",
            environment="production",
        )

        assert command.environment == "production"

    def test_execute_generic_command(self) -> None:
        """Test executing a generic command."""
        command = FlextCliGenericCommand(
            id="test-id",
            name="execute-test",
            description="Execution test",
            environment="test",
        )

        result = command.execute()

        assert result.is_success
        data = result.value
        assert isinstance(data, dict)
        assert data["command"] == "execute-test"
        assert data["environment"] == "test"
        assert data["config"] == {}
        assert data["status"] == "completed"

    def test_execute_command_with_config_data(self) -> None:
        """Test executing command with config data."""
        # Create a command and modify class variable temporarily
        original_config = FlextCliGenericCommand.config_data
        FlextCliGenericCommand.config_data = {"setting": "value", "enabled": True}

        try:
            command = FlextCliGenericCommand(
                id="config-test-id",
                name="config-command",
                description="Command with config",
            )

            result = command.execute()
            assert result.is_success

            data = result.value
            assert data["config"] == {"setting": "value", "enabled": True}
        finally:
            # Restore original config
            FlextCliGenericCommand.config_data = original_config

    def test_command_inheritance_pattern(self) -> None:
        """Test command inheritance pattern as documented."""

        class ProjectSpecificCommand(FlextCliGenericCommand):
            """Example of project-specific command extension."""

            my_field: str = "project_value"

            def execute(self) -> FlextResult[object]:
                return FlextResult[object].ok(
                    {
                        "executed": self.name,
                        "my_field": self.my_field,
                        "custom": True,
                    }
                )

        command = ProjectSpecificCommand(
            id="project-id", name="project-command", description="Project command"
        )

        result = command.execute()
        assert result.is_success

        data = result.value
        assert data["executed"] == "project-command"
        assert data["my_field"] == "project_value"
        assert data["custom"] is True


class TestFlextCliConfigFactory:
    """Test FlextCliConfigFactory class."""

    def test_create_project_config_basic(self) -> None:
        """Test creating basic project configuration with real functionality."""
        result = FlextCliConfigFactory.create_project_config("test-project")

        assert result.is_success
        config = result.value
        assert config.debug is False  # Default value
        assert config.profile == "default"  # Default value
        assert config.output_format == "table"  # Default value

    def test_create_project_config_with_overrides(self) -> None:
        """Test creating config with overrides using real functionality."""
        result = FlextCliConfigFactory.create_project_config(
            "production-project",
            environment="production",
            debug=True,
        )

        assert result.is_success
        config = result.value
        assert config.debug is True  # Verify override worked
        assert config.profile == "default"  # Default still applies

    def test_create_project_config_validation(self) -> None:
        """Test config creation with validation."""
        # Test that the factory creates valid configurations
        result = FlextCliConfigFactory.create_project_config(
            "validation-test",
            debug=False,
            profile="test"
        )

        assert result.is_success
        config = result.value
        assert isinstance(config, FlextCliConfig)
        assert config.profile == "test"

    def test_config_defaults_override_priority(self) -> None:
        """Test that overrides take priority over defaults using real functionality."""
        # Test default values
        result_default = FlextCliConfigFactory.create_project_config("default-test")
        assert result_default.is_success
        config_default = result_default.value
        assert config_default.debug is False  # Default

        # Test overrides
        result_override = FlextCliConfigFactory.create_project_config(
            "override-test",
            debug=True,  # Override default False
        )
        assert result_override.is_success
        config_override = result_override.value
        assert config_override.debug is True  # Overridden


class TestSetupFlextCliEcosystem:
    """Test setup_flext_cli_ecosystem function."""

    def test_setup_ecosystem_success(self) -> None:
        """Test successful ecosystem setup with real functionality."""
        # Import here to ensure module is loaded for coverage
        from flext_cli.ecosystem_integration import setup_flext_cli_ecosystem
        
        result = setup_flext_cli_ecosystem("test-ecosystem")

        assert result.is_success
        data = result.value
        assert data["project"] == "test-ecosystem"
        assert data["setup"] is True
        assert "config" in data
        assert isinstance(data["config"], dict)

    def test_setup_ecosystem_with_provided_config(self) -> None:
        """Test setup with pre-created configuration using real functionality."""
        config = FlextCliConfig(debug=True, profile="test")

        result = setup_flext_cli_ecosystem("preconfigured-project", config=config)

        assert result.is_success
        data = result.value
        assert data["project"] == "preconfigured-project"
        assert data["config"]["debug"] is True
        assert data["config"]["profile"] == "test"

    def test_setup_ecosystem_with_overrides(self) -> None:
        """Test setup with configuration overrides using real functionality."""
        result = setup_flext_cli_ecosystem(
            "override-ecosystem",
            debug=True,
        )

        assert result.is_success
        data = result.value
        assert data["project"] == "override-ecosystem"
        assert data["config"]["debug"] is True

    def test_setup_ecosystem_multiple_projects(self) -> None:
        """Test setup with multiple different project configurations."""
        # Test first project
        result1 = setup_flext_cli_ecosystem("project1", debug=False)
        assert result1.is_success
        assert result1.value["project"] == "project1"
        
        # Test second project with different config
        result2 = setup_flext_cli_ecosystem("project2", debug=True)
        assert result2.is_success
        assert result2.value["project"] == "project2"
        assert result2.value["config"]["debug"] is True




class TestMigrateToModernPatterns:
    """Test migrate_to_modern_patterns function."""

    def test_migrate_basic_function(self) -> None:
        """Test migration code generation for basic function."""
        migration_code = migrate_to_modern_patterns("old_setup_cli", "test-project")

        assert isinstance(migration_code, str)
        assert "old_setup_cli" in migration_code
        assert "test-project" in migration_code
        assert "from flext_cli import setup_flext_cli_ecosystem" in migration_code
        assert "old_setup_cli_modern" in migration_code

    def test_migrate_complex_project_name(self) -> None:
        """Test migration with complex project name."""
        migration_code = migrate_to_modern_patterns(
            "complex_legacy_setup", "multi-word-project-name"
        )

        assert "complex_legacy_setup" in migration_code
        assert "multi-word-project-name" in migration_code
        assert "def complex_legacy_setup_modern" in migration_code
        assert "MultiWordProjectNameCommand" in migration_code

    def test_migrate_includes_usage_examples(self) -> None:
        """Test that migration includes usage examples."""
        migration_code = migrate_to_modern_patterns("setup_app", "my-app")

        # Check for various usage examples
        assert "Usage in my-app project:" in migration_code
        assert "result = setup_app_modern(debug=True" in migration_code
        assert "if result.is_success:" in migration_code
        assert 'print(f"Setup failed: {result.error}")' in migration_code

    def test_migrate_includes_custom_command_example(self) -> None:
        """Test migration includes custom command patterns."""
        migration_code = migrate_to_modern_patterns("init_project", "data-loader")

        assert "class DataLoaderCommand(FlextCliGenericCommand)" in migration_code
        assert "project_specific_field: str" in migration_code
        assert "def execute(self) -> FlextResult[dict[str, object]]" in migration_code
        assert '"project": "data-loader"' in migration_code

    def test_migrate_shows_code_reduction(self) -> None:
        """Test migration highlights code reduction benefits."""
        migration_code = migrate_to_modern_patterns("old_function", "efficiency-test")

        assert "OLD (Previous Pattern): 30+ lines of boilerplate" in migration_code
        assert (
            "NEW (Modern FlextCli Pattern): 3 lines - 90% reduction!" in migration_code
        )
        assert "Modern setup with railway-oriented programming" in migration_code

    def test_migrate_preserves_function_naming(self) -> None:
        """Test that function naming is preserved correctly."""
        test_cases = [
            ("camelCaseFunction", "test-project"),
            ("snake_case_function", "snake-case-project"),
            ("PascalCaseFunction", "PascalCase-Project"),
            ("simple", "simple"),
        ]

        for old_func, project in test_cases:
            migration_code = migrate_to_modern_patterns(old_func, project)
            assert f"def {old_func}_modern(" in migration_code
            assert f"def {old_func}():" in migration_code  # In comment
            assert f'"{project}"' in migration_code
