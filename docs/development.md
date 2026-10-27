# Development Guide - flext-cli

<!-- TOC START -->

- [📌 Quick Navigation](#quick-navigation)
- [v0.12.0-dev Development Guidelines (Current)](#v0120-dev-development-guidelines-current)
  - [Overview](#overview)
- [When to Use Each Pattern](#when-to-use-each-pattern)
  - [Use s When](#use-s-when)
  - [Use Simple Class When](#use-simple-class-when)
  - [Use Value Object (Pydantic) When](#use-value-object-pydantic-when)
- [Architecture Decision Flowchart](#architecture-decision-flowchart)
- [Code Organization Guidelines](#code-organization-guidelines)
  - [Module Structure](#module-structure)
  - [Direct Access Pattern](#direct-access-pattern)
- [Testing Guidelines (v0.12.0-dev)](#testing-guidelines-v0120-dev)
  - [Test Organization](#test-organization)
  - [Testing Simple Classes](#testing-simple-classes)
- [Contributing to v0.12.0-dev](#contributing-to-v0120-dev)
  - [Implementation Checklist](#implementation-checklist)
  - [Pull Request Guidelines](#pull-request-guidelines)
- [v0.9.0 Development Guidelines (Historical Reference)](#v090-development-guidelines-historical-reference)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
- [Development Workflow](#development-workflow)
  - [Essential Commands](#essential-commands)
  - [Code Quality Standards](#code-quality-standards)
- [Architecture Guidelines](#architecture-guidelines)
  - [FLEXT Ecosystem Integration](#flext-ecosystem-integration)
  - [Code Organization](#code-organization)
- [Testing Guidelines](#testing-guidelines)
  - [Test Structure](#test-structure)
  - [Testing Patterns](#testing-patterns)
  - [Test Commands](#test-commands)
- [Contributing Guidelines](#contributing-guidelines)
  - [Code Style](#code-style)
  - [Pull Request Process](#pull-request-process)
  - [Commit Messages](#commit-messages)
- [Extension Development](#extension-development)
  - [Adding New Commands](#adding-new-commands)
  - [Custom Formatters](#custom-formatters)
- [Debug and Troubleshooting](#debug-and-troubleshooting)
  - [Atomic directory publication on macOS](#atomic-directory-publication-on-macos)
  - [Common Issues](#common-issues)
  - [Debug Commands](#debug-commands)

<!-- TOC END -->

**Contributing guidelines and development workflow for flext-cli.**

Native directory-query verification may share fresh physical directory and
ancestry observations within one caller-owned verification boundary. The caller
must own and discard both stores at that boundary; neither store authenticates
an original receipt. Every supplied receipt still undergoes its original native
identity, negative-query, membership and publication-effect comparisons. Failed
native observations are propagated, not stored as substitute receipts.

**Last Updated**: 2026-09-17 | **Version**: 0.12.0

---

## 📌 Quick Navigation

- [v0.12.0-dev Development Guidelines (Current)](#v0120-dev-development-guidelines-current)
  ← **Start Here**
- [v0.9.0 Development Guidelines (Historical Reference)](#v090-development-guidelines-historical-reference)

---

## v0.12.0-dev Development Guidelines (Current)

**Status**: 🔄 Active Development | **Release**: 0.12.0 | **Breaking Changes**: Yes

### Overview

FLEXT-CLI v0.12.0-dev follows a simplified architecture with clear guidelines for when
to use services vs simple classes. This guide helps you make the right architectural
decisions.

`m.Cli.CommandMetadata` owns the immutable command `name` and `help_text`
declarations. `m.Cli.ResultCommandRoute` inherits those fields without nesting a
metadata payload: its constructor and serialized fields remain flat, with the
same field constraints, model configuration and success-output defaults.
The `cli.result_route` factory accepts five keyword-only parameters: `metadata`,
`model_cls`, `handler`, `success_formatter` and optional `success_type`. Its
`metadata` input consumes only the read-only `name` and `help_text` properties of
`p.Cli.CommandMetadata`; callers can supply `m.Cli.CommandMetadata`.
`p.Cli.ResultCommandRoute` inherits that same metadata protocol. The output route
remains flat, and `success_type` retains its keyword and success-style default.

This authored API boundary groups only command identity and help to satisfy the
argument-count contract without suppressions, signature mirrors or a second
execution path. The coordinated source cutover updates the service-operation
factory and all three direct behavioral-test callers. These four call sites are
the direct factory consumers found by the workspace-wide `result_route` census;
registration APIs are unchanged. Surgical source edits keep this unique boundary
and its callers together without running generation or semantic publication in
the separately serialized infrastructure lane. The former `name`/`help_text`
factory keywords are removed, not retained as a compatibility wrapper; external
clients using that old signature must migrate and are not claimed compatible.

---

## When to Use Each Pattern

### Use s When

**Requirements**:

- ✅ Class manages **mutable state** (commands, sessions, configuration)
- ✅ Class requires **dependency injection**
- ✅ Class needs **lifecycle management** (startup, shutdown, cleanup)
- ✅ Class has **complex initialization** with external dependencies

**Example - FlextCliPrompts (Stateful Service)**:

```text
from flext_cli import m, p, s

class FlextCliPromptsSupport(s[p.Cli.RuntimeStatus]):
    """Prompt runtime state plus injected input ports."""

    state: m.Cli.PromptRuntimeState                # MANAGED STATE
    input_reader: t.Cli.PromptTextReader           # INJECTED PORT

    def configure(self, state: m.Cli.PromptRuntimeState) -> Self:
        """Replace prompt runtime state - modifies internal state."""
        self.state = state
        return self
```

**When NOT to use**:

- ❌ Operations are stateless (just transformations)
- ❌ No initialization needed
- ❌ Methods could all be static
- ❌ Just grouping related functions

### Use Simple Class When

**Requirements**:

- ✅ Class is **stateless** (no internal state to manage)
- ✅ Methods could be **static** (no `self` needed)
- ✅ **No dependency injection** required
- ✅ Just utility functions grouped together
- ✅ Pure **I/O operations** (read/write files)

**Example - FlextCliFileTools (Simple Utility Class)**:

```text
from flext_core import r, p
import json

class FlextCliFileTools:
    """Stateless file operations."""

    @staticmethod
    def read_json_file(path: str) -> p.Result[dict]:
        """Read JSON file - no state needed."""
        try:
            with open(path) as f:
                return r[dict].ok(json.load(f))
        except Exception as e:
            return r[dict].fail(str(e))

    @staticmethod
    def write_json_file(path: str, data: dict) -> p.Result[bool]:
        """Write JSON file - no state needed."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(str(e))
```

**Benefits**:

- No initialization overhead
- Clear that it's stateless
- Can use static methods
- Easy to test

### Use Value Object (Pydantic) When

**Requirements**:

- ✅ Class is **immutable data**
- ✅ Compared by **value**, not identity
- ✅ **No behavior** (no business logic)
- ✅ Just data **validation and structure**
- ✅ Configuration or context data

DOCX and XLSX RGB models inherit their shared value declaration from
`FlextCliModelsColor.RgbColor` in `_models/color.py`. Domain subclasses retain their
public identities and discriminated unions; neither document domain depends on the
other. The shared frozen declaration owns the `kind`, `value`, `tint` field order,
RGB/ARGB constraint and tint bounds without changing defaults or serialization.

---

## Architecture Decision Flowchart

```
Does the class manage mutable state?
├─ YES → Use s
│        Examples: FlextCliPrompts, cli
│
└─ NO → Does it have behavior (business logic)?
    ├─ YES → Is it stateless utility functions?
    │   ├─ YES → Use Simple Class
    │   │        Examples: FlextCliFileTools, FlextCliFormatters
    │   └─ NO → Re-evaluate: might need s
    │
    └─ NO → Is it just data with validation?
        └─ YES → Use Value Object (Pydantic)
                 Examples: FlextCliModels.*
```

---

## Code Organization Guidelines

### Module Structure

Authored private-family ancestry imports the canonical declaration module, not a
parent package's generated reexport. Private-child export retirement and these
consumer rewrites form one cutover: generation must not recover old umbrella
bindings or synthesize aliases to conceal an unresolved source dependency.

Follow the v0.12.0-dev module organization:

```
src/flext_cli/
├── api.py                # FlextCli facade (MRO composition) + singleton `cli`
├── base.py               # FlextCliServiceBase
├── services/             # 13 services composed via MRO
│   ├── cli.py            # FlextCliCli — Typer/Click boundary
│   ├── auth.py           # FlextCliAuth — keyring auth
│   ├── file_tools.py     # FlextCliFileTools — file I/O
│   ├── formatters.py     # FlextCliFormatters — Rich/text rendering
│   ├── output.py         # FlextCliOutput — JSON/YAML/CSV output
│   ├── prompts.py        # FlextCliPrompts — user interaction
│   ├── tables.py         # FlextCliTables — ASCII table generation
│   ├── pipeline.py       # FlextCliPipeline — workflow orchestration
│   ├── runtime.py        # FlextCliRuntime — runtime status
│   ├── docx.py           # FlextCliDocx — Word document operations
│   ├── pptx.py           # FlextCliPptx — PowerPoint operations
│   ├── xlsx.py           # FlextCliXlsx — Excel operations
│   └── cli_params.py     # FlextCliCommonParams — shared CLI params
├── _utilities/           # Domain engines (toml/yaml/template/…)
├── _constants/           # Validated constants (c.Cli.*)
├── _models/              # Pydantic models (m.Cli.*)
├── _config.py            # Config singleton
├── _settings.py          # Settings singleton
├── config.py             # Config validation (ADR-005)
├── constants.py          # Constant facade (c.Cli.*)
├── typings.py            # Typing aliases (t.Cli.*)
├── protocols.py          # Structural protocols (p.Cli.*)
├── models.py             # Model facade (m.Cli.*)
├── utilities.py          # Utility facade (u.Cli.*)
└── __init__.py           # Exports api.py, enforces isolation
```

### Direct Access Pattern

**Always use direct access** (no wrapper methods):

```text
# ✅ CORRECT - Public facade (methods are MRO-injected via FlextCli)
cli.print("Hello", style="green")
cli.read_json_file("settings.json")
cli.confirm("Continue?")

# ❌ WRONG - Internal utility/service chains are not public APIs.
# cli.file_tools.read_json_file("settings.json")  # NO sub-facade
# cli.prompts.confirm("Continue?")           # NO sub-facade
```

Process launch data is declared once by
`_models/process.py::FlextCliModelsProcess.ProcessOptions`. Construct it through
`m.Cli.ProcessOptions` and pass it as the `options=` argument to `u.Cli.run_raw`,
`run_bytes`, `run`, `capture`, `run_to_file`, or `process_start`. Runtime annotations
consume the generated structural contract `p.Cli.ProcessOptions`. There is no
`u.Cli.ProcessOptions` DTO alias or flat `input_data=`/`env=` launch contract.
Omitting options constructs the same canonical model used by explicit callers;
tests compare that model's defaults with omitted-option behavior rather than
freezing configured values. Namespace/facade and model-protocol generation must
publish the model and protocol together before public-runtime validation.

Managed launches use the same environment resolver as Run. With
`inherit_environment=False`, the child receives only declared overrides, minus
`remove_env_keys`; the host environment is not copied. The process family composes
the runtime through MRO, and each managed handle receives its communication
capability through `p.Cli.ProcessCommunicator`, not a concrete engine class.

The lifecycle witnesses `m.Cli.RuntimeProcessRequest`, `m.Cli.RuntimeProcessState`,
`m.Cli.RuntimeOutputTarget`, and `m.Cli.RuntimeSpawnOptions` live beside
`ProcessOptions` in the `_models/process.py` family, and the owned-stream protocols
`p.Cli.RuntimeClosableStream` and `p.Cli.RuntimeBinaryStream` live in
`_protocols/process.py`. They carry resolved launch state, OS resources and cleanup
ownership; they are not a second public launch-options model. Subprocess execution, signals,
deadlines, environment validation and descriptor forwarding retain their existing
behavior.

The single native spawn owner is `_utilities/native_runtime.py`. This original
package asset imports only the Python standard library and can be loaded directly
by a cold worker before the CLI/Core SDK is admitted. Its
`spawn_streamed_process` accepts resolved command, working directory, environment,
explicit binary stdin handle and a required structural `RuntimeSpawnOptions`
protocol. The protocol declares the six existing spawn fields as read-only
properties, with no policy defaults or second launch-options model; the ordinary
`m.Cli.RuntimeSpawnOptions` satisfies it directly.

The primitive returns the actual binary `subprocess.Popen` handle, never a JSON
result or a wait/reap wrapper. An explicit stdin handle wins over pipe, devnull or
inherit mode. Capture/combined streams, unbuffered binary I/O, environment,
platform-default session ownership, creation flags and forwarded descriptors keep
their existing semantics. Cold consumers own wait/reap at their boundary. The
typed `_utilities/runtime.py` delegates to this same primitive and retains the
ordinary timeout translation, redaction and streaming lifecycle. Native timeout
identity and platform creation-flag calculation also belong to the stdlib owner;
there is no alternate executor or compatibility path. Its Ruff permission is the
existing audited native-owner declaration moved from `runtime.py`, not an added
exemption. Consumers must authenticate and load the original package asset, not
copy its body into another execution engine.

`run_to_file` accepts `stderr_file=` when the consumer needs separate native
streams. `output_file` then receives stdout and `stderr_file` receives stderr;
both are drained, flushed and synchronized by the same contained lifecycle,
without retaining their contents in memory. Live mirroring uses the corresponding
stdout/stderr descriptors. Without `stderr_file`, the existing combined-stream
operation remains available. Destinations identifying the same physical file are
rejected before either is opened or the child starts. A completed nonzero child
exit or timeout remains visible in `ProcessOutcome`; transport completion alone
does not establish `process_succeeded`.
The durable sink follows Python's raw-I/O contract: `write` accepts a positional
buffer and returns `int | None`. Partial writes are retried; `None` or non-positive
progress produces the existing durable-write failure rather than losing output.

`atomic_iter_binary_file` consumes a required regular file through the existing
physical-parent and descriptor guards. It yields byte blocks without buffering
the whole file, rejects symlinks, and checks the descriptor version and pathname
after complete consumption. A changed input cannot complete authentication.
Consumers must exhaust the iterator before accepting a streamed report.

The DOCX renderer consumes only the writable capabilities it needs:
`p.Cli.DocxFontVariants` covers superscript, subscript, all-caps and small-caps;
`p.Cli.DocxParagraphPagination` covers the four pagination flags. Each property
accepts and returns `bool | None`, matching the
[python-docx text API](https://python-docx.readthedocs.io/en/latest/api/text.html).
The authored owner is `_protocols/docx.py::FlextCliProtocolsDocx`; canonical namespace
conformance publishes both contracts through `p.Cli`. They require no runtime type
checks or adapter objects. Other document, font and paragraph operations retain
their existing external types; rendering behavior and inherited formatting remain
unchanged. Public regressions compare rendered bytes read by python-docx with the
same library's real property setters, using the typed input specs as expectations
rather than freezing configured defaults or assuming boolean XML normalization.

---

## Testing Guidelines (v0.12.0-dev)

### Test Organization

Tests are now organized by feature area:

```
tests/
├── unit/
│   ├── core/              # Core functionality tests
│   │   ├── test_api.py
│   │   ├── test_service_base.py
│   │   └── test_singleton.py
│   ├── io/                # I/O operations tests
│   │   ├── test_json_operations.py
│   │   ├── test_yaml_operations.py
│   │   └── test_csv_operations.py
│   ├── formatting/        # Output formatting tests
│   │   ├── test_rich_formatters.py
│   │   ├── test_tables.py
│   │   └── test_output.py
│   └── cli/               # CLI framework tests
│       ├── test_click_wrapper.py
│       ├── test_commands.py
│       └── test_execution.py
│
├── integration/           # Integration tests
└── fixtures/              # Test utilities (moved from src/)
```

### Testing Simple Classes

```text
import pytest
from flext_cli import FlextCliFileTools


def test_read_json_file():
    """Test static method on simple class."""
    # Simple classes use static methods
    result = FlextCliFileTools.read_json_file("test.json")

    tm.ok(result.success)
    data = result.unwrap()
    assert isinstance(data, dict)


# No initialization needed - static methods
```

---

## Contributing to v0.12.0-dev

### Implementation Checklist

Before implementing new features, review:

Key phases:

1. Documentation (complete)
1. Delete duplicates (validator.py, auth.py, testing.py)
1. Convert services to simple classes
1. Fix context (service → value object)
1. Remove API wrappers
1. Remove unused infrastructure
1. Reorganize tests
1. Quality gates

### Pull Request Guidelines

1. **Follow the Architecture**:

    - Services only for state
    - Simple classes for utilities
    - Value objects for data

1. **Use Direct Access**:

    - No wrapper methods
    - Clear ownership
   1. **Quality Gates (MANDATORY)**:

      ```bash
      make check # Must pass 100%
      ```

1. **Test Organization**:

    - Tests in appropriate directories
    - No file > 30K lines
    - Feature-based organization

---

## v0.9.0 Development Guidelines (Historical Reference)

**Note**: The following documentation describes v0.9.0 patterns. This is kept for
historical reference during the migration period.

## Development Setup

### Prerequisites

- Python 3.13+
- Make for build automation
- Git for version control

### Initial Setup

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete development setup
make setup
```

---

## Development Workflow

### Essential Commands

```bash
make setup # Complete development environment setup
make check # All quality checks (lint + type + test)
make test  # Run test suite
make fmt   # Auto-format code
make clean # Clean build artifacts
```

### Code Quality Standards

- **Type Safety**: Complete Python 3.13+ type annotations
- **Linting**: Zero Ruff violations
- **Testing**: Comprehensive test coverage
- **Documentation**: All public APIs documented

---

## Architecture Guidelines

### FLEXT Ecosystem Integration

Follow these patterns when extending flext-cli:

1. **CLI Patterns**: Use flext-cli abstractions
1. **Integration**: Follow flext-core patterns (see flext-core documentation)
1. **Type Safety**: Complete type annotations required
1. **Testing**: Comprehensive test coverage

### Code Organization

```text
# ✅ Correct - Use flext-cli patterns
from flext_cli import cli


class ProjectCliService:
    """Project CLI service following FLEXT patterns."""

    def __init__(self):
        self._cli_api = cli()

    def process_data(self, data: dict):
        """Process CLI data."""
        if not data:
            return "Data cannot be empty"

        # Business logic
        return {"processed": True, "data": data}


# ❌ Avoid - Direct framework imports
# import click  # Use flext-cli abstractions instead
# import rich   # Use FlextCliOutput instead
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests
├── conftest.py       # Shared fixtures
└── test_*.py         # Test modules
```

### Testing Patterns

```text
import pytest
from flext_cli import cli


def test_cli_api_operation():
    """Test CLI API operations."""
    api = cli()

    result = api.process_command("test")

    tm.not_none(result)
    assert "test" in str(result)


def test_error_handling():
    """Test proper error handling."""
    api = cli()

    result = api.process_command("")  # Invalid input

    # Test appropriate error handling
    assert result or "error" in str(result)
```

### Test Commands

```bash
# Run all tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_api.py -v
```

---

## Contributing Guidelines

### Code Style

- Follow PEP 8 with 79-character line limit
- Use descriptive variable names
- Add docstrings for all public functions/classes
- Include type hints for all function signatures

### Pull Request Process

1. Create feature branch from main
1. Implement changes with tests
1. Run `make check` to ensure quality
1. Submit pull request with description
1. Address review feedback
1. Merge after approval

### Commit Messages

Follow conventional commit format:

```
feat: add new CLI command for data export
fix: resolve authentication timeout issue
docs: update API documentation
test: add integration tests for settings module
```

---

## Extension Development

### Adding New Commands

1. Create command handler:

```text
from flext_core  import config, settings, c, e, d, h, p, r, s, t, u, x
from flext_cli import cli

class DataCommands(s):
    """Data management commands."""

    def handle_export(self, **kwargs) -> p.Result[bool]:
        """Handle data export command."""
        # Implementation
        return r[bool].ok(value=True)
```

1. Register with CLI:

```text
from flext_cli import FlextCliCommands

cli = FlextCliCommands()
cli.register_command_group(
    name="data",
    commands={"export": data_handler.handle_export},
    description="Data management",
)
```

1. Add tests:

```text
def test_data_export_command():
    """Test data export functionality."""
    handler = DataCommands()
    result = handler.handle_export(format="json")
    tm.ok(result.success)
```

### Custom Formatters

```text
from flext_cli import FlextCliOutput


class ProjectFormatters(FlextCliOutput):
    """Project-specific output formatters."""

    def format_project_data(self, data: dict) -> p.Result[str]:
        """Format project-specific data."""
        # Custom formatting logic
        return r[str].ok("formatted_output")
```

---

## Debug and Troubleshooting

### Atomic directory publication on macOS

Physical-tree authentication reads the complete two-word filesystem identifier from
`fstatfs` on the open descriptor. It deliberately does not use `os.fstatvfs().f_fsid`,
which CPython truncates to the first word on macOS. The binding follows Darwin's
64-bit-inode `statfs` layout: `fstatfs` on arm64 and `fstatfs$INODE64` on x86_64.
Unsupported architectures and unavailable identities fail closed. These identities are
local mount measurements, not persistent identifiers across reboots.

Directory publication uses descriptor-relative `renameatx_np` with `RENAME_EXCL`. An
existing destination is rejected; syscall failures propagate without a check-then-rename
fallback. Linux retains `/proc/self/fdinfo` mount IDs and `renameat2(RENAME_NOREPLACE)`;
the Windows rename branch is unchanged.

External contracts:
[Darwin statfs ABI](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/mount.h),
[Darwin symbol selection](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/cdefs.h),
[exclusive rename](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/man/man2/rename.2),
and
[CPython statvfs conversion](https://github.com/python/cpython/blob/main/Modules/posixmodule.c).

### Common Issues

1. **Import Errors**: Ensure proper module structure
1. **Type Errors**: Run `make check` for detailed analysis
1. **Test Failures**: Use `pytest -v` for verbose output
1. **Dependency Issues**: Try `make setup`

### Debug Commands

```bash
# Run tests
make test PROJECT=flext-cli

# Type checking and linting
make check PROJECT=flext-cli

# Dependency versions (pinned in flext-infra/config/tooling.yaml)
# Run from workspace root: make deps
```

---

For architectural details, see [architecture.md](architecture.md). For API usage, see
[API Reference](api-reference/README.md).
