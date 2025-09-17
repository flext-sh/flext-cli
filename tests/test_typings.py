"""Tests for typings.py centralized typings to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import typings
from flext_core import FlextTypes as CoreFlextTypes


class TestTypingsImports:
    """Test that all typing imports work correctly."""

    def test_flext_types_import(self) -> None:
        """Test FlextTypes class import."""
        assert hasattr(typings, "FlextTypes")
        assert typings.FlextTypes is not None
        assert isinstance(typings.FlextTypes, type)

    def test_type_variables_import(self) -> None:
        """Test type variable imports."""
        type_vars = ["E", "F", "P", "R", "T", "U", "V"]

        for type_var in type_vars:
            assert hasattr(typings, type_var)
            assert getattr(typings, type_var) is not None

    def test_flext_types_inheritance(self) -> None:
        """Test that FlextTypes inherits from CoreFlextTypes."""
        assert issubclass(typings.FlextTypes, CoreFlextTypes)

    def test_flext_types_instantiation(self) -> None:
        """Test that FlextTypes can be instantiated."""
        # Should be able to create an instance
        instance = typings.FlextTypes()
        assert instance is not None


class TestAllExports:
    """Test module __all__ exports."""

    def test_all_exports_exist(self) -> None:
        """Test that all declared exports exist."""
        for export_name in typings.__all__:
            assert hasattr(typings, export_name), f"Export {export_name} not found"

    def test_all_exports_count(self) -> None:
        """Test minimum number of exports."""
        assert len(typings.__all__) >= 8, (
            f"Expected at least 8 exports, got {len(typings.__all__)}"
        )

    def test_expected_exports(self) -> None:
        """Test that expected exports are present."""
        expected_minimum = {"E", "F", "FlextTypes", "P", "R", "T", "U", "V"}
        actual = set(typings.__all__)
        assert expected_minimum.issubset(actual), (
            f"Missing exports: {expected_minimum - actual}"
        )


class TestModuleStructure:
    """Test module structure."""

    def test_module_docstring(self) -> None:
        """Test module has proper docstring."""
        assert typings.__doc__ is not None
        assert "Centralized typings" in typings.__doc__
