"""Tests for ecosystem_integration.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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
                return FlextResult[object].ok({
                    "executed": self.name,
                    "my_field": self.my_field,
                    "custom": True,
                })

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

    @patch("flext_cli.ecosystem_integration.create_flext_cli_config")
    def test_create_project_config_basic(self, mock_create_config: MagicMock) -> None:
        """Test creating basic project configuration."""
        mock_config = FlextCliConfig(debug=False)
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(mock_config)

        result = FlextCliConfigFactory.create_project_config("test-project")

        assert result.is_success
        config = result.value
        assert config.debug is False  # Verify we get the expected config

        # Check that defaults were applied
        mock_create_config.assert_called_once_with(
            project_name="test-project", environment="development", debug=False
        )

    @patch("flext_cli.ecosystem_integration.create_flext_cli_config")
    def test_create_project_config_with_overrides(
        self, mock_create_config: MagicMock
    ) -> None:
        """Test creating config with overrides."""
        mock_config = FlextCliConfig(debug=True)
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(mock_config)

        result = FlextCliConfigFactory.create_project_config(
            "production-project",
            environment="production",
            debug=True,
            custom_field="custom_value",
        )

        assert result.is_success
        config = result.value
        assert config.debug is True  # Verify override worked

        # Verify the call included all parameters
        mock_create_config.assert_called_once_with(
            project_name="production-project",
            environment="production",
            debug=True,
            custom_field="custom_value",
        )

    @patch("flext_cli.ecosystem_integration.create_flext_cli_config")
    def test_create_project_config_failure(self, mock_create_config: MagicMock) -> None:
        """Test handling config creation failure."""
        mock_create_config.return_value = FlextResult[FlextCliConfig].fail(
            "Config creation failed"
        )

        result = FlextCliConfigFactory.create_project_config("failing-project")

        assert result.is_failure
        assert "Config creation failed" in result.error

    @patch("flext_cli.ecosystem_integration.create_flext_cli_config")
    def test_config_defaults_override_priority(
        self, mock_create_config: MagicMock
    ) -> None:
        """Test that overrides take priority over defaults."""
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(
            FlextCliConfig()
        )

        # Override default values
        FlextCliConfigFactory.create_project_config(
            "override-test",
            environment="staging",  # Override default "development"
            debug=True,  # Override default False
            extra_setting="extra",  # Additional setting
        )

        # Verify that overrides were merged correctly
        expected_call = {
            "project_name": "override-test",
            "environment": "staging",  # Overridden
            "debug": True,  # Overridden
            "extra_setting": "extra",  # Added
        }

        mock_create_config.assert_called_once_with(**expected_call)


class TestSetupFlextCliEcosystem:
    """Test setup_flext_cli_ecosystem function."""

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    @patch.object(FlextCliConfigFactory, "create_project_config")
    def test_setup_ecosystem_success(
        self, mock_create_config: MagicMock, mock_setup_cli: MagicMock
    ) -> None:
        """Test successful ecosystem setup."""
        # Mock configuration creation
        mock_config = FlextCliConfig()
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(mock_config)

        # Mock CLI setup
        mock_setup_cli.return_value = FlextResult[bool].ok(data=True)

        result = setup_flext_cli_ecosystem("test-ecosystem")

        assert result.is_success
        data = result.value
        assert data["project"] == "test-ecosystem"
        assert data["setup"] is True
        assert "config" in data

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    def test_setup_ecosystem_with_provided_config(
        self, mock_setup_cli: MagicMock
    ) -> None:
        """Test setup with pre-created configuration."""
        config = FlextCliConfig()
        mock_setup_cli.return_value = FlextResult[bool].ok(data=True)

        result = setup_flext_cli_ecosystem("preconfigured-project", config=config)

        assert result.is_success
        data = result.value
        assert data["project"] == "preconfigured-project"

        # Verify setup_cli was called with provided config
        mock_setup_cli.assert_called_once_with(config)

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    @patch.object(FlextCliConfigFactory, "create_project_config")
    def test_setup_ecosystem_config_creation_failure(
        self, mock_create_config: MagicMock, mock_setup_cli: MagicMock
    ) -> None:
        """Test handling of config creation failure."""
        mock_create_config.return_value = FlextResult[FlextCliConfig].fail(
            "Configuration failed"
        )

        result = setup_flext_cli_ecosystem("failing-project")

        assert result.is_failure
        assert "Config creation failed" in result.error

        # CLI setup should not be called if config creation fails
        mock_setup_cli.assert_not_called()

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    @patch.object(FlextCliConfigFactory, "create_project_config")
    def test_setup_ecosystem_cli_setup_failure(
        self, mock_create_config: MagicMock, mock_setup_cli: MagicMock
    ) -> None:
        """Test handling of CLI setup failure."""
        # Config creation succeeds
        mock_config = FlextCliConfig()
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(mock_config)

        # CLI setup fails
        mock_setup_cli.return_value = FlextResult[bool].fail("CLI setup error")

        result = setup_flext_cli_ecosystem("setup-fail")

        assert result.is_failure
        assert "CLI setup failed" in result.error

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    @patch.object(FlextCliConfigFactory, "create_project_config")
    def test_setup_ecosystem_with_overrides(
        self, mock_create_config: MagicMock, mock_setup_cli: MagicMock
    ) -> None:
        """Test setup with configuration overrides."""
        mock_config = FlextCliConfig(debug=True)
        mock_create_config.return_value = FlextResult[FlextCliConfig].ok(mock_config)
        mock_setup_cli.return_value = FlextResult[bool].ok(data=True)

        result = setup_flext_cli_ecosystem(
            "override-ecosystem",
            environment="production",
            debug=True,
            custom_setting="value",
        )

        assert result.is_success

        # Verify config factory was called with overrides
        mock_create_config.assert_called_once_with(
            project_name="override-ecosystem",
            environment="production",
            debug=True,
            custom_setting="value",
        )

    @patch("flext_cli.ecosystem_integration.setup_flext_cli")
    @patch.object(FlextCliConfigFactory, "create_project_config")
    def test_setup_ecosystem_exception_handling(
        self, mock_create_config: MagicMock, mock_setup_cli: MagicMock
    ) -> None:
        """Test exception handling in setup function."""
        # Make config creation raise an exception
        mock_create_config.side_effect = RuntimeError("Unexpected error")

        result = setup_flext_cli_ecosystem("exception-project")

        assert result.is_failure
        assert "Ecosystem CLI setup failed" in result.error
        assert "Unexpected error" in result.error


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
