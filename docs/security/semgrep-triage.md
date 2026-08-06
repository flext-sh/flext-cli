# Triagem Semgrep — flext-sh/flext-cli

Gerado do dump da plataforma Semgrep (deployment `datacosmos`, 2026-08-06).

Bead de rastreio: `mro-p57t.4`

## Resumo

**6 findings** — high 0, medium 5, low 1
Confiança: high 4, medium 0, low 2

| regra | achados |
|---|---|
| `package_managers.dependabot.dependabot-missing-cooldown.dependabot-missing-cooldown` | 3 |
| `package_managers.uv.uv-missing-dependency-cooldown.uv-missing-dependency-cooldown` | 1 |
| `python.django.security.audit.unvalidated-password.unvalidated-password` | 1 |
| `python.lang.security.audit.dangerous-annotations-usage.dangerous-annotations-usage` | 1 |

## Findings

Coluna **Decisão** a preencher: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | conf | regra | arquivo | linha | Decisão |
|---|---|---|---|---|---|---|
| 1 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 4 | |
| 2 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 11 | |
| 3 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 18 | |
| 4 | medium | high | `uv-missing-dependency-cooldown` | `pyproject.toml` | 586 | |
| 5 | medium | low | `unvalidated-password` | `src/flext_cli/_utilities/_xlxx/xlsx_protection.py` | 65 | |
| 6 | low | low | `dangerous-annotations-usage` | `src/flext_cli/_utilities/model_commands.py` | 89 | |

## Como triar

1. Abrir `arquivo:linha` e seguir o fluxo até o sink.
2. Classificar: **corrigir** (entrada externa alcança o sink), **falso-positivo** (registrar via `nosemgrep` ou `.semgrepignore` com justificativa), **risco-aceito** (com prazo de revisão).
3. Priorizar findings high com confidence=high.

Dados brutos: `~/semgrep-violations/by-repo/flext-sh__flext-cli.json`

