# Triagem Snyk Code (SAST) — flext-sh/flext-cli

Gerado do scan Snyk da org Datacosmos (dump 2026-08-06).

**4 achados** — critical 0, high 0, medium 0, low 4

| categoria | achados |
|---|---|
| Hardcoded Non-Cryptographic Secret | 3 |
| Use of Hardcoded Passwords | 1 |

## Achados

Coluna **Decisão**: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | categoria | arquivo | linha | CWE | Decisão |
|---|---|---|---|---|---|---|
| 1 | low | Use of Hardcoded Passwords | `tests/unit/_cases/test_examples_smoke/testsflextcliexamplessmoke_part_05.py` | 78 | - | |
| 2 | low | Hardcoded Non-Cryptographic Secret | `tests/unit/test_examples_models_utilities_cov.py` | 153 | - | |
| 3 | low | Hardcoded Non-Cryptographic Secret | `tests/unit/test_examples_models_utilities_cov.py` | 169 | - | |
| 4 | low | Hardcoded Non-Cryptographic Secret | `tests/unit/test_examples_models_utilities_cov.py` | 243 | - | |

## Como triar

1. Abrir `arquivo:linha` e seguir o fluxo de dados até o sink.
2. Classificar: **corrigir** (entrada externa alcança o sink sem sanitização), **falso-positivo** (credencial de fixture, path de constante — registrar em `.snyk` com justificativa), **risco-aceito** (com prazo de revisão).

Dados brutos: `~/snyk-violations/sast/flext-sh__flext-cli.sast.json`
