"""FLEXT CLI base constants.

Owns every fixed compiled ``re.Pattern`` for the CLI domain. Consumer modules
import the pre-compiled ``*_REGEXES`` constants directly; runtime-supplied
regex construction must not live on this constants surface.
"""

from __future__ import annotations

import re
from typing import ClassVar, Final

from rich.errors import ConsoleError, LiveError, StyleError

from flext_core import t


class FlextCliConstantsBase:
    """Base CLI constants for metadata, paths, symbols, and static values."""

    ENCODING_DEFAULT: Final[str] = "utf-8"

    CLI_SAFE_EXCEPTIONS: ClassVar[t.VariadicTuple[type[Exception]]] = (
        ValueError,
        TypeError,
        KeyError,
        ConsoleError,
        StyleError,
        LiveError,
    )

    PATH_FLEXT_DIR_NAME: Final[str] = ".flext"

    DICT_KEY_STATUS: Final[str] = "status"
    DICT_KEY_COMMAND: Final[str] = "command"
    DICT_KEY_MESSAGE: Final[str] = "message"
    DICT_KEY_APP_NAME: Final[str] = "app_name"
    DICT_KEY_INITIALIZED: Final[str] = "initialized"
    DICT_KEY_COMMANDS_COUNT: Final[str] = "commands_count"
    DICT_KEY_COMMANDS: Final[str] = "commands"
    DICT_KEY_NAME: Final[str] = "name"
    DICT_KEY_SERVICE: Final[str] = "service"
    DICT_KEY_AUTH_TOKEN: Final[str] = "token"
    DICT_KEY_USERNAME: Final[str] = "username"
    DICT_KEY_USER_SECRET: Final[str] = "password"
    DICT_KEY_RULES: Final[str] = "rules"
    DICT_KEY_RULE_ID: Final[str] = "id"
    DICT_KEY_ENABLED: Final[str] = "enabled"
    DICT_KEY_ACTION: Final[str] = "action"
    DICT_KEY_CHECK: Final[str] = "check"

    MSG_NO_ARGS: Final[str] = "No args"

    RULES_REGISTRY_FILENAME: Final[str] = "engine-registry.yml"
    RULES_DIR_NAME: Final[str] = "rules"
    RULES_ACTION_KEY: Final[str] = "fix_action"

    SUBDIR_CACHE: Final[str] = "cache"
    SUBDIR_LOGS: Final[str] = "logs"
    STANDARD_SUBDIRS: ClassVar[t.StrSequence] = (SUBDIR_CACHE, SUBDIR_LOGS)

    SYMBOL_SUCCESS_MARK: Final[str] = "✓"
    SYMBOL_FAILURE_MARK: Final[str] = "✗"

    FILE_NOT_FOUND_PATTERN_ORDER: ClassVar[t.VariadicTuple[str]] = (
        "no such file",
        "not found",
        "does not exist",
        "errno 2",
        "cannot open",
    )
    CLI_USAGE_ERROR_PATTERN_ORDER: ClassVar[t.VariadicTuple[str]] = (
        "no such option",
        "no such command",
        "missing option",
        "missing argument",
        "got unexpected extra argument",
        "unrecognized arguments",
        "cli exited with code 2",
    )
    FILE_NOT_FOUND_REGEXES: ClassVar[t.VariadicTuple[t.RegexPattern]] = tuple(
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in FILE_NOT_FOUND_PATTERN_ORDER
    )
    CLI_USAGE_ERROR_REGEXES: ClassVar[t.VariadicTuple[t.RegexPattern]] = tuple(
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in CLI_USAGE_ERROR_PATTERN_ORDER
    )

    CMD_SERVICE_NAME: Final[str] = "FlextCliCmd"
