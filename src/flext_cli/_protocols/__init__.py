# AUTO-GENERATED FILE — Regenerate with: make gen
"""Protocols package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBase as FlextCliProtocolsBase,
    )
    from flext_cli._protocols.domain import (
        FlextCliProtocolsDomain as FlextCliProtocolsDomain,
    )
    from flext_cli._protocols.pipeline import (
        FlextCliProtocolsPipeline as FlextCliProtocolsPipeline,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("._base_parts",),
    build_lazy_import_map({
        "._base_parts": ("_base_parts",),
        "._base_parts.flextcliprotocolsbase_part_05": ("FlextCliProtocolsBase",),
        ".domain": ("FlextCliProtocolsDomain",),
        ".pipeline": ("FlextCliProtocolsPipeline",),
    }),
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
