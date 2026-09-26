"""Split test constants namespace."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from flext_cli import c

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliConstantsRulesOptions:
    """Split test constants namespace."""

    # ── RULES (services/rules.py) ──────────────────────────────────
    RULES_SCOPE_CASES: ClassVar[
        t.VariadicTuple[t.Quad[t.JsonValue, str, t.StrSequence, int]]
    ] = (
        ({"lint": {"rule_a": True, "rule_b": False}}, "lint", ("rule_a", "rule_b"), 2),
        ({}, "lint", ("rule_a",), 0),
        ({"lint": {"extra": 1}}, "lint", ("rule_a",), 0),
        ({"lint": {"rule_a": 99, "unrelated": "x"}}, "lint", ("rule_a",), 1),
    )

    RULES_MATCH_FILTER_CASES: ClassVar[
        t.VariadicTuple[t.Triple[str, t.StrSequence, bool]]
    ] = (
        ("my-rule", (), True),
        ("my-rule", ("my-*",), True),
        ("my-rule", ("other-*",), False),
        ("my-rule", ("MY-RULE",), True),
        ("my-rule", ("*rule*",), True),
        ("my-rule", ("foobar",), False),
    )

    RULES_REGISTRY_YAML: ClassVar[str] = "rules:\n  - id: rule-a\n    kind: lint\n"
    RULES_FILE_YAML: ClassVar[str] = (
        "rules:\n  - id: rule-a\n    action: check\n    check: lint\n    config: {}\n"
    )
    RULES_FILE_NO_ID_YAML: ClassVar[str] = (
        "rules:\n  - action: check\n    check: lint\n"
    )
    RULES_FILE_DISABLED_YAML: ClassVar[str] = (
        "rules:\n"
        "  - id: rule-disabled\n"
        "    enabled: false\n"
        "    action: check\n"
        "    check: lint\n"
    )
    RULES_FILE_NO_MATCHER_KEYS_YAML: ClassVar[str] = (
        "rules:\n  - id: rule-empty\n    description: no action or check\n"
    )
    RULES_FILE_UNKNOWN_YAML: ClassVar[str] = (
        "rules:\n  - id: rule-unknown\n    action: unknown\n    check: unknown\n"
    )
    RULES_FILE_INVALID_MAPPING_YAML: ClassVar[str] = (
        "rules:\n"
        "  - id: rule-invalid\n"
        "    action: check\n"
        "    check: lint\n"
        "    config: bad\n"
    )
    RULES_BASIC_MATCHER: ClassVar[t.Cli.RuleMatcher] = (
        frozenset({"check"}),
        frozenset({"lint"}),
        frozenset(),
        frozenset(),
    )
    RULES_MAPPING_MATCHER: ClassVar[t.Cli.RuleMatcher] = (
        frozenset({"check"}),
        frozenset({"lint"}),
        frozenset({"config"}),
        frozenset(),
    )
    RULES_LIST_MATCHER: ClassVar[t.Cli.RuleMatcher] = (
        frozenset({"check"}),
        frozenset({"lint"}),
        frozenset(),
        frozenset({"actions"}),
    )
    RULES_CATALOG_BASIC: ClassVar[t.Cli.RuleCatalog[str]] = MappingProxyType({
        "lint": (RULES_BASIC_MATCHER,)
    })
    RULES_CATALOG_MAPPING: ClassVar[t.Cli.RuleCatalog[str]] = MappingProxyType({
        "lint": (RULES_MAPPING_MATCHER,)
    })
    RULES_FILE_CATALOG_BASIC: ClassVar[t.Cli.RuleCatalog[str]] = MappingProxyType({
        "file-lint": (RULES_BASIC_MATCHER,)
    })
    RULES_FILE_CATALOG_MAPPING: ClassVar[t.Cli.RuleCatalog[str]] = MappingProxyType({
        "file-lint": (RULES_MAPPING_MATCHER,)
    })

    # ── TOML ───────────────────────────────────────────────────────
    TOML_VALID_CONTENT: ClassVar[str] = (
        f'[tool.flext]\nproject = "my-project"\nversion = "{c.Cli.CLI_VERSION}"\n'
    )
    TOML_INVALID_CONTENT: ClassVar[str] = "[invalid toml\nmissing = "
    TOML_SECTION_CONTENT: ClassVar[str] = "[section]\nkey = true\ncount = 42\n"


__all__: list[str] = ["TestsFlextCliConstantsRulesOptions"]
