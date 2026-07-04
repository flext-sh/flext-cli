"""Generic local-rule loading helpers shared through ``u.Cli.rules_*``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import c, p, r, t
from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_03 import (
    FlextCliUtilitiesRules as FlextCliUtilitiesRulesPart03,
)
from flext_cli._utilities.json import FlextCliUtilitiesJson as uj
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as uy

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesRules:
    """Implementation part for FlextCliUtilitiesRules."""

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
            FlextCliUtilitiesRulesPart03.rules_resolve_directory(
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


__all__: list[str] = ["FlextCliUtilitiesRules"]
