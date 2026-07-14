# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import services as services
    from flext_cli._config import FlextCliConfig as FlextCliConfig, config as config
    from flext_cli._settings import (
        FlextCliSettings as FlextCliSettings,
        settings as settings,
    )
    from flext_cli.api import FlextCli as FlextCli, cli as cli
    from flext_cli.base import FlextCliServiceBase as FlextCliServiceBase, s as s
    from flext_cli.constants import FlextCliConstants as FlextCliConstants, c as c
    from flext_cli.models import FlextCliModels as FlextCliModels, m as m
    from flext_cli.protocols import FlextCliProtocols as FlextCliProtocols, p as p
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
    from flext_cli.services.prompts import FlextCliPrompts as FlextCliPrompts
    from flext_cli.services.rules import FlextCliRules as FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime as FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables as FlextCliTables
    from flext_cli.services.xlsx import FlextCliXlsx as FlextCliXlsx
    from flext_cli.services.yaml_model import FlextCliYamlModel as FlextCliYamlModel
    from flext_cli.typings import FlextCliTypes as FlextCliTypes, t as t
    from flext_cli.utilities import FlextCliUtilities as FlextCliUtilities, u as u
    from flext_core import d as d, e as e, h as h, r as r, x as x

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextCliConfig", "config"),
    "._settings": ("FlextCliSettings", "settings"),
    ".api": ("FlextCli", "cli"),
    ".base": ("FlextCliServiceBase", "s"),
    ".constants": ("FlextCliConstants", "c"),
    ".models": ("FlextCliModels", "m"),
    ".protocols": ("FlextCliProtocols", "p"),
    ".services": ("services",),
    ".services.auth": ("FlextCliAuth",),
    ".services.cli": ("FlextCliCli",),
    ".services.cli_params": ("FlextCliCommonParams",),
    ".services.cmd": ("FlextCliCmd",),
    ".services.file_tools": ("FlextCliFileTools",),
    ".services.formatters": ("FlextCliFormatters",),
    ".services.output": ("FlextCliOutput",),
    ".services.pipeline": ("FlextCliPipeline",),
    ".services.prompts": ("FlextCliPrompts",),
    ".services.rules": ("FlextCliRules",),
    ".services.runtime": ("FlextCliRuntime",),
    ".services.tables": ("FlextCliTables",),
    ".services.xlsx": ("FlextCliXlsx",),
    ".services.yaml_model": ("FlextCliYamlModel",),
    ".typings": ("FlextCliTypes", "t"),
    ".utilities": ("FlextCliUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
}

_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}

_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliRules",
    "FlextCliRuntime",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "FlextCliXlsx",
    "FlextCliYamlModel",
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
