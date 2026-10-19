"""Heavy ``u.Cli`` utility namespace materialized on demand.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m
from flext_cli._utilities import (
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConfig,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesDocx,
    FlextCliUtilitiesEnv,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFileTestHelpersMixin,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesFramework,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPptx,
    FlextCliUtilitiesProcesses,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesReport,
    FlextCliUtilitiesRules,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesTemplate,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesXlsx,
    FlextCliUtilitiesYaml,
    FlextCliUtilitiesYamlModel,
)
from flext_cli._utilities._options.flextcliutilitiesoptions_part_02 import (
    FlextCliUtilitiesOptionsPart02,
)


class FlextCliUtilitiesModelConfig:
    """Native configuration owned beside the namespace it protects."""

    model_config = m.ConfigDict(ignored_types=(type,))


class FlextCliUtilitiesCli(
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConfig,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesEnv,
    FlextCliUtilitiesTemplate,
    FlextCliUtilitiesFileTestHelpersMixin,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesFramework,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesOptionsPart02,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesReport,
    FlextCliUtilitiesProcesses,
    FlextCliUtilitiesRules,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesXlsx,
    FlextCliUtilitiesDocx,
    FlextCliUtilitiesPptx,
    FlextCliUtilitiesYaml,
    FlextCliUtilitiesYamlModel,
):
    """Compose utilities; document adapters load only during their operation."""


__all__: tuple[str, ...] = ("FlextCliUtilitiesCli", "FlextCliUtilitiesModelConfig")
