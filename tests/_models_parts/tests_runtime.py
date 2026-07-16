"""Split test model namespace."""

from __future__ import annotations

from typing import Annotated, ClassVar, Self

from flext_cli import m
from tests import t


class TestsFlextCliModelsRuntime:
    """Split test model namespace."""

    class ApiResponse(m.BaseModel):
        """API response for type scenario tests -- Pydantic v2."""

        model_config: ClassVar[p.ConfigDict] = m.ConfigDict(extra="forbid")
        status: Annotated[str, m.Field(description="Status")]
        data: Annotated[t.JsonMapping | None, m.Field(description="Payload")] = None
        message: Annotated[str, m.Field(description="Message")]
        error: Annotated[str | None, m.Field(description="Error")] = None

    class ModelCommandSource(m.BaseModel):
        """Partial override source for the model-command DSL (all optional)."""

        name: Annotated[str | None, m.Field(description="Command name")] = None
        value: Annotated[int | None, m.Field(description="Command value")] = None

    class ModelCommandSample(m.BaseModel):
        """Target model for derive_model/model_command tests."""

        name: Annotated[str, m.Field(description="Required command name")]
        value: Annotated[int, m.Field(description="Command value with default")] = 42

    class ModelCommandNullable(m.BaseModel):
        """Target model exercising nullable optional fields."""

        name: Annotated[str, m.Field(description="Required command name")]
        optional: Annotated[str | None, m.Field(description="Optional value")] = None

    class ModelCommandRequired(m.BaseModel):
        """Target model with only required fields."""

        key: Annotated[str, m.Field(description="Required key")]
        count: Annotated[int, m.Field(description="Required count")]

    class RuntimeCommandCase(m.BaseModel):
        """Runtime command parametrization case."""

        model_config: ClassVar[p.ConfigDict] = m.ConfigDict(frozen=True)

        case_id: Annotated[str, m.Field(description="Pytest case id")]
        command: Annotated[t.StrSequence, m.Field(description="Command argv")]
        timeout: Annotated[
            int | None, m.Field(description="Optional timeout in seconds")
        ] = None
        env: Annotated[
            t.StrMapping | None,
            m.Field(description="Optional child environment overrides"),
        ] = None
        use_tmp_path: Annotated[
            bool, m.Field(description="Use pytest tmp_path as cwd")
        ] = False
        input_data: Annotated[
            bytes | None, m.Field(description="Optional stdin payload")
        ] = None
        expect_success: Annotated[
            bool, m.Field(description="Whether command should succeed")
        ] = True
        stdout_has: Annotated[str, m.Field(description="Expected stdout substring")] = (
            ""
        )
        stderr_has: Annotated[str, m.Field(description="Expected stderr substring")] = (
            ""
        )
        exit_code: Annotated[
            int | None, m.Field(description="Expected exit code when applicable")
        ] = None
        expected: Annotated[str, m.Field(description="Expected captured output")] = ""
        error_has: Annotated[str, m.Field(description="Expected error substring")] = ""

        @staticmethod
        def id_for(case: TestsFlextCliModelsRuntime.RuntimeCommandCase) -> str:
            """Return pytest id for one case."""
            return case.case_id

        @classmethod
        def run_raw_cases(cls) -> tuple[Self, ...]:
            """Cases for raw command execution."""
            return (
                cls.model_validate({
                    "case_id": "echo",
                    "command": ("echo", "hello"),
                    "exit_code": 0,
                    "stdout_has": "hello",
                }),
                cls.model_validate({
                    "case_id": "stderr",
                    "command": ("sh", "-c", "echo error >&2"),
                    "exit_code": 0,
                    "stderr_has": "error",
                }),
                cls.model_validate({
                    "case_id": "nonzero-exit",
                    "command": ("sh", "-c", "exit 42"),
                    "exit_code": 42,
                }),
                cls.model_validate({
                    "case_id": "cwd",
                    "command": ("pwd",),
                    "exit_code": 0,
                    "use_tmp_path": True,
                }),
                cls.model_validate({
                    "case_id": "env",
                    "command": ("sh", "-c", "echo $TEST_VAR"),
                    "env": {"TEST_VAR": "raw_value"},
                    "exit_code": 0,
                    "stdout_has": "raw_value",
                }),
                cls.model_validate({
                    "case_id": "input",
                    "command": ("cat",),
                    "exit_code": 0,
                    "input_data": b'{"type":"RECORD"}',
                    "stdout_has": '{"type":"RECORD"}',
                }),
                cls.model_validate({
                    "case_id": "timeout",
                    "command": ("sleep", "10"),
                    "error_has": "timeout",
                    "expect_success": False,
                    "timeout": 1,
                }),
                cls.model_validate({
                    "case_id": "invalid-command",
                    "command": ("nonexistent_command_xyz",),
                    "error_has": "execution error",
                    "expect_success": False,
                }),
            )

        @classmethod
        def output_cases(cls) -> tuple[Self, ...]:
            """Cases shared by run and capture."""
            return (
                cls.model_validate({
                    "case_id": "success",
                    "command": ("echo", "hello"),
                    "expected": "hello",
                    "stdout_has": "hello",
                }),
                cls.model_validate({
                    "case_id": "cwd",
                    "command": ("pwd",),
                    "use_tmp_path": True,
                }),
                cls.model_validate({
                    "case_id": "env",
                    "command": ("sh", "-c", "echo $TEST_VAR"),
                    "env": {"TEST_VAR": "test_value"},
                    "expected": "test_value",
                    "stdout_has": "test_value",
                }),
                cls.model_validate({
                    "case_id": "nonzero-failure",
                    "command": ("sh", "-c", "exit 1"),
                    "error_has": "failed",
                    "expect_success": False,
                }),
                cls.model_validate({
                    "case_id": "timeout",
                    "command": ("sleep", "10"),
                    "error_has": "timeout",
                    "expect_success": False,
                    "timeout": 1,
                }),
            )


__all__: list[str] = ["TestsFlextCliModelsRuntime"]
