"""Split example model common namespace."""

from __future__ import annotations

from typing import Annotated, ClassVar

from examples import c, t
from flext_cli import m, settings


class ExamplesFlextCliModelsExamplesCommon:
    """Split example model common namespace."""

    # -------------------------------------------------------------------
    # Example 06 - Configuration
    # -------------------------------------------------------------------

    class MyAppSettings(m.Value):
        """Custom settings for YOUR CLI application — Pydantic v2 only."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid", validate_assignment=True
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
            payload_data: t.JsonMapping = {
                "App Name": self.app_name,
                "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                "Max Workers": str(self.max_workers),
                "Timeout": f"{self.timeout}s",
                "Debug": str(settings.debug),
                "App": settings.cli_app_name,
            }
            payload = m.Cli.DisplayData(data=payload_data)
            if isinstance(payload.data, dict):
                safe_data: t.Cli.TableMappingRow = {
                    k: str(v) for k, v in payload.data.items()
                }
                cli.show_table(
                    safe_data, show_header=True, title="⚙️  Application Settings"
                )


__all__: list[str] = ["ExamplesFlextCliModelsExamplesCommon"]
