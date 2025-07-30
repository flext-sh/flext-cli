# FLEXT-CLI Test Suite

Comprehensive test suite for the flext-cli library with 70+ tests covering all functionality.

## Test Structure

### Core Tests (`test_api_core.py`)

- **CliApi Class Tests**: Initialization, health checks, supported formats
- **Export Functionality**: JSON/CSV export, validation, error handling
- **Formatting Tests**: JSON, table, error handling
- **Command System**: Registration, execution, validation

### Convenience Functions (`test_convenience_functions.py`)

- **Export Function**: Boolean return values, error handling
- **Format Function**: String returns, error handling
- **Health Function**: Dict returns, consistency
- **Module Exports**: Validation of public API

### Export Formats (`test_export_formats.py`)

- **JSON Export**: Basic, complex data, Unicode, file size reporting
- **CSV Export**: Valid/invalid data, special characters, field detection
- **YAML Export**: PyYAML availability, error handling
- **Error Handling**: Permissions, disk space, serialization

### Integration Tests (`test_integration.py`)

- **FlextCore Patterns**: FlextResult usage, logger integration, type safety
- **Real-World Workflows**: Data pipelines, batch processing, error recovery
- **API Consistency**: Module-level vs direct API usage

### Performance Tests (`test_performance.py`)

- **Export Performance**: Small/medium/large datasets
- **Format Performance**: Table rendering, multiple operations
- **Scalability**: Command registry, concurrent operations
- **Benchmarks**: Timing consistency, regression detection

## Usage Examples (`../examples/basic_usage.py`)

Comprehensive real-world examples demonstrating:

- Basic export and formatting operations
- Advanced API usage with custom commands
- Error handling patterns
- Real-world scenarios (surveys, logs, API monitoring)

## Test Features

### Comprehensive Mocking

- Mock `flext_core` dependencies for isolated testing
- Mock logger for message validation
- Mock file system operations for error testing

### Edge Case Coverage

- Empty data, None values, Unicode content
- Invalid formats, unsupported operations
- File system errors, permission issues
- Command failures, validation errors

### Performance Validation

- Export operations complete in < 500ms for 1000 records
- Table formatting in < 200ms for 100 records
- Command operations in < 1ms average
- Benchmark consistency within 10ms variance

### Integration Validation

- FlextResult pattern usage throughout
- Proper error handling without exceptions
- Type safety with flext-core types
- Consistent API behavior

## Running Tests

### Individual Test Files

```bash
# Run specific test file
python -m pytest tests/test_api_core.py -v

# Run with coverage
python -m pytest tests/ --cov=src/flext_cli --cov-report=html
```

### Functional Testing

```bash
# Simple functional validation
python -c "
import sys; sys.path.insert(0, 'src')
import sys; sys.modules['flext_core'] = type('M', (), {'FlextResult': type('R', (), {'ok': lambda d: type('R', (), {'is_success': True, 'data': d})(), 'fail': lambda e: type('R', (), {'is_success': False, 'error': e})()}), 'get_logger': lambda: type('L', (), {'info': lambda *a: None, 'exception': lambda *a: None})()})()
sys.modules['flext_core.types'] = type('M', (), {})()
from flext_cli import CliApi, export, format_data, health
api = CliApi()
assert api.health().is_success
assert export([{'test': 'data'}], '/tmp/test.json')
print('✅ Core functionality working')
"
```

## Test Coverage

- **Core API**: 100% method coverage
- **Export Formats**: JSON, CSV, YAML with error cases
- **Error Handling**: All failure paths tested
- **Edge Cases**: Unicode, empty data, invalid inputs
- **Performance**: Timing and scalability validation
- **Integration**: flext-core pattern compliance

## Quality Assurance

### Validation Criteria

- All core functionality tested with positive/negative cases
- Error handling covers all failure modes
- Performance tests ensure scalability
- Integration tests verify flext-core compliance
- Examples demonstrate real-world usage

### Test Environment

- Python 3.13+ compatible
- Mocked external dependencies
- Temporary file handling
- Cross-platform compatibility

The test suite provides confidence that flext-cli works correctly across all use cases and maintains high performance standards.
