# AUTO-GENERATED FILE — Regenerate with: make gen
"""Services package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_cli.services._prompts_parts.flextcliprompts_part_03 import (
        FlextCliPrompts as FlextCliPrompts,
    )
    from flext_cli.services._prompts_parts.flextcliprompts_support import (
        FlextCliPromptsSupport as FlextCliPromptsSupport,
    )
    from flext_cli.services.auth import FlextCliAuth as FlextCliAuth
    from flext_cli.services.cli import FlextCliCli as FlextCliCli
    from flext_cli.services.cli_params import (
        FlextCliCommonParams as FlextCliCommonParams,
    )
    from flext_cli.services.cmd import FlextCliCmd as FlextCliCmd
    from flext_cli.services.file_tools import FlextCliFileTools as FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters as FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput as FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline as FlextCliPipeline
    from flext_cli.services.rules import FlextCliRules as FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime as FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables as FlextCliTables
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._cli_parts",
        "._prompts_parts",
    ),
    build_lazy_import_map(
        {
            "._cli_parts": ("_cli_parts",),
            "._prompts_parts": ("_prompts_parts",),
            "._prompts_parts.flextcliprompts_part_03": ("FlextCliPrompts",),
            "._prompts_parts.flextcliprompts_support": ("FlextCliPromptsSupport",),
            ".auth": ("FlextCliAuth",),
            ".cli": ("FlextCliCli",),
            ".cli_params": ("FlextCliCommonParams",),
            ".cmd": ("FlextCliCmd",),
            ".file_tools": ("FlextCliFileTools",),
            ".formatters": ("FlextCliFormatters",),
            ".output": ("FlextCliOutput",),
            ".pipeline": ("FlextCliPipeline",),
            ".rules": ("FlextCliRules",),
            ".runtime": ("FlextCliRuntime",),
            ".tables": ("FlextCliTables",),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
