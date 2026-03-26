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
        variables: t.StrMapping = Field(default_factory=dict)

    class SystemInfo(FlextModels.Value):
        python_version: Annotated[str, Field(default="")]
        platform: Annotated[str, Field(default="")]
        architecture: t.StrSequence = Field(default_factory=list)
        processor: Annotated[str, Field(default="")]
        hostname: Annotated[str, Field(default="")]
        memory_total: Annotated[int, Field(default=0)]
        cpu_count: Annotated[int, Field(default=0)]
