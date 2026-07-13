"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from tests import c
from tests import u
from flext_tests import tm

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_load_local_definitions_rule_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "invalid.yml").write_text(
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_MAPPING,
            )
            tm.fail(result)
            tm.that((result.error or ""), has="config must be a mapping")

    def test_rules_load_local_definitions_file_catalog_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "file.yml").write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
                file_rule_catalog=c.Tests.RULES_FILE_CATALOG_BASIC,
            )
            tm.ok(result)
            tm.that(result.value, is_=(list, tuple))
            tm.that(result.value[1][0][0], eq="file-lint")

    def test_rules_load_local_definitions_file_catalog_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "file-invalid.yml").write_text(
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
                file_rule_catalog=c.Tests.RULES_FILE_CATALOG_MAPPING,
            )
            tm.fail(result)
            tm.that((result.error or ""), has="config must be a mapping")

    def test_rules_matches_filters_empty(self) -> None:
        tm.that(u.Cli.rules_matches_filters("rule-a", ()), eq=True)

    @pytest.mark.parametrize(
        ("rule_id", "rule_filters", "expected"), c.Tests.RULES_MATCH_FILTER_CASES
    )
    def test_rules_matches_filters_parametrized(
        self, rule_id: str, rule_filters: t.StrSequence, expected: bool
    ) -> None:
        result = u.Cli.rules_matches_filters(rule_id, rule_filters)
        assert result is expected

    def test_rules_resolve_directory_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_resolve_directory(
                config_path,
                package_rules_dir=Path(tmpdir) / "pkg_rules",
                rules_dir_name="rules",
            )
            tm.that(result, eq=rules_dir)

    def test_rules_resolve_directory_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_rules = Path(tmpdir) / "pkg_rules"
            pkg_rules.mkdir()
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_resolve_directory(
                config_path, package_rules_dir=pkg_rules, rules_dir_name="rules"
            )
            tm.that(result, eq=pkg_rules)

    def test_rules_match_catalog_entry_by_action(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("check", "", catalog)
        tm.that(result, none=False)
        tm.that(result[0], eq="lint")

    def test_rules_match_catalog_entry_by_check(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("", "lint", catalog)
        tm.that(result, none=False)

    def test_rules_match_catalog_entry_no_match(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("unknown", "unknown", catalog)
        tm.that(result, none=True)


__all__: list[str] = ["TestsFlextCliRulesCov"]
