"""Heavy ``u.Cli`` utility namespace materialized on demand."""

from __future__ import annotations

from ._options_parts.flextcliutilitiesoptions_part_02 import FlextCliUtilitiesOptions
from .auth import FlextCliUtilitiesAuth
from .cmd import FlextCliUtilitiesCmd
from .commands import FlextCliUtilitiesCommands
from .config import FlextCliUtilitiesConfig
from .conversion import FlextCliUtilitiesConversion
from .docx import FlextCliUtilitiesDocx
from .env import FlextCliUtilitiesEnv
from .file_test_helpers import FlextCliUtilitiesFileTestHelpersMixin
from .files import FlextCliUtilitiesFiles
from .formatters import FlextCliUtilitiesFormatters
from .framework import FlextCliUtilitiesFramework
from .json import FlextCliUtilitiesJson
from .matching import FlextCliUtilitiesMatching
from .model_commands import FlextCliUtilitiesModelCommands
from .output import FlextCliUtilitiesOutput
from .params import FlextCliUtilitiesParams
from .pipeline import FlextCliUtilitiesPipeline
from .pptx import FlextCliUtilitiesPptx
from .processes import FlextCliUtilitiesProcesses
from .prompts import FlextCliUtilitiesPrompts
from .rules import FlextCliUtilitiesRules
from .runtime import FlextCliUtilitiesRuntime
from .settings import FlextCliUtilitiesSettings
from .tables import FlextCliUtilitiesTables
from .template import FlextCliUtilitiesTemplate
from .toml import FlextCliUtilitiesToml
from .validation import FlextCliUtilitiesValidation
from .xlsx import FlextCliUtilitiesXlsx
from .yaml import FlextCliUtilitiesYaml
from .yaml_model import FlextCliUtilitiesYamlModel


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
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPrompts,
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


__all__: tuple[str, ...] = ("FlextCliUtilitiesCli",)
