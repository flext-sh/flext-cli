"""Behavioral tests for the ``u.Cli.rules_*`` declarative rule-loading DSL.

Exercises the public contract exposed through ``FlextCliUtilitiesRules`` /
``FlextCliRules``: scope resolution, YAML config/registry loading, local
definition matching against declarative catalogs, filter matching, directory
resolution, catalog lookup, and matcher validation. Assertions target observable
return values and ``r[T]`` outcomes (success/failure, value, error) only.
"""

from __future__ import annotations


import pytest

from tests import c
from tests import u
from flext_tests import tm

from pathlib import Path

from tests import t


class TestsFlextCliRulesCov:
    """Public behavioral contract for the local-rule loading DSL."""

    @staticmethod
    def _seed(tmp_path: Path, files: t.StrMapping) -> Path:
        """Write a ``rules/`` dir + ``config.yml`` and return the config path."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(exist_ok=True)
        for name, content in files.items():
            (rules_dir / name).write_text(content)
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        return config_path

    # ------------------------------------------------------------------ scope

    def test_resolve_scope_keeps_only_allowed_keys_with_values(self) -> None:
        result = u.Cli.rules_resolve_scope(
            {"lint": {"rule_a": True, "rule_b": False}},
            scope_key="lint",
            allowed_keys=("rule_a", "rule_b"),
        )
        tm.that(result, eq={"rule_a": True, "rule_b": False})

    @pytest.mark.parametrize(
        ("settings", "scope_key", "allowed_keys", "expected_len"),
        c.Tests.RULES_SCOPE_CASES,
    )
    def test_resolve_scope_filters_to_allowed_key_count(
        self,
        settings: t.JsonValue,
        scope_key: str,
        allowed_keys: t.StrSequence,
        expected_len: int,
    ) -> None:
        result = u.Cli.rules_resolve_scope(
            settings, scope_key=scope_key, allowed_keys=allowed_keys
        )
        tm.that(len(result), eq=expected_len)
        assert all(key in allowed_keys for key in result)

    def test_load_scoped_config_returns_normalized_scope(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yml"
        config_path.write_text("lint:\n  rule_a: true\n  rule_b: false\n")
        result = u.Cli.rules_load_scoped_config(
            config_path, scope_key="lint", allowed_keys=("rule_a", "rule_b")
        )
        tm.ok(result)
        tm.that(result.value["lint"], eq={"rule_a": True, "rule_b": False})

    # --------------------------------------------------------------- registry

    def test_load_registry_from_local_rules_dir(self, tmp_path: Path) -> None:
        config_path = self._seed(
            tmp_path, {"engine-registry.yml": c.Tests.RULES_REGISTRY_YAML}
        )
        result = u.Cli.rules_load_registry(
            config_path,
            package_rules_dir=tmp_path / "pkg_rules",
            registry_filename="engine-registry.yml",
            rules_dir_name="rules",
        )
        tm.ok(result)
        tm.that(result.value, eq={"rules": [{"id": "rule-a", "kind": "lint"}]})

    def test_load_registry_falls_back_to_package_dir(self, tmp_path: Path) -> None:
        pkg_rules_dir = tmp_path / "pkg_rules"
        pkg_rules_dir.mkdir()
        (pkg_rules_dir / "engine-registry.yml").write_text(c.Tests.RULES_REGISTRY_YAML)
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        result = u.Cli.rules_load_registry(
            config_path,
            package_rules_dir=pkg_rules_dir,
            registry_filename="engine-registry.yml",
        )
        tm.ok(result)
        tm.that(result.value, eq={"rules": [{"id": "rule-a", "kind": "lint"}]})

    def test_load_registry_prefers_local_over_package(self, tmp_path: Path) -> None:
        package_rules_dir = tmp_path / "pkg_rules"
        package_rules_dir.mkdir()
        (package_rules_dir / "engine-registry.yml").write_text(
            "rules:\n  - id: package-rule\n"
        )
        config_path = self._seed(
            tmp_path, {"engine-registry.yml": c.Tests.RULES_REGISTRY_YAML}
        )
        result = u.Cli.rules_load_registry(
            config_path,
            package_rules_dir=package_rules_dir,
            registry_filename="engine-registry.yml",
        )
        tm.ok(result)
        tm.that(result.value, eq={"rules": [{"id": "rule-a", "kind": "lint"}]})

    def test_load_registry_missing_file_fails_with_message(
        self, tmp_path: Path
    ) -> None:
        pkg_rules_dir = tmp_path / "pkg_rules"
        pkg_rules_dir.mkdir()
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        result = u.Cli.rules_load_registry(
            config_path,
            package_rules_dir=pkg_rules_dir,
            registry_filename="engine-registry.yml",
        )
        tm.fail(result)
        tm.that((result.error or ""), has="engine-registry.yml")

    # ------------------------------------------------- local rule definitions

    def test_load_local_definitions_missing_dir_fails(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "pkg_rules",
            rule_filters=(),
            rule_catalog={},
        )
        tm.fail(result)
        tm.that((result.error or ""), has="not found")

    def test_load_local_definitions_loads_matching_rule(self, tmp_path: Path) -> None:
        config_path = self._seed(tmp_path, {"test-rule.yml": c.Tests.RULES_FILE_YAML})
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
        )
        tm.ok(result)
        loaded_rules, loaded_file_rules = result.value
        tm.that(loaded_file_rules, eq=[])
        tm.that(loaded_rules[0][0], eq="lint")
        tm.that(loaded_rules[0][1]["id"], eq="rule-a")

    def test_load_local_definitions_keeps_rule_when_filter_matches(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(tmp_path, {"test-rule.yml": c.Tests.RULES_FILE_YAML})
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=("rule-*",),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
        )
        tm.ok(result)
        tm.that(result.value[0][0][0], eq="lint")

    def test_load_local_definitions_drops_rule_when_filter_excludes(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(tmp_path, {"test-rule.yml": c.Tests.RULES_FILE_YAML})
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=("nonmatch-*",),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
        )
        tm.ok(result)
        tm.that(result.value, eq=([], []))

    def test_load_local_definitions_skips_registry_noid_disabled_empty(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(
            tmp_path,
            {
                "engine-registry.yml": c.Tests.RULES_REGISTRY_YAML,
                "no-id.yml": c.Tests.RULES_FILE_NO_ID_YAML,
                "disabled.yml": c.Tests.RULES_FILE_DISABLED_YAML,
                "empty.yml": c.Tests.RULES_FILE_NO_MATCHER_KEYS_YAML,
            },
        )
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
        )
        tm.ok(result)
        tm.that(result.value, eq=([], []))

    def test_load_local_definitions_unknown_rule_fails(self, tmp_path: Path) -> None:
        config_path = self._seed(
            tmp_path, {"unknown.yml": c.Tests.RULES_FILE_UNKNOWN_YAML}
        )
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
        )
        tm.fail(result)
        tm.that((result.error or ""), has="rule-unknown")

    def test_load_local_definitions_matcher_validation_fails(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(
            tmp_path, {"invalid.yml": c.Tests.RULES_FILE_INVALID_MAPPING_YAML}
        )
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_MAPPING,
        )
        tm.fail(result)
        tm.that((result.error or ""), has="config must be a mapping")

    def test_load_local_definitions_routes_to_file_catalog(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(tmp_path, {"file.yml": c.Tests.RULES_FILE_YAML})
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            file_rule_catalog=c.Tests.RULES_FILE_CATALOG_BASIC,
        )
        tm.ok(result)
        loaded_rules, loaded_file_rules = result.value
        tm.that(loaded_rules, eq=[])
        tm.that(loaded_file_rules[0][0], eq="file-lint")

    def test_load_local_definitions_file_catalog_validation_fails(
        self, tmp_path: Path
    ) -> None:
        config_path = self._seed(
            tmp_path, {"file-invalid.yml": c.Tests.RULES_FILE_INVALID_MAPPING_YAML}
        )
        result = u.Cli.rules_load_local_definitions(
            config_path,
            package_rules_dir=tmp_path / "rules",
            rule_filters=(),
            rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            file_rule_catalog=c.Tests.RULES_FILE_CATALOG_MAPPING,
        )
        tm.fail(result)
        tm.that((result.error or ""), has="config must be a mapping")

    # ----------------------------------------------------------------- filters

    def test_matches_filters_empty_filter_matches_any(self) -> None:
        tm.that(u.Cli.rules_matches_filters("rule-a", ()), eq=True)

    @pytest.mark.parametrize(
        ("rule_id", "rule_filters", "expected"), c.Tests.RULES_MATCH_FILTER_CASES
    )
    def test_matches_filters_glob_and_substring(
        self, rule_id: str, rule_filters: t.StrSequence, expected: bool
    ) -> None:
        assert u.Cli.rules_matches_filters(rule_id, rule_filters) is expected

    # ------------------------------------------------------- directory resolve

    def test_resolve_directory_prefers_local_rules_dir(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        result = u.Cli.rules_resolve_directory(
            config_path,
            package_rules_dir=tmp_path / "pkg_rules",
            rules_dir_name="rules",
        )
        tm.that(result, eq=rules_dir)

    def test_resolve_directory_falls_back_to_package(self, tmp_path: Path) -> None:
        pkg_rules = tmp_path / "pkg_rules"
        pkg_rules.mkdir()
        config_path = tmp_path / "config.yml"
        config_path.write_text("project: test\n")
        result = u.Cli.rules_resolve_directory(
            config_path, package_rules_dir=pkg_rules, rules_dir_name="rules"
        )
        tm.that(result, eq=pkg_rules)

    # ------------------------------------------------------------- catalog lookup

    def test_match_catalog_entry_by_action(self) -> None:
        result = u.Cli.rules_match_catalog_entry(
            "check", "", c.Tests.RULES_CATALOG_BASIC
        )
        tm.that(result, none=False)
        tm.that(result[0], eq="lint")

    def test_match_catalog_entry_by_check(self) -> None:
        result = u.Cli.rules_match_catalog_entry(
            "", "lint", c.Tests.RULES_CATALOG_BASIC
        )
        tm.that(result, none=False)
        tm.that(result[0], eq="lint")

    def test_match_catalog_entry_no_match_returns_none(self) -> None:
        result = u.Cli.rules_match_catalog_entry(
            "unknown", "unknown", c.Tests.RULES_CATALOG_BASIC
        )
        tm.that(result, none=True)

    # ------------------------------------------------------- matcher validation

    def test_validate_matcher_valid_returns_none(self) -> None:
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": ["check"]}
        result = u.Cli.rules_validate_matcher(
            rule_def, c.Tests.RULES_BASIC_MATCHER, rule_id_key="id"
        )
        tm.that(result, none=True)

    def test_validate_matcher_reports_non_mapping_field(self) -> None:
        rule_def: t.JsonMapping = {"id": "rule-a", "config": "not-a-mapping"}
        result = u.Cli.rules_validate_matcher(
            rule_def, c.Tests.RULES_MAPPING_MATCHER, rule_id_key="id"
        )
        tm.that(result, none=False)
        tm.that(result, has="config must be a mapping")

    def test_validate_matcher_reports_empty_required_list(self) -> None:
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": []}
        result = u.Cli.rules_validate_matcher(
            rule_def, c.Tests.RULES_LIST_MATCHER, rule_id_key="id"
        )
        tm.that(result, none=False)
        tm.that(result, has="actions must be a non-empty list")


__all__: list[str] = ["TestsFlextCliRulesCov"]
