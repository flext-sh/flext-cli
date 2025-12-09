# CLI Architecture

Panorama da arquitetura implementada no **flext-cli** 0.10.0, conforme o código-fonte.

## Princípios

- **Facade única**: `FlextCli` compõe serviços (`core`, `cmd`, `output`, `prompts`, `tables`) e utilidades (`formatters`, `file_tools`, `utilities`) e mantém wrappers legados.
- **Fronteiras claras de framework**: Typer/Click ficam em `cli.py`; Rich/Tabulate são usados apenas em `formatters.py` e `services/tables.py`.
- **Contratos explícitos**: `models.py`, `context.py` e `protocols.py` definem os tipos de entrada/saída validados com Pydantic v2.
- **Retornos com `FlextResult[T]`**: erros e sucessos são encadeáveis em autenticação, orquestração e I/O.

## Mapa dos módulos

```
src/flext_cli/
├── api.py                # Facade FlextCli e base para CLIs Typer
├── base.py               # Base de serviços com acesso ao config singleton
├── cli.py                # Única fronteira com Typer/Click
├── cli_params.py         # Parâmetros reutilizáveis para comandos Typer/Click
├── commands.py           # Registro e resolução de comandos estruturais
├── config.py             # Singleton de configuração validada
├── constants.py          # Constantes e mensagens compartilhadas
├── context.py            # Contexto de execução imutável
├── debug.py              # Utilidades de depuração
├── file_tools.py         # I/O de arquivos (texto, JSON, YAML, CSV, zip)
├── formatters.py         # Saída Rich e helpers de layout
├── mixins.py             # Mixins de logging e contexto herdados do flext-core
├── models.py             # Modelos Pydantic usados pelos serviços e workflows
├── protocols.py          # Protocolos estruturais para CLI, prompt e exibição
├── utilities.py          # Helpers utilitários (validação, mapeamento, config)
├── services/
│   ├── core.py           # Registro/execução de comandos, sessões, plugins e caches
│   ├── cmd.py            # Operações de configuração e ponte com utilidades/arquivos
│   ├── output.py         # Formatação e exibição de resultados
│   ├── prompts.py        # Interação com usuário (prompt/confirm/select)
│   └── tables.py         # Geração de tabelas ASCII via Tabulate
└── __init__.py           # Exporta API pública e reforça isolamento de frameworks
```

## Fluxo em tempo de execução

1. **Bootstrap**: `FlextCli` registra o identificador do CLI no `FlextContainer` e instancia os serviços e utilidades compartilhados.
2. **Registro de comandos**: modelos em `commands.py` são validados em `FlextCliCore.register_command` antes de serem armazenados.
3. **Execução**: `FlextCliCore.execute_command` resolve o comando registrado; `FlextCliCmd` fornece operações utilitárias ligadas à configuração persistida.
4. **Entrada/Saída**: `prompts.py` coleta entrada; `output.py`, `formatters.py` e `tables.py` geram saídas em Rich/ASCII/JSON/YAML/CSV sem expor o Rich diretamente.
5. **Configuração e contexto**: `config.py` gerencia configuração imutável; `context.py` acompanha execução e sessões armazenadas em `core`.

## Integração com flext-core

- `FlextResult`: envelope de sucesso/falha usado por todas as operações públicas.
- `FlextService`: herdado em `FlextCliServiceBase` para logging, contexto e ciclo de vida.
- `FlextContainer`: registro do identificador do CLI ao inicializar `FlextCli` ou `FlextCliCli`.

## Exemplo mínimo

```python
from flext_cli import FlextCli

cli = FlextCli()
command = cli.Models.CliCommand(name="hello", handler="handlers:hello")
cli.core.register_command(command)

# Execução usando o registro interno
cli.core.execute_command(command.name)

# Wrappers permanecem para compatibilidade
table = cli.create_table([{"name": "Alice", "age": 30}], headers=["name", "age"]).unwrap()
cli.print(table, style="green")
```

## Referências rápidas

- **API**: `docs/api-reference.md`
- **Guia de desenvolvimento**: `docs/development.md`

## Related Documentation

**Within Project**:

- [Getting Started](getting-started.md) - Installation and basic usage
- [API Reference](api-reference.md) - Complete API documentation
- [Development Guide](development.md) - Contributing and extending

**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/overview.md) - Clean architecture and CQRS patterns
- [flext-core Service Patterns](https://github.com/organization/flext/tree/main/flext-core/docs/guides/service-patterns.md) - Service patterns and dependency injection

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
