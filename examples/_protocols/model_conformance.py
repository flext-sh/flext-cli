# AUTO-GENERATED FILE — Regenerate with: make gen
"""Static instance-to-protocol evidence required by candidate admission.

Copyright (c) 2026 FLEXT Team. All rights reserved.
examples/_protocols/model_conformance
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examples import ExamplesFlextCliModels, ExamplesFlextCliProtocols

    def model_protocol_1(
        value: (ExamplesFlextCliModels.AdvancedDatabaseConfig),
    ) -> ExamplesFlextCliProtocols.AdvancedDatabaseConfig:
        return value

    def model_protocol_2(
        value: (ExamplesFlextCliModels.AppSettingsAdvanced),
    ) -> ExamplesFlextCliProtocols.AppSettingsAdvanced:
        return value

    def model_protocol_3(
        value: (ExamplesFlextCliModels.MyAppSettings),
    ) -> ExamplesFlextCliProtocols.MyAppSettings:
        return value
