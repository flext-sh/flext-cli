"""FLEXT CLI output string authorities."""

from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar, TYPE_CHECKING

from flext_core import c, t

from .enums import FlextCliConstantsEnums as ce

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliConstantsOutput:
    """Flat output/message constants authority."""

    EMOJI_INFO: ClassVar[str] = "i"
    EMOJI_SUCCESS: ClassVar[str] = "\u2705"
    EMOJI_ERROR: ClassVar[str] = "\u274c"
    EMOJI_WARNING: ClassVar[str] = "\u26a0\ufe0f"
    EMOJI_DEBUG: ClassVar[str] = "D"

    MSG_SUBDIR_EXISTS: ClassVar[str] = "{symbol} {subdir} directory exists"
    MSG_SUBDIR_MISSING: ClassVar[str] = "{symbol} {subdir} directory missing"

    LOG_MSG_SETTINGS_DISPLAYED: ClassVar[str] = "Settings displayed"
    LOG_MSG_SETTINGS_VALIDATION_RESULTS: ClassVar[str] = (
        "Settings validation results: {results}"
    )

    PROMPT_DEFAULT_TIMEOUT: ClassVar[int] = c.DEFAULT_TIMEOUT_SECONDS
    PROMPT_MIN_PASSWORD_LENGTH: ClassVar[int] = 1
    PROMPT_CONFIRM_YES: ClassVar[str] = " [Y/n]: "
    PROMPT_CONFIRM_NO: ClassVar[str] = " [y/N]: "
    PROMPT_ERROR_FMT: ClassVar[str] = "[bold red]Error:[/bold red] {message}"
    PROMPT_SUCCESS_FMT: ClassVar[str] = "[bold green]Success:[/bold green] {message}"
    PROMPT_WARNING_FMT: ClassVar[str] = "[bold yellow]Warning:[/bold yellow] {message}"
    PROMPT_DEFAULT_FMT: ClassVar[str] = " [{default}]"
    PROMPT_SEP: ClassVar[str] = ": "
    PROMPT_LOG_FMT: ClassVar[str] = "User input for '{message}': {input}"
    PROMPT_SPACE: ClassVar[str] = " "
    PROMPT_YES_VALUES: ClassVar[frozenset[str]] = frozenset({"y", "yes"})
    PROMPT_NO_VALUES: ClassVar[frozenset[str]] = frozenset({"n", "no"})

    OUTPUT_EMPTY_STYLE: ClassVar[str] = ""
    OUTPUT_DEFAULT_MESSAGE_TYPE: ClassVar[ce.MessageTypes] = ce.MessageTypes.INFO
    OUTPUT_DEFAULT_FORMAT_TYPE: ClassVar[ce.OutputFormats] = ce.OutputFormats.TABLE
    OUTPUT_HEADER_RULE_WIDTH: ClassVar[int] = 60
    OUTPUT_PLAIN_MESSAGE_THRESHOLD: ClassVar[int] = 10000
    OUTPUT_LOG_LEVEL_DEBUG: ClassVar[str] = "DEBUG"
    OUTPUT_LOG_LEVEL_ERROR: ClassVar[str] = "ERROR"
    OUTPUT_LOG_LEVEL_INFO: ClassVar[str] = "INFO"
    OUTPUT_LOG_LEVEL_WARNING: ClassVar[str] = "WARN"
    OUTPUT_REPORTS_DIR_NAME: ClassVar[str] = ".reports"
    OUTPUT_SCOPE_WORKSPACE: ClassVar[str] = "workspace"
    OUTPUT_STATUS_FAIL: ClassVar[str] = "[FAIL]"
    OUTPUT_STATUS_OK: ClassVar[str] = "[OK]"
    OUTPUT_SUMMARY_DEFAULT_VERB: ClassVar[str] = "summary"
    OUTPUT_EXECUTION_ERROR: ClassVar[str] = "execution error"
    OUTPUT_TABLE_ERROR_LABEL: ClassVar[str] = "[table error]"
    OUTPUT_TABLE_CONFIG_INVALID: ClassVar[str] = "Invalid table configuration"
    OUTPUT_TABLE_CONFIG_INVALID_FMT: ClassVar[str] = (
        f"{OUTPUT_TABLE_CONFIG_INVALID}: {{error}}"
    )
    OUTPUT_TABLE_DATA_INVALID: ClassVar[str] = "Table data invalid"
    OUTPUT_TABLE_DATA_INVALID_FMT: ClassVar[str] = (
        f"{OUTPUT_TABLE_DATA_INVALID}: {{error}}"
    )
    OUTPUT_TABLE_NORMALIZATION_FAILED: ClassVar[str] = "Table normalization failed"
    OUTPUT_TABLE_ROW_INVALID: ClassVar[str] = "Table row invalid after validation"
    OUTPUT_TABLE_FORMATTING_OPERATION: ClassVar[str] = "Table formatting"

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

    MESSAGE_STYLE_MAP: ClassVar[t.MappingKV[ce.MessageTypes, ce.MessageStyles]] = (
        MappingProxyType({
            ce.MessageTypes.INFO: ce.MessageStyles.BLUE,
            ce.MessageTypes.SUCCESS: ce.MessageStyles.BOLD_GREEN,
            ce.MessageTypes.ERROR: ce.MessageStyles.BOLD_RED,
            ce.MessageTypes.WARNING: ce.MessageStyles.BOLD_YELLOW,
            ce.MessageTypes.DEBUG: ce.MessageStyles.DIM,
        })
    )

    MESSAGE_EMOJI_MAP: ClassVar[t.MappingKV[ce.MessageTypes, str]] = MappingProxyType({
        ce.MessageTypes.INFO: EMOJI_INFO,
        ce.MessageTypes.SUCCESS: EMOJI_SUCCESS,
        ce.MessageTypes.ERROR: EMOJI_ERROR,
        ce.MessageTypes.WARNING: EMOJI_WARNING,
        ce.MessageTypes.DEBUG: EMOJI_DEBUG,
    })


__all__: t.MutableSequenceOf[str] = ["FlextCliConstantsOutput"]
