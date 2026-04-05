"""FLEXT CLI configuration and registry constants."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, Final

from flext_core import t


class FlextCliConstantsConfig:
    """CLI defaults, messages, registries, and output configuration."""

    class ValidationLists:
        """Validation lists."""

        OUTPUT_FORMATS: ClassVar[t.StrSequence] = (
            "json",
            "yaml",
            "csv",
            "table",
            "plain",
        )

    class CliDefaults:
        """Default CLI constants."""

        DEFAULT_APP_NAME: Final[str] = "flext-cli"
        DEFAULT_NO_COLOR: Final[bool] = False
        DEFAULT_VERBOSE: Final[bool] = False
        DEFAULT_QUIET: Final[bool] = False

    FLEXT_CLI: Final[str] = "flext-cli"
    CLI_VERSION: Final[str] = "2.0.0"
    OPTIONAL_UNION_ARG_COUNT: Final[int] = 2
    CLI_SCALAR_TYPES_TUPLE: ClassVar[
        tuple[type[str], type[int], type[float], type[bool]]
    ] = (str, int, float, bool)

    class CmdMessages:
        """Command messages."""

        SUBDIR_EXISTS: Final[str] = "{symbol} {subdir} directory exists"
        SUBDIR_MISSING: Final[str] = "{symbol} {subdir} directory missing"

    class LogMessages:
        """Log messages."""

        CONFIG_DISPLAYED: Final[str] = "Configuration displayed"
        CONFIG_VALIDATION_RESULTS: Final[str] = "Config validation results: {results}"

    class ErrorMessages:
        """Error messages."""

        INVALID_CREDENTIALS: Final[str] = (
            "Invalid credentials: missing token or username/password"
        )
        CONFIG_VALIDATION_FAILED: Final[str] = "Config validation failed: {error}"
        JSON_WRITE_FAILED: Final[str] = "JSON write failed: {error}"
        TOKEN_SAVE_FAILED: Final[str] = "Failed to save token: {error}"  # noqa: S105 - user-facing error message, not a secret
        TOKEN_LOAD_FAILED: Final[str] = "Failed to load token: {error}"  # noqa: S105 - user-facing error message, not a secret
        TOKEN_FILE_NOT_FOUND: Final[str] = "Token file does not exist"  # noqa: S105 - user-facing error message, not a secret
        TOKEN_FILE_EMPTY: Final[str] = "Token file is empty"  # noqa: S105 - user-facing error message, not a secret
        INVALID_OUTPUT_FORMAT: Final[str] = "Invalid output format: {format}"
        CONFIG_INFO_FAILED: Final[str] = "Config info failed: {error}"
        FAILED_CLEAR_CREDENTIALS: Final[str] = "Failed to clear credentials: {error}"

    class CliParamsRegistry:
        """CLI parameters registry."""

        SHORT_FLAG_VERBOSE: Final[str] = "v"
        SHORT_FLAG_QUIET: Final[str] = "q"
        SHORT_FLAG_DEBUG: Final[str] = "d"
        SHORT_FLAG_TRACE: Final[str] = "t"
        SHORT_FLAG_LOG_LEVEL: Final[str] = "L"
        SHORT_FLAG_OUTPUT_FORMAT: Final[str] = "o"
        SHORT_FLAG_CONFIG_FILE: Final[str] = "c"
        PRIORITY_VERBOSE: Final[int] = 1
        PRIORITY_QUIET: Final[int] = 2
        PRIORITY_DEBUG: Final[int] = 3
        PRIORITY_TRACE: Final[int] = 4
        PRIORITY_LOG_LEVEL: Final[int] = 5
        PRIORITY_LOG_FORMAT: Final[int] = 6
        PRIORITY_OUTPUT_FORMAT: Final[int] = 7
        PRIORITY_NO_COLOR: Final[int] = 8
        PRIORITY_CONFIG_FILE: Final[int] = 9
        KEY_SHORT: Final[str] = "short"
        KEY_PRIORITY: Final[str] = "priority"
        KEY_CHOICES: Final[str] = "choices"
        KEY_CASE_SENSITIVE: Final[str] = "case_sensitive"
        KEY_FIELD_NAME_OVERRIDE: Final[str] = "field_name_override"
        LOG_FORMAT_OVERRIDE: Final[str] = "log-format"
        CASE_INSENSITIVE: Final[bool] = False

    class CliParamsDefaults:
        """CLI parameters defaults."""

        VALID_LOG_FORMATS: ClassVar[t.StrSequence] = (
            "compact",
            "detailed",
            "full",
        )

    class CmdErrorMessages:
        """Command error messages."""

        SHOW_CONFIG_FAILED: Final[str] = "Show config failed: {error}"

    class MixinsValidationMessages:
        """Mixin validation messages."""

        FIELD_CANNOT_BE_EMPTY: Final[str] = "{field_name} cannot be empty"
        INVALID_ENUM_VALUE: Final[str] = (
            "Invalid {field_name}. Valid values: {valid_values}"
        )
        COMMAND_STATE_INVALID: Final[str] = (
            "Cannot {operation}: command is in '{current_status}' state, requires '{required_status}'"
        )
        SESSION_STATUS_INVALID: Final[str] = (
            "Invalid session status '{current_status}'. Valid states: {valid_states}"
        )
        CONFIG_MISSING_FIELDS: Final[str] = (
            "Missing required configuration fields: {missing_fields}"
        )

    class Prompts:
        """Prompt display constants."""

        DEFAULT_TIMEOUT: Final[int] = 30
        MIN_PASSWORD_LENGTH: Final[int] = 1
        CONFIRM_YES: Final[str] = " [Y/n]: "
        CONFIRM_NO: Final[str] = " [y/N]: "
        ERROR_FMT: Final[str] = "[bold red]Error:[/bold red] {message}"
        SUCCESS_FMT: Final[str] = "[bold green]Success:[/bold green] {message}"
        WARNING_FMT: Final[str] = "[bold yellow]Warning:[/bold yellow] {message}"
        PROMPT_DEFAULT_FMT: Final[str] = " [{default}]"
        PROMPT_SEP: Final[str] = ": "
        PROMPT_LOG_FMT: Final[str] = "User input for '{message}': {input}"
        PROMPT_SPACE: Final[str] = " "
        YES_VALUES: ClassVar[frozenset[str]] = frozenset({"y", "yes"})
        NO_VALUES: ClassVar[frozenset[str]] = frozenset({"n", "no"})

    class CommandsDefaults:
        """Commands service defaults."""

        DEFAULT_NAME: Final[str] = "flext"
        DEFAULT_DESCRIPTION: Final[str] = "FLEXT CLI"

    class CommandsErrorMessages:
        """Commands service error messages."""

        INVALID_COMMAND_NAME: Final[str] = "Invalid command name"
        COMMAND_NOT_FOUND: Final[str] = "Command not found: {name}"
        HANDLER_NOT_CALLABLE: Final[str] = "Handler not callable for: {name}"
        COMMAND_EXECUTION_FAILED: Final[str] = "Command execution failed: {error}"
        COMMAND_NAME_EMPTY: Final[str] = "Command name must be non-empty string"

    class FormattersErrorMessages:
        """Formatter error messages."""

        TREE_CREATION_FAILED: Final[str] = "Tree creation failed: {error}"

    class TablesErrorMessages:
        """Table error messages."""

        TABLE_DATA_EMPTY: Final[str] = "Table data cannot be empty"
        INVALID_TABLE_FORMAT: Final[str] = (
            "Invalid table format: {table_format}. Available: {available_formats}"
        )

    class OutputDefaults:
        """Output defaults."""

        EMPTY_STYLE: Final[str] = ""
        DEFAULT_MESSAGE_TYPE: Final[str] = "info"
        DEFAULT_FORMAT_TYPE: Final[str] = "table"

    class Lists:
        """Lists constants."""

        LOG_LEVELS_LIST: ClassVar[t.StrSequence] = (
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        )

    TABLE_FORMATS: ClassVar[t.StrMapping] = MappingProxyType({
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
    })

    MESSAGE_STYLE_MAP: ClassVar[Mapping[str, str]] = MappingProxyType({
        "info": "blue",
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "debug": "dim",
    })

    MESSAGE_EMOJI_MAP: ClassVar[Mapping[str, str]] = MappingProxyType({
        "info": "i",
        "success": "\u2705",
        "error": "\u274c",
        "warning": "\u26a0\ufe0f",
        "debug": "D",
    })

    CLI_PARAM_REGISTRY: ClassVar[
        Mapping[str, Mapping[str, t.Scalar | t.StrSequence]]
    ] = MappingProxyType({
        "verbose": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_VERBOSE,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_VERBOSE,
        },
        "quiet": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_QUIET,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_QUIET,
        },
        "debug": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_DEBUG,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_DEBUG,
        },
        "trace": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_TRACE,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_TRACE,
        },
        "cli_log_level": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_LOG_LEVEL,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_LOG_LEVEL,
            CliParamsRegistry.KEY_CHOICES: Lists.LOG_LEVELS_LIST,
            CliParamsRegistry.KEY_CASE_SENSITIVE: CliParamsRegistry.CASE_INSENSITIVE,
            CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE: "log_level",
        },
        "log_verbosity": {
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_LOG_FORMAT,
            CliParamsRegistry.KEY_CHOICES: Lists.LOG_LEVELS_LIST,
            CliParamsRegistry.KEY_CASE_SENSITIVE: CliParamsRegistry.CASE_INSENSITIVE,
            CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE: CliParamsRegistry.LOG_FORMAT_OVERRIDE,
        },
        "output_format": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_OUTPUT_FORMAT,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_OUTPUT_FORMAT,
            CliParamsRegistry.KEY_CHOICES: list(ValidationLists.OUTPUT_FORMATS),
            CliParamsRegistry.KEY_CASE_SENSITIVE: CliParamsRegistry.CASE_INSENSITIVE,
        },
        "no_color": {
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_NO_COLOR,
        },
        "config_file": {
            CliParamsRegistry.KEY_SHORT: CliParamsRegistry.SHORT_FLAG_CONFIG_FILE,
            CliParamsRegistry.KEY_PRIORITY: CliParamsRegistry.PRIORITY_CONFIG_FILE,
        },
    })
