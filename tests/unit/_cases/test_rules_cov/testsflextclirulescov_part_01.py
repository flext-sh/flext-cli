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

    def test_rules_resolve_scope_with_data(self) -> None:
        result = u.Cli.rules_resolve_scope(
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
        allowed_keys: t.StrSequence,
        expected_len: int,
    ) -> None:
        result = u.Cli.rules_resolve_scope(
            settings,
            scope_key=scope_key,
            allowed_keys=allowed_keys,
        )
        assert len(result) == expected_len

    def test_rules_load_scoped_config_valid(self) -> None:
        yaml_content = "lint:\n  rule_a: true\n  rule_b: false\n"
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yml",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(yaml_content)
            config_path = Path(f.name)
        result = u.Cli.rules_load_scoped_config(
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
            result = u.Cli.rules_load_registry(
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
            result = u.Cli.rules_load_registry(
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
                c.Tests.RULES_REGISTRY_YAML,
            )
            (package_rules_dir / "engine-registry.yml").write_text(
                "rules:\n  - id: package-rule\n",
            )
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("project: test\n")
            result = u.Cli.rules_load_registry(
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
            result = u.Cli.rules_load_registry(
                config_path,
                package_rules_dir=pkg_rules_dir,
                registry_filename="engine-registry.yml",
            )
            assert result.failure


__all__: list[str] = ["TestsFlextCliRulesCov"]
