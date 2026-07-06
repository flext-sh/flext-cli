# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.models import FlextCliModels, m
    from flext_cli.protocols import FlextCliProtocols, p
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline
    from flext_cli.services.rules import FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.settings import FlextCliSettings
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, u
    from flext_core._root_typing_parts.facades import d, e, h, r, x
_LAZY_IMPORTS = merge_lazy_imports(
    (".services",),
    build_lazy_import_map(
        {
            ".api": (
                "FlextCli",
                "cli",
            ),
            ".base": (
                "FlextCliServiceBase",
                "s",
            ),
            ".constants": (
                "FlextCliConstants",
                "c",
            ),
            ".models": (
                "FlextCliModels",
                "m",
            ),
            ".protocols": (
                "FlextCliProtocols",
                "p",
            ),
            ".services._prompts_parts.flextcliprompts_part_03": ("FlextCliPrompts",),
            ".services._prompts_parts.flextcliprompts_support": (
                "FlextCliPromptsSupport",
            ),
            ".services.auth": ("FlextCliAuth",),
            ".services.cli": ("FlextCliCli",),
            ".services.cli_params": ("FlextCliCommonParams",),
            ".services.cmd": ("FlextCliCmd",),
            ".services.file_tools": ("FlextCliFileTools",),
            ".services.formatters": ("FlextCliFormatters",),
            ".services.output": ("FlextCliOutput",),
            ".services.pipeline": ("FlextCliPipeline",),
            ".services.rules": ("FlextCliRules",),
            ".services.runtime": ("FlextCliRuntime",),
            ".services.tables": ("FlextCliTables",),
            ".settings": ("FlextCliSettings",),
            ".typings": (
                "FlextCliTypes",
                "t",
            ),
            ".utilities": (
                "FlextCliUtilities",
                "u",
            ),
            "flext_core._root_typing_parts.facades": (
                "d",
                "e",
                "h",
                "r",
                "x",
            ),
        },
    ),
    exclude_names=(
        "_cli_parts",
        "_prompts_parts",
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


__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliProtocols",
    "FlextCliRules",
    "FlextCliRuntime",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "cli",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)
