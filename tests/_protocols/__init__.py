# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests._protocols.tests_cli import TestsFlextCliProtocolsTestsCli
    from tests._protocols.tests_runtime import TestsFlextCliProtocolsTestsRuntime


__all__: tuple[str, ...] = (
    "TestsFlextCliProtocolsTestsCli",
    "TestsFlextCliProtocolsTestsRuntime",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "TestsFlextCliProtocolsTestsCli": ".tests_cli",
        "TestsFlextCliProtocolsTestsRuntime": ".tests_runtime",
    },
    public_exports=__all__,
    deferred_members={
        "TestsFlextCliProtocolsTestsCli": (
            "SampleInput",
            "SampleOutput",
            "RepeatableInput",
            "ReportRow",
            "UserPreferences",
            "DeploymentConfig",
            "ImportRecord",
            "SummaryStats",
            "ProjectFailureInfo",
        ),
        "TestsFlextCliProtocolsTestsRuntime": (
            "ApiResponse",
            "ModelCommandSample",
            "ModelCommandNullable",
            "ModelCommandRequired",
            "RuntimeCommandCase",
        ),
    },
)
