# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import _models_parts as _models_parts
    from enum import StrEnum, unique
    from flext_cli import d, e, h, r, s, x
    from typing import Final, TYPE_CHECKING

    from ._models_parts.examples_advanced import ExamplesFlextCliModelsExamplesAdvanced
    from ._models_parts.examples_common import ExamplesFlextCliModelsExamplesCommon
    from ._models_parts.examples_database import ExamplesFlextCliModelsExamplesDatabase
    from ._models_parts.examplesflextclimodels_part_01 import ExamplesFlextCliModels
    from .constants import ExamplesFlextCliConstants, ExamplesFlextCliConstants as c
    from .ex_01_getting_started import ExamplesFlextCliGettingStarted
    from .ex_02_output_formatting import export_report
    from .ex_04_file_operations import (
        load_deployment_config,
        load_user_preferences,
        save_deployment_config,
        save_user_preferences,
        validate_and_import_data,
    )
    from .ex_05_authentication import Ex05Authentication
    from .ex_06_settings import Ex06Settings
    from .ex_11_complete_integration import DataManagerCLI
    from .ex_12_pydantic_driven_cli import (
        convert_and_validate_with_pydantic,
        create_database_config_from_cli,
        perform_connection_test,
        validate_business_rules,
        validate_required_fields,
    )
    from .models import m
    from .protocols import ExamplesFlextCliProtocols, ExamplesFlextCliProtocols as p
    from .typings import ExamplesFlextCliTypes, ExamplesFlextCliTypes as t
    from .utilities import ExamplesFlextCliUtilities, ExamplesFlextCliUtilities as u
__all__: tuple[str, ...] = (
    "TYPE_CHECKING",
    "DataManagerCLI",
    "Ex05Authentication",
    "Ex06Settings",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliModelsExamplesAdvanced",
    "ExamplesFlextCliModelsExamplesCommon",
    "ExamplesFlextCliModelsExamplesDatabase",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "Final",
    "MappingProxyType",
    "StrEnum",
    "_models_parts",
    "c",
    "convert_and_validate_with_pydantic",
    "create_database_config_from_cli",
    "d",
    "e",
    "export_report",
    "h",
    "load_deployment_config",
    "load_user_preferences",
    "m",
    "p",
    "perform_connection_test",
    "r",
    "s",
    "save_deployment_config",
    "save_user_preferences",
    "t",
    "u",
    "unique",
    "validate_and_import_data",
    "validate_business_rules",
    "validate_required_fields",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._models_parts": ("_models_parts",),
            "._models_parts.examples_advanced": (
                "ExamplesFlextCliModelsExamplesAdvanced",
            ),
            "._models_parts.examples_common": ("ExamplesFlextCliModelsExamplesCommon",),
            "._models_parts.examples_database": (
                "ExamplesFlextCliModelsExamplesDatabase",
            ),
            "._models_parts.examplesflextclimodels_part_01": (
                "ExamplesFlextCliModels",
            ),
            ".constants": ("ExamplesFlextCliConstants", "c"),
            ".ex_01_getting_started": ("ExamplesFlextCliGettingStarted",),
            ".ex_02_output_formatting": ("export_report",),
            ".ex_04_file_operations": (
                "load_deployment_config",
                "load_user_preferences",
                "save_deployment_config",
                "save_user_preferences",
                "validate_and_import_data",
            ),
            ".ex_05_authentication": ("Ex05Authentication",),
            ".ex_06_settings": ("Ex06Settings",),
            ".ex_11_complete_integration": ("DataManagerCLI",),
            ".ex_12_pydantic_driven_cli": (
                "convert_and_validate_with_pydantic",
                "create_database_config_from_cli",
                "perform_connection_test",
                "validate_business_rules",
                "validate_required_fields",
            ),
            ".models": ("m",),
            ".protocols": ("ExamplesFlextCliProtocols", "p"),
            ".typings": ("ExamplesFlextCliTypes", "t"),
            ".utilities": ("ExamplesFlextCliUtilities", "u"),
            "enum": ("StrEnum", "unique"),
            "flext_cli": ("d", "e", "h", "r", "s", "x"),
            "types": ("MappingProxyType",),
            "typing": ("Final", "TYPE_CHECKING"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
