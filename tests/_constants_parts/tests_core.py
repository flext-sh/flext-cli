"""Split test constants namespace."""

from __future__ import annotations

import re
from enum import StrEnum, unique
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from flext_cli import c

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliConstantsCore:
    """Split test constants namespace."""

    AUTH_TOKEN_MIN_LENGTH: Final[int] = 20
    AUTH_VALUE_SAMPLE: Final[str] = "token-123"
    COMMAND_DURATION_TOLERANCE: Final[float] = 1e-9
    CREDENTIAL_SAMPLE_VALUE: Final[str] = "secret-pass"
    DOCUMENT_STACK_MODULES: Final[t.StrSequence] = ("openpyxl", "docx", "pptx")
    ENV_EXPAND_HOME_VALUE: Final[str] = "/home/tester"
    ENV_EXPAND_OPT_VALUE: Final[str] = "/opt/x"
    ENV_READ_ABSENT_NAME: Final[str] = "FLEXT_CLI_ENV_READ_ABSENT"
    ENV_READ_CASES: Final[t.MappingKV[str, str]] = MappingProxyType({
        "FLEXT_CLI_ENV_READ_A": "value-a",
        "FLEXT_CLI_ENV_READ_B": "value-b",
    })
    ENV_READ_PROBE_NAME: Final[str] = "FLEXT_CLI_ENV_READ_PROBE"
    ENV_READ_PROBE_VALUE: Final[str] = "probe-value"
    VERSION_COMPATIBLE: Final[str] = "1.0"
    VERSION_VALID_SEMVER: Final[str] = "1.2.3"
    VERSION_VALID_SEMVER_COMPLEX: Final[str] = "1.2.3-alpha.1+build.123"

    @unique
    class Environment(StrEnum):
        """Canonical environments used in flext-cli tests."""

        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
        TEST = "test"

    MATCH_REGEX_PHONE_RE: Final[t.RegexPattern] = re.compile(r"\d{3}-\d{4}")
    MATCH_REGEX_ALPHA_RE: Final[t.RegexPattern] = re.compile(r"alpha")
    MATCH_REGEX_BETA_RE: Final[t.RegexPattern] = re.compile(r"beta")

    PROMPT_EDGE_MESSAGES: Final[t.StrSequence] = (
        "",
        (
            "This is a very long message that tests how the system "
            "handles extended text input"
        ),
        "!@#$%^&*()",
        "你好世界🌍",
    )

    VERSION_STR_CASES: Final[t.MappingKV[str, str]] = MappingProxyType({
        "valid_semver": VERSION_VALID_SEMVER,
        "valid_semver_complex": VERSION_VALID_SEMVER_COMPLEX,
        "invalid_no_dots": "version",
        "invalid_non_numeric": "a.b.c",
    })

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
    FILES_DETECT_FORMAT_FAIL_CASES: Final[t.StrSequence] = (
        "data.xml",
        "data.parquet",
        "data",
    )


__all__: list[str] = ["TestsFlextCliConstantsCore"]
