"""Constants for flext-cli tests.

Provides TestsFlextCliConstants, extending FlextTestsConstants with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- c (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from re import Pattern
from types import MappingProxyType
from typing import Final

from flext_tests import FlextTestsConstants

from flext_cli import c
from tests import t

# ---------------------------------------------------------------------------
# Module-level content strings (not class-level to avoid ClassVar confusion)
# ---------------------------------------------------------------------------

_YAML_VALID_CONTENT: Final[str] = "key: value\nnested:\n  foo: bar\n"
_YAML_INVALID_CONTENT: Final[str] = "key: [unterminated"
_YAML_NON_MAPPING_CONTENT: Final[str] = "- item1\n- item2\n"
_YAML_EMPTY_CONTENT: Final[str] = ""
_YAML_NULL_CONTENT: Final[str] = "null\n"

_TOML_VALID_CONTENT: Final[str] = (
    '[tool.flext]\nproject = "my-project"\nversion = "1.0.0"\n'
)
_TOML_INVALID_CONTENT: Final[str] = "[invalid toml\nmissing = "
_TOML_SECTION_CONTENT: Final[str] = "[section]\nkey = true\ncount = 42\n"


class TestsFlextCliConstants(FlextTestsConstants, c):
    """Constants for flext-cli tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsConstants - for test infrastructure (.Tests.*)
    2. c - for domain constants (.Cli.*)

    Access patterns:
    - c.Tests.* (generic test infrastructure)
    - c.Cli.* (domain constants from production)
    - c.Tests.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or c
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from c
    """

    class Tests(FlextTestsConstants.Tests):
        """Test-specific constant values for flext-cli."""

        SEMVER_RE: Final[Pattern[str]] = re.compile(
            r"^\d+\.\d+\.\d+(?:[-.][\w\.]+)?(?:\+[\w\.]+)?$"
        )

        VERSION_EMPTY_MSG: Final[str] = "Version must be non-empty string"
        VERSION_INFO_TOO_SHORT_MSG: Final[str] = (
            "Version info must have at least 3 parts"
        )

        PROMPT_LONG: Final[str] = (
            "This is a very long message that tests how the system handles extended text input"
        )
        PROMPT_SPECIAL: Final[str] = "!@#$%^&*()"
        PROMPT_UNICODE: Final[str] = "你好世界🌍"
        PROMPT_EDGE_MESSAGES: Final[tuple[str, ...]] = (
            "",
            PROMPT_LONG,
            PROMPT_SPECIAL,
            PROMPT_UNICODE,
        )

        VERSION_STR_VALID_SEMVER: Final[str] = "1.2.3"
        VERSION_STR_VALID_SEMVER_COMPLEX: Final[str] = "1.2.3-alpha.1+build.123"
        VERSION_STR_INVALID_NO_DOTS: Final[str] = "version"
        VERSION_STR_INVALID_NON_NUMERIC: Final[str] = "a.b.c"
        VERSION_STR_CASES: Final[Mapping[str, str]] = MappingProxyType({
            "valid_semver": VERSION_STR_VALID_SEMVER,
            "valid_semver_complex": VERSION_STR_VALID_SEMVER_COMPLEX,
            "invalid_no_dots": VERSION_STR_INVALID_NO_DOTS,
            "invalid_non_numeric": VERSION_STR_INVALID_NON_NUMERIC,
        })

        VERSION_INFO_VALID_TUPLE: Final[tuple[int, int, int]] = (1, 2, 3)
        VERSION_INFO_VALID_COMPLEX_TUPLE: Final[tuple[int | str, ...]] = (
            1,
            2,
            3,
            "alpha",
            1,
        )
        VERSION_INFO_SHORT_TUPLE: Final[tuple[int, int]] = (1, 2)
        VERSION_INFO_EMPTY_TUPLE: Final[tuple[()]] = ()

        ENVIRONMENT_DEVELOPMENT: Final[str] = "development"
        ENVIRONMENT_STAGING: Final[str] = "staging"
        ENVIRONMENT_PRODUCTION: Final[str] = "production"
        ENVIRONMENT_TEST: Final[str] = "test"

        ENVIRONMENTS: Final[t.StrSequence] = (
            ENVIRONMENT_DEVELOPMENT,
            ENVIRONMENT_STAGING,
            ENVIRONMENT_PRODUCTION,
            ENVIRONMENT_TEST,
        )
        ENVIRONMENT_SET: Final[frozenset[str]] = frozenset(ENVIRONMENTS)

        LOG_LEVEL_SET: Final[frozenset[str]] = frozenset({
            c.LogLevel.DEBUG,
            c.LogLevel.INFO,
            c.LogLevel.WARNING,
            c.LogLevel.ERROR,
            c.LogLevel.CRITICAL,
        })
        LOG_LEVEL_TO_EXPECTED: Final[Mapping[str, str]] = MappingProxyType({
            c.LogLevel.DEBUG: c.LogLevel.DEBUG,
            c.LogLevel.INFO: c.LogLevel.INFO,
            c.LogLevel.WARNING: c.LogLevel.WARNING,
            c.LogLevel.ERROR: c.LogLevel.ERROR,
            c.LogLevel.CRITICAL: c.LogLevel.CRITICAL,
        })
        LOG_LEVEL_SCENARIOS: Final[tuple[tuple[str, str], ...]] = (
            (c.LogLevel.DEBUG, c.LogLevel.DEBUG),
            (c.LogLevel.INFO, c.LogLevel.INFO),
            (c.LogLevel.WARNING, c.LogLevel.WARNING),
            (c.LogLevel.ERROR, c.LogLevel.ERROR),
            (c.LogLevel.CRITICAL, c.LogLevel.CRITICAL),
        )

        CONVERSION_STR_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.STR, "hello", "hello"),
            (c.Cli.TypeKind.STR, None, ""),
            (c.Cli.TypeKind.STR, 42, ""),
        )
        CONVERSION_BOOL_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.BOOL, True, True),
            (c.Cli.TypeKind.BOOL, False, False),
            (c.Cli.TypeKind.BOOL, None, False),
            (c.Cli.TypeKind.BOOL, "x", False),
        )
        CONVERSION_DICT_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.DICT, {"k": "v"}, {"k": "v"}),
            (c.Cli.TypeKind.DICT, None, {}),
            (c.Cli.TypeKind.DICT, "str", {}),
        )

        FILES_DETECT_FORMAT_CASES: Final[tuple[tuple[str, str], ...]] = (
            ("data.json", c.Cli.OutputFormats.JSON),
            ("data.yaml", c.Cli.OutputFormats.YAML),
            ("data.yml", c.Cli.OutputFormats.YAML),
            ("data.csv", c.Cli.OutputFormats.CSV),
            ("data.txt", c.Cli.OutputFormats.TEXT),
            ("data.log", c.Cli.OutputFormats.TEXT),
        )
        FILES_DETECT_FORMAT_FAIL_CASES: Final[tuple[str, ...]] = (
            "data.xml",
            "data.parquet",
            "data",
        )

        # ── YAML ────────────────────────────────────────────────────────
        YAML_VALID_CONTENT: Final[str] = _YAML_VALID_CONTENT
        YAML_INVALID_CONTENT: Final[str] = _YAML_INVALID_CONTENT
        YAML_NON_MAPPING_CONTENT: Final[str] = _YAML_NON_MAPPING_CONTENT
        YAML_EMPTY_CONTENT: Final[str] = _YAML_EMPTY_CONTENT
        YAML_NULL_CONTENT: Final[str] = _YAML_NULL_CONTENT

        # parse(text) → (text, expect_ok, expect_empty_dict)
        YAML_PARSE_CASES: Final[tuple[tuple[str, bool, bool], ...]] = (
            (_YAML_VALID_CONTENT, True, False),
            (_YAML_EMPTY_CONTENT, True, True),
            (_YAML_NULL_CONTENT, True, True),
            (_YAML_INVALID_CONTENT, False, False),
            (_YAML_NON_MAPPING_CONTENT, False, False),
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
            (_YAML_EMPTY_CONTENT, False),
            (_YAML_VALID_CONTENT, False),  # mapping not a list
        )

        # ── MATCHING ───────────────────────────────────────────────────
        # matches(msg, *patterns) → (msg, patterns, expected)
        MATCH_SIMPLE_CASES: Final[tuple[tuple[str, tuple[str, ...], bool], ...]] = (
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
        FORMATTER_TREE_LABELS: Final[tuple[str, ...]] = (
            "Root",
            "Branch",
            "",
        )

        # (columns, rows, title)
        FORMATTER_TABLE_CASES: Final[
            tuple[tuple[tuple[str, ...], tuple[tuple[str, ...], ...], str], ...]
        ] = (
            (("Name", "Value"), (("foo", "bar"), ("baz", "qux")), "My Table"),
            (("A",), (("1",),), ""),
            (("X", "Y", "Z"), (), "Empty"),
        )

        FORMATTER_PANEL_CASES: Final[tuple[tuple[str, str], ...]] = (
            ("Hello world content", "My Title"),
            ("No title content", ""),
        )

        FORMATTER_RULE_LABELS: Final[tuple[str, ...]] = (
            "Section Header",
            "Done",
            "",
        )

        # ── OUTPUT (services/output.py) ────────────────────────────────
        # display_message: (message, message_type | None)
        OUTPUT_DISPLAY_CASES: Final[
            tuple[tuple[str, c.Cli.MessageTypes | None], ...]
        ] = (
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
        OUTPUT_HEADER_LABELS: Final[tuple[str, ...]] = (
            "Section Start",
            "Processing",
            "",
        )

        OUTPUT_TEXT_CASES: Final[tuple[tuple[str, str | None], ...]] = (
            ("plain text", None),
            ("styled text", "bold blue"),
            ("", None),
        )

        # ── TABLES (services/tables.py) ────────────────────────────────
        # format_table: (data, config_kwargs, expect_ok)
        TABLE_FORMAT_CASES: Final[
            tuple[tuple[t.JsonMapping | list[t.JsonValue], dict[str, str], bool], ...]
        ] = (
            ({"a": 1, "b": 2}, {}, True),
            ([["x", "y"], ["1", "2"]], {}, True),
            ([{"col": "val"}], {"tablefmt": "grid"}, True),
        )

        # show_table: just data (no return value to assert)
        TABLE_SHOW_CASES: Final[tuple[t.JsonMapping | list[t.JsonValue], ...]] = (
            {"key": "val"},
            [["col1", "col2"], ["a", "b"]],
        )

        # ── AUTH (services/auth.py) ────────────────────────────────────
        # validate_credentials: (username, password, expect_ok)
        AUTH_CRED_CASES: Final[tuple[tuple[str, str, bool], ...]] = (
            ("admin", "secret123", True),
            ("", "secret123", False),
            ("admin", "", False),
            ("   ", "secret123", False),
        )

        # save_auth_token: (token, expect_ok)
        AUTH_TOKEN_SAVE_CASES: Final[tuple[tuple[str, bool], ...]] = (
            ("valid-token-abc123", True),
            ("", False),
            ("   ", False),
        )

        # auth_extract_token: (payload, expect_ok)
        AUTH_EXTRACT_CASES: Final[tuple[tuple[t.JsonValue, bool], ...]] = (
            ({c.Cli.DICT_KEY_AUTH_TOKEN: "mytoken"}, True),
            ({c.Cli.DICT_KEY_AUTH_TOKEN: ""}, False),
            ({}, False),
            ([], False),
            ("string", False),
        )

        # ── COMMANDS (services/commands.py) ────────────────────────────
        # execute_command: (name, registered, expect_ok)
        COMMANDS_EXEC_CASES: Final[tuple[tuple[str, bool, bool], ...]] = (
            ("run", True, True),
            ("missing", False, False),
            ("", False, False),
            ("   ", False, False),
        )

        COMMANDS_NAMES: Final[frozenset[str]] = frozenset({
            "init",
            "run",
            "status",
            "deploy",
        })

        # ── FORMATTERS (services/formatters.py) ───────────────────────
        FORMATTERS_PRINT_CASES: Final[tuple[tuple[str, str | None], ...]] = (
            ("Hello formatters", None),
            ("Styled", "bold green"),
            ("", None),
        )

        # ── RULES (services/rules.py) ──────────────────────────────────
        RULES_SCOPE_SETTINGS: Final[
            tuple[tuple[t.JsonValue, str, tuple[str, ...]], ...]
        ] = (
            ({"lint": {"rule_a": True, "rule_b": False}}, "lint", ("rule_a", "rule_b")),
            ({}, "lint", ("rule_a",)),
            ({"lint": {"extra": 1}}, "lint", ("rule_a",)),
        )

        RULES_SCOPE_CASES: Final[
            tuple[tuple[t.JsonValue, str, tuple[str, ...], int], ...]
        ] = (
            (
                {"lint": {"rule_a": True, "rule_b": False}},
                "lint",
                ("rule_a", "rule_b"),
                2,
            ),
            ({}, "lint", ("rule_a",), 0),
            ({"lint": {"extra": 1}}, "lint", ("rule_a",), 0),
            ({"lint": {"rule_a": 99, "unrelated": "x"}}, "lint", ("rule_a",), 1),
        )

        RULES_ALLOWED_KEYS: Final[frozenset[str]] = frozenset({
            "rule_a",
            "rule_b",
            "rule_c",
        })

        RULES_MATCH_FILTER_CASES: Final[
            tuple[tuple[str, tuple[str, ...], bool], ...]
        ] = (
            ("my-rule", (), True),
            ("my-rule", ("my-*",), True),
            ("my-rule", ("other-*",), False),
            ("my-rule", ("MY-RULE",), True),
            ("my-rule", ("*rule*",), True),
            ("my-rule", ("foobar",), False),
        )

        RULES_REGISTRY_YAML: Final[str] = "rules:\n  - id: rule-a\n    kind: lint\n"
        RULES_FILE_YAML: Final[str] = (
            "rules:\n"
            "  - id: rule-a\n"
            "    action: check\n"
            "    check: lint\n"
            "    config: {}\n"
        )
        RULES_FILE_NO_ID_YAML: Final[str] = (
            "rules:\n  - action: check\n    check: lint\n"
        )
        RULES_FILE_DISABLED_YAML: Final[str] = (
            "rules:\n"
            "  - id: rule-disabled\n"
            "    enabled: false\n"
            "    action: check\n"
            "    check: lint\n"
        )
        RULES_FILE_NO_MATCHER_KEYS_YAML: Final[str] = (
            "rules:\n  - id: rule-empty\n    description: no action or check\n"
        )
        RULES_FILE_UNKNOWN_YAML: Final[str] = (
            "rules:\n  - id: rule-unknown\n    action: unknown\n    check: unknown\n"
        )
        RULES_FILE_INVALID_MAPPING_YAML: Final[str] = (
            "rules:\n"
            "  - id: rule-invalid\n"
            "    action: check\n"
            "    check: lint\n"
            "    config: bad\n"
        )
        RULES_BASIC_MATCHER: Final[t.Cli.RuleMatcher] = (
            frozenset({"check"}),
            frozenset({"lint"}),
            frozenset(),
            frozenset(),
        )
        RULES_MAPPING_MATCHER: Final[t.Cli.RuleMatcher] = (
            frozenset({"check"}),
            frozenset({"lint"}),
            frozenset({"config"}),
            frozenset(),
        )
        RULES_LIST_MATCHER: Final[t.Cli.RuleMatcher] = (
            frozenset({"check"}),
            frozenset({"lint"}),
            frozenset(),
            frozenset({"actions"}),
        )
        RULES_CATALOG_BASIC: Final[t.Cli.RuleCatalog[str]] = MappingProxyType({
            "lint": (RULES_BASIC_MATCHER,),
        })
        RULES_CATALOG_MAPPING: Final[t.Cli.RuleCatalog[str]] = MappingProxyType({
            "lint": (RULES_MAPPING_MATCHER,),
        })
        RULES_FILE_CATALOG_BASIC: Final[t.Cli.RuleCatalog[str]] = MappingProxyType({
            "file-lint": (RULES_BASIC_MATCHER,),
        })
        RULES_FILE_CATALOG_MAPPING: Final[t.Cli.RuleCatalog[str]] = MappingProxyType({
            "file-lint": (RULES_MAPPING_MATCHER,),
        })

        # ── OPTIONS (utilities/options.py) ─────────────────────────────
        # Option registry for building Typer options
        OPTIONS_REGISTRY_VALID: Final[t.Cli.OptionRegistry] = MappingProxyType({
            "project": {
                "help": "Project name",
                "short": "p",
                "default": "",
            },
            "verbose": {
                "help": "Enable verbose output",
                "short": "v",
                "default": False,
            },
            "custom_name": {
                "help": "Custom option name",
                "short": "c",
                "default": "",
                c.Cli.CLI_PARAM_KEY_FIELD_NAME_OVERRIDE: "custom-name",
            },
        })
        OPTIONS_REGISTRY_EMPTY: Final[t.Cli.OptionRegistry] = MappingProxyType({})

        # (field_name, registry, expect_build_ok)
        OPTIONS_BUILD_CASES: Final[tuple[tuple[str, bool], ...]] = (
            ("project", True),
            ("verbose", True),
            ("custom_name", True),
        )
        OPTIONS_IS_STRING_SEQUENCE_CASES: Final[
            tuple[tuple[t.Cli.CliDefaultSource, bool], ...]
        ] = (
            (("alpha", "beta"), True),
            (["alpha", "beta"], True),
            ("alpha", False),
            (b"alpha", False),
        )
        OPTIONS_NORMALIZE_ATOM_CASES: Final[
            tuple[tuple[t.Cli.CliDefaultSource, t.Cli.DefaultAtom | None], ...]
        ] = (
            (True, True),
            ("value", "value"),
            (("alpha", "beta"), ("alpha", "beta")),
            (["alpha", "beta"], ("alpha", "beta")),
        )
        OPTIONS_REORDER_CASES: Final[
            tuple[
                tuple[
                    tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]
                ],
                ...,
            ]
        ] = (
            (
                ("--verbose", "build", "target"),
                ("--verbose",),
                (),
                ("build", "--verbose", "target"),
            ),
            (
                ("--project", "alpha", "deploy", "now"),
                (),
                ("--project",),
                ("deploy", "--project", "alpha", "now"),
            ),
            (
                ("--project=alpha", "deploy", "now"),
                (),
                ("--project",),
                ("deploy", "--project=alpha", "now"),
            ),
            (("build", "target"), ("--verbose",), ("--project",), ("build", "target")),
            (
                ("--unknown", "build"),
                ("--verbose",),
                ("--project",),
                ("--unknown", "build"),
            ),
        )
        OPTIONS_FIELD_DEFAULT_VALID_MAPPING: Final[t.Cli.DefaultMapping] = (
            MappingProxyType({
                "name": "alpha",
                "count": 3,
                "tags": ("x", "y"),
            })
        )
        OPTIONS_FIELD_DEFAULT_INVALID_MAPPING: Final[t.JsonMapping] = {
            "nested": {"ignore": True},
        }

        # ── TOML ───────────────────────────────────────────────────────
        TOML_VALID_CONTENT: Final[str] = _TOML_VALID_CONTENT
        TOML_INVALID_CONTENT: Final[str] = _TOML_INVALID_CONTENT
        TOML_SECTION_CONTENT: Final[str] = _TOML_SECTION_CONTENT

        # (content, expect_ok)
        TOML_READ_CASES: Final[tuple[tuple[str, bool], ...]] = (
            (_TOML_VALID_CONTENT, True),
            (_TOML_SECTION_CONTENT, True),
            (_TOML_INVALID_CONTENT, False),
        )

        TOML_NESTED_PATH_CASES: Final[
            tuple[tuple[tuple[str, ...], t.JsonValue | None], ...]
        ] = (
            (("tool", "flext", "project"), "my-project"),
            (("tool", "missing", "key"), None),
            (("nonexistent",), None),
        )

        # ── TABLES (_utilities/tables.py) ─────────────────────────────
        # tables_normalize_data: (data, expect_ok)
        TABLE_NORMALIZE_CASES: Final[
            tuple[tuple[t.JsonMapping | list[t.JsonValue], bool], ...]
        ] = (
            ({"key": "val"}, True),
            ([["a", "b"], ["c", "d"]], True),
            ([{"col": "val"}], True),
        )

        # tables_resolve_config: (kwargs, expect_ok)
        TABLE_CONFIG_CASES: Final[tuple[tuple[t.JsonMapping, bool], ...]] = (
            ({}, True),
            ({"table_format": c.Cli.TabularFormat.GRID}, True),
            ({"table_format": c.Cli.TabularFormat.PLAIN}, True),
        )

        # ── COMMANDS (_utilities/commands.py) ──────────────────────────
        CMD_NAMES_VALID: Final[tuple[str, ...]] = ("build", "test", "deploy")
        CMD_NAMES_INVALID: Final[tuple[str, ...]] = ("", "  ")

        # ── AUTH (_utilities/auth.py) ──────────────────────────────────
        AUTH_TOKEN_FILE_CASES: Final[tuple[tuple[str | None, bool], ...]] = (
            ("custom_path.json", True),
            (None, True),
            ("", True),
            ("  ", True),
        )

        AUTH_EXTRACT_PAYLOAD_CASES: Final[tuple[tuple[t.JsonValue, bool], ...]] = (
            ({c.Cli.DICT_KEY_AUTH_TOKEN: "token123"}, True),
            ({c.Cli.DICT_KEY_AUTH_TOKEN: ""}, False),
            ({}, False),
            ("not-a-mapping", False),
        )


c = TestsFlextCliConstants

__all__: list[str] = ["TestsFlextCliConstants", "c"]
