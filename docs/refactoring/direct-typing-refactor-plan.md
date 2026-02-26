# Direct Typing Refactor Plan — flext-cli

**Goal**: Use direct typing in tests and modules; remove conversions, `isinstance`, `cast`, type narrowings, dicts in favor of centralized Pydantic v2 models; remove bypasses and silent errors.

**Constraint**: Do not recreate things that only exist in tests — use existing functionality (e.g. `m.Cli.`\*, `FlextCliSettings`) or remove.

**Scope**: flext-cli (tests + src). Align with CLAUDE.md §3, flext-strict-typing, flext-patterns.

______________________________________________________________________

## Phase 1 — Tests: \_helpers.py + conftest.py

- Use existing `m.Cli.`\* models (CliCommand, CliSession, TokenData, PasswordAuth) where test data matches; avoid introducing new test-only models that duplicate src.
- Return `Mapping` or model instances from helpers; type fixtures with existing models or TypedDict where it improves clarity.
- conftest: no new cast/isinstance for narrowing.
- **Done**: conftest factories use TypeGuard `_is_json_dict(unwrapped)` instead of `isinstance(unwrapped, dict)` for transform result handling.

## Phase 2 — Tests: helpers/\_impl.py + integration_test_complete_workflow.py

- helpers/\_impl: Prefer `FlextCliSettings` / `m.Cli.CliParamsConfig` when structure is known (docstrings added); `extract_config_values` return `Mapping`; keep `ValidationHelper.assert_field_type` (isinstance for assertions is acceptable).
- integration_test: **No test-only Pydantic models** (PipelineInput, ProcessedPipelineData, etc. removed per constraint). Use `_is_json_dict` / `_is_json_list` TypeGuards for dict/list narrowing; pipeline uses `dict[str, t.GeneralValueType]` and `_validate_pipeline_data`, `_transform_pipeline_data`, `_generate_pipeline_stats`, `_create_pipeline_report_from_data` with existing types only.
- **Done**: integration_test uses `_is_json_dict` / `_is_json_list`; helpers/\_impl exports these TypeGuards; conftest uses `_is_json_dict(unwrapped)` in factories.

## Phase 3 — flext-cli src: model boundaries and conversions

- Prefer Pydantic models at boundaries; remove unused `cast` import and `cast_if` helper (use TypeAdapter.validate_python result directly); no new cast(); reduce broad isinstance where a model or protocol can be used.
- **Done**: Removed `cast_if`; `to_dict_json` / `to_list_json` use TypeAdapter.validate_python with ValidationError fallback only (no cast_if). `ensure_dict` uses `isinstance(result, dict)`; `get_map_val` uses `isinstance` for JsonValue compatibility.
- output.py: `convert_field_value` (models.py) catch only `ValidationError`, not bare Exception.

## Phase 4 — Bypasses and silent errors

