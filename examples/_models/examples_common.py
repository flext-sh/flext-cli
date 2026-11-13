"""Split example model common namespace.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from examples import c, t
from flext_cli import m, settings


class ExamplesFlextCliModelsExamplesCommon:
    """Split example model common namespace."""

    # -------------------------------------------------------------------
    # Example 13 - Single result command
    # -------------------------------------------------------------------

    class GreetingRequest(m.Value):
        """Greet one person by name."""

        name: Annotated[str, m.Field(description="Person to greet")]
        shout: Annotated[bool, m.Field(description="Greet in upper case")] = False

    # -------------------------------------------------------------------
    # Example 06 - Configuration
    # -------------------------------------------------------------------

    class MyAppSettings(m.Value):
        """Custom settings for YOUR CLI application — Pydantic v2 only."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        app_name: Annotated[str, m.Field(description="Application name")] = (
            c.EXAMPLE_DEFAULT_TOOL_NAME
        )
        api_key: Annotated[str, m.Field(description="API key")] = ""
        max_workers: Annotated[int, m.Field(ge=1, description="Max workers")] = (
            c.EXAMPLE_DEFAULT_MAX_WORKERS
        )
        timeout: Annotated[int, m.Field(ge=1, description="Timeout in seconds")] = (
            c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS
        )

        def display(self, cli: t.CliApi) -> None:
            """Display app settings; uses the canonical CLI settings singleton."""
            rows: t.Cli.TableMappingRow = {
                "App Name": self.app_name,
                "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                "Max Workers": str(self.max_workers),
                "Timeout": f"{self.timeout}s",
                "Debug": str(settings.debug),
                "App": settings.cli_app_name,
            }
            cli.show_table(rows, show_header=True, title="⚙️  Application Settings")


__all__: list[str] = ["ExamplesFlextCliModelsExamplesCommon"]
