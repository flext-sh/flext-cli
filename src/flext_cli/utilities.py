"""FLEXT CLI utility facade."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from flext_cli._utilities._cli_namespace import (
        FlextCliUtilitiesCli,
    )
    from flext_core.utilities import FlextUtilities as _FlextCoreUtilitiesBase
else:

    class FlextCoreUtilitiesBaseProxyMeta(type):
        """Proxy metaclass that materializes the core utility base on demand."""

        _target_cls: type | None = None

        def _target(cls) -> type:
            if cls._target_cls is None:
                module = import_module("flext_core.utilities")
                cls._target_cls = cast("type", getattr(module, "u"))
            return cls._target_cls

        def __getattr__(cls, name: str) -> object:
            return getattr(cls._target(), name)

    class _FlextCoreUtilitiesBase(metaclass=FlextCoreUtilitiesBaseProxyMeta):
        """Lazy proxy for inherited ``flext_core.u`` utilities."""

        def __getattr__(self, name: str) -> object:
            return getattr(type(self), name)

    class FlextCliUtilitiesCliProxyMeta(type):
        """Proxy metaclass that materializes the CLI namespace on demand."""

        _target_cls: type | None = None

        def _target(cls) -> type:
            if cls._target_cls is None:
                module = import_module("flext_cli._utilities._cli_namespace")
                cls._target_cls = cast("type", getattr(module, "FlextCliUtilitiesCli"))
            return cls._target_cls

        def __getattr__(cls, name: str) -> object:
            return getattr(cls._target(), name)

        def __setattr__(cls, name: str, value: object) -> None:
            if name.startswith("_"):
                super().__setattr__(name, value)
                return
            setattr(cls._target(), name, value)

        def __delattr__(cls, name: str) -> None:
            if name.startswith("_"):
                super().__delattr__(name)
                return
            delattr(cls._target(), name)

        def __call__(cls) -> object:
            return cls._target()()

    class FlextCliUtilitiesCli(metaclass=FlextCliUtilitiesCliProxyMeta):
        """Lazy proxy for the heavy ``u.Cli`` utility namespace."""


class FlextCliUtilities(_FlextCoreUtilitiesBase):
    """CLI utility facade composed from internal utility mixins."""

    Cli = FlextCliUtilitiesCli


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]
