"""CLI services domain module."""

from collections.abc import Callable
from typing import ClassVar, TypedDict, cast

from flext_core import (
    FlextDomainService,
    FlextProtocols,
    FlextResult,
    FlextUtilities,
    get_logger,
)

from flext_cli.context import FlextCliExecutionContext


class BasicSessionData(TypedDict, total=False):
    """Type definition for basic CLI session data."""

    id: str
    user_id: str | None
    created_at: object | None  # Could be datetime
    active: bool
    commands: list[object]  # List of command objects
    commands_count: int  # Derived field


# Use flext-core protocols instead of local definitions
CLIServiceProtocol = FlextProtocols.Domain.Service
CLICommandServiceProtocol = FlextProtocols.Application.Handler[str, object]
CLISessionServiceProtocol = FlextProtocols.Domain.Service


class BasicFlextCliCommandService(FlextDomainService[FlextResult[object]]):
    """Basic CLI command service implementation."""

    # Define fields for Pydantic model
    commands: ClassVar[dict[str, object]] = {}

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        # Use model_copy to set mutable fields since the model is frozen
        if not self.commands:
            object.__setattr__(self, "commands", {})
        # Expose module-level logger name for tests to patch
        object.__setattr__(self, "_logger", get_logger(__name__))

    def register_command(
        self,
        name: str,
        handler: Callable[[FlextCliExecutionContext], object]
        | Callable[[FlextCliExecutionContext], FlextResult[object]],
    ) -> None:
        """Register a command handler."""
        self.commands[name] = handler

    def execute_command(
        self,
        command_name: str,
        context: FlextCliExecutionContext,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute a CLI command."""
        if command_name not in self.commands:
            return FlextResult[object].fail(f"Command '{command_name}' not found")
        try:
            handler = self.commands[command_name]
            # Runtime callable guard
            if callable(handler):
                result: object = handler(context, **kwargs)
            else:
                return FlextResult[object].fail("Handler is not callable")
            return (
                result
                if isinstance(result, FlextResult)
                else FlextResult[object].ok(result)
            )
        except Exception as e:
            return FlextResult[object].fail(f"Command execution failed: {e}")

    def execute(self) -> FlextResult[FlextResult[object]]:
        """Execute domain service operation (FlextDomainService requirement)."""
        # Default service execution - returns success with empty command list
        command_list = list(self.commands.keys())
        result = FlextResult[object].ok(command_list)
        return FlextResult[FlextResult[object]].ok(result)

    def execute_command_operation(self, operation: object) -> FlextResult[object]:
        """Execute specific command operation (preserving original functionality)."""
        if isinstance(operation, str):
            # Operation is a command name - use execute_command
            context = FlextCliExecutionContext(user_id=None, session_id=None)
            return self.execute_command(operation, context)
        return FlextResult[object].fail(f"Unsupported operation type: {type(operation)}")

    def list_commands(self) -> list[str]:
        """List available commands."""
        return list(self.commands.keys())


class BasicFlextCliSessionService(FlextDomainService[FlextResult[object]]):
    """Basic CLI session service implementation."""

    # Define fields for Pydantic model
    sessions: ClassVar[dict[str, BasicSessionData]] = {}

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        # Use object.__setattr__ since the model is frozen
        if not self.sessions:
            object.__setattr__(self, "sessions", {})

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session."""
        session_id = FlextUtilities.generate_id()
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "created_at": None,  # Would use actual timestamp
            "active": True,
        }
        return FlextResult[str].ok(session_id)

    def get_session(self, session_id: str) -> FlextResult[BasicSessionData]:
        """Get session information."""
        if session_id not in self.sessions:
            return FlextResult[BasicSessionData].fail(
                f"Session '{session_id}' not found"
            )
        # Enrich with commands_count to match tests
        data = dict(self.sessions[session_id])
        commands = data.get("commands", [])
        if isinstance(commands, list):
            data["commands_count"] = len(commands)
        return FlextResult[BasicSessionData].ok(cast("BasicSessionData", data))

    def end_session(self, session_id: str) -> FlextResult[None]:
        """End a CLI session."""
        if session_id not in self.sessions:
            return FlextResult[None].fail(f"Session '{session_id}' not found")
        self.sessions[session_id]["active"] = False
        return FlextResult[None].ok(None)

    def execute(self) -> FlextResult[FlextResult[object]]:
        """Execute domain service operation (FlextDomainService requirement)."""
        # Default service execution - returns success with session count
        session_count = len(self.sessions)
        result = FlextResult[object].ok(session_count)
        return FlextResult[FlextResult[object]].ok(result)

    def execute_session_operation(self, operation: object) -> FlextResult[object]:
        """Execute specific session operation (preserving original functionality)."""
        if isinstance(operation, dict) and "action" in operation:
            action = operation.get("action")
            if action == "create_session":
                user_id = operation.get("user_id")
                return self.create_session(user_id)  # type: ignore[return-value]
            if action == "get_session":
                session_id = operation.get("session_id")
                if isinstance(session_id, str):
                    return self.get_session(session_id)  # type: ignore[return-value]
            elif action == "end_session":
                session_id = operation.get("session_id")
                if isinstance(session_id, str):
                    return self.end_session(session_id)  # type: ignore[return-value]
        return FlextResult[object].fail(f"Unsupported operation: {operation}")


# Create default service instances
default_command_service: BasicFlextCliCommandService = BasicFlextCliCommandService()
default_session_service: BasicFlextCliSessionService = BasicFlextCliSessionService()
