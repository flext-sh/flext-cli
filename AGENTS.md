# AGENTS.md — Project Pointer

<!-- BEGIN AI-HUB MANAGED UNIVERSAL CORE -->
<!-- UNIVERSAL-GOVERNANCE v4 -->

## Universal Agent Engineering Core

`~/.agents` is the sole universal authority. AI Hub distributes and configures
it but never competes with it. Project law may be stricter; the newest explicit
operator instruction prevails and lower authority must be reconciled.

1. **Truth with evidence.** Claims require the exact command, working directory,
   exit status, decisive output, and bounded scope.
2. **Research before mutation.** Read current authority, intent, owner Bead,
   implementation owner, consumers, generated projections, concurrent WIP, and
   validation route. Never invent behavior or results.
3. **One active intent.** Preserve the goal, target, Bead, exclusions, phase,
   required gates, and stop condition through delegation and continuation.
4. **Root cause and one owner.** Change the canonical owner and complete the
   cutover. No bypass, fallback, shim, suppression, hardcode, fake, duplicate
   route, silent default, or old-and-new coexistence.
5. **Fix forward.** Preserve shared work; never destructively discard unknown
   changes. Re-read mutable files and classify relevant paths and hunks.
6. **Typed and generated boundaries.** Parse untrusted input once into canonical
   types. Change sources, not projections; regenerate and prove idempotence.
7. **Continuous green.** No completion while the project or environment is
   broken, partially migrated, dirty from task WIP, ahead of remote, missing
   real-use QA, or carrying stale generated output or docs. Run native global
   and changed-scope gates; Python requires Ruff, Pyrefly, Pyright, Mypy, and
   Pytest coverage plus applicable build and integrated validation.
8. **Beads is execution truth.** Beads owns work, plans, memory, dependencies,
   status, evidence, and closure. GitHub is its continuous external coordination,
   PR, review, and CI mirror after the orchestrator organizes Beads completely.
9. **Separated roles.** The orchestrator coordinates, owns semantic Beads state,
   validates, approves or rejects merges, rolls out, and closes; it does not
   implement. Workers directly implement one Bead in one branch and worktree but
   never merge or close. The standing documenter continuously audits, updates,
   validates, and removes stale canonical skills, ADRs, docs, Python docstrings,
   examples, and executable snippets under the same validated PR flow; the
   governance/CI helper also remains active.
10. **No stall by reporting.** Five-minute status reports include the agent table
    and epic evolution and never pause execution. Compaction, continuation, and
    status transfer context only.
11. **Historical material is evidence only.** Archives, generated or tool homes,
    backups, sessions, caches, and legacy trees are never live authority.
12. **Stop only for a real blocker.** Ask one precise question only when authority
   conflicts or an action would be destructive; otherwise continue to the
   observable stop condition.
13. **Short validated slices.** Deliver in small, independently validated
   units that merge to the integration branch quickly — one Bead, one
   reviewable PR, hours not days. Mega-lanes and long-lived WIP are defects;
   the orchestrator splits any unit that cannot merge green within a session.
14. **Living documentation.** Project knowledge is durable, never rebuilt
   per session. On entering a project, read its docs first and validate key
   claims quickly against live reality. Every change that produces new
   understanding or behavior updates the affected docs in the SAME change;
   stale docs are defects filed as beads, never worked around.
15. **Tests reflect canonical reality.** Tests are executable checks of current
    behavior, never a source of truth; a test that violates canonical policy is
    corrected to match the policy, not accommodated. Performance optimization is
    evidence-first: profile with cProfile to find the hot path before changing
    anything, then optimize with the project's typed OO/MRO/lazy-import patterns;
    accelerate test selection with impact analysis (e.g. pytest-testmon) and
    parallelism (pytest-xdist) rather than deleting or weakening coverage.
16. **Parametrized config, generators, and managed binaries.** config, settings,
    and templates are the sole source of configuration and business rules; the
    correct generator produces every derived surface (never hand-edit a
    projection). ai-hub owns the installation of binaries and the provisioning of
    environments; no manual, machine-specific path or binary hardcode. There is
    no product-, agent-, or daemon-specific hardcoded code anywhere — every such
    value is parametrized through config/settings/templates.

<!-- /UNIVERSAL-GOVERNANCE -->
<!-- END AI-HUB MANAGED UNIVERSAL CORE -->

