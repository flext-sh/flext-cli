"""Extracted facade class for yaml.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._yaml import FlextCliUtilitiesYamlEditing


class FlextCliUtilitiesYaml(
    FlextCliUtilitiesYamlEditing,
):
    """Facade for yaml."""


__all__: list[str] = ["FlextCliUtilitiesYaml"]
