"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY cli wrappers - NO direct Rich imports!
All data transport uses Pydantic v2 models from flext_cli (m.Cli).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableSequence

from examples import c, m, t
from flext_cli import cli, u
from flext_core import r


class ExamplesFlextCliUtilities(u):
    """Public examples utility facade extending flext-cli utilities."""

    @classmethod
    def to_json_dict(
        cls,
        data: t.ContainerMapping,
    ) -> m.Cli.DisplayData:
        """Normalize settings/mapping to DisplayData for create_table/display_config_table."""
        json_value: t.Cli.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_python(
            cls.Cli.normalize_json_value(data),
        )
        normalized = m.Cli.CliNormalizedJson(json_value).root
        resolved = m.Cli.NormalizedJsonDict(value=normalized, default={}).resolved
        result_dict = dict(resolved.items())
        return m.Cli.DisplayData(data=result_dict)

    @staticmethod
    def print_demo_completion(
        demo_name: str,
        features: t.StrSequence,
        *,
        style: c.Cli.MessageStyles = c.Cli.MessageStyles.GREEN,
        bold_style: c.Cli.MessageStyles = c.Cli.MessageStyles.BOLD_GREEN,
    ) -> None:
        """Print standardized demo completion message using cli."""
        cli.print(f"\n🎉 {demo_name} Complete", style=bold_style)
        cli.print(f"✅ {demo_name} Completed!", style=style)
        cli.print("\nKey Features Demonstrated:", style=c.Cli.MessageStyles.CYAN)
        for feature in features:
            cli.print(f"  • {feature}", style=c.Cli.MessageStyles.WHITE)
        cli.print(
            "\nAll operations used r pattern for error handling!",
            style=c.Cli.MessageStyles.YELLOW,
        )

    @staticmethod
    def handle_command_result(
        result: r[m.Value],
        action: str,
        success_fields: t.StrSequence | None = None,
    ) -> None:
        """Generic handler for CQRS command results."""
        success_fields = success_fields or ["id", "status"]

        if result.success:
            raw = result.value
            data = raw.model_dump()
            cli.print(
                f"✅ {action.title()} successful", style=c.Cli.MessageStyles.GREEN
            )
            for field in success_fields:
                if field in data:
                    display_name = field.replace("_", " ").title()
                    cli.print(f"{display_name}: {data[field]}")
        else:
            cli.print(
                f"❌ Failed to {action}: {result.error}", style=c.Cli.MessageStyles.RED
            )

    @staticmethod
    def print_demo_error(
        demo_name: str,
        error: str,
        *,
        bold_style: c.Cli.MessageStyles = c.Cli.MessageStyles.BOLD_RED,
    ) -> None:
        """Print standardized demo error message."""
        cli.print(f"❌ {demo_name} failed: {error}", style=bold_style)
        cli.print(
            "This failure demonstrates r error handling!",
            style=c.Cli.MessageStyles.YELLOW,
        )
        cli.print(
            "The error was caught and wrapped in a r for clean handling.",
            style=c.Cli.MessageStyles.WHITE,
        )

    @staticmethod
    def display_config_table(
        config_data: m.Cli.DisplayData | m.Value,
        headers: t.StrSequence | None = None,
    ) -> None:
        """Display configuration as a table using canonical example models."""
        if headers is None:
            headers = ["Setting", "Value"]
        rows: MutableSequence[t.StrMapping] = []
        if isinstance(config_data, m.Cli.DisplayData):
            for key, value in config_data.data.items():
                rows.append({"Setting": str(key), "Value": str(value)})
        else:
            dumped = config_data.model_dump(mode="json")
            for key, value in dumped.items():
                rows.append({"Setting": str(key), "Value": str(value)})
        cli.show_table(rows, headers=headers)

    @staticmethod
    def display_success_summary(
        operation: str,
        details: m.Cli.SuccessSummaryDetails | None = None,
    ) -> None:
        """Display a standardized success summary using cli."""
        cli.print(
            f"✅ {operation} completed successfully!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )
        if details is not None:
            for key, value in details.root.items():
                cli.print(f"   {key}: {value}", style=c.Cli.MessageStyles.CYAN)

    @staticmethod
    def display_validation_errors(
        errors: t.StrSequence,
        context: str = "validation",
    ) -> None:
        """Display validation errors in a consistent format using cli."""
        cli.print(
            f"❌ {context.title()} failed with {len(errors)} error(s):",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        for i, error in enumerate(errors, 1):
            cli.print(f"   {i}. {error}", style=c.Cli.MessageStyles.RED)


u = ExamplesFlextCliUtilities

__all__: list[str] = [
    "ExamplesFlextCliUtilities",
    "u",
]
