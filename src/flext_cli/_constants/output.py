"""FLEXT CLI output string authorities."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Final

from flext_cli._constants.enums import FlextCliConstantsEnums as ce
from flext_core import c, t

if TYPE_CHECKING:
    from flext_cli import t


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

    PROMPT_DEFAULT_TIMEOUT: Final[int] = c.DEFAULT_TIMEOUT_SECONDS
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
    OUTPUT_DEFAULT_MESSAGE_TYPE: Final[ce.MessageTypes] = ce.MessageTypes.INFO
    OUTPUT_DEFAULT_FORMAT_TYPE: Final[ce.OutputFormats] = ce.OutputFormats.TABLE

    TABLE_FORMATS: ClassVar[t.StrMapping] = MappingProxyType({
        ce.TabularFormat.PLAIN: "Minimal formatting, no borders",
        ce.TabularFormat.SIMPLE: "Simple ASCII borders",
        ce.TabularFormat.GRID: "Grid-style ASCII table",
        ce.TabularFormat.FANCY_GRID: "Fancy grid with double lines",
        ce.TabularFormat.PIPE: "Markdown pipe table",
        ce.TabularFormat.ORGTBL: "Emacs org-mode table",
        ce.TabularFormat.JIRA: "Jira markup table",
        ce.TabularFormat.PRESTO: "Presto SQL output",
        ce.TabularFormat.PRETTY: "Pretty ASCII table",
        ce.TabularFormat.PSQL: "PostgreSQL psql output",
        ce.TabularFormat.RST: "reStructuredText grid",
        ce.TabularFormat.MEDIAWIKI: "MediaWiki markup",
        ce.TabularFormat.MOINMOIN: "MoinMoin markup",
        ce.TabularFormat.YOUTRACK: "YouTrack markup",
        ce.TabularFormat.HTML: "HTML table",
        ce.TabularFormat.UNSAFEHTML: "Unsafe HTML table",
        ce.TabularFormat.LATEX: "LaTeX table",
        ce.TabularFormat.LATEX_RAW: "Raw LaTeX table",
        ce.TabularFormat.LATEX_BOOKTABS: "LaTeX booktabs table",
        ce.TabularFormat.LATEX_LONGTABLE: "LaTeX longtable",
        ce.TabularFormat.TEXTILE: "Textile markup",
        ce.TabularFormat.TSV: "Tab-separated values",
    })

    MESSAGE_STYLE_MAP: ClassVar[
        t.MappingKV[
            ce.MessageTypes,
            ce.MessageStyles,
        ]
    ] = MappingProxyType({
        ce.MessageTypes.INFO: ce.MessageStyles.BLUE,
        ce.MessageTypes.SUCCESS: ce.MessageStyles.BOLD_GREEN,
        ce.MessageTypes.ERROR: ce.MessageStyles.BOLD_RED,
        ce.MessageTypes.WARNING: ce.MessageStyles.BOLD_YELLOW,
        ce.MessageTypes.DEBUG: ce.MessageStyles.DIM,
    })

    MESSAGE_EMOJI_MAP: ClassVar[t.MappingKV[ce.MessageTypes, str]] = MappingProxyType({
        ce.MessageTypes.INFO: EMOJI_INFO,
        ce.MessageTypes.SUCCESS: EMOJI_SUCCESS,
        ce.MessageTypes.ERROR: EMOJI_ERROR,
        ce.MessageTypes.WARNING: EMOJI_WARNING,
        ce.MessageTypes.DEBUG: EMOJI_DEBUG,
    })


__all__: t.MutableSequenceOf[str] = ["FlextCliConstantsOutput"]
