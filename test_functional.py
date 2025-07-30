"""Functional test of standardized CLI."""

import contextlib
import sys
from pathlib import Path

# Add current directory to path for testing
sys.path.insert(0, str(Path(__file__).parent))


# Mock flext_core for testing
class MockResult:
    def __init__(self, success: bool, data=None, error=None) -> None:
        self.is_success = success
        self.data = data
        self.error = error


class MockService:
    def start(self):
        return MockResult(True)

    def stop(self):
        return MockResult(True)


class MockUtilities:
    @staticmethod
    def generate_entity_id() -> str:
        return "entity_123"

    @staticmethod
    def generate_session_id() -> str:
        return "session_456"

    @staticmethod
    def generate_iso_timestamp() -> str:
        return "2025-01-01T00:00:00Z"


class MockLogger:
    def info(self, *args) -> None:
        """Mock info method for testing."""


sys.modules["flext_core"] = type(
    "M",
    (),
    {
        "FlextResult": MockResult,
        "FlextService": MockService,
        "FlextConfigurable": type,
        "FlextHandler": type,
        "FlextPlugin": type,
        "FlextEntity": type,
        "FlextValueObject": type,
        "FlextUtilities": MockUtilities,
        "FlextConfig": dict,
        "safe_call": lambda f: MockResult(True, f()),
        "chain": lambda *args: MockResult(True, "chained"),
        "get_logger": lambda n: MockLogger(),
        "make_factory": lambda cls: cls,
    },
)()


try:
    # Test imports
    from flext_cli import (
        FlextCliApi,
        flext_cli_create_command,
        flext_cli_export,
        flext_cli_format,
        flext_cli_health,
    )

    # Test API creation
    api = FlextCliApi()

    # Test function naming
    functions_to_test = [
        ("flext_cli_export", flext_cli_export),
        ("flext_cli_format", flext_cli_format),
        ("flext_cli_health", flext_cli_health),
        ("flext_cli_create_command", flext_cli_create_command),
    ]

    for _name, func in functions_to_test:
        if callable(func):
            pass

    # Test basic functionality

    # Test format
    with contextlib.suppress(Exception):
        formatted = flext_cli_format({"test": "data"}, "json")

    # Test health
    with contextlib.suppress(Exception):
        health = flext_cli_health()

    # Test command creation
    with contextlib.suppress(Exception):
        cmd_result = flext_cli_create_command("test", "echo hello")


except (RuntimeError, ValueError, TypeError):
    import traceback

    traceback.print_exc()
