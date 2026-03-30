# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if TYPE_CHECKING:
    from tests.conftest import *
    from tests.constants import *
    from tests.helpers import *
    from tests.models import *
    from tests.typings import *
    from tests.unit import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    (
        "tests.helpers",
        "tests.unit",
    ),
    {
        "Examples": "tests.conftest",
        "FlextCliTestConstants": "tests.constants",
        "FlextCliTestModels": "tests.models",
        "FlextCliTestTypes": "tests.typings",
        "InfoTuples": "tests.conftest",
        "c": ("tests.constants", "FlextCliTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": "flext_tests",
        "e": "flext_tests",
        "h": "flext_tests",
        "helpers": "tests.helpers",
        "m": ("tests.models", "FlextCliTestModels"),
        "models": "tests.models",
        "p": "flext_tests",
        "pytest_collection_modifyitems": "tests.conftest",
        "pytest_configure": "tests.conftest",
        "r": "flext_tests",
        "s": "flext_tests",
        "t": ("tests.typings", "FlextCliTestTypes"),
        "typings": "tests.typings",
        "u": "flext_tests",
        "unit": "tests.unit",
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
