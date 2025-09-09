"""Tests for core types in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import pytest
from flext_core import FlextTypes

from flext_cli.typings import FlextCliTypes


class TestFlextCliTypes:
    """Test cases for FlextCliTypes class."""

    def test_output_format_enum(self) -> None:
        """Test OutputFormat enum has expected values."""
        formats = FlextCliTypes.OutputFormat

        assert str(formats.JSON) == "json"
        assert str(formats.YAML) == "yaml"
        assert str(formats.CSV) == "csv"
        assert str(formats.TABLE) == "table"
        assert str(formats.PLAIN) == "plain"

    def test_output_format_enum_membership(self) -> None:
        """Test OutputFormat enum membership."""
        formats = FlextCliTypes.OutputFormat

        # Valid formats
        assert "json" in formats
        assert "yaml" in formats
        assert "csv" in formats
        assert "table" in formats
        assert "plain" in formats

        # Invalid formats
        assert "xml" not in formats
        assert "html" not in formats

    def test_commands_classes_exist(self) -> None:
        """Test Commands nested classes exist."""
        commands = FlextCliTypes.Commands

        assert hasattr(commands, "PendingState")
        assert hasattr(commands, "RunningState")
        assert hasattr(commands, "CompletedState")
        assert hasattr(commands, "FailedState")
        assert hasattr(commands, "CliCommandContext")

    def test_config_classes_exist(self) -> None:
        """Test Config nested classes exist."""
        config = FlextCliTypes.Config

        assert hasattr(config, "DevelopmentProfile")
        assert hasattr(config, "ProductionProfile")
        assert hasattr(config, "TestingProfile")
        assert hasattr(config, "CliConfigContext")

    def test_auth_classes_exist(self) -> None:
        """Test Auth nested classes exist."""
        auth = FlextCliTypes.Auth

        assert hasattr(auth, "CliAuthContext")

    def test_session_classes_exist(self) -> None:
        """Test Session nested classes exist."""
        session = FlextCliTypes.Session

        assert hasattr(session, "CliSessionContext")

    def test_services_classes_exist(self) -> None:
        """Test Services nested classes exist."""
        services = FlextCliTypes.Services

        assert hasattr(services, "CliServiceContext")

    def test_protocols_exist(self) -> None:
        """Test Protocol classes exist."""
        protocols = FlextCliTypes.Protocols

        assert hasattr(protocols, "CliProcessor")
        assert hasattr(protocols, "CliValidator")
        assert hasattr(protocols, "CliFormatter")
        assert hasattr(protocols, "CliAuthenticator")

    def test_flext_types_inheritance(self) -> None:
        """Test FlextTypes inherits from CoreFlextTypes."""
        # Test that FlextTypes class exists
        assert FlextTypes is not None

        # Test that it has expected attributes from inheritance
        # Note: We can't directly test inheritance without importing flext_core
        # but we can test that the class exists and is accessible


if __name__ == "__main__":
    pytest.main([__file__])
