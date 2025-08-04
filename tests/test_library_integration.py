"""Integration tests for FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

import click
import flext_cli
from flext_core.result import FlextResult


class TestLibraryImports:
    """Test library imports and public API."""

    def test_library_version(self) -> None:
        """Test library version is accessible."""
        assert hasattr(flext_cli, "__version__")
        assert isinstance(flext_cli.__version__, str)
        if flext_cli.__version__ != "0.9.0":
            raise AssertionError(f"Expected {'0.9.0'}, got {flext_cli.__version__}")

    def test_all_public_api_accessible(self) -> None:
        """Test all public API components are accessible."""
        # Core Domain Entities
        assert hasattr(flext_cli, "CLICommand")
        assert hasattr(flext_cli, "CLIPlugin")
        assert hasattr(flext_cli, "CLISession")
        assert hasattr(flext_cli, "CommandStatus")
        assert hasattr(flext_cli, "CommandType")

        # Configuration
        assert hasattr(flext_cli, "CLIConfig")
        assert hasattr(flext_cli, "CLISettings")
        assert hasattr(flext_cli, "get_config")
        assert hasattr(flext_cli, "get_settings")

        # Core Utilities
        assert hasattr(flext_cli, "CLIContext")
        assert hasattr(flext_cli, "CLIHelper")
        assert hasattr(flext_cli, "handle_service_result")
        assert hasattr(flext_cli, "setup_cli")

        # Decorators
        assert hasattr(flext_cli, "async_command")
        assert hasattr(flext_cli, "confirm_action")
        assert hasattr(flext_cli, "measure_time")
        assert hasattr(flext_cli, "require_auth")
        assert hasattr(flext_cli, "retry")
        assert hasattr(flext_cli, "validate_config")
        assert hasattr(flext_cli, "with_spinner")

        # Types
        assert hasattr(flext_cli, "ClickPath")
        assert hasattr(flext_cli, "PositiveInt")
        assert hasattr(flext_cli, "URL")
        assert hasattr(flext_cli, "ExistingFile")
        assert hasattr(flext_cli, "ExistingDir")
        assert hasattr(flext_cli, "NewFile")

    def test_public_api_matches_all_export(self) -> None:
        """Test that __all__ matches actual public API."""
        for item in flext_cli.__all__:
            if not hasattr(flext_cli, item):
                raise AssertionError(f"Expected {item} in __all__ but not accessible")

    def test_entity_classes_instantiable(self) -> None:
        """Test that entity classes can be instantiated."""
        # CLICommand
        command = flext_cli.CLICommand(
            id="test_cmd_001",
            name="test",
            command_line="echo test",
        )
        if command.name != "test":
            raise AssertionError(f"Expected {'test'}, got {command.name}")

        # CLIPlugin
        plugin = flext_cli.CLIPlugin(
            id="test_plugin_001",
            name="test-plugin",
            entry_point="test.main",
        )
        if plugin.name != "test-plugin":
            raise AssertionError(f"Expected {'test-plugin'}, got {plugin.name}")

        # CLISession
        session = flext_cli.CLISession(id="test_session_001", session_id="test-session")
        if session.session_id != "test-session":
            raise AssertionError(f"Expected {'test-session'}, got {session.session_id}")

        # CLIContext
        context = flext_cli.CLIContext()
        if context.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {context.profile}")

    def test_configuration_classes_instantiable(self) -> None:
        """Test that configuration classes can be instantiated."""
        config = flext_cli.CLIConfig()
        if config.api_url != "http://localhost:8000":
            raise AssertionError(
                f"Expected {'http://localhost:8000'}, got {config.api_url}"
            )

        settings = flext_cli.CLISettings()
        if settings.project_name != "flext-cli":
            raise AssertionError(f"Expected {'flext-cli'}, got {settings.project_name}")

    def test_enums_accessible(self) -> None:
        """Test that enums are accessible and have expected values."""
        # CommandStatus
        if flext_cli.CommandStatus.PENDING != "pending":
            raise AssertionError(
                f"Expected {'pending'}, got {flext_cli.CommandStatus.PENDING}"
            )
        assert flext_cli.CommandStatus.RUNNING == "running"
        if flext_cli.CommandStatus.COMPLETED != "completed":
            raise AssertionError(
                f"Expected {'completed'}, got {flext_cli.CommandStatus.COMPLETED}"
            )
        assert flext_cli.CommandStatus.FAILED == "failed"
        if flext_cli.CommandStatus.CANCELLED != "cancelled":
            raise AssertionError(
                f"Expected {'cancelled'}, got {flext_cli.CommandStatus.CANCELLED}"
            )

        # CommandType
        if flext_cli.CommandType.SYSTEM != "system":
            raise AssertionError(
                f"Expected {'system'}, got {flext_cli.CommandType.SYSTEM}"
            )
        assert flext_cli.CommandType.PIPELINE == "pipeline"
        if flext_cli.CommandType.PLUGIN != "plugin":
            raise AssertionError(
                f"Expected {'plugin'}, got {flext_cli.CommandType.PLUGIN}"
            )
        assert flext_cli.CommandType.DATA == "data"
        if flext_cli.CommandType.CONFIG != "config":
            raise AssertionError(
                f"Expected {'config'}, got {flext_cli.CommandType.CONFIG}"
            )
        assert flext_cli.CommandType.AUTH == "auth"
        if flext_cli.CommandType.MONITORING != "monitoring":
            raise AssertionError(
                f"Expected {'monitoring'}, got {flext_cli.CommandType.MONITORING}"
            )

    def test_click_types_accessible(self) -> None:
        """Test that Click types are accessible and configured."""
        # PositiveInt
        assert hasattr(flext_cli.PositiveInt, "name")
        if flext_cli.PositiveInt.name != "positive_int":
            raise AssertionError(
                f"Expected {'positive_int'}, got {flext_cli.PositiveInt.name}"
            )

        # URL
        assert hasattr(flext_cli.URL, "name")
        if flext_cli.URL.name != "url":
            raise AssertionError(f"Expected {'url'}, got {flext_cli.URL.name}")

        # Path types
        if not (flext_cli.ExistingFile.exists):
            raise AssertionError(f"Expected True, got {flext_cli.ExistingFile.exists}")
        assert flext_cli.ExistingFile.file_okay is True
        if flext_cli.ExistingFile.dir_okay:
            raise AssertionError(
                f"Expected False, got {flext_cli.ExistingFile.dir_okay}"
            )
        if not (flext_cli.ExistingDir.exists):
            raise AssertionError(f"Expected True, got {flext_cli.ExistingDir.exists}")
        if flext_cli.ExistingDir.file_okay:
            raise AssertionError(
                f"Expected False, got {flext_cli.ExistingDir.file_okay}"
            )
        if not (flext_cli.ExistingDir.dir_okay):
            raise AssertionError(f"Expected True, got {flext_cli.ExistingDir.dir_okay}")


class TestLibraryFunctionality:
    """Test library functionality integration."""

    def test_config_functions_work(self) -> None:
        """Test configuration functions work correctly."""
        config = flext_cli.get_config()
        settings = flext_cli.get_settings()

        assert isinstance(config, flext_cli.CLIConfig)
        assert isinstance(settings, flext_cli.CLISettings)

    def test_setup_cli_function(self) -> None:
        """Test setup_cli function works."""
        result = flext_cli.setup_cli()
        assert isinstance(result, FlextResult)
        assert result.success

    def test_helper_class_instantiation(self) -> None:
        """Test helper class can be instantiated."""
        helper = flext_cli.CLIHelper()
        assert isinstance(helper, flext_cli.CLIHelper)

    def test_handle_service_result_decorator(self) -> None:
        """Test handle_service_result decorator works."""

        @flext_cli.handle_service_result
        def test_function() -> FlextResult[str]:
            return FlextResult.ok("test result")

        result = test_function()
        if result != "test result":
            raise AssertionError(f"Expected {'test result'}, got {result}")

    def test_decorator_functions_accessible(self) -> None:
        """Test that decorator functions are accessible and callable."""
        decorators = [
            flext_cli.async_command,
            flext_cli.confirm_action,
            flext_cli.measure_time,
            flext_cli.require_auth,
            flext_cli.retry,
            flext_cli.validate_config,
            flext_cli.with_spinner,
        ]

        for decorator in decorators:
            assert callable(decorator)


class TestLibraryCompatibility:
    """Test library compatibility with external libraries."""

    def test_pydantic_compatibility(self) -> None:
        """Test compatibility with Pydantic."""
        config = flext_cli.CLIConfig()

        # Should have Pydantic methods
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")

        # Should be able to dump to dict
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        if "api_url" not in config_dict:
            raise AssertionError(f"Expected {'api_url'} in {config_dict}")

    def test_click_compatibility(self) -> None:
        """Test compatibility with Click."""
        # Types should be Click types
        assert isinstance(flext_cli.PositiveInt, click.ParamType)
        assert isinstance(flext_cli.URL, click.ParamType)
        assert isinstance(flext_cli.ExistingFile, click.Path)

    def test_rich_compatibility(self) -> None:
        """Test compatibility with Rich (implicitly through Console usage)."""

        # This is tested implicitly through the handle_service_result decorator
        # which uses Rich Console internally
        @flext_cli.handle_service_result
        def test_function() -> str:
            return "test"

        result = test_function()
        if result != "test":
            raise AssertionError(f"Expected {'test'}, got {result}")

    def test_pathlib_compatibility(self) -> None:
        """Test compatibility with pathlib."""
        flext_cli.CLIConfig()

        # Directory fields should work with Path objects
        custom_path = Path("/custom/path")
        config_with_path = flext_cli.CLIConfig(config_dir=custom_path)
        if config_with_path.config_dir != custom_path:
            raise AssertionError(
                f"Expected {custom_path}, got {config_with_path.config_dir}"
            )


class TestLibraryDocumentation:
    """Test library documentation and metadata."""

    def test_module_docstring(self) -> None:
        """Test module has proper docstring."""
        assert flext_cli.__doc__ is not None
        if "FLEXT CLI Library" not in flext_cli.__doc__:
            raise AssertionError(
                f"Expected {'FLEXT CLI Library'} in {flext_cli.__doc__}"
            )
        assert "Command Line Interface Development Toolkit" in flext_cli.__doc__

    def test_classes_have_docstrings(self) -> None:
        """Test that main classes have docstrings."""
        classes_to_check = [
            flext_cli.CLICommand,
            flext_cli.CLIPlugin,
            flext_cli.CLISession,
            flext_cli.CLIConfig,
            flext_cli.CLISettings,
            flext_cli.CLIContext,
            flext_cli.CLIHelper,
        ]

        for cls in classes_to_check:
            assert cls.__doc__ is not None, f"{cls.__name__} missing docstring"
            assert len(cls.__doc__.strip()) > 0

    def test_functions_have_docstrings(self) -> None:
        """Test that main functions have docstrings."""
        functions_to_check = [
            flext_cli.get_config,
            flext_cli.get_settings,
            flext_cli.setup_cli,
            flext_cli.handle_service_result,
        ]

        for func in functions_to_check:
            assert func.__doc__ is not None, f"{func.__name__} missing docstring"
            assert len(func.__doc__.strip()) > 0


class TestLibraryPerformance:
    """Test library performance characteristics."""

    def test_import_time(self) -> None:
        """Test that library imports quickly."""
        start_time = time.time()
        importlib.reload(flext_cli)
        import_time = time.time() - start_time

        # Should import in less than 1 second
        assert import_time < 1.0, f"Import took {import_time:.2f}s, too slow"

    def test_memory_usage_reasonable(self) -> None:
        """Test that library doesn't consume excessive memory."""
        # Get memory usage before and after import
        # This is a basic check, not precise memory measurement
        modules_before = len(sys.modules)
        importlib.reload(flext_cli)
        modules_after = len(sys.modules)

        # Should not import an excessive number of modules
        new_modules = modules_after - modules_before
        assert new_modules < 50, f"Imported {new_modules} modules, might be too many"

    def test_entity_creation_performance(self) -> None:
        """Test that entity creation is reasonably fast."""
        start_time = time.time()
        for i in range(1000):
            flext_cli.CLICommand(
                id=f"test_cmd_{i:04d}", name="test", command_line="test"
            )
        creation_time = time.time() - start_time

        # Should create 1000 entities in less than 1 second
        assert creation_time < 1.0, (
            f"Entity creation took {creation_time:.2f}s for 1000 objects"
        )
