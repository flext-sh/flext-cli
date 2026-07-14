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

    VERSION_EMPTY_MSG: Final[str] = "Version must be non-empty string"
    VERSION_INFO_TOO_SHORT_MSG: Final[str] = "Version info must have at least 3 parts"

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
        "valid_semver": "1.2.3",
        "valid_semver_complex": "1.2.3-alpha.1+build.123",
        "invalid_no_dots": "version",
        "invalid_non_numeric": "a.b.c",
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
