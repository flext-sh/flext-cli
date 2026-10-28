"""Pydantic models for flext-cli examples only.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from examples._models import (
    ExamplesFlextCliModelsExamplesAdvanced,
    ExamplesFlextCliModelsExamplesCommon,
    ExamplesFlextCliModelsExamplesDatabase,
)


class ExamplesFlextCliModelsPart01:
    """Implementation part for ExamplesFlextCliModelsPart01."""

    class Examples(
        ExamplesFlextCliModelsExamplesCommon,
        ExamplesFlextCliModelsExamplesAdvanced,
        ExamplesFlextCliModelsExamplesDatabase,
    ):
        """Examples namespace for example-domain models."""


__all__: list[str] = ["ExamplesFlextCliModelsPart01"]
