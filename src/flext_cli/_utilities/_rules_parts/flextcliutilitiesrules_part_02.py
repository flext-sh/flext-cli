"""Generic local-rule loading helpers shared through ``u.Cli.rules_*``."""

from __future__ import annotations

from pathlib import Path

from flext_cli import m, p, r, t
from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_03 import (
    FlextCliUtilitiesRules as FlextCliUtilitiesRulesPart03,
)
from flext_cli._utilities.json import FlextCliUtilitiesJson as uj
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as uy


class FlextCliUtilitiesRules:
    """Implementation part for FlextCliUtilitiesRules."""

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
        rules_dir = FlextCliUtilitiesRulesPart03.rules_resolve_directory(
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
                if not FlextCliUtilitiesRulesPart03.rules_matches_filters(
                    rule_id, options.rule_filters
                ):
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
                    FlextCliUtilitiesRulesPart03.rules_match_catalog_entry(
                        action_name,
                        check_name,
                        file_catalog,
                    )
                )
                if file_match is not None:
                    file_kind, file_matcher = file_match
                    rule_validation = (
                        FlextCliUtilitiesRulesPart03.rules_validate_matcher(
                            typed_rule_def,
                            file_matcher,
                            rule_id_key=options.rule_id_key,
                        )
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
                    FlextCliUtilitiesRulesPart03.rules_match_catalog_entry(
                        action_name,
                        check_name,
                        options.rule_catalog,
                    )
                )
                if rule_match is None:
                    unknown_rules.append(rule_id)
                    continue
                rule_kind, rule_matcher = rule_match
                rule_validation = FlextCliUtilitiesRulesPart03.rules_validate_matcher(
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


__all__: list[str] = ["FlextCliUtilitiesRules"]
