# FLEXT-CLI Examples

These examples show how to use flext-cli as a library through the public facade and the local examples runtime aliases.

## Core Pattern

- Import `c`, `m`, `p`, `r`, `s`, `t`, and `u` from `examples`
- Import the public facade as `cli` from `flext_cli`
- Derive reusable walkthroughs from local `s`
- Validate example payloads with `m.*.model_validate(...)`
- Keep fallible flows in `p.Result[...]` and `r[...]`
- Avoid direct service-class imports inside examples

## Start Here

1. `ex_01_getting_started.py`
   Minimal tour of `s`, `m.Examples`, the public `cli` facade, and the `r` result contract.
2. `ex_02_output_formatting.py`
   Table-string export through `cli.format_table()`.
3. `ex_04_file_operations.py`
   Typed file reads and writes.
4. `ex_11_complete_integration.py`
   A minimal end-to-end workflow using prompts plus JSON persistence.
5. `ex_12_pydantic_driven_cli.py`
   Railway-style Pydantic validation for a typed CLI payload.

## Quick Start

```python
from __future__ import annotations

from examples import c, m, p, r, s, t
from flext_cli import cli


class Demo(s):
    def execute(self) -> p.Result[t.JsonMapping]:
        settings = m.Examples.MyAppSettings.model_validate({
            "app_name": "my-cli-tool",
            "api_key": "example-api-key",
            "max_workers": 4,
            "timeout": 30,
        })
        cli.print(settings.app_name, style=c.Cli.MessageStyles.BOLD_GREEN)
        return r[t.JsonMapping].ok(settings.model_dump(mode="json"))
```

## Public Surfaces To Prefer

### Local Examples Aliases

```python
from examples import c, m, p, r, s, t, u
```

Use these for example-owned constants, models, utilities, and service setup.

### Public CLI Facade

```python
from examples import c
from flext_cli import cli

cli.print("hello", style=c.Cli.MessageStyles.GREEN)
result = cli.read_json_file("settings.json")
```

Keep interaction with flext-cli on the public facade unless the example is explicitly documenting an internal type.

### Service Base Via `s`

```python
from __future__ import annotations

from examples import p, r, s, t


class Demo(s):
    def execute(self) -> p.Result[t.JsonMapping]:
        return r[t.JsonMapping].ok({"output_format": self.settings.output_format})
```

This is the shortest path to typed settings access and a consistent result contract.

## Learning Path

### Beginner

1. `ex_01_getting_started.py`
2. `ex_02_output_formatting.py`

### Intermediate

1. `ex_04_file_operations.py`
2. `ex_05_authentication.py`
3. `ex_06_settings.py`

### Advanced

1. `ex_11_complete_integration.py`
2. `ex_12_pydantic_driven_cli.py`

## Best Practices

- Use the local `examples` aliases before reaching for direct imports.
- Prefer `cli` public methods for output, prompts, and file operations.
- Keep examples small and didactic; delete ceremony instead of wrapping it.
- Return `p.Result[...]` from fallible flows and build outcomes with `r[...]`.
- Let Pydantic 2 models own validation and serialization.
- Reuse `m.Examples.*` and `u.*` instead of duplicating payload shaping logic.

## Additional Resources

- `../src/flext_cli/`
- `../tests/`
- `../README.md`
- `../AGENTS.md`

Copyright (c) 2025 FLEXT Team. All rights reserved.
