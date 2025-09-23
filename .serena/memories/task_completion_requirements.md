# Task Completion Requirements - FLEXT-CLI

## MANDATORY Quality Gates (ZERO TOLERANCE)
After EVERY code change, ALL of these must pass:

### 1. Ruff Linting (ZERO violations)
```bash
ruff check .
# Must show: "All checks passed!"
```

### 2. MyPy Type Checking (ZERO errors in src/)
```bash  
mypy .
# Must show no errors in src/ directory
```

### 3. PyRight Type Checking (ZERO errors)
```bash
pyright
# Must show no errors 
```

### 4. Pytest with Coverage (Target: near 100%)
```bash
pytest -q --maxfail=1 --cov=src --cov=examples --cov=tests --cov=. \
       --cov-report=term-missing:skip-covered \
       --cov-fail-under=100
```

## Code Quality Requirements

### API Compliance
- ALL tests must use actual API methods from `src/`
- NO compatibility layers, aliases, or wrappers
- Tests must expect string outputs from `format_data()`, not Rich objects
- Use `FlextCliModels.FlextCliConfig` not `FlextCliConfig`

### Architecture Compliance  
- One unified class per module
- All methods return `FlextResult[T]`
- No `try/except` fallbacks or error suppression
- No `# type: ignore` without specific error codes
- No `Any` types in production code

### Import Requirements
- Root-level imports only: `from flext_core import X`
- NO internal imports: `from flext_core.result import X` 
- Direct access patterns: `FlextCliModels.X` not `FlextCliX`

### Test Requirements
- Use actual API methods: `format_data`, `display_data`, `export_data`, `batch_export`
- Expect correct return types (strings for formatted output)
- NO mocking of core functionality
- Test real FlextResult patterns

## Completion Checklist
- [ ] All quality gates pass (ruff, mypy, pyright, pytest)
- [ ] Test coverage expanded toward 100%
- [ ] All tests use actual API methods only
- [ ] All compatibility layers removed
- [ ] All aliases/wrappers eliminated
- [ ] Architecture follows unified class pattern
- [ ] Imports follow root-level pattern only