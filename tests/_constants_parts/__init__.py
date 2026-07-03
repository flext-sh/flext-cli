# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests._constants_parts.tests_core import (
        TestsFlextCliConstantsCore as TestsFlextCliConstantsCore,
    )
    from flext_cli.tests._constants_parts.tests_rules_options import (
        TestsFlextCliConstantsRulesOptions as TestsFlextCliConstantsRulesOptions,
    )
    from flext_cli.tests._constants_parts.tests_yaml_output import (
        TestsFlextCliConstantsYamlOutput as TestsFlextCliConstantsYamlOutput,
    )
    from flext_cli.tests._constants_parts.testsflextcliconstants_part_01 import (
        TestsFlextCliConstants as TestsFlextCliConstants,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".tests_core": ("TestsFlextCliConstantsCore",),
        ".tests_rules_options": ("TestsFlextCliConstantsRulesOptions",),
        ".tests_yaml_output": ("TestsFlextCliConstantsYamlOutput",),
        ".testsflextcliconstants_part_01": ("TestsFlextCliConstants",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
