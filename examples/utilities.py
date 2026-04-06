"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY cli wrappers - NO direct Rich imports!
All data transport uses Pydantic v2 models from flext_cli (m.Cli).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableSequence

from examples.models import m
from examples.typings import t
from flext_cli import cli, u as _cli_u
from flext_core import r


class FlextCliExamplesUtilities(_cli_u):
    """Public examples utility facade extending flext-cli utilities."""

    @classmethod
    def to_json_dict(
        cls,
        data: t.ContainerMapping,
    ) -> m.Cli.DisplayData:
        """Normalize config/mapping to DisplayData for create_table/display_config_table."""
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
        style: str = "green",
    ) -> None:
        """Print standardized demo completion message using cli."""
        cli.print(f"\n🎉 {demo_name} Complete", style=f"bold {style}")
        cli.print(f"✅ {demo_name} Completed!", style=style)
        cli.print("\nKey Features Demonstrated:", style="cyan")
        for feature in features:
            cli.print(f"  • {feature}", style="white")
        cli.print(
            "\nAll operations used r pattern for error handling!",
            style="yellow",
        )

    @staticmethod
    def handle_command_result(
        result: r[m.Value],
        action: str,
        success_fields: t.StrSequence | None = None,
    ) -> None:
        """Generic handler for CQRS command results."""
        success_fields = success_fields or ["id", "status"]

        if result.is_success:
            raw = result.value
            data = raw.model_dump()
            cli.print(f"✅ {action.title()} successful", style="green")
            for field in success_fields:
                if field in data:
                    display_name = field.replace("_", " ").title()
                    cli.print(f"{display_name}: {data[field]}")
        else:
            cli.print(f"❌ Failed to {action}: {result.error}", style="red")

    @staticmethod
    def print_demo_error(
        demo_name: str,
        error: str,
        *,
        style: str = "red",
    ) -> None:
        """Print standardized demo error message."""
        cli.print(f"❌ {demo_name} failed: {error}", style=f"bold {style}")
        cli.print(
            "This failure demonstrates r error handling!",
            style="yellow",
        )
        cli.print(
            "The error was caught and wrapped in a r for clean handling.",
            style="white",
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
            style="bold green",
        )
        if details is not None:
            for key, value in details.root.items():
                cli.print(f"   {key}: {value}", style="cyan")

    @staticmethod
    def display_validation_errors(
        errors: t.StrSequence,
        context: str = "validation",
    ) -> None:
        """Display validation errors in a consistent format using cli."""
        cli.print(
            f"❌ {context.title()} failed with {len(errors)} error(s):",
            style="bold red",
        )
        for i, error in enumerate(errors, 1):
            cli.print(f"   {i}. {error}", style="red")


u = FlextCliExamplesUtilities

__all__ = [
    "FlextCliExamplesUtilities",
    "u",
]
