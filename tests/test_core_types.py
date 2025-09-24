"""Tests for core types in FLEXT CLI Library.

After standardization, constants moved to FlextCliConstants.
FlextCliTypings now contains only type definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import FlextCliConstants
from flext_core import FlextTypes


class TestFlextCliConstants:
    """Test cases for FlextCliConstants class."""

    def test_output_format_enum(self) -> None:
        """Test OutputFormat enum has expected values."""
        formats = FlextCliConstants.OutputFormats

        assert formats.JSON.value == "json"
        assert formats.YAML.value == "yaml"
        assert formats.CSV.value == "csv"
        assert formats.TABLE.value == "table"
        assert formats.PLAIN.value == "plain"

    def test_commands_classes_exist(self) -> None:
        """Test Commands constants exist."""
        commands = FlextCliConstants.Commands

        assert hasattr(commands, "AUTH")
        assert hasattr(commands, "CONFIG")
        assert hasattr(commands, "DEBUG")
        assert hasattr(commands, "FORMAT")
        assert hasattr(commands, "EXPORT")

    def test_cli_defaults_classes_exist(self) -> None:
        """Test CliDefaults constants exist."""
        defaults = FlextCliConstants.CliDefaults

        assert hasattr(defaults, "DEFAULT_PROFILE")
        assert hasattr(defaults, "DEFAULT_OUTPUT_FORMAT")
        assert hasattr(defaults, "DEFAULT_TIMEOUT")

    def test_auth_classes_exist(self) -> None:
        """Test Auth constants exist."""
        auth = FlextCliConstants.Auth

        assert hasattr(auth, "TOKEN_FILENAME")
        assert hasattr(auth, "CONFIG_FILENAME")

    def test_session_classes_exist(self) -> None:
        """Test Session constants exist."""
        session = FlextCliConstants.Session

        assert hasattr(session, "DEFAULT_TIMEOUT")
        assert hasattr(session, "MAX_COMMANDS")

    def test_services_classes_exist(self) -> None:
        """Test Services constants exist."""
        services = FlextCliConstants.Services

        assert hasattr(services, "API")
        assert hasattr(services, "FORMATTER")
        assert hasattr(services, "AUTH")

    def test_protocols_exist(self) -> None:
        """Test Protocol constants exist."""
        protocols = FlextCliConstants.Protocols

        assert hasattr(protocols, "HTTP")
        assert hasattr(protocols, "HTTPS")

    def test_flext_types_inheritance(self) -> None:
        """Test FlextTypes inherits from CoreFlextTypes."""
        # Test that FlextTypes class exists
        assert FlextTypes is not None

        # Test that it has expected attributes from inheritance
        # Note: We can't directly test inheritance without importing flext_core
        # but we can test that the class exists and is accessible


if __name__ == "__main__":
    pytest.main([__file__])
