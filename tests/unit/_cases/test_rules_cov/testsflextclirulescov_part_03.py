"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from tests import c
from tests import u
from flext_tests import tm

from tests import t


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_load_local_definitions_rule_validation_fails(self) -> None:
        """Verify that rules load local definitions rule validation fails."""
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
        """Verify that rules load local definitions file catalog success."""
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
        """Verify that rules load local definitions file catalog validation fails."""
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
        """Verify that rules matches filters empty."""
        tm.that(u.Cli.rules_matches_filters("rule-a", ()), eq=True)

    @pytest.mark.parametrize(
        ("rule_id", "rule_filters", "expected"), c.Tests.RULES_MATCH_FILTER_CASES
    )
    def test_rules_matches_filters_parametrized(
        self, rule_id: str, rule_filters: t.StrSequence, *, expected: bool
    ) -> None:
        """Verify that rules matches filters parametrized."""
        result = u.Cli.rules_matches_filters(rule_id, rule_filters)
        tm.that(result is expected, eq=True)

    def test_rules_resolve_directory_local(self) -> None:
        """Verify that rules resolve directory local."""
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
        """Verify that rules resolve directory fallback."""
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
        """Verify that rules match catalog entry by action."""
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("check", "", catalog)
        result = tm.not_none(result)
        tm.that(result[0], eq="lint")

    def test_rules_match_catalog_entry_by_check(self) -> None:
        """Verify that rules match catalog entry by check."""
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("", "lint", catalog)
        result = tm.not_none(result)

    def test_rules_match_catalog_entry_no_match(self) -> None:
        """Verify that rules match catalog entry no match."""
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("unknown", "unknown", catalog)
        tm.that(result, none=True)


__all__: list[str] = ["TestsFlextCliRulesCov"]
