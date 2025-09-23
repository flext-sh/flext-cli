# FLEXT-CLI Code Style and Conventions

## File Structure

```
src/flext_cli/
├── __init__.py          # Public API exports
├── flext_cli_api.py     # Main CLI API class
├── flext_cli_main.py    # CLI command registration
├── flext_cli_formatters.py # Rich output abstraction
├── models.py            # Pydantic models
├── constants.py         # Project constants
├── typings.py          # Type definitions
└── [other modules...]
```

## Class Design (MANDATORY)

- **One class per module**: Each module contains exactly one primary class
- **Unified naming**: `Flext[Domain][Module]` pattern (e.g., `FlextCliApi`)
- **Nested helpers**: No standalone functions, use nested classes for helpers
- **Inheritance**: Extend `FlextService` or `FlextService` from flext-core

## Import Strategy (ZERO TOLERANCE)

```python
# ✅ CORRECT - Root level imports only
from flext_core import FlextResult, FlextLogger, FlextContainer
from flext_cli import FlextCliApi, FlextCliModels

# ❌ FORBIDDEN - Internal imports
from flext_core.result import FlextResult
from flext_cli.models import SomeModel
```

## Error Handling (MANDATORY)

```python
# ✅ CORRECT - FlextResult railway pattern
def process_data(data: dict) -> FlextResult[ProcessedData]:
    if not data:
        return FlextResult[ProcessedData].fail("Input cannot be empty")
    return FlextResult[ProcessedData].ok(processed_data)

# ❌ FORBIDDEN - try/except fallbacks
try:
    result = process()
except Exception:
    return default_value  # FORBIDDEN
```

## Type Annotations

- **Required**: All functions must have complete type annotations
- **Forbidden**: `Any` types, `# type: ignore` without codes
- **Preferred**: Use Pydantic models for complex types

## Documentation

- **English only**: All code, comments, docstrings
- **Format**: Google-style docstrings
- **Required**: All public methods must have docstrings
