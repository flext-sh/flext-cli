"""Test refactored functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


# Mock flext_core components needed
class MockFlextResult:
    def __init__(self, success: bool, data=None, error=None) -> None:
        self.is_success = success
        self.data = data
        self.error = error

    @staticmethod
    def ok(data):
        return MockFlextResult(True, data=data)

    @staticmethod
    def fail(error):
        return MockFlextResult(False, error=error)


class MockEntity:
    def __init__(self) -> None:
        pass


class MockValueObject:
    def __init__(self) -> None:
        pass


class MockMixin:
    pass


def mock_make_factory(cls):
    return cls


def mock_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class MockDecorators:
    validate_input = staticmethod(mock_decorator)


sys.modules["flext_core"] = type("M", (), {
    "FlextResult": MockFlextResult,
    "FlextEntity": MockEntity,
    "FlextValueObject": MockValueObject,
    "FlextValidatableMixin": MockMixin,
    "FlextTimestampMixin": MockMixin,
    "FlextSerializableMixin": MockMixin,
    "FlextUtilities": type("U", (), {})(),
    "get_logger": lambda name: type("L", (), {"info": lambda *a: None})(),
    "make_factory": mock_make_factory,
    "FlextDecorators": MockDecorators,
    "TValue": type,
    "FlextConfig": dict,
})()


try:
    # Test consolidated imports
    from flext_cli import (
        create_api,
        create_command,
        export,
        format_data,
    )

    # Test factory pattern
    api = create_api()

    # Test basic functionality
    success = export([{"test": "data"}], "/tmp/test.json")

    formatted = format_data({"test": "value"}, "json")

    # Test flext-core entity usage
    cmd_success = create_command("test", "echo hello")

    # Test health
    from flext_cli import health
    health_data = health()


except (RuntimeError, ValueError, TypeError):
    import traceback
    traceback.print_exc()
