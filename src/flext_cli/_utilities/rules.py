"""Generic local-rule loading helpers shared through ``u.Cli.rules_*``."""

from __future__ import annotations

import fnmatch
from collections.abc import (
    Mapping,
    MutableSequence,
)
from pathlib import Path

from flext_cli import (
    FlextCliUtilitiesJson as uj,
    FlextCliUtilitiesYaml as uy,
    c,
    m,
    p,
    r,
    t,
)


class FlextCliUtilitiesRules:
    """Generic helpers for reading project-local rules directories."""

    @staticmethod
    def rules_resolve_scope(
        settings: t.JsonValue,
        *,
        scope_key: str,
        allowed_keys: t.StrSequence,
    ) -> t.JsonMapping:
        """Extract and normalize one declarative rules scope from settings."""
        normalized = uj.json_as_mapping(settings)
        scope_raw = normalized.get(scope_key)
        scope_map = uj.json_as_mapping(scope_raw)
        return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
            key: value for key, value in scope_map.items() if key in allowed_keys
        })

    @staticmethod
    def rules_load_scoped_config(
        config_path: Path,
        *,
        scope_key: str,
        allowed_keys: t.StrSequence,
    ) -> p.Result[t.JsonMapping]:
        """Load one YAML config file and normalize a scoped rule section."""
        normalized = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
            uy.yaml_load_mapping(config_path),
        )
        normalized_scope = FlextCliUtilitiesRules.rules_resolve_scope(
            dict(normalized),
            scope_key=scope_key,
            allowed_keys=allowed_keys,
        )
        payload = dict(normalized)
        payload[scope_key] = dict(normalized_scope)
        return r[t.JsonMapping].ok(
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(payload),
        )

    @staticmethod
    def rules_load_registry(
        config_path: Path,
        *,
        package_rules_dir: Path,
        registry_filename: str,
        rules_dir_name: str = c.Cli.RULES_DIR_NAME,
    ) -> p.Result[t.JsonMapping]:
        """Load one rules registry mapping from local or packaged rules dirs."""
        package_registry = package_rules_dir / registry_filename
        candidates = [
            FlextCliUtilitiesRules.rules_resolve_directory(
                config_path,
                package_rules_dir=package_rules_dir,
                rules_dir_name=rules_dir_name,
            )
            / registry_filename,
        ]
        if package_registry not in candidates:
            candidates.append(package_registry)
        for registry_path in candidates:
            if not registry_path.is_file():
                continue
            normalized = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                uy.yaml_load_mapping(registry_path),
            )
            return r[t.JsonMapping].ok(normalized)
        return r[t.JsonMapping].fail(
            f"Failed to load rules registry: no {registry_filename} found",
        )

    @classmethod
    def rules_load_local_definitions[TRuleKind, TFileRuleKind](
        cls,
        config_path: Path,
        **kwargs: t.Cli.CliValue
        | Path
        | t.Cli.RuleCatalog[TRuleKind]
        | t.Cli.RuleCatalog[TFileRuleKind]
        | None,
    ) -> p.Result[t.Cli.RuleLoadResult[TRuleKind, TFileRuleKind]]:
        """Load local YAML rule definitions using declarative matcher catalogs."""
        options = m.Cli.LocalDefinitionsOptions[
            TRuleKind, TFileRuleKind
        ].model_validate(kwargs)
        rules_dir = cls.rules_resolve_directory(
            config_path,
            package_rules_dir=options.package_rules_dir,
            rules_dir_name=options.rules_dir_name,
        )
        if not rules_dir.is_dir():
            return r[t.Cli.RuleLoadResult[TRuleKind, TFileRuleKind]].fail(
                f"Rules directory not found: {rules_dir}",
            )
        file_catalog = options.file_rule_catalog or {}
        loaded_rules: t.MutableSequenceOf[t.Pair[TRuleKind, t.JsonMapping]] = []
        loaded_file_rules: t.MutableSequenceOf[
            t.Pair[TFileRuleKind, t.JsonMapping]
        ] = []
        loaded_file_rule_kinds: set[str] = set()
        unknown_rules: t.MutableSequenceOf[str] = []
        for rule_file in sorted(rules_dir.glob("*.yml")):
            if rule_file.name == options.registry_filename:
                continue
            rule_config = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                uy.yaml_load_mapping(rule_file),
            )
            typed_rules = uj.json_as_mapping_list(rule_config.get(options.rules_key))
            for typed_rule_def in typed_rules:
                rule_id = uj.json_get_str_key(typed_rule_def, options.rule_id_key)
                if not rule_id:
                    continue
                if not typed_rule_def.get(options.enabled_key, True):
                    continue
                if not cls.rules_matches_filters(rule_id, options.rule_filters):
                    continue
                action_name = uj.json_get_str_key(
                    typed_rule_def,
                    options.action_key,
                    default=uj.json_get_str_key(
                        typed_rule_def,
                        options.fallback_action_key,
                    ),
                    case="lower",
                )
                check_name = uj.json_get_str_key(
                    typed_rule_def,
                    options.check_key,
                    case="lower",
                )
                if not action_name and not check_name:
                    continue
                file_match: t.Pair[TFileRuleKind, t.Cli.RuleMatcher] | None = (
                    cls.rules_match_catalog_entry(
                        action_name,
                        check_name,
                        file_catalog,
                    )
                )
                if file_match is not None:
                    file_kind, file_matcher = file_match
                    rule_validation = cls.rules_validate_matcher(
                        typed_rule_def,
                        file_matcher,
                        rule_id_key=options.rule_id_key,
                    )
                    if rule_validation is not None:
                        unknown_rules.append(rule_validation)
                        continue
                    file_kind_key = str(file_kind)
                    if file_kind_key not in loaded_file_rule_kinds:
                        loaded_file_rules.append((file_kind, typed_rule_def))
                        loaded_file_rule_kinds.add(file_kind_key)
                    continue
                rule_match: t.Pair[TRuleKind, t.Cli.RuleMatcher] | None = (
                    cls.rules_match_catalog_entry(
                        action_name,
                        check_name,
                        options.rule_catalog,
                    )
                )
                if rule_match is None:
                    unknown_rules.append(rule_id)
                    continue
                rule_kind, rule_matcher = rule_match
                rule_validation = cls.rules_validate_matcher(
                    typed_rule_def,
                    rule_matcher,
                    rule_id_key=options.rule_id_key,
                )
                if rule_validation is not None:
                    unknown_rules.append(rule_validation)
                    continue
                loaded_rules.append((rule_kind, typed_rule_def))
        if unknown_rules:
            unknown = ", ".join(sorted(unknown_rules))
            return r[t.Cli.RuleLoadResult[TRuleKind, TFileRuleKind]].fail(
                f"Unknown rule mapping for: {unknown}",
            )
        return r[t.Cli.RuleLoadResult[TRuleKind, TFileRuleKind]].ok(
            (loaded_rules, loaded_file_rules),
        )

    @staticmethod
    def rules_matches_filters(rule_id: str, rule_filters: t.StrSequence) -> bool:
        if not rule_filters:
            return True
        rule_id_lower = rule_id.lower()
        return any(
            fnmatch.fnmatch(rule_id_lower, active_filter.lower())
            or active_filter.lower() in rule_id_lower
            for active_filter in rule_filters
        )

    @staticmethod
    def rules_resolve_directory(
        config_path: Path,
        *,
        package_rules_dir: Path,
        rules_dir_name: str,
    ) -> Path:
        local_rules_dir = config_path.parent / rules_dir_name
        if local_rules_dir.is_dir():
            return local_rules_dir
        return package_rules_dir

    @staticmethod
    def rules_match_catalog_entry[TKind](
        action_name: str,
        check_name: str,
        rule_catalog: t.Cli.RuleCatalog[TKind],
    ) -> t.Pair[TKind, t.Cli.RuleMatcher] | None:
        for rule_kind, matchers in rule_catalog.items():
            for matcher in matchers:
                actions, checks, _, _ = matcher
                if action_name and action_name in actions:
                    return (rule_kind, matcher)
                if check_name and check_name in checks:
                    return (rule_kind, matcher)
        return None

    @staticmethod
    def rules_validate_matcher(
        rule_def: t.JsonMapping,
        matcher: t.Cli.RuleMatcher,
        *,
        rule_id_key: str,
    ) -> str | None:
        rule_id = uj.json_get_str_key(rule_def, rule_id_key)
        _, _, required_mapping_keys, required_non_empty_list_keys = matcher
        for key in required_mapping_keys:
            if not isinstance(rule_def.get(key), Mapping):
                return f"{rule_id}: {key} must be a mapping"
        for key in required_non_empty_list_keys:
            raw_value = rule_def.get(key)
            if not isinstance(raw_value, MutableSequence) or not raw_value:
                return f"{rule_id}: {key} must be a non-empty list"
        return None


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesRules"]
