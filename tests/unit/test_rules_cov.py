"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from flext_cli._utilities.rules import FlextCliUtilitiesRules
from flext_cli.services.rules import FlextCliRules
from tests import c, t


class TestsFlextCliRulesUtilsCov:
    """Coverage for FlextCliUtilitiesRules."""

    def test_rules_resolve_scope_with_data(self) -> None:
        result = FlextCliUtilitiesRules.rules_resolve_scope(
            {"lint": {"rule_a": True, "rule_b": False}},
            scope_key="lint",
            allowed_keys=("rule_a", "rule_b"),
        )
        assert "rule_a" in result
        assert "rule_b" in result

    @pytest.mark.parametrize(
        ("settings", "scope_key", "allowed_keys", "expected_len"),
        c.Tests.RULES_SCOPE_CASES,
    )
    def test_rules_resolve_scope_parametrized(
        self,
        settings: t.JsonValue,
        scope_key: str,
        allowed_keys: tuple[str, ...],
        expected_len: int,
    ) -> None:
        result = FlextCliUtilitiesRules.rules_resolve_scope(
            settings,
            scope_key=scope_key,
            allowed_keys=allowed_keys,
        )
        assert len(result) == expected_len

    def test_rules_load_scoped_config_valid(self) -> None:
        yaml_content = "lint:\n  rule_a: true\n  rule_b: false\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            config_path = Path(f.name)
        result = FlextCliUtilitiesRules.rules_load_scoped_config(
            config_path,
            scope_key="lint",
            allowed_keys=("rule_a", "rule_b"),
        )
        assert result.success

    def test_rules_load_registry_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            registry_file = rules_dir / "engine-registry.yml"
            registry_file.write_text(c.Tests.RULES_REGISTRY_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_registry(
                config_path,
                package_rules_dir=rules_dir,
                registry_filename="engine-registry.yml",
                rules_dir_name="rules",
            )
            assert result.success

    def test_rules_load_registry_package_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_rules_dir = Path(tmpdir) / "pkg_rules"
            pkg_rules_dir.mkdir()
            registry_file = pkg_rules_dir / "engine-registry.yml"
            registry_file.write_text(c.Tests.RULES_REGISTRY_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_registry(
                config_path,
                package_rules_dir=pkg_rules_dir,
                registry_filename="engine-registry.yml",
            )
            assert result.success

    def test_rules_load_registry_checks_local_then_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            local_rules_dir = Path(tmpdir) / "rules"
            package_rules_dir = Path(tmpdir) / "pkg_rules"
            local_rules_dir.mkdir()
            package_rules_dir.mkdir()
            (local_rules_dir / "engine-registry.yml").write_text(
                c.Tests.RULES_REGISTRY_YAML
            )
            (package_rules_dir / "engine-registry.yml").write_text(
                "rules:\n  - id: package-rule\n"
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_registry(
                config_path,
                package_rules_dir=package_rules_dir,
                registry_filename="engine-registry.yml",
            )
            assert result.success
            value = result.value
            assert isinstance(value, dict)
            rules_val = value.get("rules")
            assert isinstance(rules_val, list)
            rule = rules_val[0]
            assert isinstance(rule, dict)
            assert rule.get("id") == "rule-a"

    def test_rules_load_registry_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_rules_dir = Path(tmpdir) / "pkg_rules"
            pkg_rules_dir.mkdir()
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_registry(
                config_path,
                package_rules_dir=pkg_rules_dir,
                registry_filename="engine-registry.yml",
            )
            assert result.failure

    def test_rules_load_local_definitions_no_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't create pkg_rules_dir or local rules/ dir — triggers failure path
            pkg_rules_dir = Path(tmpdir) / "pkg_rules"
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=pkg_rules_dir,
                rule_filters=(),
                rule_catalog={},
            )
            assert result.failure

    def test_rules_load_local_definitions_with_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=catalog,
            )
            assert result.success

    def test_rules_load_local_definitions_with_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=("rule-*",),
                rule_catalog=catalog,
            )
            assert result.success

    def test_rules_load_local_definitions_filter_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=("nonmatch-*",),
                rule_catalog=catalog,
            )
            assert result.success

    def test_rules_load_local_definitions_skips_registry_missing_id_disabled_and_empty_matchers(
        self,
    ) -> None:
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
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            )
            assert result.success
            assert result.value == ([], [])

    def test_rules_load_local_definitions_unknown_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "unknown.yml").write_text(c.Tests.RULES_FILE_UNKNOWN_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
            )
            assert result.failure
            assert "rule-unknown" in (result.error or "")

    def test_rules_load_local_definitions_rule_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            (rules_dir / "invalid.yml").write_text(
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
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
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
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
                c.Tests.RULES_FILE_INVALID_MAPPING_YAML
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=c.Tests.RULES_CATALOG_BASIC,
                file_rule_catalog=c.Tests.RULES_FILE_CATALOG_MAPPING,
            )
            assert result.failure
            assert "config must be a mapping" in (result.error or "")

    def test_rules_matches_filters_empty(self) -> None:
        assert FlextCliUtilitiesRules._rules_matches_filters("rule-a", ()) is True

    @pytest.mark.parametrize(
        ("rule_id", "rule_filters", "expected"),
        c.Tests.RULES_MATCH_FILTER_CASES,
    )
    def test_rules_matches_filters_parametrized(
        self,
        rule_id: str,
        rule_filters: tuple[str, ...],
        expected: bool,
    ) -> None:
        result = FlextCliUtilitiesRules._rules_matches_filters(rule_id, rule_filters)
        assert result is expected

    def test_rules_resolve_directory_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliUtilitiesRules._rules_resolve_directory(
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
            result = FlextCliUtilitiesRules._rules_resolve_directory(
                config_path,
                package_rules_dir=pkg_rules,
                rules_dir_name="rules",
            )
            assert result == pkg_rules

    def test_rules_match_catalog_entry_by_action(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = FlextCliUtilitiesRules._rules_match_catalog_entry("check", "", catalog)
        assert result is not None
        assert result[0] == "lint"

    def test_rules_match_catalog_entry_by_check(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = FlextCliUtilitiesRules._rules_match_catalog_entry("", "lint", catalog)
        assert result is not None

    def test_rules_match_catalog_entry_no_match(self) -> None:
        catalog = c.Tests.RULES_CATALOG_BASIC
        result = FlextCliUtilitiesRules._rules_match_catalog_entry(
            "unknown", "unknown", catalog
        )
        assert result is None

    def test_rules_validate_matcher_valid(self) -> None:
        matcher = c.Tests.RULES_BASIC_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": ["check"]}
        result = FlextCliUtilitiesRules._rules_validate_matcher(
            rule_def, matcher, rule_id_key="id"
        )
        assert result is None

    def test_rules_validate_matcher_invalid_mapping(self) -> None:
        matcher = c.Tests.RULES_MAPPING_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "config": "not-a-mapping"}
        result = FlextCliUtilitiesRules._rules_validate_matcher(
            rule_def, matcher, rule_id_key="id"
        )
        assert result is not None
        assert "config" in result

    def test_rules_validate_matcher_invalid_list(self) -> None:
        matcher = c.Tests.RULES_LIST_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": []}
        result = FlextCliUtilitiesRules._rules_validate_matcher(
            rule_def, matcher, rule_id_key="id"
        )
        assert result is not None
        assert "actions" in result


class TestsFlextCliServiceRulesCov:
    """Coverage for FlextCliRules service."""

    def test_service_rules_resolve_scope(self) -> None:
        result = FlextCliRules.rules_resolve_scope(
            {"lint": {"rule_a": True}},
            scope_key="lint",
            allowed_keys=("rule_a",),
        )
        assert "rule_a" in result

    def test_service_rules_load_scoped_config(self) -> None:
        yaml_content = "lint:\n  rule_a: true\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            config_path = Path(f.name)
        result = FlextCliRules.rules_load_scoped_config(
            config_path,
            scope_key="lint",
            allowed_keys=("rule_a",),
        )
        assert result.success

    def test_service_rules_load_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            registry_file = rules_dir / "engine-registry.yml"
            registry_file.write_text(c.Tests.RULES_REGISTRY_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = FlextCliRules.rules_load_registry(
                config_path,
                package_rules_dir=rules_dir,
                registry_filename="engine-registry.yml",
            )
            assert result.success

    def test_service_rules_load_local_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_dir = Path(tmpdir) / "rules"
            rules_dir.mkdir()
            rule_file = rules_dir / "test-rule.yml"
            rule_file.write_text(c.Tests.RULES_FILE_YAML)
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            catalog = c.Tests.RULES_CATALOG_BASIC
            result = FlextCliRules.rules_load_local_definitions(
                config_path,
                package_rules_dir=rules_dir,
                rule_filters=(),
                rule_catalog=catalog,
            )
            assert result.success
