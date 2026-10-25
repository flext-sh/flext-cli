"""Heavy ``u.Cli`` utility namespace materialized on demand.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_cli import m
from flext_cli._utilities import (
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConfig,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesDag,
    FlextCliUtilitiesDocx,
    FlextCliUtilitiesEnv,
    FlextCliUtilitiesFileChanges,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFileTestHelpersMixin,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesFramework,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesMarkdown,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPptx,
    FlextCliUtilitiesProcesses,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesReport,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesTemplate,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesXlsx,
    FlextCliUtilitiesYaml,
)
from flext_cli._utilities._options.fields import FlextCliUtilitiesOptionsFields


class FlextCliUtilitiesCli(
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConfig,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesDag,
    FlextCliUtilitiesEnv,
    FlextCliUtilitiesTemplate,
    FlextCliUtilitiesFileTestHelpersMixin,
    FlextCliUtilitiesFileChanges,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesFramework,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesMarkdown,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesOptionsFields,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesReport,
    FlextCliUtilitiesProcesses,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesXlsx,
    FlextCliUtilitiesDocx,
    FlextCliUtilitiesPptx,
    FlextCliUtilitiesYaml,
):
    """Compose utilities; document adapters load only during their operation."""

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(ignored_types=(type,))


__all__: tuple[str, ...] = ("FlextCliUtilitiesCli",)
