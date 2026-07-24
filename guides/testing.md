<!-- Generated from docs/guides/testing.md for flext-cli. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-cli - FLEXT Testing Guide

> Project profile: `flext-cli`

<!-- TOC START -->
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Test Categories](#test-categories)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [End-to-End Tests](#end-to-end-tests)
- [Test Markers](#test-markers)
- [Running Tests](#running-tests)
  - [Basic Test Execution](#basic-test-execution)
  - [Coverage Analysis](#coverage-analysis)
  - [Parallel Test Execution](#parallel-test-execution)
- [Test Fixtures](#test-fixtures)
  - [Pytest Fixtures](#pytest-fixtures)
  - [Using Fixtures](#using-fixtures)
- [Mocking and Stubbing](#mocking-and-stubbing)
  - [Unit Test Mocking](#unit-test-mocking)
  - [Integration Test Stubbing](#integration-test-stubbing)
- [Performance Testing](#performance-testing)
  - [Load Testing](#load-testing)
  - [Memory Testing](#memory-testing)
- [Test Data Management](#test-data-management)
  - [Test Fixtures Directory](#test-fixtures-directory)
  - [Loading Test Data](#loading-test-data)
- [Continuous Integration](#continuous-integration)
  - [GitHub Actions Workflow](#github-actions-workflow)
- [Best Practices](#best-practices)
  - [1. Test Naming](#1-test-naming)
  - [2. Test Organization](#2-test-organization)
  - [3. Assertion Quality](#3-assertion-quality)
  - [4. Test Independence](#4-test-independence)
- [Troubleshooting](#troubleshooting)
  - [Common Test Issues](#common-test-issues)
- [Resources](#resources)
<!-- TOC END -->

This guide covers testing strategies, best practices, and procedures for FLEXT applications and libraries.

## Overview

FLEXT maintains comprehensive test coverage across all **33 projects** with the following standards:

- **85%+ coverage** for foundation libraries (flext-core)
- **75%+ coverage** for applications and domain libraries
- **100% test pass rate** across all projects
- **Zero Pyrefly errors** in strict mode (successor to MyPy)
- **Zero Ruff violations** in production code

## Test Structure

FLEXT uses a hierarchical test structure:

```text
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (component interaction)
├── e2e/           # End-to-end tests (full workflow)
├── fixtures/      # Test data and fixtures
└── conftest.py    # Pytest configuration
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

```python
from __future__ import annotations

import pytest
from flext_ldif import ldif


class TestLdifParsing:
    def test_parse_valid_ldif(self):
        """Test parsing valid LDIF content."""
        content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

        result = ldif.parse_string(content)

        assert result.success
        response = result.unwrap()
        assert len(response.entries) == 1
        assert response.entries[0].dn.value == "cn=test,dc=example,dc=com"

    def test_parse_invalid_ldif(self):
        """Test parsing invalid LDIF content."""
        content = "invalid ldif content"

        result = ldif.parse_string(content)

        assert result.success
        assert len(result.unwrap().entries) == 0
```

### Integration Tests

Test component interactions and workflows:

```python
from __future__ import annotations

import pytest
from flext_ldif import FlextLdifSettings, ldif


class TestLdifIntegration:
    def test_ldif_with_settings(self):
        """Test LDIF processing with a configured settings instance."""
        settings = FlextLdifSettings(
            ldif=FlextLdifSettings.LdifSettings(
                ldif_encoding="utf-8", ldif_strict_validation=True
            )
        )
        parser = ldif(settings=settings)

        result = parser.parse_string(
            "dn: cn=test,dc=example,dc=com\ncn: test\nobjectClass: inetOrgPerson"
        )

        assert result.success
        assert len(result.unwrap().entries) == 1
```

### End-to-End Tests

Test complete workflows and user scenarios:

```python
from __future__ import annotations

import pytest
from pathlib import Path
from flext_ldif import ldif


class TestLdifEndToEnd:
    def test_parse_ldif_file(self, tmp_path):
        """Test reading and parsing an LDIF file end-to-end."""
        input_dir = tmp_path / "ldif"
        input_dir.mkdir()

        sample_ldif = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

        input_file = input_dir / "test.ldif"
        input_file.write_text(sample_ldif, encoding="utf-8")

        result = ldif.parse_string(input_file.read_text(encoding="utf-8"))

        assert result.success
        entries = result.unwrap().entries
        assert len(entries) == 1
        assert (input_dir / "test.ldif").exists()
```

## Test Markers

FLEXT uses pytest markers to categorize tests:

```python
from __future__ import annotations

import pytest


@pytest.mark.unit
def test_unit_function():
    """Unit test - fast and isolated."""
    pass


@pytest.mark.integration
def test_integration_workflow():
    """Integration test - component interaction."""
    pass


@pytest.mark.e2e
def test_end_to_end_scenario():
    """End-to-end test - complete workflow."""
    pass


@pytest.mark.slow
def test_performance_benchmark():
    """Slow test - performance or load testing."""
    pass
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
make test

# Run specific test categories
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
pytest tests/e2e/         # End-to-end tests only

# Run with markers
pytest -m unit           # Unit tests
pytest -m integration    # Integration tests
pytest -m "not slow"     # Skip slow tests
```

### Coverage Analysis

Coverage thresholds and source directories are configured in each project's `pyproject.toml` under `[tool.coverage]`. Use `make test` which reads these automatically.

```bash
# Run with coverage (reads [tool.coverage] from pyproject.toml)
make test

# HTML coverage report
pytest --cov --cov-report=html
```

### Parallel Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Specific number of workers
pytest -n 4
```

## Test Fixtures

### Pytest Fixtures

```python
from __future__ import annotations

import pytest
from flext_ldif import FlextLdifSettings, ldif


class _LdifService:
    """Tiny helper used by the fixtures so the example stays executable."""

    def __init__(self, settings: FlextLdifSettings) -> None:
        self.settings = settings

    def parse(self, content: str):
        return ldif.parse_string(content)


@pytest.fixture
def ldif_config():
    """Provide LDIF configuration for tests."""
    return FlextLdifSettings(
        ldif=FlextLdifSettings.LdifSettings(
            ldif_encoding="utf-8", ldif_strict_validation=False
        )
    )


@pytest.fixture
def ldif_service(ldif_config):
    """Provide LDIF service instance."""
    return _LdifService(settings=ldif_config)


@pytest.fixture
def sample_ldif_content():
    """Provide sample LDIF content for tests."""
    return """dn: cn=test,dc=example,dc=com
cn: test
sn: user
objectClass: inetOrgPerson"""


@pytest.fixture
def temp_directories(tmp_path):
    """Provide temporary directories for file tests."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()
    output_dir.mkdir()

    return input_dir, output_dir
```

### Using Fixtures

```python
from __future__ import annotations

from flext_ldif import ldif


def test_ldif_parsing(ldif_service, sample_ldif_content):
    """Test LDIF parsing with fixtures."""
    result = ldif_service.parse(sample_ldif_content)
    assert result.success


def test_file_migration(ldif_service, temp_directories):
    """Test LDIF file round-trip with temporary directories."""
    input_dir, output_dir = temp_directories

    # Create test file
    test_file = input_dir / "test.ldif"
    test_file.write_text("dn: cn=test,dc=example,dc=com\ncn: test", encoding="utf-8")

    # Verify the file can be read and parsed
    result = ldif.parse_string(test_file.read_text(encoding="utf-8"))
    assert result.success
```

## Mocking and Stubbing

### Unit Test Mocking

```python
from __future__ import annotations

from unittest.mock import Mock, patch
from flext_cli import r


def process_with_service(service):
    """Function that delegates to an external service."""
    return service.process()


def test_with_mocked_dependency():
    """Test with mocked external dependency."""
    with patch("flext_ldif.external_service") as mock_service:
        # Configure mock
        mock_service.process.return_value = r.ok("processed")

        # Test function that uses mock
        result = process_with_service(mock_service)

        # Verify mock was called
        mock_service.process.assert_called_once()
        assert result.success
```

### Integration Test Stubbing

```python
from __future__ import annotations

from unittest.mock import Mock
from flext_cli import r


def integration_function(service):
    """Integration point that uses an external service."""
    return service.process()


def test_with_stubbed_service():
    """Test with stubbed service."""
    # Create stub service
    stub_service = Mock()
    stub_service.process.return_value = r.ok("stubbed")

    # Test integration
    result = integration_function(stub_service)
    assert result.success
```

## Performance Testing

### Load Testing

```python
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from flext_ldif import ldif


@pytest.mark.slow
def test_concurrent_processing():
    """Test concurrent processing performance."""
    content = "dn: test\ncn: test"

    def process_entry():
        return ldif.parse_string(content)

    # Run concurrent processing
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_entry) for _ in range(100)]
        results = [future.result() for future in futures]

    end_time = time.time()

    # Verify all succeeded
    assert all(result.success for result in results)

    # Verify performance (should complete in < 1 second)
    assert (end_time - start_time) < 1.0
```

### Memory Testing

```python
from __future__ import annotations

import os

import psutil
import pytest
from flext_ldif import ldif


@pytest.mark.slow
def test_memory_usage():
    """Test memory usage during large content processing."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Process large dataset
    large_content = "dn: test\ncn: test\n" * 10000

    result = ldif.parse_string(large_content)
    assert result.success

    # Check memory usage (should not exceed 100MB)
    current_memory = process.memory_info().rss
    memory_used = current_memory - initial_memory

    assert memory_used < 100 * 1024 * 1024  # 100MB
```

## Test Data Management

### Test Fixtures Directory

```text
tests/
├── fixtures/
│   ├── ldif/
│   │   ├── valid.ldif
│   │   ├── invalid.ldif
│   │   └── large.ldif
│   ├── settings/
│   │   ├── dev.yaml
│   │   └── prod.yaml
│   └── data/
│       ├── users.json
│       └── schema.json
```

### Loading Test Data

```python
from __future__ import annotations

import json
from pathlib import Path

from flext_cli import t
from flext_ldif import ldif


def load_test_fixture(fixture_path: Path) -> str:
    """Load test fixture from fixtures directory."""
    return fixture_path.read_text(encoding="utf-8")


def load_json_fixture(fixture_path: Path) -> t.JsonMapping:
    """Load JSON test fixture."""
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def process_ldif(content: str, _config: t.JsonMapping):
    """Process LDIF content using the canonical parser."""
    return ldif.parse_string(content)


def test_with_fixture(tmp_path: Path) -> None:
    """Test using loaded fixture data."""
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    ldif_dir = fixtures / "ldif"
    ldif_dir.mkdir()
    data_dir = fixtures / "data"
    data_dir.mkdir()

    valid_ldif = ldif_dir / "valid.ldif"
    valid_ldif.write_text(
        """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson""",
        encoding="utf-8",
    )

    dev_json = data_dir / "dev.json"
    dev_json.write_text('{"encoding": "utf-8"}', encoding="utf-8")

    ldif_content = load_test_fixture(valid_ldif)
    config_data = load_json_fixture(dev_json)

    # Use fixture data in test
    result = process_ldif(ldif_content, config_data)
    assert result.success
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          poetry run pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

### 1. Test Naming

```python
from __future__ import annotations


# ✅ GOOD - Descriptive test names
def test_parse_valid_ldif_returns_success():
    """Test that parsing valid LDIF returns success result."""
    pass


def test_parse_invalid_ldif_returns_failure():
    """Test that parsing invalid LDIF returns failure result."""
    pass


# ❌ BAD - Vague test names
def test_parse():
    pass


def test_ldif():
    pass
```

### 2. Test Organization

```python
from __future__ import annotations


class TestLdifParsing:
    """Test LDIF parsing functionality."""

    def test_parse_valid_single_entry(self):
        """Test parsing single valid LDIF entry."""
        pass

    def test_parse_valid_multiple_entries(self):
        """Test parsing multiple valid LDIF entries."""
        pass

    def test_parse_invalid_format(self):
        """Test parsing invalid LDIF format."""
        pass


class TestLdifMigration:
    """Test LDIF migration functionality."""

    def test_migrate_oid_to_oud(self):
        """Test OID to OUD migration."""
        pass
```

### 3. Assertion Quality

```python
from __future__ import annotations

from flext_ldif import ldif


# ✅ GOOD - Specific assertions
def test_parse_result_specific():
    content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""
    result = ldif.parse_string(content)

    assert result.success
    response = result.unwrap()
    assert len(response.entries) == 1
    assert response.entries[0].dn.value == "cn=test,dc=example,dc=com"
    assert "cn" in response.entries[0].attributes


# ❌ BAD - Vague assertions
def test_parse_result_vague():
    content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""
    result = ldif.parse_string(content)
    assert result  # Too vague
```

### 4. Test Independence

```python
from __future__ import annotations

from flext_ldif import ldif as ldif_module


# ✅ GOOD - Independent tests
def test_parse_valid_ldif():
    ldif_service = ldif_module  # Fresh handle
    result = ldif_service.parse_string("dn: test")
    assert result.success


def test_parse_invalid_ldif():
    ldif_service = ldif_module  # Fresh handle
    result = ldif_service.parse_string("invalid")
    assert result.success
    assert len(result.unwrap().entries) == 0


# ❌ BAD - Dependent tests
ldif_service = ldif_module  # Shared handle


def test_parse_valid_ldif():
    result = ldif_service.parse_string("dn: test")
    assert result.success


def test_parse_invalid_ldif():
    result = ldif_service.parse_string("invalid")
    assert result.success
```

## Troubleshooting

### Common Test Issues

1. **Import Errors**

   ```bash
   # Set PYTHONPATH
   export PYTHONPATH=src
   pytest
   ```

1. **Fixture Not Found**

   ```python
   from __future__ import annotations

   import pytest


   @pytest.fixture(scope="function")
   def my_fixture():
       return "value"
   ```

1. **Test Timeout**

   ```bash
   # Increase timeout
   pytest --timeout=300
   ```

1. **Coverage Issues**

   ```bash
   # Check coverage configuration
   pytest --cov=src --cov-report=term-missing
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- FLEXT Quality Standards
- Test Examples
- CI/CD Configuration
