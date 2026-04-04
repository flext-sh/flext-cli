# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._utilities.json as _flext_cli__utilities_json

    json = _flext_cli__utilities_json
    import flext_cli._utilities.toml as _flext_cli__utilities_toml
    from flext_cli._utilities.json import FlextCliUtilitiesJson

    toml = _flext_cli__utilities_toml
    import flext_cli._utilities.yaml as _flext_cli__utilities_yaml
    from flext_cli._utilities.toml import FlextCliUtilitiesToml

    yaml = _flext_cli__utilities_yaml
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
_LAZY_IMPORTS = {
    "FlextCliUtilitiesJson": "flext_cli._utilities.json",
    "FlextCliUtilitiesToml": "flext_cli._utilities.toml",
    "FlextCliUtilitiesYaml": "flext_cli._utilities.yaml",
    "json": "flext_cli._utilities.json",
    "toml": "flext_cli._utilities.toml",
    "yaml": "flext_cli._utilities.yaml",
}

__all__ = [
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesYaml",
    "json",
    "toml",
    "yaml",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
