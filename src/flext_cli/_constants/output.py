"""FLEXT CLI output string authorities."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, Final

from flext_cli import FlextCliConstantsEnums
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

    LOG_MSG_SETTINGS_DISPLAYED: Final[str] = "Settings displayed"
    LOG_MSG_SETTINGS_VALIDATION_RESULTS: Final[str] = (
        "Settings validation results: {results}"
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
    OUTPUT_DEFAULT_MESSAGE_TYPE: Final[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.INFO
    )
    OUTPUT_DEFAULT_FORMAT_TYPE: Final[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.TABLE
    )

    TABLE_FORMATS: ClassVar[t.StrMapping] = MappingProxyType({
        FlextCliConstantsEnums.TabularFormat.PLAIN: "Minimal formatting, no borders",
        FlextCliConstantsEnums.TabularFormat.SIMPLE: "Simple ASCII borders",
        FlextCliConstantsEnums.TabularFormat.GRID: "Grid-style ASCII table",
        FlextCliConstantsEnums.TabularFormat.FANCY_GRID: "Fancy grid with double lines",
        FlextCliConstantsEnums.TabularFormat.PIPE: "Markdown pipe table",
        FlextCliConstantsEnums.TabularFormat.ORGTBL: "Emacs org-mode table",
        FlextCliConstantsEnums.TabularFormat.JIRA: "Jira markup table",
        FlextCliConstantsEnums.TabularFormat.PRESTO: "Presto SQL output",
        FlextCliConstantsEnums.TabularFormat.PRETTY: "Pretty ASCII table",
        FlextCliConstantsEnums.TabularFormat.PSQL: "PostgreSQL psql output",
        FlextCliConstantsEnums.TabularFormat.RST: "reStructuredText grid",
        FlextCliConstantsEnums.TabularFormat.MEDIAWIKI: "MediaWiki markup",
        FlextCliConstantsEnums.TabularFormat.MOINMOIN: "MoinMoin markup",
        FlextCliConstantsEnums.TabularFormat.YOUTRACK: "YouTrack markup",
        FlextCliConstantsEnums.TabularFormat.HTML: "HTML table",
        FlextCliConstantsEnums.TabularFormat.UNSAFEHTML: "Unsafe HTML table",
        FlextCliConstantsEnums.TabularFormat.LATEX: "LaTeX table",
        FlextCliConstantsEnums.TabularFormat.LATEX_RAW: "Raw LaTeX table",
        FlextCliConstantsEnums.TabularFormat.LATEX_BOOKTABS: "LaTeX booktabs table",
        FlextCliConstantsEnums.TabularFormat.LATEX_LONGTABLE: "LaTeX longtable",
        FlextCliConstantsEnums.TabularFormat.TEXTILE: "Textile markup",
        FlextCliConstantsEnums.TabularFormat.TSV: "Tab-separated values",
    })

    MESSAGE_STYLE_MAP: ClassVar[
        Mapping[
            FlextCliConstantsEnums.MessageTypes,
            FlextCliConstantsEnums.MessageStyles,
        ]
    ] = MappingProxyType({
        FlextCliConstantsEnums.MessageTypes.INFO: FlextCliConstantsEnums.MessageStyles.BLUE,
        FlextCliConstantsEnums.MessageTypes.SUCCESS: FlextCliConstantsEnums.MessageStyles.BOLD_GREEN,
        FlextCliConstantsEnums.MessageTypes.ERROR: FlextCliConstantsEnums.MessageStyles.BOLD_RED,
        FlextCliConstantsEnums.MessageTypes.WARNING: FlextCliConstantsEnums.MessageStyles.BOLD_YELLOW,
        FlextCliConstantsEnums.MessageTypes.DEBUG: FlextCliConstantsEnums.MessageStyles.DIM,
    })

    MESSAGE_EMOJI_MAP: ClassVar[Mapping[FlextCliConstantsEnums.MessageTypes, str]] = (
        MappingProxyType({
            FlextCliConstantsEnums.MessageTypes.INFO: EMOJI_INFO,
            FlextCliConstantsEnums.MessageTypes.SUCCESS: EMOJI_SUCCESS,
            FlextCliConstantsEnums.MessageTypes.ERROR: EMOJI_ERROR,
            FlextCliConstantsEnums.MessageTypes.WARNING: EMOJI_WARNING,
            FlextCliConstantsEnums.MessageTypes.DEBUG: EMOJI_DEBUG,
        })
    )


__all__: list[str] = ["FlextCliConstantsOutput"]
