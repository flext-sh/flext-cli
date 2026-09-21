"""FLEXT CLI configuration and registry constants."""

from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar, Self

from flext_core import FlextSettings, c, t

from .enums import FlextCliConstantsEnums as ce


class FlextCliConstantsSettings(FlextSettings):
    """CLI defaults, messages, registries, and output configuration.

    MRO carries ``FlextSettings`` (ENFORCE-042); the class is a namespace
    holder, never instantiated — class-attribute access resolves via the MRO.
    """

    # ENFORCE-042 namespace-holder contract: ``FlextSettings`` contributes
    # namespacing only — instance machinery stays plain object semantics so the
    # settings singleton/validation machinery cannot leak into instantiated
    # facade composites (e.g. the ``u`` logging facade).
    def __new__(cls, *args: object, **kwargs: object) -> Self:
        return object.__new__(cls)

    def __init__(self, *args: object, **kwargs: object) -> None:
        _ = self, args, kwargs

    def __setattr__(self, name: str, value: object) -> None:
        object.__setattr__(self, name, value)

    __eq__ = object.__eq__

    __hash__ = object.__hash__

    OUTPUT_FORMATS: ClassVar[t.StrSequence] = tuple(
        output_format.value for output_format in ce.OutputFormats
    )
    LOG_LEVELS: ClassVar[t.StrSequence] = tuple(item.value for item in c.LogLevel)
    MESSAGE_TYPES: ClassVar[t.StrSequence] = tuple(
        item.value for item in ce.MessageTypes
    )

    CLI_DEFAULT_NO_COLOR: ClassVar[bool] = False
    CLI_DEFAULT_VERBOSE: ClassVar[bool] = False
    CLI_DEFAULT_QUIET: ClassVar[bool] = False
    # NOTE (multi-agent): canonical scalar defaults consumed by _settings.py —
    # the settings foundation imports this PURE private module directly
    # (no facade cycle) so defaults stay SSOT with the enums (§1.8/§2.5).
    CLI_DEFAULT_LOG_VERBOSITY: ClassVar[str] = ce.LogVerbosity.COMPACT.value
    CLI_DEFAULT_LOG_LEVEL: ClassVar[str] = c.LogLevel.INFO.value
    CLI_DEFAULT_OUTPUT_FORMAT: ClassVar[str] = ce.OutputFormats.TABLE.value
    CLI_PROCESS_HEARTBEAT_SECONDS: ClassVar[float] = 30.0
    CLI_PROCESS_HEARTBEAT_MAX_SECONDS: ClassVar[float] = 60.0
    CLI_PROCESS_HEARTBEAT_MESSAGE: ClassVar[str] = "flext-cli: process still running"
    ENV_DEFAULT_CI: ClassVar[bool] = False
    ENV_VAR_HOME: ClassVar[str] = "HOME"
    ENV_VAR_CI: ClassVar[str] = "CI"
    ENV_VAR_PYTEST_CURRENT_TEST: ClassVar[str] = "PYTEST_CURRENT_TEST"
    ENV_VAR_SHELL_COMMAND: ClassVar[str] = "_"

    FLEXT_CLI: ClassVar[str] = "flext-cli"
    CLI_VERSION: ClassVar[str] = "2.0.0"
    OPTIONAL_UNION_ARG_COUNT: ClassVar[int] = 2
    CLI_SCALAR_TYPES_TUPLE: ClassVar[
        tuple[type[str], type[int], type[float], type[bool]]
    ] = t.PRIMITIVES_TYPES

    CLI_PARAM_SHORT_FLAG_VERBOSE: ClassVar[str] = "v"
    CLI_PARAM_SHORT_FLAG_QUIET: ClassVar[str] = "q"
    CLI_PARAM_SHORT_FLAG_DEBUG: ClassVar[str] = "d"
    CLI_PARAM_SHORT_FLAG_TRACE: ClassVar[str] = "t"
    CLI_PARAM_SHORT_FLAG_LOG_LEVEL: ClassVar[str] = "L"
    CLI_PARAM_SHORT_FLAG_OUTPUT_FORMAT: ClassVar[str] = "o"
    CLI_PARAM_SHORT_FLAG_CONFIG_FILE: ClassVar[str] = "c"
    CLI_PARAM_PRIORITY_VERBOSE: ClassVar[int] = 1
    CLI_PARAM_PRIORITY_QUIET: ClassVar[int] = 2
    CLI_PARAM_PRIORITY_DEBUG: ClassVar[int] = 3
    CLI_PARAM_PRIORITY_TRACE: ClassVar[int] = 4
    CLI_PARAM_PRIORITY_LOG_LEVEL: ClassVar[int] = 5
    CLI_PARAM_PRIORITY_LOG_FORMAT: ClassVar[int] = 6
    CLI_PARAM_PRIORITY_OUTPUT_FORMAT: ClassVar[int] = 7
    CLI_PARAM_PRIORITY_NO_COLOR: ClassVar[int] = 8
    CLI_PARAM_PRIORITY_CONFIG_FILE: ClassVar[int] = 9
    CLI_PARAM_KEY_SHORT: ClassVar[str] = "short"
    CLI_PARAM_KEY_DEFAULT: ClassVar[str] = "default"
    CLI_PARAM_KEY_PRIORITY: ClassVar[str] = "priority"
    CLI_PARAM_KEY_CHOICES: ClassVar[str] = "choices"
    CLI_PARAM_KEY_CASE_SENSITIVE: ClassVar[str] = "case_sensitive"
    CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: ClassVar[str] = "field_name_override"
    CLI_PARAM_LOG_FORMAT_OVERRIDE: ClassVar[str] = "log-format"
    CLI_PARAM_CASE_INSENSITIVE: ClassVar[bool] = False
    CLI_VALID_LOG_FORMATS: ClassVar[t.StrSequence] = tuple(
        item.value for item in ce.LogVerbosity
    )

    COMMANDS_DEFAULT_NAME: ClassVar[str] = "flext"
    COMMANDS_DEFAULT_DESCRIPTION: ClassVar[str] = "FLEXT CLI"

    CLI_PARAM_REGISTRY: ClassVar[
        t.MappingKV[str, t.MappingKV[str, t.Scalar | t.StrSequence]]
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
            CLI_PARAM_KEY_CHOICES: LOG_LEVELS,
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
            CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: "log_level",
        },
        "log_verbosity": {
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_LOG_FORMAT,
            CLI_PARAM_KEY_CHOICES: LOG_LEVELS,
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
            CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: CLI_PARAM_LOG_FORMAT_OVERRIDE,
        },
        "output_format": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_OUTPUT_FORMAT,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_OUTPUT_FORMAT,
            CLI_PARAM_KEY_CHOICES: list(OUTPUT_FORMATS),
            CLI_PARAM_KEY_CASE_SENSITIVE: CLI_PARAM_CASE_INSENSITIVE,
        },
        "no_color": {CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_NO_COLOR},
        "config_file": {
            CLI_PARAM_KEY_SHORT: CLI_PARAM_SHORT_FLAG_CONFIG_FILE,
            CLI_PARAM_KEY_PRIORITY: CLI_PARAM_PRIORITY_CONFIG_FILE,
        },
    })