- Remove or replace `# type: ignore`; replace bare `except Exception` that swallow with explicit `ValidationError` or `r.fail`/re-raise; no silent `continue` for non-validation errors (e.g. `ScalarConfigRestore.from_config_items` catch only `ValidationError`).
- **Done**: output.py — removed unused `cast` import; added debug logging at every fallback that returns a default (ensure_str, ensure_list, to_dict_json, to_list_json, \_coerce_to_list, \_try_iterate_items, \_iterate_sequence).
- **Done**: test_protocols.py — removed all `cast()`; duck test uses `obj: object = duck` then `isinstance(obj, p.Cli.CliFormatter)` to avoid unreachable warning.
- **Done**: test_cli.py — test_model_command_validation: comment clarified; kept single `# type: ignore[arg-type]` for intentional invalid-type negative test.
- **Done**: test_models.py — decorator exception test catches only `(ValueError, ValidationError)`.
- **Done**: test_file_tools.py — restore-on-failure test catches only `OSError` (then re-raises).
- **Done**: test_typings.py — replaced match/case on types in `process_value`, `process_union`, `handle_edge_cases` with `isinstance` checks.
- **Done**: conftest.py — `flext_test_docker` startup cleanup: `except Exception` → `except OSError`.
- **Done**: settings.py — \_propagate_to_context / \_register_in_container: `except Exception` → `except (AttributeError, TypeError)`; auto_output_format isatty and \_try_terminal_width: `except Exception` → `except OSError`.
- **Done**: models.py — system_info/config_info TypeAdapter validate_python: `except Exception` → `except ValidationError`; exec-generated builder_config setattr: `except Exception` → `except (AttributeError, TypeError)`.
- **Done**: tests/helpers/\_impl.py — all test-double `except Exception` → `except (ValueError, TypeError, ValidationError)` (ProtocolHelpers, TypingHelpers, CliHelpers).
- **Done**: integration_test_complete_workflow.py — recovery loop: `except Exception` → `except (ValueError, TypeError, KeyError, ValidationError)`.
- **Done**: tests/base.py — DynamicTestHandler.handle and create_transform_handler transform: `except Exception` → `except (ValueError, TypeError, ValidationError)`.
- **Done**: commands.py — `execute_command` no longer silently swallows `TypeError` on handler signature mismatch; added `logging.getLogger(__name__).debug(...)` before falling back to no-args call.
- **Done**: output.py — create_formatter: `except Exception` → `except (ValueError, TypeError, ValidationError)`; \_prepare_table_data_safe: `except Exception` → `except (ValueError, TypeError, ValidationError)`; \_format_table_data: match Sequence/dict_items → isinstance(data, Sequence) and isinstance(dict_items, list); \_coerce_to_list, \_is_mapping_value, \_is_sequence_value, \_is_custom_iterable_value, \_iterate_mapping, \_iterate_sequence, \_iterate_model, \_normalize_iterable_item, \_convert_iterable_to_list: match/case → isinstance; \_format_csv_dict, \_replace_none_for_csv: match → isinstance.
- **Done**: utilities.py — CliValidation.to_str, v_empty, v_step: match → isinstance/if; TypeNormalizer.normalize_union_type: match arg → isinstance(arg, type) / isinstance(arg, types.UnionType); parse_kwargs: match value → isinstance(value, str).
- **Done**: core.py — \_build_execution_context: match context → isinstance(context, dict); execute_command: `except Exception` → `except (ValueError, TypeError, OSError)`; list_commands extract_command_names: `except Exception` → `except (ValueError, TypeError, OSError)`; profile creation: match profiles_value → isinstance(profiles_value, dict).
- **Done**: cmd.py — get_config_value: match config_data → isinstance(config_data, Mapping).
- **Done (batch)**: settings.py — \_propagate_to_context / \_register_in_container: `except Exception` → `except (AttributeError, TypeError)`; auto_output_format isatty: `except Exception` → `except OSError`; load_from_config_file: `except Exception` → `except (OSError, ValueError, ValidationError, yaml.YAMLError)`; update_from_cli_args: `except Exception` → `except (ValidationError, TypeError, AttributeError)`; validate_cli_overrides inner/outer: `except Exception` → `except (ValidationError, TypeError, AttributeError)` / `(ValidationError, TypeError)`; load_config: `except Exception` → `except (ValidationError, TypeError)`; save_config: `except Exception` → `except (ValidationError, TypeError, AttributeError)`.
- **Done**: file_tools.py — \_execute_file_operation: `except Exception` → `except (OSError, ValueError, TypeError, ValidationError)`.
- **Done**: cmd.py — show_config_paths, validate_config, get_config_info: `except Exception` → `except (OSError, ValueError, TypeError)` / `(OSError, ValueError, TypeError, KeyError)`.
- **Done**: core.py — register_command: `except Exception` → `except (ValueError, TypeError, AttributeError)`.

### Phase 4 audit (agents)

- **Tests**: No remaining cast/type: ignore/except pass; isinstance only in assertions or TypeGuards; no type(x) is T narrowing; dict contracts aligned with plan.
- **Src**: file_tools `_load_structured_file`, cli `_to_json_value`/prompt normalization, models `convert_field_value`, cmd `edit_config`, utilities `process`/`process_mapping` skip path — all have debug logging where they fall back or skip; no silent swallow.
- **Boundaries**: Optional — prefer existing `m.Cli.*` / `FlextCliSettings` at API boundaries (e.g. authenticate, save_config) where shape matches; no new models.
- **Done**: settings.save_config accepts `FlextCliSettings | Mapping`, uses `to_save` from model_dump() or config; api.get_auth_token uses TokenData.model_validate(data) as primary path, extract only on ValidationError; protocol save_config left as Mapping to avoid circular import (protocols → settings → utilities → models → protocols).
- **Done (polymorphic → Pydantic)**: cli.\_extract_typed_value delegates to m.Cli.TypedExtract(type_kind, value, default).result(); dict result normalized with \_to_json_value in cli. core.\_build_execution_context uses m.Cli.ExecutionContextInput(raw=context).to_mapping(list_processor=...). Removed polymorphic branches from cli and core in favor of centralized models.
- **Done (output ensure\_\* / get_map_val)**: models.Cli.EnsureTypeRequest(kind=str|bool, value, default).result() and MapGetValue(map, key, default).result(). output.ensure_str, ensure_bool delegate to EnsureTypeRequest; output.get_map_val delegates to MapGetValue. norm_json kept as isinstance/u.is_dict_like/u.is_list_like (no JsonNormalizeInput to avoid circular deps).

______________________________________________________________________

## Success criteria

- More Pydantic models at boundaries; fewer dict-based contracts; no new test-only duplicates of src models.
- No new cast(); no new type: ignore; no silent bypasses.
- isinstance only where necessary (e.g. test assertions); prefer model_validate for input validation. All changes pass make validate and tests.
