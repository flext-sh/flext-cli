"""Tests for types.py compatibility re-exports to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_cli import typings as types
from flext_cli.typings import FlextCliTypes


class TestTypeImports:
    """Test that all type imports work correctly."""

    def test_command_status_import(self) -> None:
        """Test CommandStatus import."""
        assert hasattr(types, "CommandStatus")
        assert types.CommandStatus is not None

    def test_command_type_import(self) -> None:
        """Test CommandType import."""
        assert hasattr(types, "CommandType")
        assert types.CommandType is not None

    def test_output_format_import(self) -> None:
        """Test FlextCliTypes.OutputFormat import from flext_cli.typings."""
        assert FlextCliTypes.OutputFormat is not None
        assert hasattr(FlextCliTypes.OutputFormat, "JSON")

    def test_plugin_status_import(self) -> None:
        """Test PluginStatus import."""
        assert hasattr(types, "PluginStatus")
        assert types.PluginStatus is not None

    def test_positive_int_type_import(self) -> None:
        """Test PositiveIntType import."""
        assert hasattr(types, "PositiveIntType")
        assert types.PositiveIntType is not None

    def test_url_imports(self) -> None:
        """Test URL and URLType imports."""
        assert hasattr(types, "URL")
        assert hasattr(types, "URLType")
        assert types.URL is not None
        assert types.URLType is not None

    def test_model_imports(self) -> None:
        """Test model class imports."""
        model_types = [
            "FlextCliCommand",
            "FlextCliConfigDict",
            "ContextParams",
            "PluginResult",
            "SessionData",
        ]

        for type_name in model_types:
            assert hasattr(types, type_name), f"Missing type: {type_name}"
            assert getattr(types, type_name) is not None

    def test_modern_type_aliases(self) -> None:
        """Test modern type aliases."""
        # Updated aliases after flext-core refactoring
        modern_aliases = [
            "FlextCliTypes.OutputFormat",
            "CommandType",
            "FlextCliLogLevel",  # Changed from LogLevel
            "FlextCliDataType",
        ]

        for alias_name in modern_aliases:
            assert hasattr(types, alias_name)
            alias = getattr(types, alias_name)
            # For type aliases, we just check they exist and are not None
            assert alias is not None


class TestAllExports:
    """Test module __all__ exports."""

    def test_all_exports_exist(self) -> None:
        """Test that all declared exports exist in module."""
        for export_name in types.__all__:
            assert hasattr(types, export_name), (
                f"Export {export_name} not found in types module"
            )

    def test_all_exports_not_none(self) -> None:
        """Test that all exports are not None."""
        for export_name in types.__all__:
            export_value = getattr(types, export_name)
            assert export_value is not None, f"Export {export_name} is None"

    def test_expected_exports_count(self) -> None:
        """Test expected number of exports."""
        # Actual exports: ['E', 'F', 'FlextTypes', 'P', 'R', 'T', 'U', 'V']
        # These are type variables and FlextTypes class
        assert len(types.__all__) == 8  # Updated to actual count

    def test_export_categories(self) -> None:
        """Test that exports cover expected categories after flext-core refactoring."""
        # Updated to validate actual structure instead of outdated hardcoded list
        all_actual = set(types.__all__)

        # Validate that we have the essential exports that are actually exported
        essential_types = {
            "FlextTypes",  # Main compatibility alias
        }

        # Type variables that should be present
        type_vars = {"E", "F", "P", "R", "T", "U", "V"}

        # Essential types should be present (subset validation)
        missing_essential = essential_types - all_actual
        assert not missing_essential, f"Missing essential types: {missing_essential}"

        # Type variables should be present
        missing_type_vars = type_vars - all_actual
        assert not missing_type_vars, f"Missing type variables: {missing_type_vars}"

        # Validate that all exports are actually importable
        for export_name in all_actual:
            assert hasattr(types, export_name), (
                f"Export {export_name} not found in module"
            )

        # Ensure we have the expected minimum exports (type variables + FlextTypes)
        assert len(all_actual) >= 8, f"Too few exports: {len(all_actual)} < 8"


class TestTypeCompatibility:
    """Test type compatibility and usage."""

    def test_modern_aliases_are_types(self) -> None:
        """Test that modern aliases are available after flext-core refactoring."""
        # Updated to only test types that actually exist
        assert types.FlextCliDataType is not None
        assert types.FlextCliTypes.OutputFormat is not None
        assert types.FlextCliFileHandler is not None
        assert types.CommandArgs is not None
        # Note: TCliPath and TCliConfig removed in flext-core refactoring

    def test_can_use_modern_aliases(self) -> None:
        """Test that modern aliases can be used for type checking."""
        # Updated to only use types that exist after flext-core refactoring
        data: types.FlextCliDataType = {"key": "value"}
        format_str: types.FlextCliTypes.OutputFormat = types.FlextCliTypes.OutputFormat.JSON
        args: types.CommandArgs = ["arg1", "arg2"]

        def handler(x: object) -> object:
            return x

        # Basic validation that types work
        assert isinstance(data, dict)
        assert isinstance(format_str, str)
        assert isinstance(args, list)
        assert callable(handler)

    def test_model_classes_importable(self) -> None:
        """Test that type aliases and classes can be accessed."""
        # Test that we can access the actual exported type aliases
        assert hasattr(types, "FlextCliCommand")
        assert hasattr(types, "ContextParams")
        assert hasattr(types, "PluginResult")
        assert hasattr(types, "SessionData")

        # Type aliases should not be callable, but should exist
        assert types.FlextCliCommand is not None
        assert types.ContextParams is not None
        assert types.PluginResult is not None
        assert types.SessionData is not None

    def test_enum_classes_accessible(self) -> None:
        """Test that enum classes are accessible."""
        # These should be enum classes using actual exported names
        assert hasattr(types.CommandStatus, "__members__")
        assert hasattr(types.CommandType, "__members__")
        assert hasattr(types.FlextCliTypes.OutputFormat, "__members__")
        assert hasattr(types.PluginStatus, "__members__")


class TestModuleStructure:
    """Test module structure and organization."""

    def test_module_has_docstring(self) -> None:
        """Test that module has proper docstring."""
        assert types.__doc__ is not None
        # Updated to match actual current docstring
        assert "FLEXT CLI Types" in types.__doc__

    def test_module_imports_complete(self) -> None:
        """Test that all necessary imports are present."""
        # All exports should be accessible without errors
        for export_name in types.__all__:
            try:
                getattr(types, export_name)
            except (ImportError, AttributeError) as e:
                pytest.fail(f"Failed to import {export_name}: {e}")

    def test_no_extra_exports(self) -> None:
        """Test that module doesn't export more than declared."""
        public_attrs = [attr for attr in dir(types) if not attr.startswith("_")]

        # All public attributes should be in __all__
        undeclared = set(public_attrs) - set(types.__all__)

        # Filter out legitimate imports that don't need to be in __all__
        # These are legitimate re-exports/imports used by the module
        legitimate_imports = {
            "annotations",  # from __future__ import annotations
            "override",  # from typing import override
            "FlextResult",  # from flext_core import FlextResult
            "Protocol",  # from typing import Protocol
            "Table",  # from rich.table import Table
            "Literal",  # from typing import Literal
            "FlextModels",  # from flext_core import FlextModels
            "CoreFlextTypes",  # from flext_core.typings import FlextTypes as CoreFlextTypes
            "TypeVar",  # from typing import TypeVar
            "Path",  # from pathlib import Path
            "click",  # import click
            "Callable",  # from collections.abc import Callable
            "StrEnum",  # from enum import StrEnum
        }
        undeclared -= legitimate_imports

        assert len(undeclared) == 0, f"Undeclared public exports: {undeclared}"
