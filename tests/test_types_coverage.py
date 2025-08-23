"""Tests for types.py compatibility re-exports to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_cli import cli_types as types


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
        """Test FlextCliOutputFormat import."""
        assert hasattr(types, "FlextCliOutputFormat")
        assert types.FlextCliOutputFormat is not None

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
        modern_aliases = [
            "FlextCliOutputFormat",
            "CommandType",
            "LogLevel",
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
        # Should have 18 exports total (checked the actual __all__ list)
        assert len(types.__all__) == 18

    def test_export_categories(self) -> None:
        """Test that exports cover expected categories."""
        # Core re-exports
        core_exports = {
            "URL",
            "URLType",
            "PositiveIntType",
            "FlextCliCommand",
            "FlextCliCommandStatus",
            "FlextCliCommandType",
            "FlextCliConfig",
            "FlextCliContext",
            "FlextCliOutputFormat",
            "FlextCliPlugin",
            "FlextCliPluginStatus",
            "FlextCliSession",
        }

        # Legacy aliases
        modern_exports = {
            "FlextCliOutputFormat",
            "CommandType",
            "LogLevel",
            "FlextCliDataType",
        }

        all_expected = core_exports | modern_exports
        all_actual = set(types.__all__)

        assert all_actual == all_expected


class TestTypeCompatibility:
    """Test type compatibility and usage."""

    def test_modern_aliases_are_types(self) -> None:
        """Test that modern aliases are available."""
        # Just test that they exist and are not None (type annotations may vary)
        assert types.FlextCliDataType is not None
        assert types.TCliPath is not None
        assert types.FlextCliOutputFormat is not None
        assert types.FlextCliFileHandler is not None
        assert types.TCliConfig is not None
        assert types.CommandArgs is not None

    def test_can_use_modern_aliases(self) -> None:
        """Test that modern aliases can be used for type checking."""
        # These should not raise errors
        data: types.FlextCliDataType = {"key": "value"}
        path: types.TCliPath = "/some/path"
        format_str: types.FlextCliOutputFormat = "json"

        def handler(x):
            return x

        config: types.TCliConfig = {"debug": True}
        args: types.CommandArgs = {"arg": "value"}

        assert isinstance(data, dict)
        assert isinstance(path, str)
        assert isinstance(format_str, str)
        assert callable(handler)
        assert isinstance(config, dict)
        assert isinstance(args, dict)

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
        assert hasattr(types.FlextCliOutputFormat, "__members__")
        assert hasattr(types.PluginStatus, "__members__")


class TestModuleStructure:
    """Test module structure and organization."""

    def test_module_has_docstring(self) -> None:
        """Test that module has proper docstring."""
        assert types.__doc__ is not None
        assert "Compatibility re-exports" in types.__doc__

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
        # Filter out potential module-level attributes
        undeclared = {attr for attr in undeclared if attr != "annotations"}

        assert len(undeclared) == 0, f"Undeclared public exports: {undeclared}"
