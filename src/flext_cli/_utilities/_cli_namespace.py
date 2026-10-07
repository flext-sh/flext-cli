"""Heavy ``u.Cli`` utility namespace materialized on demand.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities import FlextCliUtilitiesOptionsPart02
from flext_cli._utilities import FlextCliUtilitiesAuth
from flext_cli._utilities import FlextCliUtilitiesCmd
from flext_cli._utilities import FlextCliUtilitiesCommands
from flext_cli._utilities import FlextCliUtilitiesConfig
from flext_cli._utilities import FlextCliUtilitiesConversion
from flext_cli._utilities import FlextCliUtilitiesDocx
from flext_cli._utilities import FlextCliUtilitiesEnv
from flext_cli._utilities import FlextCliUtilitiesFileTestHelpersMixin
from flext_cli._utilities import FlextCliUtilitiesFiles
from flext_cli._utilities import FlextCliUtilitiesFormatters
from flext_cli._utilities import FlextCliUtilitiesFramework
from flext_cli._utilities import FlextCliUtilitiesJson
from flext_cli._utilities import FlextCliUtilitiesMatching
from flext_cli._utilities import FlextCliUtilitiesOutput
from flext_cli._utilities import FlextCliUtilitiesParams
from flext_cli._utilities import FlextCliUtilitiesPipeline
from flext_cli._utilities import FlextCliUtilitiesPptx
from flext_cli._utilities import FlextCliUtilitiesProcesses
from flext_cli._utilities import FlextCliUtilitiesPrompts
from flext_cli._utilities import FlextCliUtilitiesReport
from flext_cli._utilities import FlextCliUtilitiesRules
from flext_cli._utilities import FlextCliUtilitiesRuntime
from flext_cli._utilities import FlextCliUtilitiesSettings
from flext_cli._utilities import FlextCliUtilitiesTables
from flext_cli._utilities import FlextCliUtilitiesTemplate
from flext_cli._utilities import FlextCliUtilitiesToml
from flext_cli._utilities import FlextCliUtilitiesValidation
from flext_cli._utilities import FlextCliUtilitiesXlsx
from flext_cli._utilities import FlextCliUtilitiesYaml
from flext_cli._utilities import FlextCliUtilitiesYamlModel


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
