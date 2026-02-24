# Direct Typing Refactor Plan — flext-cli

**Goal**: Use direct typing in tests and modules; remove conversions, `isinstance`, `cast`, type narrowings, dicts in favor of centralized Pydantic v2 models; remove bypasses and silent errors.

**Constraint**: Do not recreate things that only exist in tests — use existing functionality (e.g. `m.Cli.`*, `FlextCliSettings`) or remove.

**Scope**: flext-cli (tests + src). Align with CLAUDE.md §3, flext-strict-typing, flext-patterns.

---

## Phase 1 — Tests: _helpers.py + conftest.py

- Use existing `m.Cli.`* models (CliCommand, CliSession, TokenData, PasswordAuth) where test data matches; avoid introducing new test-only models that duplicate src.
- Return `Mapping` or model instances from helpers; type fixtures with existing models or TypedDict where it improves clarity.
- conftest: no new cast/isinstance for narrowing.

## Phase 2 — Tests: helpers/_impl.py + integration_test_complete_workflow.py

- helpers/_impl: Prefer `FlextCliSettings` / `m.Cli.CliParamsConfig` when structure is known (docstrings added); `extract_config_values` return `Mapping`; keep `ValidationHelper.assert_field_type` (isinstance for assertions is acceptable).
- integration_test: Use existing `FlextCliSettings`, `PipelineUserRecord`, `PipelineInput`, `ProcessedPipelineData`; keep type aliases/TypedDict only where they reference existing types; do not add duplicate test-only models.

## Phase 3 — flext-cli src: model boundaries and conversions

- Prefer Pydantic models at boundaries; remove unused `cast` import; no new cast(); reduce broad isinstance where a model or protocol can be used.

## Phase 4 — Bypasses and silent errors

- Remove or replace `# type: ignore`; replace bare `except Exception` that swallow with explicit `ValidationError` or `r.fail`/re-raise; no silent `continue` for non-validation errors (e.g. `ScalarConfigRestore.from_config_items` catch only `ValidationError`).

---

## Success criteria

- More Pydantic models at boundaries; fewer dict-based contracts; no new test-only duplicates of src models.
- No new cast(); no new type: ignore; no silent bypasses.
- isinstance only where necessary (e.g. test assertions); prefer model_validate for input validation. All changes pass make validate and tests.

