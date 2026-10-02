"""Compose worksheet validation, conditional-format, and protection rules.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from flext_cli import m, p, r, t
from flext_cli._utilities._xlxx.xlsx_conditional import FlextCliUtilitiesXlsxConditional
from flext_cli._utilities._xlxx.xlsx_protection import FlextCliUtilitiesXlsxProtection
from flext_cli._utilities._xlxx.xlsx_validations import FlextCliUtilitiesXlsxValidations


class FlextCliUtilitiesXlsxRules(
    FlextCliUtilitiesXlsxConditional,
    FlextCliUtilitiesXlsxProtection,
    FlextCliUtilitiesXlsxValidations,
):
    """Apply every rule family through one fail-loud worksheet boundary."""

    # NOTE (multi-agent, mro-j2yt.1): each stage retains the same plan models;
    # no dump, revalidation, or rule-specific transport is introduced.
    @classmethod
    def _apply_rules(
        cls,
        worksheet: Worksheet,
        plan: m.Cli.XlsxSheetRulesPlan,
    ) -> p.Result[bool]:
        validations = cls._apply_validations(worksheet, plan.validations)
        if validations.failure:
            return r[bool].from_failure(validations)
        conditional = cls._apply_conditional_formats(
            worksheet,
            plan.conditional_formats,
        )
        if conditional.failure:
            return r[bool].from_failure(conditional)
        protection = cls._apply_protection(worksheet, plan.protection)
        if protection.failure:
            return r[bool].from_failure(protection)
        return r[bool].ok(value=True)


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesXlsxRules",)
