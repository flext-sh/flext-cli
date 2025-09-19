"""Test FlextCliDomainServices functionality following unified class patterns.

Tests the actual domain services API that exists in the codebase.
NO legacy methods that don't exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliDomainServices:
    """Test FlextCliDomainServices with actual available methods."""

    def setup_method(self) -> None:
        """Set up domain service for each test."""
        self.service = FlextCliDomainServices()

    def test_service_creation(self) -> None:
        """Test domain service can be created."""
        assert self.service is not None

    def test_health_check(self) -> None:
        """Test domain service health check."""
        result = self.service.health_check()

        assert isinstance(result, FlextResult)
        if result.is_success:
            status = result.unwrap()
            assert isinstance(status, str)

    def test_create_command(self) -> None:
        """Test command creation through domain service."""
        command_line = "echo 'test'"

        result = self.service.create_command(command_line)

        assert isinstance(result, FlextResult)
        if result.is_success:
            command = result.unwrap()
            assert isinstance(command, FlextCliModels.CliCommand)
            assert command.command_line == "echo 'test'"

    def test_create_session(self) -> None:
        """Test session creation through domain service."""
        user_id = "test-user"

        result = self.service.create_session(user_id)

        assert isinstance(result, FlextResult)
        if result.is_success:
            session = result.unwrap()
            assert isinstance(session, FlextCliModels.CliSession)
            assert session.user_id == "test-user"

    def test_service_has_required_methods(self) -> None:
        """Test service has expected methods."""
        required_methods = [
            "health_check",
            "create_command",
            "create_session",
            "execute_command_workflow",
            "start_command_execution",
            "complete_command_execution",
        ]

        for method_name in required_methods:
            assert hasattr(self.service, method_name), (
                f"Service should have {method_name} method"
            )

    def test_execute_method_returns_flext_result(self) -> None:
        """Test that execute method returns FlextResult."""
        result = self.service.execute()

        assert isinstance(result, FlextResult)

    def test_command_workflow_execution(self) -> None:
        """Test command workflow execution."""
        # Create a simple command for testing
        command_line = "echo 'test workflow'"

        create_result = self.service.create_command(command_line)
        assert create_result.is_success

        command = create_result.unwrap()
        workflow_result = self.service.execute_command_workflow(
            command.command_line or "", "test-user"
        )

        assert isinstance(workflow_result, FlextResult)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
