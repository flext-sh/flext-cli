"""FLEXT CLI Constants Tests - Comprehensive Constant Validation Testing.

Tests for FlextCliConstants covering initialization, values, and integration
with remaining production constants.

Modules tested: flext_cli.constants.FlextCliConstants
Scope: All constant values, format validation, usage scenarios

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import c, u


class TestsCliConstants:
    """Comprehensive test suite for FlextCliConstants functionality."""

    def test_cli_version_is_semver(self) -> None:
        """Test CLI_VERSION follows semver format (major.minor.patch)."""
        version = c.Cli.CLI_VERSION
        tm.that(version, is_=str)
        parts = version.split(".")
        tm.that(len(parts) >= 3, eq=True)
        for part in parts[:3]:
            tm.that(part.isdigit(), eq=True)

    def test_flext_cli_constant(self) -> None:
        """Test FLEXT_CLI constant."""
        tm.that(c.Cli.FLEXT_CLI, is_=str)
        tm.that(c.Cli.FLEXT_CLI, empty=False)

    def test_paths_flext_dir_name(self) -> None:
        """Test Paths.FLEXT_DIR_NAME constant."""
        tm.that(c.Cli.Paths.FLEXT_DIR_NAME, is_=str)
        tm.that(c.Cli.Paths.FLEXT_DIR_NAME, eq=".flext")
        tm.that(c.Cli.Paths.FLEXT_DIR_NAME.startswith("."), eq=True)

    def test_service_status_enum(self) -> None:
        """Test ServiceStatus enum values."""
        tm.that(c.Cli.ServiceStatus.OPERATIONAL, is_=str)
        tm.that(c.Cli.ServiceStatus.OPERATIONAL, eq="operational")

    def test_get_enum_values(self) -> None:
        """Test get_enum_values extracts values from StrEnum."""
        values = u.get_enum_values(c.Cli.ServiceStatus)
        tm.that(values, is_=tuple)
        tm.that(values, empty=False)
        for v in values:
            tm.that(v, is_=str)

    def test_cli_defaults(self) -> None:
        """Test CliDefaults constants."""
        tm.that(c.Cli.CliDefaults.DEFAULT_APP_NAME, is_=str)
        tm.that(c.Cli.CliDefaults.DEFAULT_APP_NAME, empty=False)
        tm.that(c.Cli.CliDefaults.DEFAULT_VERBOSE, is_=bool)
        tm.that(c.Cli.CliDefaults.DEFAULT_QUIET, is_=bool)
        tm.that(c.Cli.CliDefaults.DEFAULT_NO_COLOR, is_=bool)

    def test_error_messages(self) -> None:
        """Test ErrorMessages constants."""
        tm.that(c.Cli.ErrorMessages.TOKEN_FILE_NOT_FOUND, is_=str)
        tm.that(c.Cli.ErrorMessages.TOKEN_FILE_NOT_FOUND, empty=False)
        tm.that(c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT, is_=str)

    def test_emojis(self) -> None:
        """Test Emojis constants."""
        tm.that(c.Cli.Emojis.SUCCESS, is_=str)
        tm.that(c.Cli.Emojis.ERROR, is_=str)
        tm.that(c.Cli.Emojis.WARNING, is_=str)
        tm.that(c.Cli.Emojis.INFO, is_=str)

    def test_symbols(self) -> None:
        """Test Symbols constants."""
        tm.that(c.Cli.Symbols.SUCCESS_MARK, is_=str)
        tm.that(c.Cli.Symbols.FAILURE_MARK, is_=str)

    def test_message_types(self) -> None:
        """Test MessageTypes enum."""
        tm.that(c.Cli.MessageTypes.SUCCESS, is_=str)
        tm.that(c.Cli.MessageTypes.ERROR, is_=str)
        tm.that(c.Cli.MessageTypes.WARNING, is_=str)
        tm.that(c.Cli.MessageTypes.INFO, is_=str)

    def test_subdirectories(self) -> None:
        """Test Subdirectories constants."""
        tm.that(c.Cli.Subdirectories.CACHE, is_=str)
        tm.that(c.Cli.Subdirectories.LOGS, is_=str)
        tm.that(c.Cli.Subdirectories.STANDARD_SUBDIRS, is_=list)
        tm.that(c.Cli.Subdirectories.STANDARD_SUBDIRS, empty=False)

    def test_table_formats(self) -> None:
        """Test TABLE_FORMATS constant."""
        tm.that(c.Cli.TABLE_FORMATS, is_=dict)
        tm.that(c.Cli.TABLE_FORMATS, empty=False)

    def test_output_defaults(self) -> None:
        """Test OutputDefaults constants."""
        tm.that(c.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE, is_=str)
        tm.that(c.Cli.OutputDefaults.DEFAULT_MESSAGE_TYPE, is_=str)

    def test_cmd_defaults(self) -> None:
        """Test CmdDefaults constants."""
        tm.that(c.Cli.CmdDefaults.SERVICE_NAME, is_=str)
        tm.that(c.Cli.CmdDefaults.SERVICE_NAME, empty=False)

    def test_log_verbosity(self) -> None:
        """Test LogVerbosity enum."""
        tm.that(c.Cli.LogVerbosity.COMPACT, is_=str)
        tm.that(c.Cli.LogVerbosity.DETAILED, is_=str)
        tm.that(c.Cli.LogVerbosity.FULL, is_=str)

    def test_constants_uniqueness(self) -> None:
        """Test that key constants have unique values."""
        unique_values = {
            c.Cli.Emojis.SUCCESS,
            c.Cli.Emojis.ERROR,
            c.Cli.Emojis.WARNING,
            c.Cli.Emojis.INFO,
        }
        tm.that(len(unique_values), eq=4)
