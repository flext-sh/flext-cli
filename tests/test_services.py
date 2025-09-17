"""Test FlextCliServices functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.services import FlextCliServices
from flext_core import FlextResult


class TestFlextCliServices:
    """Test FlextCliServices with direct flext-core usage."""

    def test_create_command_processor(self) -> None:
        """Test command processor creation."""
        result = FlextCliServices.create_command_processor()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "Command processor created successfully"

    def test_create_session_processor(self) -> None:
        """Test session processor creation."""
        result = FlextCliServices.create_session_processor()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "Session processor created successfully"

    def test_create_config_processor(self) -> None:
        """Test config processor creation."""
        result = FlextCliServices.create_config_processor()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "Config processor created successfully"

    def test_services_class_attributes(self) -> None:
        """Test that services class has expected attributes."""
        assert hasattr(FlextCliServices, "registry")
        assert hasattr(FlextCliServices, "orchestrator")
        assert hasattr(FlextCliServices, "metrics")

    def test_all_methods_return_flext_result(self) -> None:
        """Test that all service methods return FlextResult."""
        methods = [
            FlextCliServices.create_command_processor,
            FlextCliServices.create_session_processor,
            FlextCliServices.create_config_processor,
        ]

        for method in methods:
            result = method()
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert isinstance(result.value, str)
