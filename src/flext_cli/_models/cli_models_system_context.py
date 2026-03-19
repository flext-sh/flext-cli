from __future__ import annotations

from typing import Annotated

from flext_core import FlextModels
from pydantic import Field

from flext_cli import t


class FlextCliModelsSystemContext:
    class PathInfo(FlextModels.Value):
        index: Annotated[
            int,
            Field(default=0, description="Path index in sys.path"),
        ]
        path: Annotated[str, Field(...)]
        exists: Annotated[bool, Field(default=False)]
        is_file: Annotated[bool, Field(default=False)]
        is_dir: Annotated[bool, Field(default=False)]

    class EnvironmentInfo(FlextModels.Value):
        python_version: Annotated[str, Field(default="")]
        os_name: Annotated[str, Field(default="")]
        os_version: Annotated[str, Field(default="")]
        variables: Annotated[dict[str, str], Field(default_factory=dict)]

    class SystemInfo(FlextModels.Value):
        python_version: Annotated[str, Field(default="")]
        platform: Annotated[str, Field(default="")]
        architecture: Annotated[list[str], Field(default_factory=list)]
        processor: Annotated[str, Field(default="")]
        hostname: Annotated[str, Field(default="")]
        memory_total: Annotated[int, Field(default=0)]
        cpu_count: Annotated[int, Field(default=0)]

    class ContextExecutionResult(FlextModels.Value):
        success: Annotated[bool, Field(default=True)]
        context_id: Annotated[str, Field(default="")]
        metadata: Annotated[
            dict[str, t.Cli.JsonValue],
            Field(default_factory=dict),
        ]
        context_executed: Annotated[
            bool,
            Field(
                default=False,
                description="Whether context was executed",
            ),
        ]
        command: Annotated[
            str,
            Field(default="", description="Command executed in context"),
        ]
        arguments_count: Annotated[
            int,
            Field(default=0, description="Number of arguments"),
        ]
        timestamp: Annotated[
            str,
            Field(default="", description="Execution timestamp"),
        ]
