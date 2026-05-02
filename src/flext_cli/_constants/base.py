"""FLEXT CLI base constants."""

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
    DICT_KEY_SERVICE: Final[str] = "service"
    DICT_KEY_AUTH_TOKEN: Final[str] = "token"
    DICT_KEY_USERNAME: Final[str] = "username"
    DICT_KEY_USER_SECRET: Final[str] = "password"

    SUBDIR_CACHE: Final[str] = "cache"
    SUBDIR_LOGS: Final[str] = "logs"
    STANDARD_SUBDIRS: ClassVar[t.StrSequence] = (SUBDIR_CACHE, SUBDIR_LOGS)

    SYMBOL_SUCCESS_MARK: Final[str] = "\u2713"
    SYMBOL_FAILURE_MARK: Final[str] = "\u2717"
    SYMBOL_WARN: Final[str] = "\u26a0"
    SYMBOL_SKIP: Final[str] = "\u25cb"

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
    FILE_NOT_FOUND_REGEXES: ClassVar[t.VariadicTuple[re.Pattern[str]]] = tuple(
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in FILE_NOT_FOUND_PATTERN_ORDER
    )
    CLI_USAGE_ERROR_REGEXES: ClassVar[t.VariadicTuple[re.Pattern[str]]] = tuple(
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in CLI_USAGE_ERROR_PATTERN_ORDER
    )

    CMD_SERVICE_NAME: Final[str] = "FlextCliCmd"

    UI_DEFAULT_PROMPT_SUFFIX: Final[str] = ": "
