# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_CLI_TESTS_UNIT_LAZY_IMPORTS_PART_02 = build_lazy_import_map(
    {
        ".conftest": (
            "make_capture_prompts",
            "make_failing_prompts",
            "make_prompts",
            "reset_settings",
        ),
        ".test_services_auth_branch_cov": ("TestsFlextCliServicesAuthBranchCov",),
        ".test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
        ".test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
        ".test_services_tables_branch_cov": ("TestsFlextCliServicesTablesBranchCov",),
        ".test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
        ".test_settings": ("TestsFlextCliSettingsUnit",),
        ".test_tables": ("TestsFlextCliTables",),
        ".test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
        ".test_tables_cov": ("TestsFlextCliTableUtilsCov",),
        ".test_toml_cov": ("TestsFlextCliTomlUtilsCov",),
        ".test_toml_sync_cov": ("TestsFlextCliTomlSyncCoverage",),
        ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
        ".test_typings": ("TestsFlextCliTypesUnit",),
        ".test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
        ".test_version": ("TestsFlextCliVersion",),
        ".test_yaml_cov": ("TestsFlextCliYamlCov",),
    },
)

__all__: list[str] = ["FLEXT_CLI_TESTS_UNIT_LAZY_IMPORTS_PART_02"]
