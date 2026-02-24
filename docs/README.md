# flext-cli Documentation

<!-- TOC START -->

- [Visão geral](#viso-geral)
- [Navegação rápida](#navegao-rpida)
- [O que observar na 0.10.0](#o-que-observar-na-0100)
- [Status](#status)
- [Links úteis](#links-teis)

<!-- TOC END -->

Documentação alinhada ao **flext-cli** 0.10.0 conforme o código-fonte atual.

## Visão geral

- **Facade única (`FlextCli`)**: expõe serviços (`core`, `cmd`, `output`, `prompts`, `tables`) e utilidades (`formatters`, `file_tools`, `utilities`) como atributos públicos.
- **Wrappers de compatibilidade**: `print`, `create_table`, `print_table` e `create_tree` delegam para os serviços internos sem acoplar frameworks.
- **Isolamento de frameworks**: Typer/Click permanecem em `cli.py`; Rich/Tabulate ficam confinados a `formatters.py` e `services/tables.py`.
- **Contratos e modelos**: `models.py`, `constants.py` e `protocols.py` documentam os tipos validados com Pydantic v2.
- **Resultados previsíveis**: operações retornam `FlextResult[T]` para composições seguras.

## Navegação rápida

- **Primeiros passos**: [Getting Started](getting-started.md)
- **Arquitetura**: [Architecture](architecture.md)
- **APIs**: [API Reference](api-reference.md)
- **Contribuição**: [Development Guide](development.md)

## O que observar na 0.10.0

- Compatibilidade mantida pelos wrappers principais (`print`, `create_table`, `create_tree`).
- Serviços com estado em `services/` separados de utilidades stateless em `formatters.py`, `file_tools.py` e `utilities.py`.
- Configuração centralizada em `FlextCliSettings` e exposta via `FlextCliServiceBase` para todos os serviços.
- Registro do identificador da aplicação no `FlextContainer` na inicialização do `FlextCli`.

## Status

- **Versão**: 0.10.0 (ver `src/flext_cli/__version__.py`).
- **Compatibilidade**: Python 3.13+.
- **QA**: Ruff, Pyright e Pytest conforme configurado no projeto.

## Links úteis

- [Main README](../README.md)
- [Examples](../examples/)
- [Tests](../tests/)
