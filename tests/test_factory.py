"""Test FlextCli direct constructors functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.client import FlextCliClient as FlextApiClient


class TestFlextCliDirectConstructors:
    """Test FlextCli direct constructors following FLEXT patterns."""

    def test_create_auth_service(self) -> None:
        """Test auth service direct constructor."""
        auth_service = FlextCliAuth()

        assert auth_service is not None
        assert hasattr(auth_service, "authenticate_user")
        assert hasattr(auth_service, "login")

    def test_create_api_client(self) -> None:
        """Test API client direct constructor."""
        api_client = FlextApiClient()

        assert api_client is not None
        assert hasattr(api_client, "base_url")
        assert hasattr(api_client, "timeout")

    def test_auth_service_methods_return_flext_result(self) -> None:
        """Test that auth service methods return FlextResult."""
        auth_service = FlextCliAuth()

        # Test login method
        login_result = auth_service.login("test_user", "test_password")
        assert isinstance(login_result, FlextResult)

        # Test authenticate_user method
        auth_result = auth_service.authenticate_user("test_user", "test_password")
        assert isinstance(auth_result, FlextResult)
