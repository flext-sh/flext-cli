# AGENTS.md — flext-cli

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
**Package:** `flext_cli` · ~17.3k src LOC · deps: `flext-core`

## Overview

Developer CLI and SSOT for 11 CLI-adjacent domains consumed workspace-wide via MRO (`Toml, Yaml, Csv, Json, Xlsx, Cli, Tui, Run, Dag, Templates, Workflow`). Wraps typer/click/rich + serialization + templating + workflow/DAG.

## Structure

```text
src/flext_cli/
├── api.py base.py services/          # FlextCli facade + service base
├── _utilities/                       # domain engines (toml/yaml/template/xlsx/…)
├── vendor/                           # vendored docx/ + pptx/ (not first-party)
├── constants.py typings.py protocols.py models.py utilities.py
└── _constants/ _typings/ _protocols/ _models/
```

Domains are nested MRO namespaces under `Cli` (`m.Cli.*`, `u.Cli.*`, …), not 11 top-level dirs.

## Code Map

| Symbol | Kind | Location | Role |
| --- | --- | --- | --- |
| `FlextCli` | class | `api.py` | public facade (`.execute`) |
| `FlextCliModels` | class | `models.py` | nested `Cli` model facade |
| `template_render` | func | `_utilities/template.py` | jinja render (typed context → `r`) |

## Conventions (specific to this package)

- Consume CLI domains via MRO (`m.Cli.Toml*`, `u.Cli.Toml*`, …) — never fork locally; extend the owning domain here.
- Domain-first naming: `yaml_read_files`, `TomlPhaseConfig`, `CSV_DEFAULT_DELIMITER`.
- `u.Cli.render_template` / `config_load` / `yaml_validate_schema` back ADR-005 config SSOT.
- Do not create parallel domain APIs; `vendor/` stays a separate vendored surface.

## Commands

```bash
make check PROJECT=flext-cli
make test  PROJECT=flext-cli
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
