"""Test flext_cli.__init__ module imports and unified class patterns.

Tests the main module imports following FLEXT unified class patterns.
NO legacy aliases, wrappers, or compatibility functions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

import flext_cli
from flext_cli import (
    FlextCliApi,
    FlextCliAuth,
    FlextCliConstants,
    FlextCliFormatters,
    FlextCliModels,
)
from flext_core import FlextResult


class TestFlextCliImports:
    """Test flext_cli module imports following unified class patterns."""

    def test_core_classes_importable(self) -> None:
        """Test that core unified classes are importable."""
        # Test that all main classes can be imported and instantiated
        api = FlextCliApi()
        auth = FlextCliAuth()
        config = FlextCliModels.FlextCliConfig()
        formatters = FlextCliFormatters()

        assert api is not None
        assert auth is not None
        assert config is not None
        assert formatters is not None

    def test_flext_result_available(self) -> None:
        """Test FlextResult is available from flext_cli."""
        # Test creating FlextResult instances
        success_result = FlextResult[str].ok("test")
        failure_result = FlextResult[str].fail("test error")

        assert success_result.is_success
        assert failure_result.is_failure

    def test_constants_available(self) -> None:
        """Test FlextCliConstants is available."""
        assert hasattr(FlextCliConstants, "HTTP")
        assert hasattr(FlextCliConstants, "TIMEOUTS")

    def test_models_available(self) -> None:
        """Test FlextCliModels is available with nested classes."""
        assert hasattr(FlextCliModels, "Pipeline")
        assert hasattr(FlextCliModels, "PipelineConfig")
        assert hasattr(FlextCliModels, "CliCommand")

    def test_unified_class_pattern_compliance(self) -> None:
        """Test that classes follow unified class pattern."""
        # All classes should be instantiable
        classes_to_test = [
            FlextCliApi,
            FlextCliAuth,
            FlextCliModels.FlextCliConfig,
            FlextCliFormatters,
        ]

        for cls in classes_to_test:
            instance = cls()
            assert instance is not None
            # Should have validate_business_rules method (unified pattern)
            if hasattr(instance, "validate_business_rules"):
                result = instance.validate_business_rules()
                assert isinstance(result, FlextResult)

    def test_no_legacy_functions_available(self) -> None:
        """Test that legacy functions are NOT available (compliance check)."""
        # These legacy patterns should NOT exist
        legacy_functions = [
            "get_auth_headers",
            "save_auth_token",
            "require_auth",
            "handle_service_result",  # Should be class method only
        ]

        for func_name in legacy_functions:
            assert not hasattr(flext_cli, func_name), (
                f"Legacy function {func_name} should not be available"
            )

    def test_version_info_available(self) -> None:
        """Test version information is available."""
        assert hasattr(flext_cli, "__version__")
        assert hasattr(flext_cli, "__author__")
        assert isinstance(flext_cli.__version__, str)


class TestFlextCliAuth:
    """Test FlextCliAuth unified class methods."""

    def setup_method(self) -> None:
        """Set up auth service for each test."""
        self.auth_service = FlextCliAuth()

    def test_auth_service_creation(self) -> None:
        """Test auth service can be created."""
        assert self.auth_service is not None

    def test_auth_service_has_required_methods(self) -> None:
        """Test auth service has required methods."""
        # Test that auth service has the expected methods
        assert hasattr(self.auth_service, "authenticate_user")
        assert hasattr(self.auth_service, "login")
        assert hasattr(self.auth_service, "validate_business_rules")

    def test_auth_service_business_rules_validation(self) -> None:
        """Test auth service business rules validation."""
        result = self.auth_service.validate_business_rules()
        assert isinstance(result, FlextResult)


class TestFlextCliApi:
    """Test FlextCliApi unified class methods."""

    def setup_method(self) -> None:
        """Set up API service for each test."""
        self.api_service = FlextCliApi()

    def test_api_service_creation(self) -> None:
        """Test API service can be created."""
        assert self.api_service is not None

    def test_api_service_has_required_methods(self) -> None:
        """Test API service has expected methods."""
        assert hasattr(self.api_service, "format_output")
        assert hasattr(self.api_service, "display_output")

    def test_api_service_format_output(self) -> None:
        """Test API service format_output method."""
        test_data = {"key": "value", "number": 123}
        result = self.api_service.format_output(test_data, "json")

        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)
            assert "key" in formatted
            assert "value" in formatted


if __name__ == "__main__":
    pytest.main([__file__])
