<!-- AUTO-GENERATED FILE — regenerate through `make gen` from the workspace root. -->
<!-- Source of truth: `<workspace-root>/docs/guides/using-flext-cli.md`; adjust that workspace source, never this member projection. -->

# flext-cli - Using flext-cli

> Project profile: `flext-cli`

<!-- TOC START -->

- [Aliases](#aliases)
- [Purpose](#purpose)
- [Settings](#settings)
- [Model-driven command](#model-driven-command)
- [Single-command CLI](#single-command-cli)
- [Testing a command](#testing-a-command)
- [Exit-code contract](#exit-code-contract)
- [Managed process communication](#managed-process-communication)
- [Guarded directory materialization](#guarded-directory-materialization)
- [Good practices](#good-practices)
- [Bad practices](#bad-practices)
- [Related](#related)

<!-- TOC END -->

`flext_cli` provides a unified Typer abstraction for model-driven CLI applications.

## Aliases

Import the aliases used by each example from the public `flext_cli` package root.

`flext_cli` reexports `d`, `e`, `h`, `r`, `x` from `flext_core`.

| Alias | Purpose                                   |
| ----- | ----------------------------------------- |
| `c`   | constants                                 |
| `m`   | models                                    |
| `p`   | protocols                                 |
| `r`   | result (reexported from `flext_core`)     |
| `s`   | service / runtime (`FlextCliServiceBase`) |
| `t`   | typings                                   |
| `u`   | utilities                                 |

**Important:** `s` is the service/runtime alias. CLI settings are accessed via
`FlextCliSettings` (no short alias).

## Purpose

- Define CLI commands as Pydantic models.
- Let `FlextCliCli` convert model fields into Typer options.
- Keep output formatting, prompts, and runtime consistent across FLEXT CLI tools.

## Settings

Import the existing settings class; without overrides, `fetch_global()` returns
its shared per-class singleton:

```python
from flext_cli import FlextCliSettings

settings = FlextCliSettings.fetch_global()
```

If you need a project-specific subclass, extend `FlextSettings` (or `FlextCliSettings`)
with `m.SettingsConfigDict`:

```python
from flext_core import FlextSettings, m


class FlextApiSettings(FlextSettings):
    """API settings read from ``FLEXT_API_*`` environment variables."""

    model_config = m.SettingsConfigDict(env_prefix="FLEXT_API_", extra="ignore")
```

## Model-driven command

```python
from __future__ import annotations

from flext_cli import FlextCliCli, FlextCliSettings, m, t

settings = FlextCliSettings.fetch_global()


class GreetInput(m.BaseModel):
    """Greeting command input."""

    name: str
    shout: bool = False


def greet_handler(model: GreetInput) -> t.JsonValue:
    """Build the greeting payload for one input model.

    Returns:
        A JSON payload carrying the greeting message.

    """
    message = f"Hello, {model.name}!"
    if model.shout:
        message = message.upper()
    return {"message": message}


command = FlextCliCli.model_command(
    model_cls=GreetInput,
    handler=greet_handler,
    settings=settings,
)
cli = FlextCliCli()
app = cli.create_app_with_common_params(name="greeting", help_text="Greeting commands")
cli.register_command(app, name="greet", help_text="Build a greeting", command=command)
```

**Common mistakes to avoid:**

- `FlextCliCli.build_model_command(...)` does not exist; use
  `FlextCliCli.model_command(...)`.
- `m.CliInput` / `m.CliOutput` do not exist; use plain `m.BaseModel` subclasses.

## Single-command CLI

When a module or console script exposes exactly one operation,
`cli.run_result_command` is the whole CLI: it builds the application, registers
one result command named after `prog_name`, runs it and returns the exit code.
The application holds only that command, so Typer builds it as a single command
and the options follow the program name directly (`python -m pkg.mod --name Ada`),
with no subcommand token.

```python
from __future__ import annotations

from flext_cli import c, cli, m, p, r


class GreetingRequest(m.BaseModel):
    """Greet one person by name."""

    name: str


def greet(request: GreetingRequest) -> p.Result[str]:
    """Return the greeting for one request."""
    return r[str].ok(f"Hello, {request.name}!")


code = cli.run_result_command(
    GreetingRequest,
    greet,
    prog_name="greet",
    args=["--name", "Ada"],
    success_formatter=str,
)
assert code == c.Cli.EXIT_CODE_SUCCESS
```

- The request model's docstring is the command help.
- Without `success_formatter` a successful run prints nothing; pass `str`,
  `lambda value: value.model_dump_json(indent=2)` or any other formatter to print.
- `args=None` reads `sys.argv[1:]`.
- The call returns the exit code of the contract below and raises no `SystemExit`;
  a domain failure prints its message once on stderr.

`examples/ex_13_single_result_command.py` runs this pattern as a module.

## Testing a command

Use `FlextCliCli.invoke_app` with the adapter-owned application, not Typer's `CliRunner`
directly. This independent example constructs and invokes a real model-backed command;
handlers return their value but do not automatically print it.

```python
from tests import c, m, tm

from flext_cli import FlextCliCli


class GreetInput(m.BaseModel):
    """Greeting command input."""

    name: str


def greet_handler(model: GreetInput) -> str:
    """Return the greeting for one input model."""
    return f"Hello, {model.name}!"


def test_greet_command() -> None:
    """The registered greeting command exits successfully."""
    cli = FlextCliCli()
    app = cli.create_app_with_common_params(
        name="greeting",
        help_text="Greeting commands",
    )
    command = cli.model_command(model_cls=GreetInput, handler=greet_handler)
    cli.register_command(
        app,
        name="greet",
        help_text="Build a greeting",
        command=command,
    )
    invocation = cli.invoke_app(app, args=["greet", "--name", "Ada"])
    tm.ok(invocation.success)
    tm.that(invocation.value.exit_code, eq=c.Cli.EXIT_CODE_SUCCESS)
    assert greet_handler(GreetInput(name="Ada")) == "Hello, Ada!"
```

## Exit-code contract

A command registered with `cli.register_result_command` and run through
`cli.execute_app` / `cli.finalize_result` exits with one of three codes, all declared
in `c.Cli`:

| Outcome                   | Exit code                 | Output                                      |
| ------------------------- | ------------------------- | ------------------------------------------- |
| Success                   | `c.Cli.EXIT_CODE_SUCCESS` | the formatted result                        |
| Usage error               | `c.Cli.EXIT_CODE_USAGE`   | Click's usage line and one `Error:` message |
| Domain failure (`r.fail`) | `c.Cli.EXIT_CODE_FAILURE` | the failure message, once on stderr         |

A usage error is a missing required option, an unknown option, a value of the wrong
type, or input the request model rejects (for example a `Field(gt=0)` violated by
`--block 0`). Click owns its rendering: the message names the option as the user
types it (`Missing option '--folder'.`) and no traceback is printed. The request
model's `ValidationError` is converted once, where the model is validated, into
Click's own `BadParameter`.

A domain failure renders through the CLI output boundary only: the styled
failure message, then the cause's traceback, notes and error code. The border
emits no structured log event for the same failure, so stderr carries it once.
`cli.run_result_command` returns the same three codes.

## Managed process communication

The existing `u.Cli.process_start` owner returns `p.Cli.ManagedProcess`; it remains
responsible for spawning, captured streams and child lifecycle. Its
`stdin_write(data, timeout=...)` contract sends the complete byte message without
closing stdin or starting another process. The default deadline comes from Core's
`c.DEFAULT_TIMEOUT_SECONDS`; a consumer may supply its remaining operation budget.
An absent input stream, an exited child, an invalid deadline or incomplete delivery
returns a failure before dependent work. Native I/O failures retain their original
exception and the number of bytes already sent. `stdout_read_until` reads the reply
on that same handle, and the caller still owns termination and reaping.

This communication contract supports the AI Hub JSONC document session: one SDK
parse retains its tree while Python composes the declared changes, then the same
child applies the complete batch. It does not authorize another process runner,
parser, hidden retry or unverified success. Qualification requires real request/reply
and failure evidence; this contract alone is not runtime proof.

## Guarded directory materialization

Directory creation consumes the original `m.Cli.AtomicDirectoryChainPlan`; it never
re-elects a parent after an effect. The native creator retains successful creation
receipts in the caller's optional progress collection and leaves those directories
in place if a later native operation fails. Its original exception retains those
receipts as causal evidence. The existing `atomic_create_directory_chain_guarded`
Result boundary also exposes the created receipts in structured failure data.
Neither path restores a prior image or compensates published directories. Consumers
use the retained state to diagnose and plan forward, rather than copying the chain
algorithm into their own application.

## Good practices

- Use plain `m.BaseModel` subclasses for command input.
- Read settings via `FlextCliSettings.fetch_global()`; `s` is the service/runtime alias.
- Avoid ad-hoc Typer functions and direct `u.Cli.print()`/`sys.exit()` in commands.

## Bad practices

Do not replace the model command with an untyped ad-hoc handler or bypass the adapter
with direct printing and process termination. Register the model-backed command through
the public facade as shown above. A corrected handler consumes its declared input model
and returns its value:

```python
from flext_cli import m


class GreetInput(m.BaseModel):
    """Greeting command input."""

    name: str


def greet_handler(model: GreetInput) -> str:
    """Return the greeting for one input model."""
    return f"Hello, {model.name}!"


greeting = greet_handler(GreetInput(name="Ada"))  # "Hello, Ada!"
```

## Related

- `flext-cli/src/flext_cli/services/cli.py`
- Generated flext-core API reference
