# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_cli.__version__ import (
<<<<<<< HEAD
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
=======
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
>>>>>>> origin/fix/cli-contract-cure-20261001
)
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import services
    from flext_cli._settings import FlextCliSettings, settings
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.cli import main
    from flext_cli.config import FlextCliConfig, config
<<<<<<< HEAD
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.models import FlextCliModels, m
    from flext_cli.protocols import FlextCliProtocols, p
=======
    from flext_cli.constants import FlextCliConstants, FlextCliConstants as c
    from flext_cli.models import FlextCliModels, FlextCliModels as m
    from flext_cli.protocols import FlextCliProtocols, FlextCliProtocols as p
>>>>>>> origin/fix/cli-contract-cure-20261001
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.docx import FlextCliDocx
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline
    from flext_cli.services.pptx import FlextCliPptx
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.rules import FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.services.xlsx import FlextCliXlsx
    from flext_cli.services.yaml_model import FlextCliYamlModel
<<<<<<< HEAD
    from flext_cli.typings import FlextCliTypes, t
=======
    from flext_cli.typings import FlextCliTypes, FlextCliTypes as t
>>>>>>> origin/fix/cli-contract-cure-20261001
    from flext_cli.utilities import FlextCliUtilities, u
    from flext_core import d, e, h, r, x


__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliDocx",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPptx",
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
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._settings": ("FlextCliSettings", "settings"),
            ".api": ("FlextCli", "cli"),
            ".base": ("FlextCliServiceBase", "s"),
            ".cli": ("main",),
            ".config": ("FlextCliConfig", "config"),
            ".constants": ("FlextCliConstants", "c"),
            ".models": ("FlextCliModels", "m"),
            ".protocols": ("FlextCliProtocols", "p"),
            ".services": ("services",),
            ".services.auth": ("FlextCliAuth",),
            ".services.cli": ("FlextCliCli",),
            ".services.cli_params": ("FlextCliCommonParams",),
            ".services.cmd": ("FlextCliCmd",),
            ".services.docx": ("FlextCliDocx",),
            ".services.file_tools": ("FlextCliFileTools",),
            ".services.formatters": ("FlextCliFormatters",),
            ".services.output": ("FlextCliOutput",),
            ".services.pipeline": ("FlextCliPipeline",),
            ".services.pptx": ("FlextCliPptx",),
            ".services.prompts": ("FlextCliPrompts",),
            ".services.rules": ("FlextCliRules",),
            ".services.runtime": ("FlextCliRuntime",),
            ".services.tables": ("FlextCliTables",),
            ".services.xlsx": ("FlextCliXlsx",),
            ".services.yaml_model": ("FlextCliYamlModel",),
            ".typings": ("FlextCliTypes", "t"),
            ".utilities": ("FlextCliUtilities", "u"),
            "flext_core": ("d", "e", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
