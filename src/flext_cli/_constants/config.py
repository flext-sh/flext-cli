"""FLEXT CLI configuration and registry constants."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, Final

from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_core import c, t


class FlextCliConstantsSettings:
    """CLI defaults, messages, registries, and output configuration."""

    OUTPUT_FORMATS: ClassVar[tuple[str, ...]] = tuple(
        item.value for item in FlextCliConstantsEnums.OutputFormats
    )
    OUTPUT_FORMATS_SET: ClassVar[frozenset[str]] = frozenset(OUTPUT_FORMATS)
    LOG_LEVELS: ClassVar[tuple[str, ...]] = tuple(item.value for item in c.LogLevel)
    LOG_LEVELS_SET: ClassVar[frozenset[str]] = frozenset(LOG_LEVELS)
    MESSAGE_TYPES: ClassVar[tuple[str, ...]] = tuple(
        item.value for item in FlextCliConstantsEnums.MessageTypes
    )
    MESSAGE_TYPES_SET: ClassVar[frozenset[str]] = frozenset(MESSAGE_TYPES)

    OUTPUT_FORMAT_JSON: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.JSON
    )
    OUTPUT_FORMAT_YAML: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.YAML
    )
    OUTPUT_FORMAT_CSV: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.CSV
    )
    OUTPUT_FORMAT_TABLE: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.TABLE
    )
    OUTPUT_FORMAT_PLAIN: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.PLAIN
    )

    MESSAGE_TYPE_INFO: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.INFO
    )
    MESSAGE_TYPE_ERROR: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.ERROR
    )
    MESSAGE_TYPE_WARNING: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.WARNING
    )
    MESSAGE_TYPE_SUCCESS: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.SUCCESS
    )
    MESSAGE_TYPE_DEBUG: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.DEBUG
    )

    LOG_VERBOSITY_COMPACT: Final[FlextCliConstantsEnums.LogVerbosity] = (
        FlextCliConstantsEnums.LogVerbosity.COMPACT
    )
    LOG_VERBOSITY_DETAILED: Final[FlextCliConstantsEnums.LogVerbosity] = (
        FlextCliConstantsEnums.LogVerbosity.DETAILED
    )
    LOG_VERBOSITY_FULL: Final[FlextCliConstantsEnums.LogVerbosity] = (
        FlextCliConstantsEnums.LogVerbosity.FULL
    )

    LOG_LEVEL_DEBUG: Final[c.LogLevel] = c.LogLevel.DEBUG
    LOG_LEVEL_INFO: Final[c.LogLevel] = c.LogLevel.INFO
    LOG_LEVEL_WARNING: Final[c.LogLevel] = c.LogLevel.WARNING
    LOG_LEVEL_ERROR: Final[c.LogLevel] = c.LogLevel.ERROR
    LOG_LEVEL_CRITICAL: Final[c.LogLevel] = c.LogLevel.CRITICAL

    COMMAND_STATUS_COMPLETED: Final[FlextCliConstantsEnums.CommandStatus] = (
        FlextCliConstantsEnums.CommandStatus.COMPLETED
    )
    SERVICE_STATUS_OPERATIONAL: Final[FlextCliConstantsEnums.ServiceStatus] = (
        FlextCliConstantsEnums.ServiceStatus.OPERATIONAL
    )

    VALIDATION_OUTPUT_FORMATS: ClassVar[t.StrSequence] = tuple(
        item.value for item in FlextCliConstantsEnums.OutputFormats
    )

    CLI_DEFAULT_APP_NAME: Final[str] = "flext-cli"
    CLI_DEFAULT_NO_COLOR: Final[bool] = False
    CLI_DEFAULT_VERBOSE: Final[bool] = False
    CLI_DEFAULT_QUIET: Final[bool] = False

    FLEXT_CLI: Final[str] = "flext-cli"
    CLI_VERSION: Final[str] = "2.0.0"
    OPTIONAL_UNION_ARG_COUNT: Final[int] = 2
    CLI_SCALAR_TYPES_TUPLE: ClassVar[
        tuple[type[str], type[int], type[float], type[bool]]
    ] = (str, int, float, bool)

    CLI_PARAM_SHORT_FLAG_VERBOSE: Final[str] = "v"
    CLI_PARAM_SHORT_FLAG_QUIET: Final[str] = "q"
    CLI_PARAM_SHORT_FLAG_DEBUG: Final[str] = "d"
    CLI_PARAM_SHORT_FLAG_TRACE: Final[str] = "t"
    CLI_PARAM_SHORT_FLAG_LOG_LEVEL: Final[str] = "L"
    CLI_PARAM_SHORT_FLAG_OUTPUT_FORMAT: Final[str] = "o"
    CLI_PARAM_SHORT_FLAG_CONFIG_FILE: Final[str] = "c"
    CLI_PARAM_PRIORITY_VERBOSE: Final[int] = 1
    CLI_PARAM_PRIORITY_QUIET: Final[int] = 2
    CLI_PARAM_PRIORITY_DEBUG: Final[int] = 3
    CLI_PARAM_PRIORITY_TRACE: Final[int] = 4
    CLI_PARAM_PRIORITY_LOG_LEVEL: Final[int] = 5
    CLI_PARAM_PRIORITY_LOG_FORMAT: Final[int] = 6
    CLI_PARAM_PRIORITY_OUTPUT_FORMAT: Final[int] = 7
    CLI_PARAM_PRIORITY_NO_COLOR: Final[int] = 8
    CLI_PARAM_PRIORITY_CONFIG_FILE: Final[int] = 9
    CLI_PARAM_KEY_SHORT: Final[str] = "short"
    CLI_PARAM_KEY_PRIORITY: Final[str] = "priority"
    CLI_PARAM_KEY_CHOICES: Final[str] = "choices"
    CLI_PARAM_KEY_CASE_SENSITIVE: Final[str] = "case_sensitive"
    CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: Final[str] = "field_name_override"
    CLI_PARAM_LOG_FORMAT_OVERRIDE: Final[str] = "log-format"
    CLI_PARAM_CASE_INSENSITIVE: Final[bool] = False
    CLI_VALID_LOG_FORMATS: ClassVar[t.StrSequence] = tuple(
        item.value for item in FlextCliConstantsEnums.LogVerbosity
    )

    COMMANDS_DEFAULT_NAME: Final[str] = "flext"
    COMMANDS_DEFAULT_DESCRIPTION: Final[str] = "FLEXT CLI"

    LOG_LEVELS_LIST: ClassVar[t.StrSequence] = tuple(item.value for item in c.LogLevel)

    CLI_PARAM_REGISTRY: ClassVar[
        Mapping[str, Mapping[str, t.Scalar | t.StrSequence]]
    ] = MappingProxyType({
        "verbose": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_VERBOSE,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_VERBOSE,
        },
        "quiet": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_QUIET,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_QUIET,
        },
        "debug": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_DEBUG,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_DEBUG,
        },
        "trace": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_TRACE,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_TRACE,
        },
        "cli_log_level": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_LOG_LEVEL,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_LOG_LEVEL,
            CLI_PARAM_KEY_CHOICES: LOG_LEVELS_LIST,
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
            CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: "log_level",
        },
        "log_verbosity": {
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_LOG_FORMAT,
            CLI_PARAM_KEY_CHOICES: LOG_LEVELS_LIST,
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
            CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: CLI_PARAM_LOG_FORMAT_OVERRIDE,
        },
        "output_format": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_OUTPUT_FORMAT,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_OUTPUT_FORMAT,
            CLI_PARAM_KEY_CHOICES: list(VALIDATION_OUTPUT_FORMATS),
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
        },
        "no_color": {
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_NO_COLOR,
        },
        "config_file": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_CONFIG_FILE,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_CONFIG_FILE,
        },
    })
