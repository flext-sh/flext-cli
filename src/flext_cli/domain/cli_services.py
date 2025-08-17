"""CLI services domain module."""

import uuid
from collections.abc import Callable

from flext_core import FlextResult, get_logger

from flext_cli.domain.cli_context import CLIContext, CLIExecutionContext


class CLIServiceProtocol:
    """Protocol for CLI services."""

    def execute(self, context: CLIContext, **kwargs: object) -> FlextResult[object]:
        """Execute service operation."""


class CLICommandServiceProtocol:
    """Protocol for CLI command services."""

    def execute_command(
        self,
        command_name: str,
        context: CLIExecutionContext,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute a CLI command."""


class CLISessionServiceProtocol:
    """Protocol for CLI session services."""

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session."""

    def get_session(self, session_id: str) -> FlextResult[dict[str, object]]:
        """Get session information."""


class CLICommandService:
    """Basic CLI command service implementation."""

    def __init__(self) -> None:
        self.commands: dict[str, object] = {}
        # Expose module-level logger name for tests to patch
        self._logger = get_logger(__name__)

    def register_command(
        self,
        name: str,
        handler: Callable[[CLIExecutionContext], object]
        | Callable[[CLIExecutionContext], FlextResult[object]],
    ) -> None:
        """Register a command handler."""
        self.commands[name] = handler

    def execute_command(
        self,
        command_name: str,
        context: CLIExecutionContext,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute a CLI command."""
        if command_name not in self.commands:
            return FlextResult.fail(f"Command '{command_name}' not found")
        try:
            handler = self.commands[command_name]
            # Runtime callable guard
            if callable(handler):
                result = handler(context, **kwargs)
            else:
                return FlextResult.fail("Handler is not callable")
            return result if isinstance(result, FlextResult) else FlextResult.ok(result)
        except Exception as e:
            return FlextResult.fail(f"Command execution failed: {e}")

    def list_commands(self) -> list[str]:
        """List available commands."""
        return list(self.commands.keys())


class CLISessionService:
    """Basic CLI session service implementation."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, object]] = {}

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "created_at": None,  # Would use actual timestamp
            "active": True,
        }
        return FlextResult.ok(session_id)

    def get_session(self, session_id: str) -> FlextResult[dict[str, object]]:
        """Get session information."""
        if session_id not in self.sessions:
            return FlextResult.fail(f"Session '{session_id}' not found")
        # Enrich with commands_count to match tests
        data = dict(self.sessions[session_id])
        commands = data.get("commands", [])
        if isinstance(commands, list):
            data["commands_count"] = len(commands)
        return FlextResult.ok(data)

    def end_session(self, session_id: str) -> FlextResult[None]:
        """End a CLI session."""
        if session_id not in self.sessions:
            return FlextResult.fail(f"Session '{session_id}' not found")
        self.sessions[session_id]["active"] = False
        return FlextResult.ok(None)


# Create default service instances
default_command_service = CLICommandService()
default_session_service = CLISessionService()
