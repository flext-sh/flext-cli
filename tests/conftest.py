"""Pytest configuration and fixtures for flext-cli tests."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


class MockFlextResult:
    """Mock FlextResult for testing."""

    def __init__(self, success: bool, data: Any = None, error: str | None = None) -> None:
        self.is_success = success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: Any) -> "MockFlextResult":
        """Create successful result."""
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str) -> "MockFlextResult":
        """Create failed result."""
        return cls(False, error=error)


class MockLogger:
    """Mock logger for testing."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, msg: str, *args: Any) -> None:
        """Log info message."""
        formatted = msg % args if args else msg
        self.messages.append(f"INFO: {formatted}")

    def exception(self, msg: str, *args: Any) -> None:
        """Log exception message."""
        formatted = msg % args if args else msg
        self.messages.append(f"ERROR: {formatted}")

    def clear(self) -> None:
        """Clear logged messages."""
        self.messages.clear()


@pytest.fixture
def mock_flext_core(monkeypatch):
    """Mock flext_core dependencies."""
    logger = MockLogger()

    mock_module = Mock()
    mock_module.FlextResult = MockFlextResult
    mock_module.get_logger = Mock(return_value=logger)

    monkeypatch.setattr("flext_cli.api.FlextResult", MockFlextResult)
    monkeypatch.setattr("flext_cli.api.get_logger", Mock(return_value=logger))
    monkeypatch.setattr("flext_cli.api.logger", logger)

    return {"logger": logger, "FlextResult": MockFlextResult}


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return [
        {"id": 1, "name": "Alice", "age": 30, "city": "New York"},
        {"id": 2, "name": "Bob", "age": 25, "city": "San Francisco"},
        {"id": 3, "name": "Charlie", "age": 35, "city": "Chicago"},
    ]


@pytest.fixture
def single_record():
    """Single record for testing."""
    return {"id": 1, "name": "Test User", "status": "active"}


@pytest.fixture
def mixed_data():
    """Mixed data types for testing."""
    return [
        {"type": "string", "value": "hello"},
        {"type": "number", "value": 42},
        {"type": "boolean", "value": True},
        {"type": "null", "value": None},
    ]


@pytest.fixture
def json_file_path(temp_dir):
    """Path for JSON test file."""
    return temp_dir / "test_output.json"


@pytest.fixture
def csv_file_path(temp_dir):
    """Path for CSV test file."""
    return temp_dir / "test_output.csv"


@pytest.fixture
def yaml_file_path(temp_dir):
    """Path for YAML test file."""
    return temp_dir / "test_output.yaml"
