# Triagem SonarCloud — flext-sh/flext-cli

Gerado do dump da plataforma SonarCloud (2026-08-06).

Bead de rastreio: `mro-2wjm.1`

## Resumo

**86 issues** — BLOCKER 1, CRITICAL 24, MAJOR 35, MINOR 26
Tipos: VULNERABILITY 4, BUG 1, CODE_SMELL 81

| regra | issues |
|---|---|
| `python:S116` | 17 |
| `python:S3776` | 13 |
| `shelldre:S7688` | 12 |
| `python:S1192` | 9 |
| `python:S8997` | 7 |
| `python:S7504` | 5 |
| `python:S3358` | 3 |
| `python:S5754` | 2 |

## Issues

Coluna **Decisão**: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | tipo | regra | componente | linha | Decisão |
|---|---|---|---|---|---|---|
| 1 | BLOCKER | CODE_SMELL | `python:S3516` | `src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py` | 36 | |
| 2 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_cells.py` | 58 | |
| 3 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_rules.py` | 20 | |
| 4 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_rules.py` | 23 | |
| 5 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_rules.py` | 27 | |
| 6 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_style_primitives.py` | 16 | |
| 7 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_validation.py` | 77 | |
| 8 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_validation.py` | 79 | |
| 9 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/_xlsx/xlsx_validation.py` | 85 | |
| 10 | CRITICAL | CODE_SMELL | `python:S1192` | `src/flext_cli/_models/docx_styles.py` | 17 | |
| 11 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py` | 29 | |
| 12 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_02.py` | 22 | |
| 13 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_rules/_loaders.py` | 88 | |
| 14 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_runtime_process_execution.py` | 35 | |
| 15 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_runtime_process_monitor.py` | 21 | |
| 16 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py` | 18 | |
| 17 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_layout.py` | 30 | |
| 18 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_recalc.py` | 77 | |
| 19 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_recalc_evidence.py` | 30 | |
| 20 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_recalc_evidence.py` | 81 | |
| 21 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/_xlxx/xlsx_style_catalog.py` | 26 | |
| 22 | CRITICAL | CODE_SMELL | `python:S5754` | `src/flext_cli/_utilities/framework.py` | 218 | |
| 23 | CRITICAL | CODE_SMELL | `python:S5754` | `src/flext_cli/_utilities/framework.py` | 267 | |
| 24 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/pipeline.py` | 20 | |
| 25 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_cli/_utilities/template.py` | 90 | |
| 26 | MAJOR | CODE_SMELL | `shelldre:S7688` | `.github/scripts/install-git-hooks.sh` | 55 | |
| 27 | MAJOR | CODE_SMELL | `shelldre:S7688` | `.github/scripts/install-git-hooks.sh` | 104 | |
| 28 | MAJOR | CODE_SMELL | `shelldre:S7688` | `.github/scripts/install-git-hooks.sh` | 106 | |
| 29 | MAJOR | VULNERABILITY | `githubactions:S8264` | `.github/workflows/docs.yml` | 18 | |
| 30 | MAJOR | VULNERABILITY | `githubactions:S8233` | `.github/workflows/docs.yml` | 19 | |
| 31 | MAJOR | VULNERABILITY | `githubactions:S8233` | `.github/workflows/docs.yml` | 20 | |
| 32 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/PHASE_1_DELETIONS.sh` | 12 | |
| 33 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/PHASE_1_DELETIONS.sh` | 22 | |
| 34 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 17 | |
| 35 | MAJOR | CODE_SMELL | `shelldre:S7677` | `docs/refactoring/execute_phase_1.sh` | 18 | |
| 36 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 27 | |
| 37 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 37 | |
| 38 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 48 | |
| 39 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 62 | |
| 40 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 100 | |
| 41 | MAJOR | CODE_SMELL | `shelldre:S7688` | `docs/refactoring/execute_phase_1.sh` | 113 | |
| 42 | MAJOR | CODE_SMELL | `python:S8786` | `examples/constants.py` | 66 | |
| 43 | MAJOR | CODE_SMELL | `python:S108` | `examples/ex_06_settings.py` | 157 | |
| 44 | MAJOR | VULNERABILITY | `text:S8565` | `pyproject.toml` | - | |
| 45 | MAJOR | CODE_SMELL | `python:S3358` | `src/flext_cli/_models/_base/flextclimodelsbase_part_07.py` | 80 | |
| 46 | MAJOR | CODE_SMELL | `python:S3358` | `src/flext_cli/_utilities/_options_parts/flextcliutilitiesoptions_part_02.py` | 28 | |
| 47 | MAJOR | CODE_SMELL | `python:S3358` | `src/flext_cli/_utilities/_runtime_process_monitor.py` | 160 | |
| 48 | MAJOR | CODE_SMELL | `python:S8495` | `src/flext_cli/_utilities/_runtime_process_resources.py` | 83 | |
| 49 | MAJOR | BUG | `python:S3699` | `src/flext_cli/_utilities/output.py` | 111 | |
| 50 | MAJOR | CODE_SMELL | `python:S3985` | `src/flext_cli/services/_cli_parts/flextclicli_part_01.py` | 19 | |
| 51 | MAJOR | CODE_SMELL | `python:S112` | `src/flext_cli/services/_prompts_support.py` | 75 | |
| 52 | MAJOR | CODE_SMELL | `python:S5778` | `tests/test_xlsx_render.py` | 88 | |
| 53 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_config_engine.py` | 81 | |
| 54 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_expand_utilities.py` | 28 | |
| 55 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_expand_utilities.py` | 38 | |
| 56 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_expand_utilities.py` | 64 | |
| 57 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_utilities.py` | 28 | |
| 58 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_utilities.py` | 49 | |
| 59 | MAJOR | CODE_SMELL | `python:S8997` | `tests/unit/test_env_utilities.py` | 50 | |
| 60 | MAJOR | CODE_SMELL | `python:S5778` | `tests/unit/test_model_commands_cov.py` | 90 | |
| 61 | MINOR | CODE_SMELL | `python:S7504` | `conftest.py` | 21 | |
| 62 | MINOR | CODE_SMELL | `shelldre:S1192` | `docs/refactoring/execute_phase_1.sh` | 125 | |
| 63 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_constants/exceptions.py` | 52 | |
| 64 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_constants/exceptions.py` | 53 | |
| 65 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_constants/exceptions.py` | 54 | |
| 66 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_constants/exceptions.py` | 55 | |
| 67 | MINOR | CODE_SMELL | `python:S7508` | `src/flext_cli/_constants/settings.py` | 15 | |
| 68 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 25 | |
| 69 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 26 | |
| 70 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 27 | |
| 71 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 33 | |
| 72 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 34 | |
| 73 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 35 | |
| 74 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 36 | |
| 75 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 37 | |
| 76 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 38 | |
| 77 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 39 | |
| 78 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 40 | |
| 79 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 41 | |
| 80 | MINOR | CODE_SMELL | `python:S116` | `src/flext_cli/_utilities/_pptx/_types.py` | 42 | |
| 81 | MINOR | CODE_SMELL | `python:S5713` | `src/flext_cli/_utilities/_runtime_process_stream.py` | 81 | |
| 82 | MINOR | CODE_SMELL | `python:S7504` | `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py` | 51 | |
| 83 | MINOR | CODE_SMELL | `python:S7504` | `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py` | 100 | |
| 84 | MINOR | CODE_SMELL | `python:S7504` | `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py` | 111 | |
| 85 | MINOR | CODE_SMELL | `python:S7504` | `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_05.py` | 52 | |
| 86 | MINOR | CODE_SMELL | `python:S6353` | `src/flext_cli/_utilities/env.py` | 10 | |

## Como triar

1. **BLOCKER e CRITICAL primeiro**, e todo VULNERABILITY independente de severidade.
2. Classificar: **corrigir**, **falso-positivo** (marcar na plataforma SonarCloud com justificativa), **risco-aceito** (com prazo).
3. CODE_SMELL em volume alto sugere padrão — corrigir a causa raiz, não issue a issue.

Dados brutos: `~/sonarqube-violations/by-repo/flext-sh__flext-cli.json`

