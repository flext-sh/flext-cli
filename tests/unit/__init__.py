# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .test_atomic_directory_chain import TestsAtomicDirectoryChain
    from .test_atomic_directory_identity import TestsAtomicDirectoryIdentity
    from .test_atomic_directory_publish import TestsAtomicDirectoryPublish
    from .test_atomic_file_identity import TestsAtomicFileIdentity
    from .test_atomic_physical_tree import TestsAtomicPhysicalTree
    from .test_auth_utils_cov import TestsFlextCliAuthUtilsCov
    from .test_cli_service import TestsFlextCliService
    from .test_cmd_runtime_validation_branch_cov import (
        TestsFlextCliCmdRuntimeValidationBranchCov,
    )
    from .test_commands_utils_cov import TestsFlextCliCommands
    from .test_examples_smoke import TestsFlextCliExamplesSmoke
    from .test_file_tools_yaml import TestsFlextCliYamlModelLoading
    from .test_files_cov import TestsFlextCliFilesCov
    from .test_formatters_cov import TestsFlextCliFormattersCov
    from .test_json_cov import TestsFlextCliJsonCov
    from .test_matching_cov import TestsFlextCliMatchingCov
    from .test_options import TestsFlextCliOptions
    from .test_options_cov import TestsFlextCliOptionsUtilsCov
    from .test_output_cov import TestsFlextCliOutputCov
    from .test_params_branch_cov import TestsFlextCliParams
    from .test_pipeline import TestsFlextCliPipeline
    from .test_prompts import TestsFlextCliPrompts
    from .test_prompts_cov import TestsFlextCliPromptsCov
    from .test_public_contracts_cov import TestsFlextCliPublicContractsCoverage
    from .test_rules_cov import TestsFlextCliRulesCov
    from .test_runtime_process_containment import TestsFlextCliRuntimeProcessContainment
    from .test_runtime_process_descendants import TestsFlextCliRuntimeProcessDescendants
    from .test_runtime_streamed_process import TestsFlextCliRuntimeStreamedProcess
    from .test_services_auth_branch_cov import TestsFlextCliServicesAuth
    from .test_services_auth_cov import TestsFlextCliServicesAuthCov
    from .test_services_output_cov import TestsFlextCliServicesOutputCov
    from .test_services_tables_branch_cov import TestsFlextCliServicesTablesBranchCov
    from .test_services_tables_cov import TestsFlextCliServicesTablesCov
    from .test_tables_branch_cov import TestsFlextCliTablesBranchCov
    from .test_tables_cov import TestsFlextCliTables
    from .test_toml_utilities import TestsFlextCliTomlUtilities
    from .test_utilities_cov import TestsFlextCliUtilitiesCov
    from .test_yaml_cov import TestsFlextCliYamlCov
__all__: tuple[str, ...] = (
    "TestsAtomicDirectoryChain",
    "TestsAtomicDirectoryIdentity",
    "TestsAtomicDirectoryPublish",
    "TestsAtomicFileIdentity",
    "TestsAtomicPhysicalTree",
    "TestsFlextCliAuthUtilsCov",
    "TestsFlextCliCmdRuntimeValidationBranchCov",
    "TestsFlextCliCommands",
    "TestsFlextCliExamplesSmoke",
    "TestsFlextCliFilesCov",
    "TestsFlextCliFormattersCov",
    "TestsFlextCliJsonCov",
    "TestsFlextCliMatchingCov",
    "TestsFlextCliOptions",
    "TestsFlextCliOptionsUtilsCov",
    "TestsFlextCliOutputCov",
    "TestsFlextCliParams",
    "TestsFlextCliPipeline",
    "TestsFlextCliPrompts",
    "TestsFlextCliPromptsCov",
    "TestsFlextCliPublicContractsCoverage",
    "TestsFlextCliRulesCov",
    "TestsFlextCliRuntimeProcessContainment",
    "TestsFlextCliRuntimeProcessDescendants",
    "TestsFlextCliRuntimeStreamedProcess",
    "TestsFlextCliService",
    "TestsFlextCliServicesAuth",
    "TestsFlextCliServicesAuthCov",
    "TestsFlextCliServicesOutputCov",
    "TestsFlextCliServicesTablesBranchCov",
    "TestsFlextCliServicesTablesCov",
    "TestsFlextCliTables",
    "TestsFlextCliTablesBranchCov",
    "TestsFlextCliTomlUtilities",
    "TestsFlextCliUtilitiesCov",
    "TestsFlextCliYamlCov",
    "TestsFlextCliYamlModelLoading",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".test_atomic_directory_chain": ("TestsAtomicDirectoryChain",),
            ".test_atomic_directory_identity": ("TestsAtomicDirectoryIdentity",),
            ".test_atomic_directory_publish": ("TestsAtomicDirectoryPublish",),
            ".test_atomic_file_identity": ("TestsAtomicFileIdentity",),
            ".test_atomic_physical_tree": ("TestsAtomicPhysicalTree",),
            ".test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
            ".test_cli_service": ("TestsFlextCliService",),
            ".test_cmd_runtime_validation_branch_cov": (
                "TestsFlextCliCmdRuntimeValidationBranchCov",
            ),
            ".test_commands_utils_cov": ("TestsFlextCliCommands",),
            ".test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
            ".test_file_tools_yaml": ("TestsFlextCliYamlModelLoading",),
            ".test_files_cov": ("TestsFlextCliFilesCov",),
            ".test_formatters_cov": ("TestsFlextCliFormattersCov",),
            ".test_json_cov": ("TestsFlextCliJsonCov",),
            ".test_matching_cov": ("TestsFlextCliMatchingCov",),
            ".test_options": ("TestsFlextCliOptions",),
            ".test_options_cov": ("TestsFlextCliOptionsUtilsCov",),
            ".test_output_cov": ("TestsFlextCliOutputCov",),
            ".test_params_branch_cov": ("TestsFlextCliParams",),
            ".test_pipeline": ("TestsFlextCliPipeline",),
            ".test_prompts": ("TestsFlextCliPrompts",),
            ".test_prompts_cov": ("TestsFlextCliPromptsCov",),
            ".test_public_contracts_cov": ("TestsFlextCliPublicContractsCoverage",),
            ".test_rules_cov": ("TestsFlextCliRulesCov",),
            ".test_runtime_process_containment": (
                "TestsFlextCliRuntimeProcessContainment",
            ),
            ".test_runtime_process_descendants": (
                "TestsFlextCliRuntimeProcessDescendants",
            ),
            ".test_runtime_streamed_process": ("TestsFlextCliRuntimeStreamedProcess",),
            ".test_services_auth_branch_cov": ("TestsFlextCliServicesAuth",),
            ".test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
            ".test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
            ".test_services_tables_branch_cov": (
                "TestsFlextCliServicesTablesBranchCov",
            ),
            ".test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
            ".test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
            ".test_tables_cov": ("TestsFlextCliTables",),
            ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
            ".test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
            ".test_yaml_cov": ("TestsFlextCliYamlCov",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
