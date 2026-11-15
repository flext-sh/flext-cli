# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests._constants.tests_core import TestsFlextCliConstantsCore
    from tests._constants.tests_rules_options import TestsFlextCliConstantsRulesOptions
    from tests._constants.tests_yaml_output import TestsFlextCliConstantsYamlOutput
    from tests._constants.testsflextcliconstants_part_01 import (
        TestsFlextCliConstantsPart01,
    )


__all__: tuple[str, ...] = (
    "TestsFlextCliConstantsCore",
    "TestsFlextCliConstantsPart01",
    "TestsFlextCliConstantsRulesOptions",
    "TestsFlextCliConstantsYamlOutput",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "TestsFlextCliConstantsCore": ".tests_core",
        "TestsFlextCliConstantsPart01": ".testsflextcliconstants_part_01",
        "TestsFlextCliConstantsRulesOptions": ".tests_rules_options",
        "TestsFlextCliConstantsYamlOutput": ".tests_yaml_output",
    },
    public_exports=__all__,
    deferred_members={
        "TestsFlextCliConstantsCore": (
            "AUTH_TOKEN_MIN_LENGTH",
            "AUTH_VALUE_SAMPLE",
            "COMMAND_DURATION_TOLERANCE",
            "CREDENTIAL_SAMPLE_VALUE",
            "DOCUMENT_STACK_MODULES",
            "ENV_READ_ABSENT_NAME",
            "ENV_READ_CASES",
            "ENV_READ_PROBE_NAME",
            "ENV_READ_PROBE_VALUE",
            "VERSION_VALID_SEMVER",
            "VERSION_COMPATIBLE",
            "VERSION_VALID_SEMVER_COMPLEX",
            "MATCH_REGEX_PHONE_RE",
            "MATCH_REGEX_ALPHA_RE",
            "MATCH_REGEX_BETA_RE",
            "PROMPT_EDGE_MESSAGES",
            "PROMPT_SHORT_ENV_NAME",
            "PROMPT_VALID_ENV_NAME",
            "VERSION_STR_CASES",
            "CONVERSION_STR_CASES",
            "CONVERSION_BOOL_CASES",
            "CONVERSION_DICT_CASES",
            "FILES_DETECT_FORMAT_CASES",
            "FILES_DETECT_FORMAT_FAIL_CASES",
        ),
        "TestsFlextCliConstantsPart01": ("Tests",),
        "TestsFlextCliConstantsRulesOptions": (
            "RULES_SCOPE_CASES",
            "RULES_MATCH_FILTER_CASES",
            "RULES_REGISTRY_YAML",
            "RULES_FILE_YAML",
            "RULES_FILE_NO_ID_YAML",
            "RULES_FILE_DISABLED_YAML",
            "RULES_FILE_NO_MATCHER_KEYS_YAML",
            "RULES_FILE_UNKNOWN_YAML",
            "RULES_FILE_INVALID_MAPPING_YAML",
            "RULES_BASIC_MATCHER",
            "RULES_MAPPING_MATCHER",
            "RULES_LIST_MATCHER",
            "RULES_CATALOG_BASIC",
            "RULES_CATALOG_MAPPING",
            "RULES_FILE_CATALOG_BASIC",
            "RULES_FILE_CATALOG_MAPPING",
            "TOML_VALID_CONTENT",
            "TOML_INVALID_CONTENT",
            "TOML_SECTION_CONTENT",
        ),
        "TestsFlextCliConstantsYamlOutput": (
            "YAML_VALID_CONTENT",
            "YAML_INVALID_CONTENT",
            "YAML_NON_MAPPING_CONTENT",
            "YAML_PARSE_CASES",
            "YAML_DUMP_CASES",
            "MATCH_SIMPLE_CASES",
            "CLI_USAGE_ERROR_MATCH_CASES",
            "FORMATTER_TABLE_CASES",
            "FORMATTER_PANEL_CASES",
            "FORMATTER_RULE_LABELS",
            "OUTPUT_DISPLAY_CASES",
            "OUTPUT_PROGRESS_CASES",
            "OUTPUT_TEXT_CASES",
            "AUTH_CRED_CASES",
            "FORMATTERS_PRINT_CASES",
        ),
    },
)
