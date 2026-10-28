"""Split test constants namespace.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Sequence
from typing import ClassVar

from flext_cli import c
from tests import t


class TestsFlextCliConstantsYamlOutput:
    """Split test constants namespace."""

    # ── YAML ────────────────────────────────────────────────────────
    YAML_VALID_CONTENT: ClassVar[str] = "key: value\nnested:\n  foo: bar\n"
    YAML_INVALID_CONTENT: ClassVar[str] = "key: [unterminated"
    YAML_NON_MAPPING_CONTENT: ClassVar[str] = "- item1\n- item2\n"

    # parse(text) → (text, expect_ok); empty/null inputs fail loudly.
    YAML_PARSE_CASES: ClassVar[tuple[tuple[str, bool], ...]] = (
        (YAML_VALID_CONTENT, True),
        ("", False),
        ("null\n", False),
        (YAML_INVALID_CONTENT, False),
        (YAML_NON_MAPPING_CONTENT, False),
    )

    # dump case fields: data, sort_keys, expect_ok
    YAML_DUMP_CASES: ClassVar[tuple[tuple[t.JsonMapping, bool, bool], ...]] = (
        ({"b": 2, "a": 1}, False, True),
        ({"b": 2, "a": 1}, True, True),
        ({}, False, True),
    )

    # ── MATCHING ───────────────────────────────────────────────────
    # matches(msg, *patterns) → (msg, patterns, expected)
    MATCH_SIMPLE_CASES: ClassVar[tuple[tuple[str, Sequence[str], bool], ...]] = (
        ("file not found: foo.py", ("not found",), True),
        ("error occurred", ("not found",), False),
        ("warning: deprecated api", ("deprecated", "obsolete"), True),
        ("", ("any",), False),
    )

    # cli_usage_error(msg) → (msg, expected)
    CLI_USAGE_ERROR_MATCH_CASES: ClassVar[tuple[tuple[str, bool], ...]] = (
        ("Missing option '--project'", True),
        ("Got unexpected extra arguments", True),
        ("division by zero", False),
    )

    # ── FORMATTERS ─────────────────────────────────────────────────
    # table case fields: columns, rows, title
    FORMATTER_TABLE_CASES: ClassVar[
        tuple[tuple[Sequence[str], tuple[Sequence[str], ...], str], ...]
    ] = (
        (("Name", "Value"), (("foo", "bar"), ("baz", "qux")), "My Table"),
        (("A",), ((c.ParserBooleanToken.ONE,),), ""),
        (("X", "Y", "Z"), (), "Empty"),
    )

    FORMATTER_PANEL_CASES: ClassVar[tuple[tuple[str, str], ...]] = (
        ("Hello world content", "My Title"),
        ("No title content", ""),
    )

    FORMATTER_RULE_LABELS: ClassVar[Sequence[str]] = ("Section Header", "Done", "")

    # ── OUTPUT (services/output.py) ────────────────────────────────
    # display_message case fields: message, message_type or None
    OUTPUT_DISPLAY_CASES: ClassVar[
        tuple[tuple[str, c.Cli.MessageTypes | None], ...]
    ] = (
        ("All good", c.Cli.MessageTypes.SUCCESS),
        ("Something failed", c.Cli.MessageTypes.ERROR),
        ("Watch out", c.Cli.MessageTypes.WARNING),
        ("Info here", c.Cli.MessageTypes.INFO),
        ("Debug note", c.Cli.MessageTypes.DEBUG),
        ("Default message", None),
    )

    # display_progress case fields: current, total
    OUTPUT_PROGRESS_CASES: ClassVar[tuple[tuple[int, int], ...]] = (
        (0, 10),
        (5, 10),
        (10, 10),
    )

    # text display
    OUTPUT_TEXT_CASES: ClassVar[tuple[tuple[str, str | None], ...]] = (
        ("plain text", None),
        ("styled text", "bold blue"),
        ("", None),
    )

    # ── AUTH (services/auth.py) ────────────────────────────────────
    # validate_credentials case fields: username, password, expect_ok
    AUTH_CRED_CASES: ClassVar[tuple[tuple[str, str, bool], ...]] = (
        ("admin", "secret123", True),
        ("", "secret123", False),
        ("admin", "", False),
        ("   ", "secret123", False),
    )

    # ── FORMATTERS (services/formatters.py) ───────────────────────
    FORMATTERS_PRINT_CASES: ClassVar[tuple[tuple[str, str | None], ...]] = (
        ("Hello formatters", None),
        ("Styled", "bold green"),
        ("", None),
    )


__all__: list[str] = ["TestsFlextCliConstantsYamlOutput"]
