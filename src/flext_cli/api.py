"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
import threading
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from typing import ClassVar, TypeIs

from click import Command
from flext_core import (
    FlextContainer as container,
    FlextLogger as logger_core,
    FlextRuntime as runtime,
    r,
)
from pydantic import ValidationError

from flext_cli import (
    FlextCliAppBase,
    FlextCliCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliCore,
    FlextCliDebug,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliMixins,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliServiceBase,
    FlextCliSettings,
    FlextCliTables,
    c,
    m,
    p,
    t,
    u,
)


class FlextCli:
    """Coordinate CLI operations and expose domain services.

    Singleton facade over CLI services (core, cmd, output, prompts, tables).
    Thread-safe lazy initialization. All operations return r[T].
    """

    class Base(FlextCliCli):
        """CLI base."""

    class Runner(FlextCliCmd):
        """CLI runner."""

    class Commands(FlextCliCommands):
        """CLI commands."""

    class Params(FlextCliCommonParams):
        """CLI params."""

    class Output(FlextCliOutput):
        """CLI output."""

    class Formatters(FlextCliFormatters):
        """CLI formatters."""

    class Tables(FlextCliTables):
        """CLI tables."""

    class Prompts(FlextCliPrompts):
        """CLI prompts."""

    class FileTools(FlextCliFileTools):
        """CLI file tools."""

    class Config(FlextCliSettings):
        """CLI config."""

    class Core(FlextCliCore):
        """CLI core."""

    class Debug(FlextCliDebug):
        """CLI debug."""

    class Mixins(FlextCliMixins):
        """CLI mixins."""

    class AppBase(FlextCliAppBase[FlextCliSettings]):
        """CLI app base (abstract). Subclasses must implement _register_commands."""

    _instance: ClassVar[FlextCli | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()
    logger: logger_core
    config: FlextCliSettings
    formatters: FlextCliFormatters
    file_tools: FlextCliFileTools
    output: FlextCliOutput
    core: FlextCliCore
    cmd: FlextCliCmd
    prompts: FlextCliPrompts
    _name: str
    _version: str
    _description: str
    _container: container
    _cli: FlextCliCli

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        super().__init__()
        self._name = c.Cli.CliDefaults.DEFAULT_APP_NAME
        self._version = c.Cli.CLI_VERSION
        self._description = f"{self._name}{c.Cli.APIDefaults.APP_DESCRIPTION_SUFFIX}"
        self.logger = logger_core(__name__)
        self._container = container()
        key = c.Cli.APIDefaults.CONTAINER_REGISTRATION_KEY
        if not self._container.has_service(key):
            self._container.register(key, key)
        self.formatters, self.file_tools = (FlextCliFormatters(), FlextCliFileTools())
        self.output, self.core, self.cmd, self.prompts = (
            FlextCliOutput(),
            FlextCliCore(),
            FlextCliCmd(),
            FlextCliPrompts(),
        )
        self._cli = FlextCliCli()
        self._commands: MutableMapping[str, p.Cli.CliRegisteredCommand] = {}
        self._groups: MutableMapping[str, p.Cli.CliRegisteredCommand] = {}
        self._plugin_commands: MutableMapping[str, p.Cli.CliRegisteredCommand] = {}
        self.config = FlextCliServiceBase.get_cli_config()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: MutableMapping[str, set[str]] = {}
        self._users: MutableMapping[str, Mapping[str, t.Cli.JsonValue]] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @staticmethod
    def _is_ignorable_delete(result: r[bool]) -> bool:
        """Check if delete failure is file-not-found (ignorable)."""
        if result.is_success:
            return True
        err = str(result.error).lower()
        return any(
            p in err for p in ("not found", "no such file", "does not exist", "errno 2")
        )

    @staticmethod
    def _validate_token_string(token: str) -> r[bool]:
        """Validate token string; raises ValueError if empty."""
        if not token or not token.strip():
            return r[bool].fail("Token cannot be empty")
        return r[bool].ok(value=True)

    @staticmethod
    def execute_cli() -> r[bool]:
        """Execute the CLI application."""
        return r[bool].ok(value=True)

    @staticmethod
    def validate_credentials(username: str, password: str) -> r[bool]:
        """Validate credentials using Pydantic 2."""
        validation_result = u.try_(
            lambda: m.Cli.PasswordAuth(
                username=username,
                password=password,
                realm="",
            ),
        ).map_error(str)
        if validation_result.is_failure:
            return r[bool].fail(validation_result.error or "")
        return r[bool].ok(value=True)

    def authenticate(
        self,
        credentials: m.Cli.PasswordAuth | m.Cli.TokenData | t.StrMapping,
    ) -> r[str]:
        """Authenticate user with provided credentials (model or mapping)."""
        if isinstance(credentials, m.Cli.TokenData):
            return self._authenticate_with_token(credentials)
        if isinstance(credentials, m.Cli.PasswordAuth):
            return self._authenticate_with_credentials(credentials)
        if c.Cli.DictKeys.TOKEN in credentials:
            token_data_result = u.try_(
                lambda: m.Cli.TokenData(
                    token=str(credentials[c.Cli.DictKeys.TOKEN]),
                    expires_at="",
                    token_type=str(credentials.get("token_type", "")),
                ),
            ).map_error(str)
            if token_data_result.is_failure:
                return r[str].fail(token_data_result.error or "")
            return self._authenticate_with_token(token_data_result.value)
        if (
            c.Cli.DictKeys.USERNAME in credentials
            and c.Cli.DictKeys.PASSWORD in credentials
        ):
            password_auth_result = u.try_(
                lambda: m.Cli.PasswordAuth.model_validate({
                    c.Cli.DictKeys.USERNAME: credentials[c.Cli.DictKeys.USERNAME],
                    c.Cli.DictKeys.PASSWORD: credentials[c.Cli.DictKeys.PASSWORD],
                }),
            ).map_error(str)
            if password_auth_result.is_failure:
                return r[str].fail(password_auth_result.error or "")
            return self._authenticate_with_credentials(password_auth_result.value)
        return r[str].fail(c.Cli.ErrorMessages.INVALID_CREDENTIALS)

    def clear_auth_tokens(self) -> r[bool]:
        """Clear authentication tokens using file tools domain library."""
        for path in (self.config.token_file, self.config.refresh_token_file):
            del_result = self.file_tools.delete_file(str(path))
            if not self._is_ignorable_delete(del_result):
                return r[bool].fail(
                    c.Cli.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                        error=del_result.error,
                    ),
                )
        self._valid_tokens.clear()
        return r[bool].ok(value=True)

    def command(
        self,
        name: str | None = None,
    ) -> Callable[[p.Cli.CliCommandFunction], p.Cli.CliRegisteredCommand]:
        """Register a command using CLI framework abstraction."""
        return self._entity_decorator(c.Cli.EntityType.COMMAND, name)

    def _create_table(
        self,
        data: Mapping[str, t.Cli.JsonValue]
        | Sequence[Mapping[str, t.Cli.JsonValue]]
        | None,
        headers: t.StrSequence | None = None,
        _title: str | None = None,
    ) -> r[str]:
        """Create a formatted ASCII table (internal; use show_table for display)."""
        if data is None:
            return r[str].fail("Table data cannot be None")
        if isinstance(data, Mapping):
            table_data: Sequence[Mapping[str, t.Cli.JsonValue]] = [dict(data.items())]
        elif isinstance(data, list):
            table_data = data
        elif isinstance(data, tuple):
            table_data: list[Mapping[str, t.Cli.JsonValue]] = []
            for row in data:
                table_data.append(row)
        else:
            table_data: list[Mapping[str, t.Cli.JsonValue]] = []
        table_config = m.Cli.TableConfig(
            headers=headers or "keys",
            show_header=True,
            table_format="simple",
            floatfmt=".4g",
            numalign="decimal",
            stralign="left",
            align="left",
            missingval="",
            showindex=False,
            colalign=None,
            disable_numparse=False,
        )
        return FlextCliTables.create_table(table_data, config=table_config)

    def create_tree(self, label: str) -> r[FlextCliFormatters.Tree]:
        """Create a Rich tree (FlextCliFormatters.Tree; add() returns None by default)."""
        return FlextCliFormatters.create_tree(label)

    def execute(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Execute CLI service with railway pattern."""
        result_dict: Mapping[str, t.Cli.JsonValue] = {
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": "0.1.0",
            "components": {
                "config": "available",
                "formatters": "available",
                "core": "available",
                "prompts": "available",
            },
        }
        return r[Mapping[str, t.Cli.JsonValue]].ok(result_dict)

    def get_auth_token(self) -> r[str]:
        """Get authentication token using Pydantic 2 validation."""
        result = self.file_tools.read_json_file(str(self.config.token_file))
        if result.is_failure:
            return self._handle_token_file_error(str(result.error))
        data = result.value
        if not data or (runtime.is_dict_like(data) and (not data)):
            return r[str].fail(c.Cli.ErrorMessages.TOKEN_FILE_EMPTY)
        try:
            token_data = m.Cli.TokenData.model_validate(data)
            return r[str].ok(token_data.token)
        except ValidationError:
            token_result = u.extract(data, c.Cli.DictKeys.TOKEN, required=True)
            if token_result.is_success:
                token_value = token_result.value
                if u.is_dict_like(token_value):
                    return r[str].fail(c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR)
                if not isinstance(token_value, str):
                    return r[str].fail(c.Cli.APIDefaults.TOKEN_VALUE_TYPE_ERROR)
                extracted_token = str(token_value).strip()
                if extracted_token:
                    return r[str].ok(extracted_token)
            return r[str].fail(c.Cli.ErrorMessages.TOKEN_FILE_EMPTY)

    def group(
        self,
        name: str | None = None,
    ) -> Callable[[p.Cli.CliCommandFunction], p.Cli.CliRegisteredCommand]:
        """Register a command group using CLI framework abstraction."""
        return self._entity_decorator(c.Cli.EntityType.GROUP, name)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        auth_result = self.get_auth_token()
        return auth_result.is_success

    def print(self, message: str, style: str | None = None) -> None:
        """Print a message with optional style."""
        FlextCliFormatters().print(message, style=style or "")

    def _print_table(self, table_str: str) -> None:
        """Print a formatted table string (internal; use show_table for display)."""
        FlextCliFormatters().print(table_str)

    def show_table(
        self,
        data: Mapping[str, t.Cli.JsonValue] | Sequence[Mapping[str, t.Cli.JsonValue]],
        headers: t.StrSequence | None = None,
        title: str | None = None,
    ) -> None:
        """Create and print a table in one call. No result to capture; no branching."""
        table_result = self._create_table(data=data, headers=headers, _title=title)
        if table_result.is_success:
            self._print_table(table_result.value)
        else:
            self.print(f"Table error: {table_result.error}", style="red")

    def save_auth_token(self, token: str) -> r[bool]:
        """Save authentication token using file tools domain library."""
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return validation
        token_data: t.Cli.JsonValue = {c.Cli.DictKeys.TOKEN: token}
        write_result = self.file_tools.write_json_file(
            str(self.config.token_file),
            m.Cli.DisplayData.model_validate({"data": token_data}),
        )
        if write_result.is_failure:
            return r[bool].fail(
                c.Cli.ErrorMessages.TOKEN_SAVE_FAILED.format(error=write_result.error),
            )
        self._valid_tokens.add(token)
        return r[bool].ok(value=True)

    def _authenticate_with_credentials(self, credentials: m.Cli.PasswordAuth) -> r[str]:
        """Authenticate using PasswordAuth model (credentials already validated)."""
        logger_core(__name__).debug(
            "Authenticating with password auth",
            username=credentials.username,
        )
        token = secrets.token_urlsafe(c.Cli.APIDefaults.TOKEN_GENERATION_BYTES)
        self._valid_tokens.add(token)
        return r[str].ok(token)

    def _authenticate_with_token(self, credentials: m.Cli.TokenData) -> r[str]:
        """Authenticate using token (TokenData model)."""
        token = credentials.token
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return r[str].fail(validation.error or "")
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return r[str].fail(
                c.Cli.ErrorMessages.TOKEN_SAVE_FAILED.format(error=save_result.error),
            )
        return r[str].ok(token)

    def _entity_decorator(
        self,
        entity_type: c.Cli.EntityType,
        name: str | None = None,
    ) -> Callable[[p.Cli.CliCommandFunction], p.Cli.CliRegisteredCommand]:
        """Return decorator that registers a CLI entity."""

        def decorator(func: p.Cli.CliCommandFunction) -> p.Cli.CliRegisteredCommand:
            return self._register_cli_entity(entity_type, name, func)

        return decorator

    def _get_token_error_message(self, error_str: str) -> str:
        """Get error message based on exception content."""
        kw_map: t.StrMapping = {
            "dict": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "mapping": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "t.NormalizedValue": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "string": c.Cli.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
            "str": c.Cli.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
        }
        for kw, msg in kw_map.items():
            if kw in error_str:
                return msg
        return c.Cli.ErrorMessages.TOKEN_FILE_EMPTY

    def _handle_token_file_error(self, error_str: str) -> r[str]:
        """Handle file read error during token loading."""
        if u.Cli.is_file_not_found_error(error_str):
            return r[str].fail(c.Cli.ErrorMessages.TOKEN_FILE_NOT_FOUND)
        return r[str].fail(
            c.Cli.ErrorMessages.TOKEN_LOAD_FAILED.format(error=error_str),
        )

    def _register_cli_entity(
        self,
        entity_type: c.Cli.EntityType,
        name: str | None,
        func: p.Cli.CliCommandFunction,
    ) -> p.Cli.CliRegisteredCommand:
        """Register a CLI entity (command or group) with framework abstraction."""
        entity_name: str = (
            name if name is not None else str(getattr(func, "__name__", str(func)))
        )
        factory = (
            self._cli.create_command_decorator
            if entity_type == "command"
            else self._cli.create_group_decorator
        )
        decorated_func = factory(name=entity_name)(func)
        if not FlextCli._is_registered_command(decorated_func):
            msg = "decorated_func must implement CliRegisteredCommand protocol"
            raise TypeError(msg)
        registry = self._commands if entity_type == "command" else self._groups
        registered_command: p.Cli.CliRegisteredCommand = decorated_func
        registry[entity_name] = registered_command
        return registered_command

    @staticmethod
    def _is_registered_command(
        obj: t.Cli.JsonValue | p.Cli.DecoratorCommandLike | Command,
    ) -> TypeIs[p.Cli.CliRegisteredCommand]:
        """Narrow to CliRegisteredCommand when protocol attributes are present."""
        return callable(obj) and hasattr(obj, "name") and hasattr(obj, "callback")


__all__ = ["FlextCli"]
