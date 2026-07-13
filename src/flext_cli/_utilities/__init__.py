# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli._utilities.__unit__ import (
    CHILD_MODULE_PATHS as _CHILD_MODULE_PATHS,
    EXCLUDED_LAZY_NAMES as _EXCLUDED_LAZY_NAMES,
    LAZY_ALIAS_GROUPS as _LAZY_ALIAS_GROUPS,
    LAZY_MODULES as _LAZY_MODULES,
    PUBLIC_EXPORTS as _PUBLIC_EXPORTS,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli._utilities import (
        _file_test_helper_parts as _file_test_helper_parts,
        _files_parts as _files_parts,
        _json_parts as _json_parts,
        _options_parts as _options_parts,
        _rules_parts as _rules_parts,
        _toml_parts as _toml_parts,
        _yaml_roundtrip_parts as _yaml_roundtrip_parts,
    )
    from flext_cli._utilities._cli_namespace import (
        FlextCliUtilitiesCli as FlextCliUtilitiesCli,
    )
    from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04 import (
        FlextCliUtilitiesFileTestHelpersMixin as FlextCliUtilitiesFileTestHelpersMixin,
    )
    from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
        FlextCliUtilitiesFiles as FlextCliUtilitiesFiles,
    )
    from flext_cli._utilities._json_parts.flextcliutilitiesjson_part_03 import (
        FlextCliUtilitiesJson as FlextCliUtilitiesJson,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder as FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions as FlextCliUtilitiesOptions,
    )
    from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_03 import (
        FlextCliUtilitiesRules as FlextCliUtilitiesRules,
    )
    from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesToml as FlextCliUtilitiesToml,
    )
    from flext_cli._utilities._yaml_roundtrip_parts.flextcliutilitiesyamlroundtrip_part_02 import (
        FlextCliUtilitiesYamlRoundtrip as FlextCliUtilitiesYamlRoundtrip,
    )
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth as FlextCliUtilitiesAuth
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd as FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import (
        FlextCliUtilitiesCommands as FlextCliUtilitiesCommands,
    )
    from flext_cli._utilities.config import (
        FlextCliUtilitiesConfig as FlextCliUtilitiesConfig,
    )
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesConversion as FlextCliUtilitiesConversion,
    )
    from flext_cli._utilities.formatters import (
        FlextCliUtilitiesFormatters as FlextCliUtilitiesFormatters,
    )
    from flext_cli._utilities.framework import (
        FlextCliUtilitiesFramework as FlextCliUtilitiesFramework,
    )
    from flext_cli._utilities.matching import (
        FlextCliUtilitiesMatching as FlextCliUtilitiesMatching,
    )
    from flext_cli._utilities.model_commands import (
        FlextCliUtilitiesModelCommands as FlextCliUtilitiesModelCommands,
    )
    from flext_cli._utilities.output import (
        FlextCliUtilitiesOutput as FlextCliUtilitiesOutput,
    )
    from flext_cli._utilities.params import (
        FlextCliUtilitiesParams as FlextCliUtilitiesParams,
    )
    from flext_cli._utilities.pipeline import (
        FlextCliUtilitiesPipeline as FlextCliUtilitiesPipeline,
    )
    from flext_cli._utilities.processes import (
        FlextCliUtilitiesProcesses as FlextCliUtilitiesProcesses,
    )
    from flext_cli._utilities.prompts import (
        FlextCliUtilitiesPrompts as FlextCliUtilitiesPrompts,
    )
    from flext_cli._utilities.runtime import (
        FlextCliUtilitiesRuntime as FlextCliUtilitiesRuntime,
    )
    from flext_cli._utilities.settings import (
        FlextCliUtilitiesSettings as FlextCliUtilitiesSettings,
    )
    from flext_cli._utilities.tables import (
        FlextCliUtilitiesTables as FlextCliUtilitiesTables,
    )
    from flext_cli._utilities.template import (
        FlextCliUtilitiesTemplate as FlextCliUtilitiesTemplate,
    )
    from flext_cli._utilities.validation import (
        FlextCliUtilitiesValidation as FlextCliUtilitiesValidation,
    )
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as FlextCliUtilitiesYaml

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = merge_lazy_imports(
    _CHILD_MODULE_PATHS,
    build_lazy_import_map(
        _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
    ),
    exclude_names=_EXCLUDED_LAZY_NAMES,
    module_name=__name__,
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)
