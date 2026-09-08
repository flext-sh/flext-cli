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
- Config/settings canonical pattern: ADR-012.
- Codemod governance (ast-grep + make mod): ADR-014.

## Commands

```bash
make check PROJECT=flext-cli
make test  PROJECT=flext-cli
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->

<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN -->
<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:e1b7a9ae088643bf660b78ff1aea55d49076ec46518707976d77c78ed23db5db -->
# Generated session governance capsule

This projection is derived by `agentsctl sync`; edit canonical `AGENTS.md`, `rules/`, `skills/`, or `commands/`, never this output. The operator's newest request has precedence. Provider hooks are delivery mechanisms, not policy owners.

## Rule `architecture/engineering-core`

# Engineering core

For every implementation:

1. Research repository owners, dependencies, and canonical documentation.
2. Remove scope without a current requirement or consumer (YAGNI).
3. Elect one writable authority; every other copy is a generated projection
   (SSOT).
4. Apply SOLID only to a responsibility or dependency boundary under change.
5. Implement through the owner and simplify without weakening behavior.
6. Remove duplication and god components; recheck YAGNI, SSOT, SOLID.
7. Exercise runtime behavior, run every applicable native gate, and complete
   the approved landing cycle before changing phase.

At a cross-boundary failure, prove the producer contract and output. Fix its
owner when invalid or the receiver when it conforms. Never alter a correct
adjacent owner for an invalid consumer; symptom workarounds are defects.

Hardcodes, normalized failure, failover, retry, fallback, compatibility,
partial execution, keyring, and unevidenced success are defects. Typed owners
keep defaults. The first exception escapes its CLI with traceback and cause.

Git, runtime, build, and tests are baseline. Auxiliary tracking is a capability.
Auxiliary capabilities apply only when authorized and selected; installation
never selects. Do not load, probe, or gate dormant capabilities. Invalid
selected authorization, configuration, readiness, or result fails without
fallback. Require only non-derivable values.

An external token validation without its token is not executed and is recorded
as `NOT EXECUTED`, never green; it does not block offline gates, landing, or
post-merge proof. Direct invocation selects it: the token becomes required and
any failure escapes without skip, catch, fallback, or normalization.

Compose with generalized ownership,
strict execution,
runtime evidence,
storage isolation,
security closure.

## Rule `coordination/fix-forward-collaboration`

# Adopt the current state and collaborate by fix-forward

Treat every current authorized-repository change as owned input regardless of
provenance or age. Re-read shared files, attribute overlapping intent, preserve
compatible contributions, and adopt them through the integration lane. The
combined result is the target; provenance never exempts a defect from fix-forward.

Preserve unmanifested provider output, generated destinations, external files,
and ambiguous objects without promoting them to canonical input. Bulk adoption
or replacement requires divergent-object adjudication.

Never stash, reset, restore, revert, rebase, force-push, roll back code/history,
or replace shared files to remove work. Fix the canonical owner forward.
Transaction rollback may undo only its failing invocation's effects.

A severe conflict exists only when two current intentions require incompatible
behavior or when preserving both would violate a higher authority. Stop before
the conflicting effect, present both intentions and their evidence, and ask the
operator one precise question. Ordinary overlap, divergence, a red gate, or
integration work is not severe: reconcile, validate, and continue forward.
Unexpected state requires fresh preflight; it proves no actor or intention and
never authorizes an unchanged retry.

- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN -->
<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:5888ee9f8147f63364a4f7cd6906e9d837f58cb8a8546844760c526ecb1a303b -->
# Generated session governance capsule (2)

This projection is derived by `agentsctl sync`; edit canonical `AGENTS.md`, `rules/`, `skills/`, or `commands/`, never this output. The operator's newest request has precedence. Provider hooks are delivery mechanisms, not policy owners.

## Rule `architecture/engineering-core` (2)

# Engineering core (2)

For every implementation:

1. Research repository owners, dependencies, and canonical documentation.
2. Remove scope without a current requirement or consumer (YAGNI).
3. Elect one writable authority; every other copy is a generated projection
   (SSOT).
4. Apply SOLID only to a responsibility or dependency boundary under change.
5. Implement through the owner and simplify without weakening behavior.
6. Remove duplication and god components; recheck YAGNI, SSOT, SOLID.
7. Exercise runtime behavior, run every applicable native gate, and complete
   the approved landing cycle before changing phase.

At a cross-boundary failure, prove the producer contract and output. Fix its
owner when invalid or the receiver when it conforms. Never alter a correct
adjacent owner for an invalid consumer; symptom workarounds are defects.

Hardcodes, normalized failure, failover, retry, fallback, compatibility,
partial execution, keyring, and unevidenced success are defects. Typed owners
keep defaults. The first exception escapes its CLI with traceback and cause.

Git, runtime, build, and tests are baseline. Auxiliary tracking is a capability.
Auxiliary capabilities apply only when authorized and selected; installation
never selects. Do not load, probe, or gate dormant capabilities. Invalid
selected authorization, configuration, readiness, or result fails without
fallback. Require only non-derivable values.

An external token validation without its token is not executed and is recorded
as `NOT EXECUTED`, never green; it does not block offline gates, landing, or
post-merge proof. Direct invocation selects it: the token becomes required and
any failure escapes without skip, catch, fallback, or normalization.

Compose with `generalized ownership` (rule file),
`strict execution` (rule file),
`runtime evidence` (rule file),
`storage isolation` (rule file),
`security closure` (rule file).

## Rule `coordination/operator-precedence`

# Newest operator instruction wins; adjust artifacts to it

Authority order: operator request > declared orchestration contract > canonical
tracker > ADRs > skills > docs, and newest supersedes oldest. On conflict,
adjust the lower or older artifact to match; never override the operator to
satisfy stale guidance.

While orchestration and tracker runtimes are suspended, do not invoke them.
Create no substitute tracker or ledger, preserve implementation evidence only
in separately authorized Git/PR/CI, and leave phase closure open.

Exact operator authorization naming targets, disposition, recovery, and
validation survives interruption, divergence, and red gates; re-preflight and
continue. Ask only when the effect expands beyond it or two evidenced current
intentions conflict. State alone proves no intention, actor, or process.

## Rule `ethics/professional-integrity`

# Professional integrity is absolute

Never lie, fabricate evidence, hide a blocker, bypass a gate, or patch a symptom
only to make a check pass. Fix the generalized root cause with full context and
report exact command, working directory, exit code and decisive output.

## Rule `runtime/strict-execution`

# Strict execution is universal and non-optional

Every project and projected agent applies all of these policies together:

- `fail loud` (rule file);
- `no fallback` (rule file);
- `preflight before effects` (rule file);
- `required environment` (rule file);
- `atomic effects` (rule file);
- `causal subprocess propagation` (rule file);
- `no keyring` (rule file);
- `zero residue` (rule file).

The policies are cumulative. A project rule may make them narrower or reject
more inputs; it cannot relax, catch, normalize, skip, defer, or route around any
of them. Existing opposing behavior is a blocking violation to exterminate at
its owner, never grandfathered compatibility.

Resolve gate applicability before invocation. A dormant external-token gate is
not executed; selecting or invoking it applies every policy above.

## Capability indexes

Skills: caveman, context-canary, fix-forward-collaboration, governance-audit, operator-correction-learning, plan-focus-recovery, sprint-closure, strategic-compact, verification-loop
Commands: add-language-rules, database-migration, feature-development, ghi-list, pr-list, ralph-loop, security-triage, synthesize-governance
<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-END -->
