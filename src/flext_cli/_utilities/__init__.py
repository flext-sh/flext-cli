# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._utilities.base as _flext_cli__utilities_base

    base = _flext_cli__utilities_base
    import flext_cli._utilities.configuration as _flext_cli__utilities_configuration
    from flext_cli._utilities.base import FlextCliUtilitiesBase

    configuration = _flext_cli__utilities_configuration
    import flext_cli._utilities.conversion as _flext_cli__utilities_conversion
    from flext_cli._utilities.configuration import FlextCliUtilitiesConfiguration

    conversion = _flext_cli__utilities_conversion
    import flext_cli._utilities.files as _flext_cli__utilities_files
    from flext_cli._utilities.files import FlextCliUtilitiesFiles

    files = _flext_cli__utilities_files
    import flext_cli._utilities.json as _flext_cli__utilities_json
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesCliModelConverter,
        FlextCliUtilitiesConversion,
    )

    json = _flext_cli__utilities_json
    import flext_cli._utilities.matching as _flext_cli__utilities_matching
    from flext_cli._utilities.json import FlextCliUtilitiesJson

    matching = _flext_cli__utilities_matching
    import flext_cli._utilities.model_commands as _flext_cli__utilities_model_commands
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching

    model_commands = _flext_cli__utilities_model_commands
    import flext_cli._utilities.options as _flext_cli__utilities_options
    from flext_cli._utilities.model_commands import (
        FlextCliUtilitiesModelCommandBuilder,
        FlextCliUtilitiesModelCommands,
    )

    options = _flext_cli__utilities_options
    import flext_cli._utilities.toml as _flext_cli__utilities_toml
    from flext_cli._utilities.options import (
        FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions,
    )

    toml = _flext_cli__utilities_toml
    import flext_cli._utilities.validation as _flext_cli__utilities_validation
    from flext_cli._utilities.toml import FlextCliUtilitiesToml

    validation = _flext_cli__utilities_validation
    import flext_cli._utilities.yaml as _flext_cli__utilities_yaml
    from flext_cli._utilities.validation import FlextCliUtilitiesValidation

    yaml = _flext_cli__utilities_yaml
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
_LAZY_IMPORTS = {
    "FlextCliUtilitiesBase": "flext_cli._utilities.base",
    "FlextCliUtilitiesCliModelConverter": "flext_cli._utilities.conversion",
    "FlextCliUtilitiesConfiguration": "flext_cli._utilities.configuration",
    "FlextCliUtilitiesConversion": "flext_cli._utilities.conversion",
    "FlextCliUtilitiesFiles": "flext_cli._utilities.files",
    "FlextCliUtilitiesJson": "flext_cli._utilities.json",
    "FlextCliUtilitiesMatching": "flext_cli._utilities.matching",
    "FlextCliUtilitiesModelCommandBuilder": "flext_cli._utilities.model_commands",
    "FlextCliUtilitiesModelCommands": "flext_cli._utilities.model_commands",
    "FlextCliUtilitiesOptionBuilder": "flext_cli._utilities.options",
    "FlextCliUtilitiesOptions": "flext_cli._utilities.options",
    "FlextCliUtilitiesToml": "flext_cli._utilities.toml",
    "FlextCliUtilitiesValidation": "flext_cli._utilities.validation",
    "FlextCliUtilitiesYaml": "flext_cli._utilities.yaml",
    "base": "flext_cli._utilities.base",
    "configuration": "flext_cli._utilities.configuration",
    "conversion": "flext_cli._utilities.conversion",
    "json": "flext_cli._utilities.json",
    "matching": "flext_cli._utilities.matching",
    "model_commands": "flext_cli._utilities.model_commands",
    "options": "flext_cli._utilities.options",
    "toml": "flext_cli._utilities.toml",
    "validation": "flext_cli._utilities.validation",
    "yaml": "flext_cli._utilities.yaml",
}

__all__ = [
    "FlextCliUtilitiesBase",
    "FlextCliUtilitiesCliModelConverter",
    "FlextCliUtilitiesConfiguration",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesValidation",
    "FlextCliUtilitiesYaml",
    "base",
    "configuration",
    "conversion",
    "json",
    "matching",
    "model_commands",
    "options",
    "toml",
    "validation",
    "yaml",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
