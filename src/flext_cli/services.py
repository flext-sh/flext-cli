"""CLI services domain module."""

import uuid
from collections.abc import Callable
from typing import Protocol, TypedDict

from flext_core import FlextResult, get_logger

from flext_cli.context import FlextCliContext, FlextCliExecutionContext


class SessionData(TypedDict, total=False):
    """Type definition for CLI session data."""

    id: str
    user_id: str | None
    created_at: object | None  # Could be datetime
    active: bool
    commands: list[object]  # List of command objects
    commands_count: int  # Derived field


class CLIServiceProtocol(Protocol):
    """Protocol for CLI services."""

    def execute(
        self, context: FlextCliContext, **kwargs: object
    ) -> FlextResult[object]:
        """Execute service operation."""
        ...


class CLICommandServiceProtocol(Protocol):
    """Protocol for CLI command services."""

    def execute_command(
        self,
        command_name: str,
        context: FlextCliExecutionContext,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute a CLI command."""
        ...


class CLISessionServiceProtocol(Protocol):
    """Protocol for CLI session services."""

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session."""
        ...

    def get_session(self, session_id: str) -> FlextResult[SessionData]:
        """Get session information."""
        ...


class FlextCliCommandService:
    """Basic CLI command service implementation."""

    def __init__(self) -> None:
        self.commands: dict[str, object] = {}
        # Expose module-level logger name for tests to patch
        self._logger = get_logger(__name__)

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

    def list_commands(self) -> list[str]:
        """List available commands."""
        return list(self.commands.keys())


class FlextCliSessionService:
    """Basic CLI session service implementation."""

    def __init__(self) -> None:
        self.sessions: dict[str, SessionData] = {}

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "created_at": None,  # Would use actual timestamp
            "active": True,
        }
        return FlextResult[str].ok(session_id)

    def get_session(self, session_id: str) -> FlextResult[SessionData]:
        """Get session information."""
        if session_id not in self.sessions:
            return FlextResult[SessionData].fail(f"Session '{session_id}' not found")
        # Enrich with commands_count to match tests
        data = dict(self.sessions[session_id])
        commands = data.get("commands", [])
        if isinstance(commands, list):
            data["commands_count"] = len(commands)
        return FlextResult[SessionData].ok(data)  # type: ignore[arg-type]  # Dict compatible with SessionData

    def end_session(self, session_id: str) -> FlextResult[None]:
        """End a CLI session."""
        if session_id not in self.sessions:
            return FlextResult[None].fail(f"Session '{session_id}' not found")
        self.sessions[session_id]["active"] = False
        return FlextResult[None].ok(None)


# Create default service instances
default_command_service: FlextCliCommandService = FlextCliCommandService()
default_session_service: FlextCliSessionService = FlextCliSessionService()
