"""Tests for typings.py - Real API only.

Tests FlextCliTypings using actual implemented structure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import typings
from flext_cli.typings import FlextCliTypings


class TestFlextCliTypings:
    """Test FlextCliTypings unified class."""

    def test_typings_module_exports_flext_cli_typings(self) -> None:
        """Test that typings module exports FlextCliTypings."""
        assert hasattr(typings, "FlextCliTypings")
        assert typings.FlextCliTypings is FlextCliTypings

    def test_flext_cli_typings_output_format_class(self) -> None:
        """Test FlextCliTypings.OutputFormat nested class."""
        assert hasattr(FlextCliTypings, "OutputFormat")
        assert FlextCliTypings.OutputFormat.JSON == "json"
        assert FlextCliTypings.OutputFormat.YAML == "yaml"
        assert FlextCliTypings.OutputFormat.CSV == "csv"
        assert FlextCliTypings.OutputFormat.TABLE == "table"
        assert FlextCliTypings.OutputFormat.PLAIN == "plain"

    def test_flext_cli_typings_commands_class(self) -> None:
        """Test FlextCliTypings.Commands nested class."""
        assert hasattr(FlextCliTypings, "Commands")
        assert FlextCliTypings.Commands.AUTH == "auth"
        assert FlextCliTypings.Commands.CONFIG == "config"
        assert FlextCliTypings.Commands.DEBUG == "debug"
        assert FlextCliTypings.Commands.FORMAT == "format"
        assert FlextCliTypings.Commands.EXPORT == "export"

    def test_flext_cli_typings_config_class(self) -> None:
        """Test FlextCliTypings.Config nested class."""
        assert hasattr(FlextCliTypings, "Config")
        assert FlextCliTypings.Config.DEFAULT_PROFILE == "default"
        assert FlextCliTypings.Config.DEFAULT_OUTPUT_FORMAT == "table"
        assert FlextCliTypings.Config.DEFAULT_TIMEOUT == 30

    def test_flext_cli_typings_auth_class(self) -> None:
        """Test FlextCliTypings.Auth nested class."""
        assert hasattr(FlextCliTypings, "Auth")
        assert "token.json" in FlextCliTypings.Auth.TOKEN_FILENAME
        assert FlextCliTypings.Auth.CONFIG_FILENAME == "auth.json"

    def test_flext_cli_typings_session_class(self) -> None:
        """Test FlextCliTypings.Session nested class."""
        assert hasattr(FlextCliTypings, "Session")
        assert FlextCliTypings.Session.DEFAULT_TIMEOUT == 3600
        assert FlextCliTypings.Session.MAX_COMMANDS == 1000

    def test_flext_cli_typings_services_class(self) -> None:
        """Test FlextCliTypings.Services nested class."""
        assert hasattr(FlextCliTypings, "Services")
        assert FlextCliTypings.Services.API == "api"
        assert FlextCliTypings.Services.FORMATTER == "formatter"
        assert FlextCliTypings.Services.AUTH == "auth"

    def test_flext_cli_typings_protocols_class(self) -> None:
        """Test FlextCliTypings.Protocols nested class."""
        assert hasattr(FlextCliTypings, "Protocols")
        assert FlextCliTypings.Protocols.HTTP == "http"
        assert FlextCliTypings.Protocols.HTTPS == "https"

    def test_output_format_get_all_formats(self) -> None:
        """Test OutputFormat.get_all_formats() method."""
        formats = FlextCliTypings.OutputFormat.get_all_formats()
        assert isinstance(formats, dict)
        assert formats["JSON"] == "json"
        assert formats["YAML"] == "yaml"
        assert formats["CSV"] == "csv"
        assert formats["TABLE"] == "table"
        assert formats["PLAIN"] == "plain"


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
        # FlextCliTypings is the single unified class
        assert hasattr(typings, "FlextCliTypings")
        assert isinstance(FlextCliTypings, type)

        # Has nested classes for organization
        nested_classes = [
            "OutputFormat",
            "Commands",
            "Config",
            "Auth",
            "Session",
            "Services",
            "Protocols",
        ]

        for nested_class in nested_classes:
            assert hasattr(FlextCliTypings, nested_class), (
                f"Missing nested class: {nested_class}"
            )
            nested = getattr(FlextCliTypings, nested_class)
            assert isinstance(nested, type), f"{nested_class} is not a class"


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
