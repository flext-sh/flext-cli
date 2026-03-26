"""FLEXT CLI constants."""

from __future__ import annotations

import typing
from enum import StrEnum, unique

from flext_core import FlextConstants

from flext_cli import t


class FlextCliConstants(FlextConstants):
    """Constants for Flext CLI."""

    class Cli:
        """CLI related constants."""

        class Paths:
            """Path constants."""

            FLEXT_DIR_NAME = ".flext"

        class ValidationLists:
            """Validation lists."""

            OUTPUT_FORMATS: typing.ClassVar[t.StrSequence] = [
                "json",
                "yaml",
                "csv",
                "table",
                "plain",
            ]

        @unique
        class MessageTypes(StrEnum):
            """Message types enum."""

            INFO, ERROR, WARNING, SUCCESS = ("info", "error", "warning", "success")

        @unique
        class LogVerbosity(StrEnum):
            """Log verbosity enum."""

            COMPACT, DETAILED, FULL = ("compact", "detailed", "full")

        @unique
        class ServiceStatus(StrEnum):
            """Service status enum."""

            OPERATIONAL = "operational"

        class Settings:
            """Settings constants."""

            @unique
            class LogLevel(StrEnum):
                """Log level enum."""

                DEBUG, INFO, WARNING, ERROR, CRITICAL = (
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                )

        class CliDefaults:
            """Default CLI constants."""

            DEFAULT_APP_NAME = "flext-cli"
            DEFAULT_NO_COLOR, DEFAULT_VERBOSE, DEFAULT_QUIET = (
                False,
                False,
                False,
            )

        FLEXT_CLI, CLI_VERSION = ("flext-cli", "2.0.0")

        class CmdMessages:
            """Command messages."""

            SUBDIR_EXISTS, SUBDIR_MISSING = (
                "{symbol} {subdir} directory exists",
                "{symbol} {subdir} directory missing",
            )

        class LogMessages:
            """Log messages."""

            CONFIG_DISPLAYED = "Configuration displayed"
            CONFIG_VALIDATION_RESULTS = "Config validation results: {results}"

        class ErrorMessages:
            """Error messages."""

            INVALID_CREDENTIALS = (
                "Invalid credentials: missing token or username/password"
            )
            CONFIG_VALIDATION_FAILED = "Config validation failed: {error}"
            JSON_WRITE_FAILED = "JSON write failed: {error}"
            TOKEN_SAVE_FAILED, TOKEN_LOAD_FAILED = (
                "Failed to save token: {error}",
                "Failed to load token: {error}",
            )
            TOKEN_FILE_NOT_FOUND, TOKEN_FILE_EMPTY = (
                "Token file does not exist",
                "Token file is empty",
            )
            INVALID_OUTPUT_FORMAT = "Invalid output format: {format}"
            CONFIG_INFO_FAILED = "Config info failed: {error}"
            FAILED_CLEAR_CREDENTIALS = "Failed to clear credentials: {error}"

        class DictKeys:
            """Dictionary keys."""

            STATUS, SERVICE = ("status", "service")
            TOKEN, USERNAME, PASSWORD = ("token", "username", "password")

        class Subdirectories:
            """Subdirectory constants."""

            CACHE, LOGS = ("cache", "logs")
            STANDARD_SUBDIRS: typing.ClassVar[t.StrSequence] = [CACHE, LOGS]

        class Symbols:
            """Symbol constants."""

            SUCCESS_MARK, FAILURE_MARK = ("\u2713", "\u2717")

        class Styles:
            """Style constants."""

            BLUE, BOLD_GREEN, BOLD_RED, BOLD_YELLOW = (
                "blue",
                "bold green",
                "bold red",
                "bold yellow",
            )

        class Emojis:
            """Emoji constants."""

            INFO, SUCCESS, ERROR, WARNING = ("i", "\u2705", "\u274c", "\u26a0\ufe0f")

        class CliParamsRegistry:
            """CLI parameters registry."""

            SHORT_FLAG_VERBOSE, SHORT_FLAG_QUIET, SHORT_FLAG_DEBUG = ("v", "q", "d")
            SHORT_FLAG_TRACE, SHORT_FLAG_LOG_LEVEL = ("t", "L")
            SHORT_FLAG_OUTPUT_FORMAT, SHORT_FLAG_CONFIG_FILE = ("o", "c")
            PRIORITY_VERBOSE, PRIORITY_QUIET, PRIORITY_DEBUG = (1, 2, 3)
            PRIORITY_TRACE, PRIORITY_LOG_LEVEL, PRIORITY_LOG_FORMAT = (4, 5, 6)
            PRIORITY_OUTPUT_FORMAT, PRIORITY_NO_COLOR, PRIORITY_CONFIG_FILE = (7, 8, 9)
            KEY_SHORT, KEY_PRIORITY, KEY_CHOICES = ("short", "priority", "choices")
            KEY_CASE_SENSITIVE, KEY_FIELD_NAME_OVERRIDE = (
                "case_sensitive",
                "field_name_override",
            )
            LOG_FORMAT_OVERRIDE, CASE_INSENSITIVE = ("log-format", False)

        class CliParamsDefaults:
            """CLI parameters defaults."""

            VALID_LOG_FORMATS: typing.ClassVar[t.StrSequence] = [
                "compact",
                "detailed",
                "full",
            ]

        class FileErrorMessages:
            """File error messages."""

            FILE_DELETION_FAILED = "File deletion failed: {error}"
            JSON_LOAD_FAILED = "JSON load failed: {error}"

        class CmdDefaults:
            """Command defaults."""

            SERVICE_NAME = "FlextCliCmd"

        class CmdErrorMessages:
            """Command error messages."""

            SHOW_CONFIG_FAILED = "Show config failed: {error}"

        class MixinsValidationMessages:
            """Mixin validation messages."""

            FIELD_CANNOT_BE_EMPTY = "{field_name} cannot be empty"
            INVALID_ENUM_VALUE = "Invalid {field_name}. Valid values: {valid_values}"
            COMMAND_STATE_INVALID = "Cannot {operation}: command is in '{current_status}' state, requires '{required_status}'"
            SESSION_STATUS_INVALID = "Invalid session status '{current_status}'. Valid states: {valid_states}"
            CONFIG_MISSING_FIELDS = (
                "Missing required configuration fields: {missing_fields}"
            )

        class Prompts:
            """Prompt display constants."""

            DEFAULT_TIMEOUT = 30
            MIN_PASSWORD_LENGTH = 1
            CONFIRM_YES = " [Y/n]: "
            CONFIRM_NO = " [y/N]: "
            ERROR_FMT = "[bold red]Error:[/bold red] {message}"
            SUCCESS_FMT = "[bold green]Success:[/bold green] {message}"
            WARNING_FMT = "[bold yellow]Warning:[/bold yellow] {message}"
            PROMPT_DEFAULT_FMT = " [{default}]"
            PROMPT_SEP = ": "
            PROMPT_LOG_FMT = "User input for '{message}': {input}"
            PROMPT_SPACE = " "

        class CommandsDefaults:
            """Commands service defaults."""

            DEFAULT_NAME = "flext"
            DEFAULT_DESCRIPTION = "FLEXT CLI"

        class CommandsErrorMessages:
            """Commands service error messages."""

            INVALID_COMMAND_NAME = "Invalid command name"
            COMMAND_NOT_FOUND = "Command not found: {name}"
            HANDLER_NOT_CALLABLE = "Handler not callable for: {name}"
            COMMAND_EXECUTION_FAILED = "Command execution failed: {error}"
            COMMAND_NAME_EMPTY = "Command name must be non-empty string"

        class FormattersErrorMessages:
            """Formatter error messages."""

            TREE_CREATION_FAILED = "Tree creation failed: {error}"

        TABLE_FORMATS: typing.ClassVar[t.StrMapping] = {
            "plain": "Minimal formatting, no borders",
            "simple": "Simple ASCII borders",
            "grid": "Grid-style ASCII table",
            "fancy_grid": "Fancy grid with double lines",
            "pipe": "Markdown pipe table",
            "orgtbl": "Emacs org-mode table",
            "jira": "Jira markup table",
            "presto": "Presto SQL output",
            "pretty": "Pretty ASCII table",
            "psql": "PostgreSQL psql output",
            "rst": "reStructuredText grid",
            "mediawiki": "MediaWiki markup",
            "moinmoin": "MoinMoin markup",
            "youtrack": "YouTrack markup",
            "html": "HTML table",
            "unsafehtml": "Unsafe HTML table",
            "latex": "LaTeX table",
            "latex_raw": "Raw LaTeX table",
            "latex_booktabs": "LaTeX booktabs table",
            "latex_longtable": "LaTeX longtable",
            "textile": "Textile markup",
            "tsv": "Tab-separated values",
        }

        class TablesErrorMessages:
            """Table error messages."""

            TABLE_DATA_EMPTY = "Table data cannot be empty"
            INVALID_TABLE_FORMAT = (
                "Invalid table format: {table_format}. Available: {available_formats}"
            )

        class OutputDefaults:
            """Output defaults."""

            EMPTY_STYLE, DEFAULT_MESSAGE_TYPE, DEFAULT_FORMAT_TYPE = (
                "",
                "info",
                "table",
            )

        class APIDefaults:
            """API defaults."""

            APP_DESCRIPTION_SUFFIX, CONTAINER_REGISTRATION_KEY = (" CLI", "flext_cli")

        class UIDefaults:
            """UI defaults."""

            DEFAULT_PROMPT_SUFFIX = ": "

        class Lists:
            """Lists constants."""

            LOG_LEVELS_LIST: typing.ClassVar[t.StrSequence] = [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ]


__all__ = ["FlextCliConstants", "c"]

c = FlextCliConstants
