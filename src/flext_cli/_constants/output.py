"""FLEXT CLI output string authorities."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, Final

from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_core import t


class FlextCliConstantsOutput:
    """Flat output/message constants authority."""

    EMOJI_INFO: Final[str] = "i"
    EMOJI_SUCCESS: Final[str] = "\u2705"
    EMOJI_ERROR: Final[str] = "\u274c"
    EMOJI_WARNING: Final[str] = "\u26a0\ufe0f"
    EMOJI_DEBUG: Final[str] = "D"

    MSG_SUBDIR_EXISTS: Final[str] = "{symbol} {subdir} directory exists"
    MSG_SUBDIR_MISSING: Final[str] = "{symbol} {subdir} directory missing"

    LOG_MSG_CONFIG_DISPLAYED: Final[str] = "Configuration displayed"
    LOG_MSG_CONFIG_VALIDATION_RESULTS: Final[str] = (
        "Config validation results: {results}"
    )

    PROMPT_DEFAULT_TIMEOUT: Final[int] = 30
    PROMPT_MIN_PASSWORD_LENGTH: Final[int] = 1
    PROMPT_CONFIRM_YES: Final[str] = " [Y/n]: "
    PROMPT_CONFIRM_NO: Final[str] = " [y/N]: "
    PROMPT_ERROR_FMT: Final[str] = "[bold red]Error:[/bold red] {message}"
    PROMPT_SUCCESS_FMT: Final[str] = "[bold green]Success:[/bold green] {message}"
    PROMPT_WARNING_FMT: Final[str] = "[bold yellow]Warning:[/bold yellow] {message}"
    PROMPT_DEFAULT_FMT: Final[str] = " [{default}]"
    PROMPT_SEP: Final[str] = ": "
    PROMPT_LOG_FMT: Final[str] = "User input for '{message}': {input}"
    PROMPT_SPACE: Final[str] = " "
    PROMPT_YES_VALUES: ClassVar[frozenset[str]] = frozenset({"y", "yes"})
    PROMPT_NO_VALUES: ClassVar[frozenset[str]] = frozenset({"n", "no"})

    OUTPUT_EMPTY_STYLE: Final[str] = ""
    OUTPUT_DEFAULT_MESSAGE_TYPE: Final[str] = (
        FlextCliConstantsEnums.MessageTypes.INFO.value
    )
    OUTPUT_DEFAULT_FORMAT_TYPE: Final[str] = (
        FlextCliConstantsEnums.OutputFormats.TABLE.value
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
        FlextCliConstantsEnums.MessageTypes.INFO.value: FlextCliConstantsEnums.MessageStyles.BLUE,
        FlextCliConstantsEnums.MessageTypes.SUCCESS.value: FlextCliConstantsEnums.MessageStyles.BOLD_GREEN,
        FlextCliConstantsEnums.MessageTypes.ERROR.value: FlextCliConstantsEnums.MessageStyles.BOLD_RED,
        FlextCliConstantsEnums.MessageTypes.WARNING.value: FlextCliConstantsEnums.MessageStyles.BOLD_YELLOW,
        FlextCliConstantsEnums.MessageTypes.DEBUG.value: FlextCliConstantsEnums.MessageStyles.DIM,
    })

    MESSAGE_EMOJI_MAP: ClassVar[Mapping[str, str]] = MappingProxyType({
        FlextCliConstantsEnums.MessageTypes.INFO.value: EMOJI_INFO,
        FlextCliConstantsEnums.MessageTypes.SUCCESS.value: EMOJI_SUCCESS,
        FlextCliConstantsEnums.MessageTypes.ERROR.value: EMOJI_ERROR,
        FlextCliConstantsEnums.MessageTypes.WARNING.value: EMOJI_WARNING,
        FlextCliConstantsEnums.MessageTypes.DEBUG.value: EMOJI_DEBUG,
    })


__all__ = ["FlextCliConstantsOutput"]
