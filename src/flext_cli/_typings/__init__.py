# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._typings.base import FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain
    from flext_cli._typings.pipeline import FlextCliTypesPipeline
    from flext_cli._typings.xlsx import FlextCliTypesXlsx


__all__: tuple[str, ...] = (
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliTypesPipeline",
    "FlextCliTypesXlsx",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliTypesBase": ".base",
        "FlextCliTypesDomain": ".domain",
        "FlextCliTypesPipeline": ".pipeline",
        "FlextCliTypesXlsx": ".xlsx",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliTypesBase": (
            "TableMappingRow",
            "TableSequenceRow",
            "DefaultMapping",
            "TableRow",
            "TableConfigValue",
            "TabularData",
            "TableRows",
            "TableIndexValue",
            "TableIndexSelection",
            "TableShowIndex",
            "TableDisableNumparse",
            "TableColAlign",
            "CliValue",
            "CliDefaultSource",
            "CliAnnotations",
            "TomlDocument",
            "TomlTable",
            "TomlItem",
            "TomlArray",
            "TomlAoT",
            "TomlContainer",
            "TomlParent",
            "TomlValue",
            "RuntimeAnnotation",
            "SignalHandler",
            "TemplateEnvironmentCache",
        ),
        "FlextCliTypesDomain": (
            "YamlScalar",
            "YamlCollection",
            "YamlValue",
            "YamlNode",
            "YamlSequence",
            "YamlCommentSlot",
            "XlsxConditionalFormatting",
            "XlsxConditionalFormatRule",
            "DocxParagraphAlignment",
            "ResultValue",
            "RuleDefinitions",
            "RuleMatcher",
            "RuleMatchers",
            "RuleCatalog",
            "MatchedRuleDefinition",
            "MatchedRuleDefinitions",
            "RuleLoadResult",
            "RuleLoadOption",
            "CliParamValue",
            "CliParamKwargs",
            "DefaultAtom",
            "ProjectNamesValue",
            "TableHeaders",
            "IntTextValue",
            "MessageType",
            "CommandParameter",
            "ModelLike",
            "OptionRegistry",
            "NullaryOperation",
            "PromptTextReader",
            "CliCommand",
            "DirFdOperation",
            "JsonCommandFn",
            "SuccessMessageFormatter",
            "ServiceMessageFormatter",
            "TomlMappingSource",
            "TomlUnwrappedSource",
            "TomlStringListSource",
            "TomlRuntimeSource",
            "TypeKind",
            "TypedExtractValue",
            "TableDataSource",
            "TextPath",
            "JsonWriteData",
        ),
        "FlextCliTypesPipeline": (
            "PipelineStageStatus",
            "DagEdges",
            "DagGraph",
        ),
        "FlextCliTypesXlsx": (
            "XlsxCellPrimitive",
            "XlsxBinaryStream",
            "XlsxMemberNames",
            "XlsxCalcMode",
            "XlsxXmlTokens",
            "XlsxComparisonOperator",
            "XlsxValidationType",
            "XlsxArchiveViolationKind",
            "XlsxUnderlineStyle",
        ),
    },
)
