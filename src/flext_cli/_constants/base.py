"""FLEXT CLI base constants."""

from __future__ import annotations

from typing import ClassVar, Final

from rich.errors import ConsoleError, LiveError, StyleError

from flext_core import t


class FlextCliConstantsBase:
    """Base CLI constants for metadata, paths, symbols, and static values."""

    class Encoding:
        """Encoding constants."""

        DEFAULT: Final[str] = "utf-8"

    CLI_SAFE_EXCEPTIONS: ClassVar[tuple[type[Exception], ...]] = (
        ValueError,
        TypeError,
        KeyError,
        ConsoleError,
        StyleError,
        LiveError,
    )

    class Paths:
        """Path constants."""

        FLEXT_DIR_NAME: Final[str] = ".flext"

    class DictKeys:
        """Dictionary keys."""

        STATUS: Final[str] = "status"
        SERVICE: Final[str] = "service"
        AUTH_TOKEN: Final[str] = "token"
        USERNAME: Final[str] = "username"
        USER_SECRET: Final[str] = "password"

    class Subdirectories:
        """Subdirectory constants."""

        CACHE: Final[str] = "cache"
        LOGS: Final[str] = "logs"
        STANDARD_SUBDIRS: ClassVar[t.StrSequence] = (CACHE, LOGS)

    class Symbols:
        """Symbol constants."""

        SUCCESS_MARK: Final[str] = "\u2713"
        FAILURE_MARK: Final[str] = "\u2717"
        WARN: Final[str] = "\u26a0"
        SKIP: Final[str] = "\u25cb"

    class Styles:
        """Style constants."""

        BLUE: Final[str] = "blue"
        BOLD_GREEN: Final[str] = "bold green"
        BOLD_RED: Final[str] = "bold red"
        BOLD_YELLOW: Final[str] = "bold yellow"
        DIM: Final[str] = "dim"

    class Emojis:
        """Emoji constants."""

        INFO: Final[str] = "i"
        SUCCESS: Final[str] = "\u2705"
        ERROR: Final[str] = "\u274c"
        WARNING: Final[str] = "\u26a0\ufe0f"
        DEBUG: Final[str] = "D"

    class FileErrorMessages:
        """File error messages."""

        FILE_DELETION_FAILED: Final[str] = "File deletion failed: {error}"
        JSON_LOAD_FAILED: Final[str] = "JSON load failed: {error}"

    class CmdDefaults:
        """Command defaults."""

        SERVICE_NAME: Final[str] = "FlextCliCmd"

    class APIDefaults:
        """API defaults."""

        APP_DESCRIPTION_SUFFIX: Final[str] = " CLI"
        CONTAINER_REGISTRATION_KEY: Final[str] = "flext_cli"

    class UIDefaults:
        """UI defaults."""

        DEFAULT_PROMPT_SUFFIX: Final[str] = ": "
