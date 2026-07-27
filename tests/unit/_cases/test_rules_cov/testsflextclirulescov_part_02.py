"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_tests import tm
from tests import c, u


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_load_local_definitions_no_dir(self) -> None:
        """Verify that rules load local definitions no dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't create pkg_rules_dir or local rules/ dir — triggers failure path
            pkg_rules_dir = Path(tmpdir) / "pkg_rules"
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=pkg_rules_dir,
                rule_filters=(),
                rule_catalog={},
            )
            tm.fail(result)

    def test_rules_load_local_definitions_with_rules(self) -> None:
        """Verify that rules load local definitions with rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=catalog,
            )
            tm.ok(result)

    def test_rules_load_local_definitions_with_filter(self) -> None:
        """Verify that rules load local definitions with filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=("rule-*",),
                rule_catalog=catalog,
            )
            tm.ok(result)

    def test_rules_load_local_definitions_filter_excludes(self) -> None:
        """Verify that rules load local definitions filter excludes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=("nonmatch-*",),
                rule_catalog=catalog,
            )
            tm.ok(result)

    def test_rules_load_local_definitions_skips_registry_missing_id_disabled_and_empty_matchers(
        self,
    ) -> None:
        """Skip malformed, disabled, and empty local rule definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "engine-registry.yml").write_text(c.Tests.RULES_REGISTRY_YAML)
            (rules_dir / "no-id.yml").write_text(c.Tests.RULES_FILE_NO_ID_YAML)
            (rules_dir / "disabled.yml").write_text(c.Tests.RULES_FILE_DISABLED_YAML)
            (rules_dir / "empty.yml").write_text(
                c.Tests.RULES_FILE_NO_MATCHER_KEYS_YAML
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            )
            tm.ok(result)
            tm.that(result.value, eq=([], []))

    def test_rules_load_local_definitions_unknown_rule_fails(self) -> None:
        """Verify that rules load local definitions unknown rule fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "unknown.yml").write_text(c.Tests.RULES_FILE_UNKNOWN_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            )
            tm.fail(result)
            tm.that((result.error or ""), has="rule-unknown")


__all__: list[str] = ["TestsFlextCliRulesCov"]
