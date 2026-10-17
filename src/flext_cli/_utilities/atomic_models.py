"""Private value contexts for atomic publication and tree inventory.

The payloads are declared by the models family
(``flext_cli._models.atomic_publication``); this namespace re-publishes them
for the ``u.Cli`` utilities consumers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._models.atomic_publication import FlextCliModelsAtomicPublication


class FlextCliUtilitiesAtomicModels:
    """Re-published atomic payload models owned by the models family."""

    ObservedFile = FlextCliModelsAtomicPublication.ObservedFile
    StagedFile = FlextCliModelsAtomicPublication.StagedFile
    TreeEntryDetails = FlextCliModelsAtomicPublication.TreeEntryDetails


__all__: list[str] = ["FlextCliUtilitiesAtomicModels"]
