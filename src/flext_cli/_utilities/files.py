"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import importlib as _importlib

from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_01 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart01,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart04,
)


class FlextCliUtilitiesFiles(
    FlextCliUtilitiesFilesPart01,
    FlextCliUtilitiesFilesPart02,
    FlextCliUtilitiesFilesPart03,
    FlextCliUtilitiesFilesPart04,
):
    """Public facade for FlextCliUtilitiesFiles."""


__all__: list[str] = ["FlextCliUtilitiesFiles"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_01"
    ),
    "FlextCliUtilitiesFiles",
    FlextCliUtilitiesFiles,
)
setattr(
    _importlib.import_module(
        "flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_02"
    ),
    "FlextCliUtilitiesFiles",
    FlextCliUtilitiesFiles,
)
setattr(
    _importlib.import_module(
        "flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03"
    ),
    "FlextCliUtilitiesFiles",
    FlextCliUtilitiesFiles,
)
setattr(
    _importlib.import_module(
        "flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04"
    ),
    "FlextCliUtilitiesFiles",
    FlextCliUtilitiesFiles,
)
