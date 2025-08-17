"""Debug commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.table import Table

from flext_cli.cmd_debug import (
    FLEXT_API_AVAILABLE,
    SENSITIVE_VALUE_PREVIEW_LENGTH,
    _validate_dependencies,
    connectivity as _connectivity_cmd,
    debug_cmd,
    env as _env_cmd,
    get_config,
    get_default_cli_client,
    paths as _paths_cmd,
    performance as _performance_cmd,
    trace as _trace_cmd,
    validate as _validate_cmd,
)


class _CommandShim:
    """Shim that is both a Click command and a direct-call function.

    When called with a Click context as first argument, dispatch directly to the
    underlying callback, avoiding Click's CLI parsing. Otherwise, behave like
    the wrapped Click command.
    """

    def __init__(
        self,
        command: click.Command,
        *,
        prefer_passed_ctx: bool = False,
    ) -> None:
        self._cmd = command
        self._prefer_passed_ctx = prefer_passed_ctx
        try:
            # Expose click decorator params for tests
            self.__click_params__ = getattr(command.callback, "__click_params__", [])
        except Exception:
            self.__click_params__ = []

    def __call__(
        self,
        *args: object,
        **kwargs: object,
    ) -> object:  # pragma: no cover - thin shim
        if args:
            first = args[0]
            # Accept both real Click contexts and test doubles that expose `.obj`
            if isinstance(first, click.Context) or hasattr(first, "obj"):
                callback = self._cmd.callback
                wrapped = getattr(callback, "__wrapped__", None)
                if (
                    self._prefer_passed_ctx
                    and wrapped is not None
                    and not isinstance(first, click.Context)
                ):
                    # For commands like validate(): allow tests to spy on ctx.exit
                    from contextlib import suppress as _suppress  # noqa: PLC0415

                    with _suppress(Exception):
                        # Ensure patched `get_config` in this module is used inside the wrapped function
                        wrapped.__globals__["get_config"] = get_config
                    return wrapped(first, *args[1:], **kwargs)

                # Default: execute within a temporary active click context so
                # click.get_current_context works and ctx.exit raises SystemExit.
                temp_ctx = (
                    first
                    if isinstance(first, click.Context)
                    else click.Context(self._cmd)
                )
                if not isinstance(first, click.Context) and hasattr(first, "obj"):
                    from contextlib import suppress as _suppress  # noqa: PLC0415

                    with _suppress(Exception):
                        temp_ctx.obj = first.obj

                # Execute the callback within the active context
                try:
                    target = getattr(callback, "__wrapped__", callback)
                    if target and hasattr(target, "__globals__") and target.__globals__:
                        target.__globals__["get_config"] = get_config
                except Exception:
                    ...

                # Ensure the context is active when calling the callback
                if callback:
                    # Avoid `with temp_ctx:` since click.Context is not a context manager
                    return callback(*args[1:], **kwargs)
                return None
        return self._cmd(*args, **kwargs)

    def __getattr__(self, name: str) -> object:  # pragma: no cover - delegation
        return getattr(self._cmd, name)


# Public command objects with dual-behavior callable shim
connectivity = _CommandShim(_connectivity_cmd, prefer_passed_ctx=True)
performance = _CommandShim(_performance_cmd, prefer_passed_ctx=True)
validate = _CommandShim(_validate_cmd, prefer_passed_ctx=True)
trace = _CommandShim(_trace_cmd)
env = _CommandShim(_env_cmd)
paths = _CommandShim(_paths_cmd)

__all__ = [
    "FLEXT_API_AVAILABLE",
    "SENSITIVE_VALUE_PREVIEW_LENGTH",
    "Path",
    "Table",
    "_validate_dependencies",
    "connectivity",
    "debug_cmd",
    "env",
    "get_config",
    "get_default_cli_client",
    "paths",
    "performance",
    # Re-exports for tests patching
    "sys",
    "trace",
    "validate",
]
