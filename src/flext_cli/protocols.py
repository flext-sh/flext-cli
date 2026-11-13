# AUTO-GENERATED FILE — Regenerate with: make gen
"""CLI protocol facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeAlias

from flext_core import FlextProtocols

from flext_cli._protocols import (
    FlextCliProtocolsAtomicFile,
    FlextCliProtocolsAtomicQueries,
    FlextCliProtocolsBase,
    FlextCliProtocolsColor,
    FlextCliProtocolsConfig,
    FlextCliProtocolsDocx,
    FlextCliProtocolsDocxDocument,
    FlextCliProtocolsDocxStyles,
    FlextCliProtocolsDomain,
    FlextCliProtocolsFileChange,
    FlextCliProtocolsFiles,
    FlextCliProtocolsFramework,
    FlextCliProtocolsMarkdown,
    FlextCliProtocolsPipeline,
    FlextCliProtocolsPptxPresentation,
    FlextCliProtocolsProcess,
    FlextCliProtocolsProcessRuntime,
    FlextCliProtocolsRules,
    FlextCliProtocolsTableRender,
    FlextCliProtocolsTemplate,
    FlextCliProtocolsXlsx,
)


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols.

    CLI protocol refinements take precedence in MRO while ``Result`` and the
    other core protocol members remain inherited from ``FlextProtocols``.
    """

    class Cli(
        FlextCliProtocolsAtomicFile,
        FlextCliProtocolsAtomicQueries,
        FlextCliProtocolsBase,
        FlextCliProtocolsColor,
        FlextCliProtocolsConfig,
        FlextCliProtocolsDocx,
        FlextCliProtocolsDocxDocument,
        FlextCliProtocolsDocxStyles,
        FlextCliProtocolsDomain,
        FlextCliProtocolsFileChange,
        FlextCliProtocolsFiles,
        FlextCliProtocolsFramework,
        FlextCliProtocolsMarkdown,
        FlextCliProtocolsPipeline,
        FlextCliProtocolsPptxPresentation,
        FlextCliProtocolsProcess,
        FlextCliProtocolsProcessRuntime,
        FlextCliProtocolsRules,
        FlextCliProtocolsTableRender,
        FlextCliProtocolsTemplate,
        FlextCliProtocolsXlsx,
    ):
        """Unified CLI protocol namespace."""

        ModelCommandHandler: TypeAlias = FlextCliProtocolsDomain.ModelCommandHandler
        DeclarativeRuleType: TypeAlias = FlextCliProtocolsDomain.DeclarativeRuleType
        DeclarativeFileRuleType: TypeAlias = (
            FlextCliProtocolsDomain.DeclarativeFileRuleType
        )
        ProcessNativeQualificationReceipt: TypeAlias = (
            FlextCliProtocolsProcess.ProcessNativeQualificationReceipt
        )
        ProcessNativeQualificationReport: TypeAlias = (
            FlextCliProtocolsProcess.ProcessNativeQualificationReport
        )
        LocalDefinitionsOptions: TypeAlias = (
            FlextCliProtocolsRules.LocalDefinitionsOptions
        )


p = FlextCliProtocols
__all__: list[str] = ["FlextCliProtocols", "p"]
