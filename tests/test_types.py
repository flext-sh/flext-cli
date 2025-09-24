"""Tests for typings.py and constants.py - Real API only.

Tests FlextCliTypings type definitions and FlextCliConstants constants.
After standardization, constants moved from FlextCliTypings to FlextCliConstants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliConstants, FlextCliTypings, typings


class TestFlextCliTypings:
    """Test FlextCliTypings unified class - now only type definitions."""

    def test_typings_module_exports_flext_cli_typings(self) -> None:
        """Test that typings module exports FlextCliTypings."""
        assert hasattr(typings, "FlextCliTypings")
        assert typings.FlextCliTypings is FlextCliTypings


class TestFlextCliConstants:
    """Test FlextCliConstants unified class - all constants."""

    def test_output_formats_enum(self) -> None:
        """Test FlextCliConstants.OutputFormats enum."""
        assert hasattr(FlextCliConstants, "OutputFormats")
        assert FlextCliConstants.OutputFormats.JSON.value == "json"
        assert FlextCliConstants.OutputFormats.YAML.value == "yaml"
        assert FlextCliConstants.OutputFormats.CSV.value == "csv"
        assert FlextCliConstants.OutputFormats.TABLE.value == "table"
        assert FlextCliConstants.OutputFormats.PLAIN.value == "plain"

    def test_commands_class(self) -> None:
        """Test FlextCliConstants.Commands nested class."""
        assert hasattr(FlextCliConstants, "Commands")
        assert FlextCliConstants.Commands.AUTH == "auth"
        assert FlextCliConstants.Commands.CONFIG == "config"
        assert FlextCliConstants.Commands.DEBUG == "debug"
        assert FlextCliConstants.Commands.FORMAT == "format"
        assert FlextCliConstants.Commands.EXPORT == "export"

    def test_cli_defaults_class(self) -> None:
        """Test FlextCliConstants.CliDefaults nested class."""
        assert hasattr(FlextCliConstants, "CliDefaults")
        assert FlextCliConstants.CliDefaults.DEFAULT_PROFILE == "default"
        assert FlextCliConstants.CliDefaults.DEFAULT_OUTPUT_FORMAT == "table"
        assert FlextCliConstants.CliDefaults.DEFAULT_TIMEOUT == 30

    def test_auth_class(self) -> None:
        """Test FlextCliConstants.Auth nested class."""
        assert hasattr(FlextCliConstants, "Auth")
        assert "token.json" in FlextCliConstants.Auth.TOKEN_FILENAME
        assert FlextCliConstants.Auth.CONFIG_FILENAME == "auth.json"

    def test_session_class(self) -> None:
        """Test FlextCliConstants.Session nested class."""
        assert hasattr(FlextCliConstants, "Session")
        assert FlextCliConstants.Session.DEFAULT_TIMEOUT == 3600
        assert FlextCliConstants.Session.MAX_COMMANDS == 1000

    def test_services_class(self) -> None:
        """Test FlextCliConstants.Services nested class."""
        assert hasattr(FlextCliConstants, "Services")
        assert FlextCliConstants.Services.API == "api"
        assert FlextCliConstants.Services.FORMATTER == "formatter"
        assert FlextCliConstants.Services.AUTH == "auth"

    def test_protocols_class(self) -> None:
        """Test FlextCliConstants.Protocols nested class."""
        assert hasattr(FlextCliConstants, "Protocols")
        assert FlextCliConstants.Protocols.HTTP == "http"
        assert FlextCliConstants.Protocols.HTTPS == "https"

    def test_output_formats_list(self) -> None:
        """Test OUTPUT_FORMATS_LIST constant."""
        assert hasattr(FlextCliConstants, "OUTPUT_FORMATS_LIST")
        assert isinstance(FlextCliConstants.OUTPUT_FORMATS_LIST, list)
        assert "json" in FlextCliConstants.OUTPUT_FORMATS_LIST
        assert "yaml" in FlextCliConstants.OUTPUT_FORMATS_LIST
        assert "csv" in FlextCliConstants.OUTPUT_FORMATS_LIST
        assert "table" in FlextCliConstants.OUTPUT_FORMATS_LIST
        assert "plain" in FlextCliConstants.OUTPUT_FORMATS_LIST


class TestTypingsExports:
    """Test typings module exports."""

    def test_all_exports_list(self) -> None:
        """Test __all__ exports list."""
        assert hasattr(typings, "__all__")
        assert isinstance(typings.__all__, list)
        assert "FlextCliTypings" in typings.__all__

    def test_all_exports_are_accessible(self) -> None:
        """Test all declared exports are accessible."""
        for export_name in typings.__all__:
            assert hasattr(typings, export_name), f"Export {export_name} not found"
            export_value = getattr(typings, export_name)
            assert export_value is not None, f"Export {export_name} is None"

    def test_flext_cli_typings_is_only_export(self) -> None:
        """Test that FlextCliTypings is the primary export."""
        # The real API exports only FlextCliTypings
        assert len(typings.__all__) >= 1
        assert typings.__all__[0] == "FlextCliTypings"


class TestTypingsStructure:
    """Test typings module structure."""

    def test_module_has_docstring(self) -> None:
        """Test module has proper docstring."""
        assert typings.__doc__ is not None
        assert len(typings.__doc__) > 0

    def test_unified_class_pattern(self) -> None:
        """Test follows FLEXT unified class pattern."""
        # FlextCliTypings is the single unified class for type definitions
        assert hasattr(typings, "FlextCliTypings")
        assert isinstance(FlextCliTypings, type)


class TestTypeAliases:
    """Test type aliases in FlextCliTypings."""

    def test_type_variables_exist(self) -> None:
        """Test type variables are defined."""
        assert hasattr(FlextCliTypings, "T")
        assert hasattr(FlextCliTypings, "CommandHandler")

    def test_cli_type_aliases_exist(self) -> None:
        """Test CLI-specific type aliases exist."""
        # These are type aliases, check they're defined on the class
        assert hasattr(FlextCliTypings, "CliConfigData")
        assert hasattr(FlextCliTypings, "CliCommandArgs")
        assert hasattr(FlextCliTypings, "CliCommandResult")
        assert hasattr(FlextCliTypings, "CliFormatData")
        assert hasattr(FlextCliTypings, "OutputFormatType")
        assert hasattr(FlextCliTypings, "CliExitCode")
        assert hasattr(FlextCliTypings, "CommandHandlerFunc")

    def test_auth_type_aliases_exist(self) -> None:
        """Test authentication type aliases exist."""
        assert hasattr(FlextCliTypings, "AuthTokenData")
        assert hasattr(FlextCliTypings, "AuthConfigData")

    def test_debug_type_aliases_exist(self) -> None:
        """Test debug type aliases exist."""
        assert hasattr(FlextCliTypings, "DebugInfoData")
        assert hasattr(FlextCliTypings, "LoggingConfigData")
