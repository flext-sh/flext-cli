"""DSL service for declarative local rule loading."""

from __future__ import annotations

from pathlib import Path

from flext_cli import FlextCliServiceBase, p, t, u


class FlextCliRules(FlextCliServiceBase):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""

    @staticmethod
    def rules_resolve_scope(
        settings: t.JsonValue,
        *,
        scope_key: str,
        allowed_keys: t.StrSequence,
    ) -> t.JsonMapping:
        """Extract one normalized declarative rules scope from loaded settings."""
        return u.Cli.rules_resolve_scope(
            settings,
            scope_key=scope_key,
            allowed_keys=allowed_keys,
        )

    @staticmethod
    def rules_load_scoped_config(
        config_path: Path,
        *,
        scope_key: str,
        allowed_keys: t.StrSequence,
    ) -> p.Result[t.JsonMapping]:
        """Load one config file and normalize its rule scope."""
        return u.Cli.rules_load_scoped_config(
            config_path,
            scope_key=scope_key,
            allowed_keys=allowed_keys,
        )

    @staticmethod
    def rules_load_registry(
        config_path: Path,
        *,
        package_rules_dir: Path,
        registry_filename: str,
        rules_dir_name: str = "rules",
    ) -> p.Result[t.JsonMapping]:
        """Load one local or packaged rules registry."""
        return u.Cli.rules_load_registry(
            config_path,
            package_rules_dir=package_rules_dir,
            registry_filename=registry_filename,
            rules_dir_name=rules_dir_name,
        )

    @staticmethod
    def rules_load_local_definitions[TRuleKind, TFileRuleKind](
        config_path: Path,
        **kwargs: t.Cli.CliValue | Path | t.Cli.RuleCatalog[TRuleKind] | t.Cli.RuleCatalog[TFileRuleKind] | None,
    ) -> p.Result[t.Cli.RuleLoadResult[TRuleKind, TFileRuleKind]]:
        """Load one declarative local ruleset using direct matcher catalogs."""
        return u.Cli.rules_load_local_definitions(
            config_path,
            **kwargs,
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]
