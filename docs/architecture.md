# CLI Architecture

<!-- TOC START -->

- [Principles](#principles)
- [Module map](#module-map)
- [Runtime flow](#runtime-flow)
- [Integration with flext-core](#integration-with-flext-core)
- [Minimal example](#minimal-example)
- [Quick references](#quick-references)
- [Related Documentation](#related-documentation)

<!-- TOC END -->

Overview of the architecture implemented in **flext-cli** 0.12.0, as found in the
source.

## Principles

- **One facade**: `FlextCli` (exposed as `cli`, in `api.py`) composes 13 services
  through MRO — `Auth`, `Cli`, `CommonParams`, `Docx`, `FileTools`, `Formatters`,
  `Output`, `Pipeline`, `Prompts`, `Pptx`, `Runtime`, `Tables`, `Xlsx` — plus the
  utilities facade (`FlextCliUtilities`).
- **Framework boundary**: Typer and Click are imported only by
  `_utilities/framework.py`. Consumers never import them. Several public surfaces still
  expose them (`p.Cli.Application.add_typer`, `p.Cli.ExternalCommand`,
  `t.Cli.CommandParameter`, `u.Cli.framework_*`); the single transport contract
  (ADR-019 Decision 5, epic `flext-itpd1.11.8`) makes them private behind
  `cli.run(source)` / `cli.entry(source)`, with the old surfaces kept as deprecated
  pass-throughs until their census reaches zero.
- **Explicit contracts**: `m` (`models.py` + `_models/`) and `p` (`protocols.py`) define
  the input and output types, validated with Pydantic v2.
- **Results with `r[T]`**: failures and successes chain through authentication,
  orchestration and I/O.

Guarded directory provisioning retains the original
`m.Cli.AtomicDirectoryChainPlan` and the ordered receipts returned by
`u.Cli.create_guarded_directory_chain`. Before dependent effects,
`u.Cli.verify_guarded_directory_chain` checks receipt count, paths, parent
identities and the complete original ancestry. An existing directory requires
the original warm plan and an empty receipt sequence. Replanning the current
path cannot replace the original authorization. AI Hub maintenance and durable
JavaScript preparation consume this same native owner; source implementation,
consumer rewiring and runtime qualification require separate evidence.

Atomic creation returns the state authenticated by the publication itself:
the retained parent descriptor, original content and the stat returned by native
publication validation. A later path read is readback, never the authority for
the created inode. The existing void and Boolean writer interfaces retain their
contracts and share the same publication implementation with state-returning
creation; no second publisher or callback cache participates.

Batch publication retains physical publication paths in the existing Result
metadata, including when a later operation fails. The request-owned typed receipt
is shared with the native writer, which records immediately after link, replace
or unlink succeeds, before durability or final proof can fail. It never derives
an effect from a later filesystem scan. A path receipt proves the physical effect,
not successful durability or final validation of that operation.
Consumers preserve the original failure and its metadata and carry those paths
through post-publication failures. Per-file atomic writes and a failure receipt
do not attest coherent batch visibility, crash recovery or compensation; those
remain the transaction owner's separately validated responsibilities.

## Module map

```text
src/flext_cli/
├── api.py                # FlextCli facade (MRO composition) + `cli` singleton
├── base.py               # FlextCliServiceBase (service base)
├── cli.py                # console entry point
├── services/             # 13 services composed into the facade via MRO
│   ├── auth.py           # FlextCliAuth
│   ├── cli.py            # FlextCliCli — command registration and execution
│   ├── cli_params.py     # FlextCliCommonParams — reusable parameters
│   ├── docx.py           # FlextCliDocx — Word documents
│   ├── file_tools.py     # FlextCliFileTools — file I/O (text, JSON, YAML, CSV, zip)
│   ├── formatters.py     # FlextCliFormatters — Rich output, print, render_table
│   ├── output.py         # FlextCliOutput — JSON/YAML/CSV output without exposing Rich
│   ├── pipeline.py       # FlextCliPipeline — workflow orchestration
│   ├── prompts.py        # FlextCliPrompts — user interaction (prompt/confirm/select)
│   ├── pptx.py           # FlextCliPptx — PowerPoint presentations
│   ├── runtime.py        # FlextCliRuntime — runtime status
│   ├── tables.py         # FlextCliTables — ASCII tables via Tabulate
│   └── xlsx.py           # FlextCliXlsx — Excel workbooks
├── _utilities/           # domain engines; framework.py is the only Typer/Click import
├── _constants/           # declaration family: validated constants
├── _models/              # declaration family: validated Pydantic models
├── _config.py            # validated configuration (ADR-005)
├── _settings.py          # validated settings singleton
├── constants.py          # constants facade (c.Cli.*) via MRO
├── typings.py            # typing aliases (t.Cli.*) via MRO
├── protocols.py          # structural protocols (p.Cli.*) via MRO
├── models.py             # FlextCliModels (m.Cli.*) via MRO
├── utilities.py          # FlextCliUtilities (u.Cli.*) via MRO
└── __init__.py           # generated lazy exports
```

## Runtime flow

1. **Bootstrap**: `cli` (the `FlextCli` singleton) is loaded through `fetch_global()`;
   all 13 services are available through MRO.
1. **User input**: `services/cli.py` (`FlextCliCli`) registers commands and dispatches
   them over the framework adapter in `_utilities/framework.py`.
1. **Execution**: `FlextCli.execute()` reports runtime status through
   `u.Cli.cmd_status()`.
1. **Input/output**: `services/prompts.py` collects input; `services/output.py`,
   `services/formatters.py` and `services/tables.py` render Rich/ASCII/JSON/YAML/CSV
   output without exposing Rich directly.
1. **Configuration**: `_settings.py` holds immutable settings; `_config.py` validates
   them against their schemas.

## Integration with flext-core

- `r`: success/failure envelope used by every public operation.
- `s` (flext-core `FlextService`): base for logging, context and lifecycle — all 13
  services inherit from `s` via MRO.
- `c/t/p/m/u`: constants, typings, protocols, models and utilities — reached through
  MRO as `c.Cli.*`, `t.Cli.*`, `p.Cli.*`, `m.Cli.*`, `u.Cli.*`.

## Minimal example

```python
from flext_cli import cli

# Execution through the facade
runtime_status = cli.execute()

# Table rendering through MRO
cli.render_table(columns=["name", "age"], rows=[["Alice", "30"]])
cli.print("Done", style="green")
```

## Quick references

- **API**: `docs/api-reference/README.md`
- **Development guide**: `docs/development.md`

## Related Documentation

**Within Project**:

- [Getting Started](getting-started.md) - Installation and basic usage
- [API Reference](api-reference/README.md) - Complete API documentation
- [Development Guide](development.md) - Contributing and extending

**Across Projects**:

- [flext-core Foundation](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-core/docs/architecture/overview.md) -
  Clean architecture and CQRS patterns
- [flext-core Service Patterns](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-core/docs/guides/service-patterns.md) -
  Service patterns and dependency injection

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
