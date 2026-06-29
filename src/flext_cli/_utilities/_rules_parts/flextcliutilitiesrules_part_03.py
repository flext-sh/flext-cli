"""Generic local-rule loading helpers shared through ``u.Cli.rules_*``."""

from __future__ import annotations

import fnmatch
from collections.abc import (
    Mapping,
    MutableSequence,
)
from pathlib import Path

from flext_cli import t
from flext_cli._utilities.json import FlextCliUtilitiesJson as uj


class FlextCliUtilitiesRules:
    """Implementation part for FlextCliUtilitiesRules."""

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


__all__: list[str] = ["FlextCliUtilitiesRules"]
