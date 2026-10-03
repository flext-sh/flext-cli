# CLI Architecture

<!-- TOC START -->

- [Princípios](#principios)
- [Mapa dos módulos](#mapa-dos-modulos)
- [Fluxo em tempo de execução](#fluxo-em-tempo-de-execucao)
- [Integração com flext-core](#integracao-com-flext-core)
- [Exemplo mínimo](#exemplo-minimo)
- [Referências rápidas](#referencias-rapidas)
- [Related Documentation](#related-documentation)

<!-- TOC END -->

Panorama da arquitetura implementada no **flext-cli** 0.12.0, conforme o código-fonte.

## Princípios

- **Facade única**: `FlextCli` (exposta como `cli`) compõe 16 serviços via MRO — `Cli`,
  `Cmd`, `Auth`, `FileTools`, `Formatters`, `Output`, `Prompts`, `Tables`, `Pipeline`,
  `Rules`, `Runtime`, `Docx`, `Pptx`, `Xlsx`, `YamlModel`, `CliParams` — e utilidades
  (`FlextCliUtilities`).
- **Fronteiras claras de framework**: Typer/Click vivem em `services/cli.py`;
  Rich/Tabulate são usados apenas em `services/formatters.py` e `services/tables.py`.
- **Contratos explícitos**: `m` (`models.py` + `_models/`) e `p` (`protocols.py`)
  definem os tipos de entrada/saída validados com Pydantic v2.
- **Retornos com `r[T]`**: erros e sucessos são encadeáveis em autenticação,
  orquestração e I/O.

## Mapa dos módulos

```text
src/flext_cli/
├── api.py                # Facade FlextCli (composição MRO) + singleton `cli`
├── base.py               # FlextCliServiceBase (base de serviços)
├── services/             # 16 serviços que compõem a facade via MRO
│   ├── auth.py           # FlextCliAuth — auth via keyring
│   ├── cli.py            # FlextCliCli — fronteira Typer/Click
│   ├── cli_params.py     # FlextCliCommonParams — parâmetros reutilizáveis
│   ├── cmd.py            # FlextCliCmd — configuração persistida e comandos
│   ├── docx.py           # FlextCliDocx — manipulação de documentos Word
│   ├── file_tools.py     # FlextCliFileTools — file I/O (text, JSON, YAML, CSV, zip)
│   ├── formatters.py     # FlextCliFormatters — saída Rich, print, render_table
│   ├── output.py         # FlextCliOutput — saída JSON/YAML/CSV sem expor Rich
│   ├── pipeline.py       # FlextCliPipeline — orquestração de workflows
│   ├── prompts.py        # FlextCliPrompts — interação com usuário (prompt/confirm/select)
│   ├── pptx.py           # FlextCliPptx — manipulação de apresentações PowerPoint
│   ├── rules.py          # FlextCliRules — validação de regras de negócio
│   ├── runtime.py        # FlextCliRuntime — status e monitoramento de runtime
│   ├── tables.py         # FlextCliTables — geração de tabelas ASCII via Tabulate
│   ├── xlsx.py           # FlextCliXlsx — manipulação de planilhas Excel
│   └── yaml_model.py     # FlextCliYamlModel — validação de YAML contra schemas
├── _utilities/           # Engenhos de domínio (toml/yaml/template/xlsx/…)
├── _constants/           # Família de declarações: constantes validadas
├── _models/              # Família de declarações: modelos Pydantic validados
├── config.py             # Configuração validada (ADR-005)
├── _config.py            # Singleton de configuração
├── _settings.py          # Singleton de settings validados
├── constants.py          # Facade de constantes (c.Cli.*) via MRO
├── typings.py            # Aliases de tipagem (t.Cli.*) via MRO
├── protocols.py          # Protocolos estruturais (p.Cli.*) via MRO
├── models.py             # FlextCliModels (m.Cli.*) via MRO
├── utilities.py          # FlextCliUtilities (u.Cli.*) via MRO
└── __init__.py           # Importa api.py, reforça isolamento de frameworks
```

## Fluxo em tempo de execução

1. **Bootstrap**: `cli` (singleton `FlextCli`) é carregado via `fetch_global()`; todos
   os 16 serviços estão disponíveis via MRO.
1. **Entrada do usuário**: `services/cli.py` (`FlextCliCli`) é a única fronteira com
   Typer/Click; despacha para comandos registrados.
1. **Execução**: `FlextCli.execute()` relata o status do runtime via
   `u.Cli.cmd_status()`. Comandos específicos (`FlextCliCmd`) operam sobre configuração
   persistida.
1. **Entrada/Saída**: `services/prompts.py` coleta entrada; `services/output.py`,
   `services/formatters.py` e `services/tables.py` geram saídas em
   Rich/ASCII/JSON/YAML/CSV sem expor o Rich diretamente.
1. **Configuração**: `_settings.py` gerencia configuração imutável; `_config.py` valida
   contra esquemas.

## Integração com flext-core

- `r`: envelope de sucesso/falha usado por todas as operações públicas.
- `s` (FlextService de flext-core): base para logging, contexto e ciclo de vida — todos
  os 16 serviços herdam de `s` via MRO.
- `c/t/p/m/u`: constantes, tipagens, protocolos, modelos e utilitários — acessados via
  MRO como `c.Cli.*`, `t.Cli.*`, `p.Cli.*`, `m.Cli.*`, `u.Cli.*`.

## Exemplo mínimo

```python
from flext_cli import cli

# Execução via facade
runtime_status = cli.execute()

# Renderização de tabela via MRO
cli.render_table(columns=["name", "age"], rows=[["Alice", "30"]])
cli.print("Done", style="green")
```

## Referências rápidas

- **API**: `docs/api-reference/README.md`
- **Guia de desenvolvimento**: `docs/development.md`

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
