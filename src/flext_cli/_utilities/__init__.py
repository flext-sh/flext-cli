# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from ._cli_namespace import FlextCliUtilitiesCli as FlextCliUtilitiesCli
from .auth import FlextCliUtilitiesAuth as FlextCliUtilitiesAuth
from .cmd import FlextCliUtilitiesCmd as FlextCliUtilitiesCmd
from .commands import FlextCliUtilitiesCommands as FlextCliUtilitiesCommands
from .config import FlextCliUtilitiesConfig as FlextCliUtilitiesConfig
from .conversion import FlextCliUtilitiesConversion as FlextCliUtilitiesConversion
from .env import FlextCliUtilitiesEnv as FlextCliUtilitiesEnv
from .formatters import FlextCliUtilitiesFormatters as FlextCliUtilitiesFormatters
from .framework import FlextCliUtilitiesFramework as FlextCliUtilitiesFramework
from .json import FlextCliUtilitiesJson as FlextCliUtilitiesJson
from .matching import FlextCliUtilitiesMatching as FlextCliUtilitiesMatching
from .model_commands import (
    FlextCliUtilitiesModelCommands as FlextCliUtilitiesModelCommands,
)
from .output import FlextCliUtilitiesOutput as FlextCliUtilitiesOutput
from .params import FlextCliUtilitiesParams as FlextCliUtilitiesParams
from .pipeline import FlextCliUtilitiesPipeline as FlextCliUtilitiesPipeline
from .processes import FlextCliUtilitiesProcesses as FlextCliUtilitiesProcesses
from .prompts import FlextCliUtilitiesPrompts as FlextCliUtilitiesPrompts
from .rules import FlextCliUtilitiesRules as FlextCliUtilitiesRules
from .runtime import FlextCliUtilitiesRuntime as FlextCliUtilitiesRuntime
from .settings import FlextCliUtilitiesSettings as FlextCliUtilitiesSettings
from .tables import FlextCliUtilitiesTables as FlextCliUtilitiesTables
from .template import FlextCliUtilitiesTemplate as FlextCliUtilitiesTemplate
from .validation import FlextCliUtilitiesValidation as FlextCliUtilitiesValidation
from .yaml import FlextCliUtilitiesYaml as FlextCliUtilitiesYaml
from .yaml_model import FlextCliUtilitiesYamlModel as FlextCliUtilitiesYamlModel

try:
    from .xlsx import FlextCliUtilitiesXlsx as FlextCliUtilitiesXlsx
except ModuleNotFoundError:

    class FlextCliUtilitiesXlsx:
        """Fallback when openpyxl is not installed."""

__all__: tuple[str, ...] = (
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesCli",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfig",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesEnv",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesFramework",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesProcesses",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesRules",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesSettings",
    "FlextCliUtilitiesTables",
    "FlextCliUtilitiesTemplate",
    "FlextCliUtilitiesValidation",
    "FlextCliUtilitiesXlsx",
    "FlextCliUtilitiesYaml",
    "FlextCliUtilitiesYamlModel",
)
