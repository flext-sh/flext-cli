"""FLEXT CLI output string authorities.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar

from flext_cli._constants import FlextCliConstantsEnums
from flext_core import c, t


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
    OUTPUT_DEFAULT_MESSAGE_TYPE: ClassVar[FlextCliConstantsEnums.MessageTypes] = (
        FlextCliConstantsEnums.MessageTypes.INFO
    )
    OUTPUT_DEFAULT_FORMAT_TYPE: ClassVar[FlextCliConstantsEnums.OutputFormats] = (
        FlextCliConstantsEnums.OutputFormats.TABLE
    )
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
        t.MappingKV[
            FlextCliConstantsEnums.MessageTypes,
            FlextCliConstantsEnums.MessageStyles,
        ]
    ] = MappingProxyType({
        (
            FlextCliConstantsEnums.MessageTypes.INFO
        ): FlextCliConstantsEnums.MessageStyles.BLUE,
        (
            FlextCliConstantsEnums.MessageTypes.SUCCESS
        ): FlextCliConstantsEnums.MessageStyles.BOLD_GREEN,
        (
            FlextCliConstantsEnums.MessageTypes.ERROR
        ): FlextCliConstantsEnums.MessageStyles.BOLD_RED,
        (
            FlextCliConstantsEnums.MessageTypes.WARNING
        ): FlextCliConstantsEnums.MessageStyles.BOLD_YELLOW,
        (
            FlextCliConstantsEnums.MessageTypes.DEBUG
        ): FlextCliConstantsEnums.MessageStyles.DIM,
    })

    MESSAGE_EMOJI_MAP: ClassVar[
        t.MappingKV[FlextCliConstantsEnums.MessageTypes, str]
    ] = MappingProxyType({
        FlextCliConstantsEnums.MessageTypes.INFO: EMOJI_INFO,
        FlextCliConstantsEnums.MessageTypes.SUCCESS: EMOJI_SUCCESS,
        FlextCliConstantsEnums.MessageTypes.ERROR: EMOJI_ERROR,
        FlextCliConstantsEnums.MessageTypes.WARNING: EMOJI_WARNING,
        FlextCliConstantsEnums.MessageTypes.DEBUG: EMOJI_DEBUG,
    })


__all__: t.MutableSequenceOf[str] = ["FlextCliConstantsOutput"]
