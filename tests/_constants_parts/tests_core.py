"""Split test constants namespace."""

from __future__ import annotations

import re
from enum import StrEnum, unique
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from flext_cli import c

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliConstantsCore:
    """Split test constants namespace."""

    AUTH_TOKEN_MIN_LENGTH: ClassVar[int] = 20
    AUTH_VALUE_SAMPLE: ClassVar[str] = "token-123"
    COMMAND_DURATION_TOLERANCE: ClassVar[float] = 1e-9
    CREDENTIAL_SAMPLE_VALUE: ClassVar[str] = "secret-pass"
    DOCUMENT_STACK_MODULES: ClassVar[t.StrSequence] = ("openpyxl", "docx", "pptx")
    ENV_READ_ABSENT_NAME: ClassVar[str] = "FLEXT_CLI_ENV_READ_ABSENT"
    ENV_READ_CASES: ClassVar[t.MappingKV[str, str]] = MappingProxyType({
        "FLEXT_CLI_ENV_READ_A": "value-a",
        "FLEXT_CLI_ENV_READ_B": "value-b",
    })
    ENV_READ_PROBE_NAME: ClassVar[str] = "FLEXT_CLI_ENV_READ_PROBE"
    ENV_READ_PROBE_VALUE: ClassVar[str] = "probe-value"
    VERSION_VALID_SEMVER: ClassVar[str] = c.Cli.CLI_VERSION
    VERSION_COMPATIBLE: ClassVar[str] = ".".join(VERSION_VALID_SEMVER.split(".")[:2])
    VERSION_VALID_SEMVER_COMPLEX: ClassVar[str] = "1.2.3-alpha.1+build.123"

    @unique
    class Environment(StrEnum):
        """Canonical environments used in flext-cli tests."""

        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
        TEST = "test"

    MATCH_REGEX_PHONE_RE: ClassVar[t.RegexPattern] = re.compile(r"\d{3}-\d{4}")
    MATCH_REGEX_ALPHA_RE: ClassVar[t.RegexPattern] = re.compile(r"alpha")
    MATCH_REGEX_BETA_RE: ClassVar[t.RegexPattern] = re.compile(r"beta")

    PROMPT_EDGE_MESSAGES: ClassVar[t.StrSequence] = (
        "",
        (
            "This is a very long message that tests how the system "
            "handles extended text input"
        ),
        "!@#$%^&*()",
        "你好世界🌍",
    )

    PROMPT_SHORT_ENV_NAME: ClassVar[str] = "FLEXT_TEST_PROMPT_SHORT"
    PROMPT_VALID_ENV_NAME: ClassVar[str] = "FLEXT_TEST_PROMPT_VALID"

    VERSION_STR_CASES: ClassVar[t.MappingKV[str, str]] = MappingProxyType({
        "valid_semver": VERSION_VALID_SEMVER,
        "valid_semver_complex": VERSION_VALID_SEMVER_COMPLEX,
        "invalid_no_dots": "version",
        "invalid_non_numeric": "a.b.c",
    })

    CONVERSION_STR_CASES: ClassVar[
        t.VariadicTuple[t.Triple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue]]
    ] = (
        (c.Cli.TypeKind.STR, "hello", "hello"),
        (c.Cli.TypeKind.STR, None, ""),
        (c.Cli.TypeKind.STR, 42, ""),
    )
    CONVERSION_BOOL_CASES: ClassVar[
        t.VariadicTuple[t.Triple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue]]
    ] = (
        (c.Cli.TypeKind.BOOL, True, True),
        (c.Cli.TypeKind.BOOL, False, False),
        (c.Cli.TypeKind.BOOL, None, False),
        (c.Cli.TypeKind.BOOL, "x", False),
    )
    CONVERSION_DICT_CASES: ClassVar[
        t.VariadicTuple[t.Triple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue]]
    ] = (
        (c.Cli.TypeKind.DICT, {"k": "v"}, {"k": "v"}),
        (c.Cli.TypeKind.DICT, None, {}),
        (c.Cli.TypeKind.DICT, "str", {}),
    )

    FILES_DETECT_FORMAT_CASES: ClassVar[t.VariadicTuple[t.Pair[str, str]]] = (
        ("data.json", c.Cli.OutputFormats.JSON),
        ("data.yaml", c.Cli.OutputFormats.YAML),
        ("data.yml", c.Cli.OutputFormats.YAML),
        ("data.csv", c.Cli.OutputFormats.CSV),
        ("data.txt", c.Cli.OutputFormats.TEXT),
        ("data.log", c.Cli.OutputFormats.TEXT),
    )
    FILES_DETECT_FORMAT_FAIL_CASES: ClassVar[t.StrSequence] = (
        "data.xml",
        "data.parquet",
        "data",
    )


__all__: list[str] = ["TestsFlextCliConstantsCore"]
