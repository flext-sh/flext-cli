"""Domain context for CLI operations.

Provides basic types and helpers to carry state across command execution.
"""

from __future__ import annotations

from typing import Dict, Optional
from dataclasses import dataclass, field
from flext_core import FlextResult


@dataclass
class CLIContext:
    """CLI execution context carrying state across commands."""
    
    config: Dict[str, object] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    debug: bool = False
    verbose: bool = False
    
    def get_config_value(self, key: str, default: object | None = None) -> object | None:
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
    
    command_name: Optional[str] = None
    command_args: Dict[str, object] = field(default_factory=dict)
    execution_id: Optional[str] = None
    start_time: Optional[float] = None
    
    def get_execution_info(self) -> Dict[str, object]:
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
    # Allow only known keys to keep typing strictness
    allowed_keys = {
        "config",
        "environment",
        "session_id",
        "user_id",
        "debug",
        "verbose",
    }
    filtered = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return CLIContext(**filtered)  # type: ignore[arg-type]


def create_execution_context(command_name: str, **kwargs: object) -> CLIExecutionContext:
    """Create an execution context for a specific command."""
    allowed_keys = {
        "config",
        "environment",
        "session_id",
        "user_id",
        "debug",
        "verbose",
        "command_args",
        "execution_id",
        "start_time",
    }
    filtered = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return CLIExecutionContext(command_name=command_name, **filtered)  # type: ignore[arg-type]
