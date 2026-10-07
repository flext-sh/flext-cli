"""Heavy ``u.Cli`` utility namespace materialized on demand.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

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
    FlextCliUtilitiesOptionsPart02,
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