Canonical source: [../AGENTS.md](../AGENTS.md).

- Read and follow [../AGENTS.md](../AGENTS.md) first.
- Load scoped rules only from [../.agents/skills/](../.agents/skills/).
- Never use fallback instruction paths.
- Keep this file pointer-only and concise.
# flext-cli — Domain Notes

> **General FLEXT law is the AI-HUB MANAGED UNIVERSAL CORE block above + the root [`../AGENTS.md`](../AGENTS.md) — consult both for general FLEXT patterns** (facade layering, config/settings SSOT, `make`-only workflow, testing law). This section adds ONLY `flext-cli`-specific knowledge.
>
> **Standalone / independent mode:** if this package is checked out on its own (imported as a dependency, vendored, or cloned solo) there is no parent workspace, so `../AGENTS.md` does not resolve. Then read the root law from the raw file on the SAME branch/release the project is on: <https://raw.githubusercontent.com/flext-sh/flext/0.12.0-dev/AGENTS.md> (pin the branch/tag to your working line, never `main`).

**Package:** `flext_cli` · ~17.3k src LOC · deps: `flext-core`

## Overview

Developer command-line interface AND the **SSOT for 11 CLI-adjacent domains** consumed workspace-wide via MRO. Wraps typer/click/rich/tabulate + serialization (toml/yaml/csv/json/xlsx) + templating + workflow/DAG.

## Structure

```
src/flext_cli/
├── api.py                 # FlextCli facade (.execute)
├── base.py                # FlextCliServiceBase
├── services/             # CLI runtime services
├── _utilities/            # the domain engines:
│   ├── toml.py yaml.py    #   FlextCliUtilitiesToml / …Yaml
│   ├── template.py        #   template_render / _to / _dir (typed model context)
│   ├── xlsx.py cmd.py     #   xlsx / command runner
│   └── pipeline.py prompts.py
├── vendor/                # vendored docx/ + pptx/ (separate impl surface)
├── constants.py typings.py protocols.py models.py utilities.py   # AUTO-GENERATED facets
└── _constants/ _typings/ _protocols/ _models/                     # private impl (nested Cli.* namespaces)
```

The 11 domains are **nested MRO namespaces under `Cli`** (`m.Cli.*`, `u.Cli.*`, …), NOT 11 top-level dirs.

## Code Map

| Symbol | Kind | Location | Role |
|--------|------|----------|------|
| `FlextCli` | class | `api.py` | public facade |
| `FlextCliModels` | class | `models.py` | nested `Cli` model facade |
| `FlextCliUtilitiesToml` | class | `_utilities/toml.py` | TOML domain ops |
| `FlextCliUtilitiesYaml` | class | `_utilities/yaml.py` | YAML domain ops |
| `template_render` | func | `_utilities/template.py` | jinja render (typed context, returns `r`) |
| `CliParamsConfig` | model | `_models/_base_parts/…part_06.py` | CLI param typing |

## Conventions (specific to this package)

- **Owns 11 CLI domains** — `Toml, Yaml, Csv, Json, Xlsx, Cli, Tui, Run, Dag, Templates, Workflow`. Every other package MUST consume them via MRO (`m.Cli.Toml*`, `u.Cli.Toml*`, `c.Cli.Toml*`, `t.Cli.Toml*`, `p.Cli.Toml*`) — never redeclare/fork locally. Need more? **Extend the owning domain here.**
- **Domain-first naming:** domain token first — `yaml_read_files` (not `files_read_yaml`), `TomlPhaseConfig`, `CSV_DEFAULT_DELIMITER`.
- `u.Cli.render_template`, `u.Cli.config_load` / `config_load_dir`, `u.Cli.yaml_validate_schema` are the engine behind ADR-005 config SSOT.

## Anti-Patterns / Gotchas

- **Do not create a parallel domain API** — add to the existing `Cli` namespace + utility MRO.
- `template_render` takes a **typed model context**; don't bypass it with untyped mappings — the helpers propagate its `Result`.
- `vendor/` (docx/pptx) is a separate vendored surface — don't refactor it as first-party code.

## Commands

```bash
make check PROJECT=flext-cli       # ruff/pyrefly/mypy/pyright
make test  PROJECT=flext-cli       # tests/{unit,integration}
```

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->
## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.
<!-- AIHUB-WORKSPACE-PROVIDERS-END -->
