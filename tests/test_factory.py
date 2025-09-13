"""Test FlextCliFactory functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.factory import FlextCliFactory


class TestFlextCliFactory:
    """Test FlextCliFactory with direct flext-core usage."""

    def test_create_auth_service(self) -> None:
        """Test auth service creation."""
        result = FlextCliFactory.create_auth_service()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, "authenticate_user")
        assert hasattr(result.value, "login")

    def test_create_api_client(self) -> None:
        """Test API client creation."""
        result = FlextCliFactory.create_api_client()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, "base_url")
        assert hasattr(result.value, "timeout")

    def test_create_default_auth_service(self) -> None:
        """Test default auth service creation."""
        result = FlextCliFactory.create_default_auth_service()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, "authenticate_user")
        assert hasattr(result.value, "login")

    def test_factory_methods_return_flext_result(self) -> None:
        """Test that all factory methods return FlextResult."""
        methods = [
            FlextCliFactory.create_auth_service,
            FlextCliFactory.create_api_client,
            FlextCliFactory.create_default_auth_service,
        ]

        for method in methods:
            result = method()
            assert isinstance(result, FlextResult)
            assert result.is_success
