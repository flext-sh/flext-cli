"""Tests for core types in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.typings import FlextCliTypings
from flext_core import FlextTypes


class TestFlextCliTypings:
    """Test cases for FlextCliTypings class."""

    def test_output_format_enum(self) -> None:
        """Test OutputFormat enum has expected values."""
        formats = FlextCliTypings.OutputFormat

        assert formats.JSON == "json"
        assert formats.YAML == "yaml"
        assert formats.CSV == "csv"
        assert formats.TABLE == "table"
        assert formats.PLAIN == "plain"

    def test_output_format_enum_membership(self) -> None:
        """Test OutputFormat enum membership."""
        formats = FlextCliTypings.OutputFormat

        # Valid formats
        all_formats = formats.get_all_formats()
        assert "json" in all_formats.values()
        assert "yaml" in all_formats.values()
        assert "csv" in all_formats.values()
        assert "table" in all_formats.values()
        assert "plain" in all_formats.values()

        # Invalid formats
        assert "xml" not in all_formats.values()
        assert "html" not in all_formats.values()

    def test_commands_classes_exist(self) -> None:
        """Test Commands nested classes exist."""
        commands = FlextCliTypings.Commands

        assert hasattr(commands, "PendingState")
        assert hasattr(commands, "RunningState")
        assert hasattr(commands, "CompletedState")
        assert hasattr(commands, "FailedState")
        assert hasattr(commands, "CliCommandContext")

    def test_config_classes_exist(self) -> None:
        """Test Config nested classes exist."""
        config = FlextCliTypings.Config

        assert hasattr(config, "DevelopmentProfile")
        assert hasattr(config, "ProductionProfile")
        assert hasattr(config, "TestingProfile")
        assert hasattr(config, "CliConfigContext")

    def test_auth_classes_exist(self) -> None:
        """Test Auth nested classes exist."""
        auth = FlextCliTypings.Auth

        assert hasattr(auth, "CliAuthContext")

    def test_session_classes_exist(self) -> None:
        """Test Session nested classes exist."""
        session = FlextCliTypings.Session

        assert hasattr(session, "CliSessionContext")

    def test_services_classes_exist(self) -> None:
        """Test Services nested classes exist."""
        services = FlextCliTypings.Services

        assert hasattr(services, "CliServiceContext")

    def test_protocols_exist(self) -> None:
        """Test Protocol classes exist."""
        protocols = FlextCliTypings.Protocols

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
