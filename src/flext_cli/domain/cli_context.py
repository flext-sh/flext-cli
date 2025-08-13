"""Domain context for CLI operations.

Provides basic types and helpers to carry state across command execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CLIContext:
    """CLI execution context carrying state across commands."""

    config: dict[str, object] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    session_id: str | None = None
    user_id: str | None = None
    debug: bool = False
    verbose: bool = False

    def get_config_value(
        self, key: str, default: object | None = None,
    ) -> object | None:
        """Get configuration value with fallback."""
        return self.config.get(key, default)

    def set_config_value(self, key: str, value: object) -> None:
        """Set configuration value."""
        self.config[key] = value

    def has_config(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self.config


@dataclass
class CLIExecutionContext(CLIContext):
    """Extended context for command execution."""

    command_name: str | None = None
    command_args: dict[str, object] = field(default_factory=dict)
    execution_id: str | None = None
    start_time: float | None = None

    def get_execution_info(self) -> dict[str, object]:
        """Get execution information."""
        return {
            "command_name": self.command_name,
            "execution_id": self.execution_id,
            "start_time": self.start_time,
            "session_id": self.session_id,
        }


# Factory functions
def create_cli_context(**kwargs: object) -> CLIContext:
    """Create a CLI context with optional parameters."""
    # Extract and cast specific fields with correct types
    config = kwargs.get("config", {})
    environment = kwargs.get("environment", {})
    session_id = kwargs.get("session_id")
    user_id = kwargs.get("user_id")
    debug = kwargs.get("debug", False)
    verbose = kwargs.get("verbose", False)

    return CLIContext(
        config=config if isinstance(config, dict) else {},
        environment=environment if isinstance(environment, dict) else {},
        session_id=str(session_id) if session_id is not None else None,
        user_id=str(user_id) if user_id is not None else None,
        debug=bool(debug),
        verbose=bool(verbose),
    )


def create_execution_context(
    command_name: str, **kwargs: object,
) -> CLIExecutionContext:
    """Create an execution context for a specific command."""
    # Extract and cast specific fields with correct types
    config = kwargs.get("config", {})
    environment = kwargs.get("environment", {})
    session_id = kwargs.get("session_id")
    user_id = kwargs.get("user_id")
    debug = kwargs.get("debug", False)
    verbose = kwargs.get("verbose", False)
    command_args = kwargs.get("command_args", {})
    execution_id = kwargs.get("execution_id")
    start_time = kwargs.get("start_time")

    return CLIExecutionContext(
        command_name=command_name,
        config=config if isinstance(config, dict) else {},
        environment=environment if isinstance(environment, dict) else {},
        session_id=str(session_id) if session_id is not None else None,
        user_id=str(user_id) if user_id is not None else None,
        debug=bool(debug),
        verbose=bool(verbose),
        command_args=command_args if isinstance(command_args, dict) else {},
        execution_id=str(execution_id) if execution_id is not None else None,
        start_time=float(start_time)
        if start_time is not None and (isinstance(start_time, (int, float, str)))
        else None,
    )
