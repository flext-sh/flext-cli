"""Apply typed conditional-format plans through openpyxl."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openpyxl.cell.cell import Cell
from openpyxl.formatting.rule import Rule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.styles.numbers import NumberFormat, builtin_format_id

# mro-j47u (kimi): utilities consume local facades only, never private modules.
from flext_cli import c, m, p, r

from .xlsx_addresses import FlextCliUtilitiesXlsxAddresses
from .xlsx_formula_codec import FlextCliUtilitiesXlsxFormulaCodec
from .xlsx_style_codec import FlextCliUtilitiesXlsxStyleCodec
from .xlsx_validations import FlextCliUtilitiesXlsxValidations

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


class FlextCliUtilitiesXlsxConditional(
    FlextCliUtilitiesXlsxStyleCodec,
    FlextCliUtilitiesXlsxValidations,
    FlextCliUtilitiesXlsxAddresses,
):
    """Build differential styles and conditional rules from runtime plans."""

    # NOTE (multi-agent, mro-j2yt.1): conditional formulas are derived from
    # typed plans and top-left addresses; no worksheet-specific formulas live here.
    @classmethod
    def _registered_style(
        cls, worksheet: Worksheet, name: str
    ) -> p.Result[p.Cli.XlsxNamedStyleSpec]:
        try:
            probe = Cell(worksheet, row=1, column=1)
            probe.style = name
        except (KeyError, ValueError):
            return r[p.Cli.XlsxNamedStyleSpec].fail(
                f"{c.Cli.XlsxError.NAMED_STYLE_MISSING}: {name}"
            )
        visual = cls._visual_from_styleable(probe)
        if visual.failure:
            return r[p.Cli.XlsxNamedStyleSpec].fail(
                visual.error or f"Failed to read registered style: {name}"
            )
        return r[p.Cli.XlsxNamedStyleSpec].ok(
            m.Cli.XlsxNamedStyleSpec(name=name, visual=visual.value)
        )

    @classmethod
    def _differential_style(cls, spec: p.Cli.XlsxNamedStyleSpec) -> DifferentialStyle:
        visual = spec.visual
        number_format_id = builtin_format_id(visual.number_format) or 0
        return DifferentialStyle(
            font=cls._font(visual.font),
            fill=cls._fill(visual.fill),
            border=cls._border(visual.border),
            alignment=cls._alignment(visual.alignment),
            numFmt=NumberFormat(
                numFmtId=number_format_id, formatCode=visual.number_format
            ),
        )

    @classmethod
    def _rule(
        cls, plan: p.Cli.XlsxConditionalFormatPlan, style: p.Cli.XlsxNamedStyleSpec
    ) -> Rule:
        differential = cls._differential_style(style)
        if plan.kind == "contains_text":
            escaped = plan.text.replace('"', '""')
            first = cls._cell_ref(plan.area.first)
            formula = f'NOT(ISERROR(SEARCH("{escaped}",{first})))'
            return Rule(
                type="containsText",
                operator="containsText",
                text=plan.text,
                formula=(formula,),
                stopIfTrue=plan.stop_if_true,
                dxf=differential,
            )
        if plan.kind == "formula":
            return Rule(
                type="expression",
                formula=tuple(
                    FlextCliUtilitiesXlsxFormulaCodec.storage_formula(expression)
                    for expression in plan.expressions
                ),
                stopIfTrue=plan.stop_if_true,
                dxf=differential,
            )
        comparison = plan.comparison
        if isinstance(comparison, m.Cli.XlsxRangeComparison):
            formulae = (comparison.minimum, comparison.maximum)
        else:
            formulae = (comparison.expression,)
        return Rule(
            type="cellIs",
            operator=cls._comparison_operator(comparison.mode),
            formula=formulae,
            stopIfTrue=plan.stop_if_true,
            dxf=differential,
        )

    @classmethod
    def _apply_conditional_formats(
        cls, worksheet: Worksheet, plans: tuple[p.Cli.XlsxConditionalFormatPlan, ...]
    ) -> p.Result[bool]:
        try:
            for plan in plans:
                style = cls._registered_style(worksheet, plan.style)
                if style.failure:
                    return r[bool].fail(style.error or "Named style resolution failed")
                worksheet.conditional_formatting.add(
                    cls._range_ref(plan.area), cls._rule(plan, style.value)
                )
        except (TypeError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[bool].fail(f"{c.Cli.XlsxError.RENDER_FAILED}: {detail}")
        return r[bool].ok(True)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxConditional",)
