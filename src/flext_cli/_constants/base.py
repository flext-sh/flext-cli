"""FLEXT CLI base constants.

Owns every fixed compiled ``re.Pattern`` for the CLI domain. Consumer modules
import the pre-compiled ``*_REGEXES`` constants directly; runtime-supplied
regex construction must not live on this constants surface.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from flext_core import t


class FlextCliConstantsBase:
    """Base CLI constants for metadata, paths, symbols, and static values."""

    ENCODING_DEFAULT: ClassVar[str] = "utf-8"
    # NOTE (multi-agent): process finalization is owned once by ``c.Cli`` so
    # adapters and consumers cannot drift into local magic exit codes/messages.
    EXIT_CODE_SUCCESS: ClassVar[int] = 0
    EXIT_CODE_FAILURE: ClassVar[int] = 1
    PROCESS_TIMEOUT_EXIT_CODE: ClassVar[int] = 124
    OP_EXECUTE_APPLICATION: ClassVar[str] = "execute CLI application"
    ERR_EXIT_WITH_CODE: ClassVar[str] = "CLI exited with code {exit_code}"

    CLI_SAFE_EXCEPTIONS: ClassVar[t.VariadicTuple[type[Exception]]] = (
        ValueError,
        TypeError,
        KeyError,
    )
    # Pipeline retries fail loud by default; the bound prevents accidental
    # exponential fan-out when a caller declares a retry policy.
    PIPELINE_DEFAULT_RETRY: ClassVar[int] = 0
    PIPELINE_MAX_RETRY: ClassVar[int] = 3

    PATH_FLEXT_DIR_NAME: ClassVar[str] = ".flext"

    DICT_KEY_STATUS: ClassVar[str] = "status"
    DICT_KEY_COMMAND: ClassVar[str] = "command"
    DICT_KEY_MESSAGE: ClassVar[str] = "message"
    DICT_KEY_APP_NAME: ClassVar[str] = "app_name"
    DICT_KEY_INITIALIZED: ClassVar[str] = "initialized"
    DICT_KEY_COMMANDS_COUNT: ClassVar[str] = "commands_count"
    DICT_KEY_COMMANDS: ClassVar[str] = "commands"
    DICT_KEY_NAME: ClassVar[str] = "name"
    DICT_KEY_SERVICE: ClassVar[str] = "service"
    DICT_KEY_AUTH_TOKEN: ClassVar[str] = "token"
    DICT_KEY_USERNAME: ClassVar[str] = "username"
    DICT_KEY_USER_SECRET: ClassVar[str] = "password"
    DICT_KEY_RULES: ClassVar[str] = "rules"
    DICT_KEY_RULE_ID: ClassVar[str] = "id"
    DICT_KEY_ENABLED: ClassVar[str] = "enabled"
    DICT_KEY_ACTION: ClassVar[str] = "action"
    DICT_KEY_CHECK: ClassVar[str] = "check"

    MSG_NO_ARGS: ClassVar[str] = "No args"

    RULES_REGISTRY_FILENAME: ClassVar[str] = "engine-registry.yml"
    RULES_DIR_NAME: ClassVar[str] = "rules"
    RULES_ACTION_KEY: ClassVar[str] = "fix_action"

    SUBDIR_CACHE: ClassVar[str] = "cache"
    SUBDIR_LOGS: ClassVar[str] = "logs"
    STANDARD_SUBDIRS: ClassVar[t.StrSequence] = (SUBDIR_CACHE, SUBDIR_LOGS)

    SYMBOL_SUCCESS_MARK: ClassVar[str] = "✓"
    SYMBOL_FAILURE_MARK: ClassVar[str] = "✗"

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


__all__: list[str] = ["FlextCliConstantsBase"]
