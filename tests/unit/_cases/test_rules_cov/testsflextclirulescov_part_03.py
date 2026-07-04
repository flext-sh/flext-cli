"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_load_local_definitions_rule_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "invalid.yml").write_text(
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML,
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_MAPPING,
            )
            assert result.failure
            assert "config must be a mapping" in (result.error or "")

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
            assert result.success
            assert isinstance(result.value, (list, tuple))
            assert result.value[1][0][0] == "file-lint"

    def test_rules_load_local_definitions_file_catalog_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "file-invalid.yml").write_text(
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML,
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
            assert result.failure
            assert "config must be a mapping" in (result.error or "")

    def test_rules_matches_filters_empty(self) -> None:
        assert u.Cli.rules_matches_filters("rule-a", ()) is True

    @pytest.mark.parametrize(
        ("rule_id", "rule_filters", "expected"),
        c.Tests.RULES_MATCH_FILTER_CASES,
    )
    def test_rules_matches_filters_parametrized(
        self,
        rule_id: str,
        rule_filters: t.StrSequence,
        expected: bool,
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
            assert result == rules_dir

    def test_rules_resolve_directory_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_rules = Path(tmpdir) / "pkg_rules"
            pkg_rules.mkdir()
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_resolve_directory(
                config_path,
                package_rules_dir=pkg_rules,
                rules_dir_name="rules",
            )
            assert result == pkg_rules

    def test_rules_match_catalog_entry_by_action(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("check", "", catalog)
        assert result is not None
        assert result[0] == "lint"

    def test_rules_match_catalog_entry_by_check(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("", "lint", catalog)
        assert result is not None

    def test_rules_match_catalog_entry_no_match(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = u.Cli.rules_match_catalog_entry("unknown", "unknown", catalog)
        assert result is None


__all__: list[str] = ["TestsFlextCliRulesCov"]
