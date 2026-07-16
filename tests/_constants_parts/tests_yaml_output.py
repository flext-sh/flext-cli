"""Split test constants namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from flext_cli import c

from tests import p, t



class TestsFlextCliConstantsYamlOutput:
    """Split test constants namespace."""

    # ── YAML ────────────────────────────────────────────────────────
    YAML_VALID_CONTENT: Final[str] = "key: value\nnested:\n  foo: bar\n"
    YAML_INVALID_CONTENT: Final[str] = "key: [unterminated"
    YAML_NON_MAPPING_CONTENT: Final[str] = "- item1\n- item2\n"

    # parse(text) → (text, expect_ok)
    YAML_PARSE_CASES: Final[tuple[tuple[str, bool], ...]] = (
        (YAML_VALID_CONTENT, True),
        ("", False),
        ("null\n", False),
        (YAML_INVALID_CONTENT, False),
        (YAML_NON_MAPPING_CONTENT, False),
    )

    # dump: (data, sort_keys, expect_ok)
    YAML_DUMP_CASES: Final[tuple[tuple[t.JsonMapping, bool, bool], ...]] = (
        ({"b": 2, "a": 1}, False, True),
        ({"b": 2, "a": 1}, True, True),
        ({}, False, True),
    )

    # yaml_load_list: content yields non-list when invalid
    YAML_LIST_CASES: Final[tuple[tuple[str, bool], ...]] = (
        ("- a\n- b\n- c\n", True),
        ("", False),
        (YAML_VALID_CONTENT, False),  # mapping not a list
    )

    # ── MATCHING ───────────────────────────────────────────────────
    # matches(msg, *patterns) → (msg, patterns, expected)
    MATCH_SIMPLE_CASES: Final[tuple[tuple[str, t.StrSequence, bool], ...]] = (
        ("file not found: foo.py", ("not found",), True),
        ("error occurred", ("not found",), False),
        ("warning: deprecated api", ("deprecated", "obsolete"), True),
        ("", ("any",), False),
    )

    # file_not_found_error(msg) → (msg, expected)
    FILE_NOT_FOUND_MATCH_CASES: Final[tuple[tuple[str, bool], ...]] = (
        ("No such file or directory: '/tmp/missing.yml'", True),
        ("FileNotFoundError: [Errno 2]", True),
        ("connection refused", False),
        ("invalid syntax", False),
    )

    # cli_usage_error(msg) → (msg, expected)
    CLI_USAGE_ERROR_MATCH_CASES: Final[tuple[tuple[str, bool], ...]] = (
        ("Missing option '--project'", True),
        ("Got unexpected extra arguments", True),
        ("division by zero", False),
    )

    # ── FORMATTERS ─────────────────────────────────────────────────
    # (columns, rows, title)
    FORMATTER_TABLE_CASES: Final[
        tuple[tuple[t.StrSequence, tuple[t.StrSequence, ...], str], ...]
    ] = (
        (("Name", "Value"), (("foo", "bar"), ("baz", "qux")), "My Table"),
        (("A",), (("1",),), ""),
        (("X", "Y", "Z"), (), "Empty"),
    )

    FORMATTER_PANEL_CASES: Final[tuple[tuple[str, str], ...]] = (
        ("Hello world content", "My Title"),
        ("No title content", ""),
    )

    FORMATTER_RULE_LABELS: Final[t.StrSequence] = ("Section Header", "Done", "")

    # ── OUTPUT (services/output.py) ────────────────────────────────
    # display_message: (message, message_type | None)
    OUTPUT_DISPLAY_CASES: Final[tuple[tuple[str, c.Cli.MessageTypes | None], ...]] = (
        ("All good", c.Cli.MessageTypes.SUCCESS),
        ("Something failed", c.Cli.MessageTypes.ERROR),
        ("Watch out", c.Cli.MessageTypes.WARNING),
        ("Info here", c.Cli.MessageTypes.INFO),
        ("Debug note", c.Cli.MessageTypes.DEBUG),
        ("Default message", None),
    )

    # display_progress: (current, total)
    OUTPUT_PROGRESS_CASES: Final[tuple[tuple[int, int], ...]] = (
        (0, 10),
        (5, 10),
        (10, 10),
    )

    # header / text display
    OUTPUT_HEADER_LABELS: Final[t.StrSequence] = ("Section Start", "Processing", "")

    OUTPUT_TEXT_CASES: Final[tuple[tuple[str, str | None], ...]] = (
        ("plain text", None),
        ("styled text", "bold blue"),
        ("", None),
    )

    # ── AUTH (services/auth.py) ────────────────────────────────────
    # validate_credentials: (username, password, expect_ok)
    AUTH_CRED_CASES: Final[tuple[tuple[str, str, bool], ...]] = (
        ("admin", "secret123", True),
        ("", "secret123", False),
        ("admin", "", False),
        ("   ", "secret123", False),
    )

    # ── FORMATTERS (services/formatters.py) ───────────────────────
    FORMATTERS_PRINT_CASES: Final[tuple[tuple[str, str | None], ...]] = (
        ("Hello formatters", None),
        ("Styled", "bold green"),
        ("", None),
    )


__all__: list[str] = ["TestsFlextCliConstantsYamlOutput"]
