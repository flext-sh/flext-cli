from __future__ import annotations

from typing import Annotated

from flext_core import FlextModels
from pydantic import Field

from flext_cli.typings import t


class FlextCliModelsStatistics:
    class SessionStatistics(FlextModels.Value):
        commands_executed: Annotated[
            int,
            Field(default=0, description="Number of commands executed"),
        ]
        errors_count: Annotated[
            int,
            Field(default=0, description="Number of errors encountered"),
        ]
        session_duration_seconds: Annotated[
            float,
            Field(default=0.0, description="Session duration in seconds"),
        ]

    class PromptStatistics(FlextModels.Value):
        prompts_executed: Annotated[
            int,
            Field(default=0, description="Total prompts executed"),
        ]
        history_size: Annotated[
            int,
            Field(default=0, description="Current history size"),
        ]
        prompts_answered: Annotated[
            int,
            Field(default=0, description="Prompts that received answers"),
        ]
        prompts_cancelled: Annotated[
            int,
            Field(default=0, description="Prompts that were cancelled"),
        ]
        interactive_mode: Annotated[
            bool,
            Field(default=False, description="Interactive mode flag"),
        ]
        default_timeout: Annotated[
            int,
            Field(default=30, description="Default timeout in seconds"),
        ]
        timestamp: Annotated[
            str,
            Field(default="", description="Timestamp of statistics collection"),
        ]

    class CommandStatistics(FlextModels.Value):
        total_commands: Annotated[int, Field(default=0)]
        successful_commands: Annotated[int, Field(default=0)]
        failed_commands: Annotated[int, Field(default=0)]

    class CommandExecutionContextResult(FlextModels.Value):
        command_name: Annotated[str, Field(...)]
        exit_code: Annotated[int, Field(default=0)]
        output: Annotated[str, Field(default="")]
        context: Annotated[
            dict[str, t.Cli.JsonValue],
            Field(default_factory=dict),
        ]

    class WorkflowStepResult(FlextModels.Value):
        step_name: Annotated[str, Field(...)]
        success: Annotated[bool, Field(default=True)]
        message: Annotated[str, Field(default="")]
        duration: Annotated[float, Field(default=0.0)]

    class WorkflowProgress(FlextModels.Value):
        current_step: Annotated[int, Field(default=0)]
        total_steps: Annotated[int, Field(default=0)]
        current_step_name: Annotated[str, Field(default="")]
        percentage: Annotated[float, Field(default=0.0)]
