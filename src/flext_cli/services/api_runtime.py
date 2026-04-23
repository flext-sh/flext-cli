"""Runtime mixin used by the public CLI API facade."""

from __future__ import annotations

from typing import override

from flext_cli import c, p, r, t, u


class FlextCliApiRuntime:
    """Runtime behavior composed by the public API facade."""

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Execute CLI service with railway pattern."""
        result_dict: t.JsonMapping = {
            c.Cli.DICT_KEY_STATUS: c.Cli.ServiceStatus.OPERATIONAL,
            c.Cli.DICT_KEY_SERVICE: c.Cli.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": c.Cli.CLI_VERSION,
            "components": {
                "settings": "available",
                "formatters": "available",
                "prompts": "available",
                "rules": "available",
            },
        }
        return r[t.JsonMapping].ok(result_dict)


__all__: list[str] = ["FlextCliApiRuntime"]
